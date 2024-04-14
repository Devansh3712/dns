import argparse
import socket
from copy import deepcopy

from dns.answer import Answer
from dns.header import RCode
from dns.message import Message


def main(host: str, port: int, resolver: str | None):
    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_socket.bind((host, port))

    while True:
        data, source = dns_socket.recvfrom(512)
        request = Message.decode(data)

        answers: list[Answer] = []
        if resolver:
            resolver_host, resolver_port = resolver.split(":")
            resolver_port = int(resolver_port)

            rheader = deepcopy(request.header)
            rheader.qdcount = 1

            for question in request.questions:
                message = rheader.encode() + question.encode()
                resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                resolver_socket.sendto(message, (resolver_host, resolver_port))
                data, _ = resolver_socket.recvfrom(512)

                resolver_response = Message.decode(data)
                answers.extend(resolver_response.answers)

        request.header.qr = 1
        request.header.qdcount = request.header.ancount = 0
        request.header.rcode = RCode(4) if request.header.opcode else RCode(0)
        response = Message(header=request.header)

        for question in request.questions:
            response.add_question(question)
        for answer in answers:
            response.add_answer(answer)

        dns_socket.sendto(response.encode(), source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="host to run server on"
    )
    parser.add_argument("--port", type=int, default=2053, help="port to run server on")
    parser.add_argument("--resolver", type=str, help="specify the DNS resolver address")
    args = parser.parse_args()

    main(args.host, args.port, args.resolver)

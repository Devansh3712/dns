import argparse
import logging
import socket
from copy import deepcopy

from redis import Redis

from dns.message import Message
from dns.record import Record


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)s: %(asctime)s %(message)s",
    datefmt="%m-%d-%Y %H:%M:%S",
    level=logging.INFO,
)

redis = Redis(host="localhost", port=6379, decode_responses=True)


def resolve(resolver: str, request: Message) -> list[Record]:
    resolver_host, resolver_port = resolver.split(":")
    resolver_port = int(resolver_port)

    request_header = deepcopy(request.header)
    request_header.qdcount = 1

    answers: list[Record] = []
    for question in request.questions:
        name = question.qname.decode()
        if ip := redis.get(name):
            answers.append(
                Record(
                    qname=question.qname,
                    qtype=question.qtype,
                    qclass=question.qclass,
                    ttl=redis.ttl(name),
                    rdlength=len(ip),
                    rdata=ip,
                )
            )
            continue

        message = request_header.encode() + question.encode()
        resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        resolver_socket.sendto(message, (resolver_host, resolver_port))
        data, _ = resolver_socket.recvfrom(512)

        resolver_response = Message.decode(data)
        answers.extend(resolver_response.answers)

        for answer in resolver_response.answers:
            redis.setex(answer.qname.decode(), answer.ttl, answer.rdata)

    return answers


def main(host: str, port: int, resolver: str | None):
    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_socket.bind((host, port))

    while True:
        data, source = dns_socket.recvfrom(512)
        request = Message.decode(data)
        logger.info(request.questions)

        if resolver:
            answers = resolve(resolver, request)
        else:
            ...

        response_header = request.header.to_response()
        response = Message(header=response_header)

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

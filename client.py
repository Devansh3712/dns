import argparse
import socket

from dns.header import *
from dns.question import *
from dns.message import *

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
request = Message(
    header=Header(
        id=1234,
        qr=0,
        opcode=0,
        aa=0,
        tc=0,
        rd=0,
        ra=0,
        z=0,
        rcode=RCode.NO_ERROR,
        qdcount=0,
        ancount=0,
        nscount=0,
        arcount=0,
    ),
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", type=str, nargs="*")
    args = parser.parse_args()

    for domain in args.domain:
        request.add_question(
            Question(qname=domain.encode(), qtype=QType.A, qclass=QClass.IN)
        )

    sock.sendto(request.encode(), ("0.0.0.0", 2053))
    data, _ = sock.recvfrom(512)

    response = Message.decode(data)
    for answer in response.answers:
        print(f"Domain: {answer.question.qname.decode()}\tIP: {answer.rdata}")

import struct
from dataclasses import dataclass
from io import BytesIO
from socket import inet_aton, inet_ntoa

from .question import Question, QClass, QType
from .utils import decode_name


@dataclass
class Answer:
    """
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                                               |
    /                                               /
    /                      NAME                     /
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TYPE                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     CLASS                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TTL                      |
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                   RDLENGTH                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
    /                     RDATA                     /
    /                                               /
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    """

    question: Question

    # The duration in seconds a record can be cached before
    # re-querying
    ttl: int

    # Length of the RDATA field in bytes
    rdlength: int

    # Variable length string of octets that describes a resource
    rdata: str

    def encode(self) -> bytes:
        return (
            self.question.encode()
            + struct.pack("!IH", self.ttl, self.rdlength)
            + inet_aton(self.rdata)
        )

    @staticmethod
    def decode(reader: BytesIO) -> "Answer":
        qname = decode_name(reader)
        data = reader.read(10)
        qtype, qclass, ttl, rdlength = struct.unpack("!HHIH", data)
        rdata = reader.read(rdlength)

        return Answer(
            question=Question(qname=qname, qtype=QType(qtype), qclass=QClass(qclass)),
            ttl=ttl,
            rdlength=rdlength,
            rdata=inet_ntoa(rdata),
        )

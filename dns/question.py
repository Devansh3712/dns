import struct
from enum import Enum
from dataclasses import dataclass
from io import BytesIO

from .utils import encode_name, decode_name


class QType(int, Enum):
    # A IPv4 host address
    A = 1
    # An authoritative name server
    NS = 2
    # A mail destination
    MD = 3
    # A mail forwarder
    MF = 4
    # The canonical name for an alias
    CNAME = 5
    # Marks the start of a zone of authority
    SOA = 6
    # A mailbox domain name
    MB = 7
    # A mail group member
    MG = 8
    # A mail rename domain name
    MR = 9
    # A null RR
    NULL = 10
    # A well known service description
    WKS = 11
    # A domain name pointer
    PTR = 12
    # Host information
    HINFO = 13
    # Mailbox or mail list information
    MINFO = 14
    # Mail exchange
    MX = 15
    # Text strings
    TXT = 16
    # A IPv6 host address
    AAAA = 28


class QClass(int, Enum):
    IN = 1  # Internet
    CS = 2  # CSNET class
    CH = 3  # CHAOS class
    HS = 4  # Hesiod


#   0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                                               |
# /                     QNAME                     /
# /                                               /
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                     QTYPE                     |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                     QCLASS                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
@dataclass
class Question:
    """The question section is used to carry the "question" in most
    queries (the parameters that define what is being asked).
    """

    # A domain name represented as a sequence of labels, where each
    # label consists of a length octet followed by the number of octets
    # The domain name terminates with the zero length octet
    qname: bytes

    # Type of record
    qtype: QType

    # Class of query
    qclass: QClass

    def encode(self) -> bytes:
        return encode_name(self.qname) + struct.pack(
            "!HH", self.qtype.value, self.qclass.value
        )

    @staticmethod
    def decode(reader: BytesIO) -> "Question":
        qname = decode_name(reader)
        data = reader.read(4)
        qtype, qclass = struct.unpack("!HH", data)
        return Question(qname=qname, qtype=QType(qtype), qclass=QClass(qclass))

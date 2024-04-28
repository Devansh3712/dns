import struct
from enum import Enum
from dataclasses import dataclass
from io import BytesIO


class RCode(int, Enum):
    NO_ERROR = 0
    # The name server was unable to interpret the query
    FORMAT_ERROR = 1
    # The name server was unable to process this query due to
    # a problem with the name server
    SERVER_FAILURE = 2
    # Signifies that the domain name referenced in the query
    # does not exist
    NAME_ERROR = 3
    # The name server does not support the requested kind of
    # query
    NOT_IMPLEMENTED = 4
    # The name server refuses to perform the specified operation
    # for policy reasons
    REFUSED = 5


#   0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                      ID                       |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    QDCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    ANCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    NSCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    ARCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
@dataclass
class Header:
    """The header includes fields that specify which of the remaining sections
    are present, and also specify whether the message is a query or a response.
    The size of the header is 12 bytes.
    """

    # Packet Identifier
    # A random ID assigned to query packets, response packets must
    # reply with the same ID
    id: int

    # Query/Response Indicator
    # 1 for reply packet, 0 for question packet
    qr: int

    # Operation Code
    # Kind of query in this message
    opcode: int

    # Authoritative Answer
    # 1 if the responding server owns the queried domain
    aa: int

    # Truncation
    # 1 if message is greater than 512 bytes
    # Always 0 in UDP messages
    tc: int

    # Recursion Desired
    # Sender sets this to 1 if the server should recursively resolve
    # this query
    rd: int

    # Recursion Available
    # Server sets this to 1 if recursion is available
    ra: int

    # Reserved
    # Used by DNSSEC queries
    z: int

    # Response Code
    # Indicates the status of the response
    rcode: RCode

    # Question Count
    # Number of questions in the Question section
    qdcount: int

    # Answer Record Count
    # Number of records in Answer section
    ancount: int

    # Authority Record Count
    # Number of records in Authority section
    nscount: int

    # Additional Record Count
    # Number of records in Additional section
    arcount: int

    def encode(self) -> bytes:
        flags = (
            (self.qr << 15)
            | (self.opcode << 11)
            | (self.aa << 10)
            | (self.tc << 9)
            | (self.rd << 8)
            | (self.ra << 7)
            | (self.z << 4)
            | (self.rcode.value)
        )
        header = struct.pack(
            "!HHHHHH",
            self.id,
            flags,
            self.qdcount,
            self.ancount,
            self.nscount,
            self.arcount,
        )
        return header

    @staticmethod
    def decode(reader: BytesIO) -> "Header":
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack(
            "!HHHHHH", reader.read(12)
        )

        return Header(
            id=id,
            qr=(flags >> 15) & 0x01,
            opcode=(flags >> 11) & 0x0F,
            aa=(flags >> 10) & 0x01,
            tc=(flags >> 9) & 0x01,
            rd=(flags >> 8) & 0x01,
            ra=(flags >> 7) & 0x01,
            z=(flags >> 4) & 0x03,
            rcode=RCode(flags & 0x0F),
            qdcount=qdcount,
            ancount=ancount,
            nscount=nscount,
            arcount=arcount,
        )

    def to_response(self) -> "Header":
        return Header(
            id=self.id,
            qr=1,
            opcode=self.opcode,
            aa=self.aa,
            tc=self.tc,
            rd=self.rd,
            ra=self.ra,
            z=self.z,
            rcode=RCode(4) if self.opcode else RCode(0),
            qdcount=0,
            ancount=0,
            nscount=0,
            arcount=0,
        )

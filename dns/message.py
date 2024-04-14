from dataclasses import dataclass, field
from io import BytesIO

from .header import Header
from .question import Question
from .answer import Answer


@dataclass
class Message:
    """
    +---------------------+
    |        Header       |
    +---------------------+
    |       Question      | the question for the name server
    +---------------------+
    |        Answer       | RRs answering the question
    +---------------------+
    |      Authority      | RRs pointing toward an authority
    +---------------------+
    |      Additional     | RRs holding additional information
    +---------------------+
    """

    header: Header
    questions: list[Question] = field(default_factory=list)
    answers: list[Answer] = field(default_factory=list)

    def add_question(self, question: Question):
        self.questions.append(question)
        self.header.qdcount += 1

    def add_answer(self, answer: Answer):
        self.answers.append(answer)
        self.header.ancount += 1

    def encode(self) -> bytes:
        header = self.header.encode()
        questions = b"".join([question.encode() for question in self.questions])
        answers = b"".join([answer.encode() for answer in self.answers])
        return header + questions + answers

    @staticmethod
    def decode(data: bytes) -> "Message":
        reader = BytesIO(data)
        header = Header.decode(reader)
        questions = [Question.decode(reader) for _ in range(header.qdcount)]
        answers = [Answer.decode(reader) for _ in range(header.ancount)]

        return Message(header=header, questions=questions, answers=answers)

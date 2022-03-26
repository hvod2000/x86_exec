from dataclasses import dataclass


@dataclass
class Statement:
    comment: str

    def __str__(self):
        return self.add_comment()

    def add_comment(self, txt=""):
        return txt + (";" + self.comment if self.comment is not None else "")


@dataclass
class Definition(Statement):
    variable: str


@dataclass
class DefinitionByte(Definition):
    value: int

    def __str__(self):
        return self.add_comment(f"{self.variable} db {self.value}")


@dataclass
class DefinitionWord(Definition):
    value: int

    def __str__(self):
        return self.add_comment(f"{self.variable} dw {self.value}")


@dataclass
class Operator(Statement):
    pass


@dataclass
class OperatorMove(Operator):
    operand1: str
    operand2: str
    size: int | None = None

    def __str__(self):
        return self.add_comment(f"mov {self.operand1}, {self.operand2}")


@dataclass
class OperatorCbw(Operator):
    def __str__(self):
        return self.add_comment(f"cbw")


@dataclass
class OperatorCwd(Operator):
    def __str__(self):
        return self.add_comment(f"cwd")


@dataclass
class OperatorAdd(Operator):
    operand1: str
    operand2: str
    size: int | None = None

    def __str__(self):
        return self.add_comment(f"add {self.operand1}, {self.operand2}")


@dataclass
class OperatorSub(Operator):
    operand1: str
    operand2: str
    size: int | None = None

    def __str__(self):
        return self.add_comment(f"sub {self.operand1}, {self.operand2}")


@dataclass
class OperatorMul(Operator):
    operand: str
    size: int | None = None

    def __str__(self):
        return self.add_comment(f"mul {self.operand}")


@dataclass
class OperatorImul(Operator):
    operand: str
    size: int | None = None

    def __str__(self):
        return self.add_comment(f"imul {self.operand}")


@dataclass
class OperatorDiv(Operator):
    operand: str
    size: int | None = None

    def __str__(self):
        return self.add_comment(f"div {self.operand}")


@dataclass
class OperatorIdiv(Operator):
    operand: str
    size: int | None = None

    def __str__(self):
        return self.add_comment(f"idiv {self.operand}")

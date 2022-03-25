import dataclasses
from typing import Any
from string import ascii_lowercase, digits
from instruction_typechecking import typecheck as typecheck_instruction
from instruction_parser import parse_instruction
from instruction_executer import execute as execute_instruction


is_int = lambda num: num.removeprefix("-").isdigit()
dict2fun = lambda dct: lambda name: dct[name]


@dataclasses.dataclass
class Instruction:
    operation: str
    args: Any  # list[str | (str, int)]
    comment: str = ""

    def typecheck(self, regs, vars):
        if not self.operation or self.operation == "define":
            return True
        return typecheck_instruction(self, vars, regs)

    def execute(self, vars):
        return execute_instruction(self, vars)

    @property
    def constants(self):
        if self.operation in ("define", ""):
            return
        yield from ((int(arg), size) for arg, size in self.args if is_int(arg))

    @staticmethod
    def parse(source):
        if instruction := parse_instruction(source):
            return Instruction(*instruction)
        return None

    def __str__(self):
        arg2str = lambda arg: arg if isinstance(arg, str) else arg[0]
        args = ",".join(" " + arg for arg in map(arg2str, self.args))
        comment = ";" + self.comment if self.comment else ""
        if self.operation == "define":
            return " ".join(self.args) + comment
        return f"{self.operation}{args}{comment}"

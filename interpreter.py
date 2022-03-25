import dataclasses
from mymath import ceil_log
from memory import IntValue, Int
from string import ascii_lowercase, digits
from instructions import Instruction
from collections import ChainMap


def generate_registers():
    regs = [(n, Int(bytearray(2), 0, 2)) for n, s in zip("abcd", range(4))]
    subs = {n + e: s for n, r in regs for e, s in zip("lh", r.split(1, 1))}
    return {n + "x": r for n, r in regs} | subs


@dataclasses.dataclass
class Programm:
    code: list[Instruction]
    variables: dict[str, (int, int)]

    def show(self):
        print("\n".join(map(str, self.code)))

    @staticmethod
    def parse(source):
        lines = source.split("\n")
        code, variables = [], {}
        for line in lines:
            if not (instruction := Instruction.parse(line)):
                raise Exception(f"unknown instruction: {line}")
            if instruction.operation == "define":
                name, size, value = instruction.args
                variables[name] = (int(value), 2 if size == "dw" else 1)
            code.append(instruction)
        return Programm(code, variables)


@dataclasses.dataclass
class Process:
    program: Programm
    constants: dict[str, Int]
    registers: dict[str, Int]
    variables: dict[str, Int]
    namespace: ChainMap[str, Int]
    next_instruction: int

    def step(self):
        self.program.code[self.next_instruction].execute(self.namespace)
        self.next_instruction += 1

    def show(self):
        int2str = lambda n: str(int(n)).ljust(ceil_log(256**n.size, 10) + 1)
        variables = sorted(self.namespace.items())
        print(" ".join(f"{n}={int2str(v)}" for n, v in variables))

    @staticmethod
    def start(program):
        variables, registers = program.variables.items(), generate_registers()
        variables = {n: Int.from_value(IntValue(*v)) for (n, v) in variables}
        namespace = ChainMap({}, registers, variables)
        return Process(program, {}, registers, variables, namespace, 0)

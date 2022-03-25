import dataclasses
from typing import Any
from mymath import ceil_log
from memory import IntValue, Int
from string import ascii_lowercase, digits
from instructions import Instruction
from mycollections import ChainDict


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

    def typecheck(self):
        self.typecheck = lambda x: None
        registers = {n: (None, v.size) for n, v in generate_registers().items()}
        for i, instr in enumerate(self.code):
            if not instr.typecheck(registers, self.variables):
                raise ValueError(f"Failed to typecheck line #{i}: {instr}")

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
    constants: dict[(str, int), Int]
    registers: dict[(str, int), Int]
    variables: dict[(str, int), Int]
    namespace: Any  #  ChainDict[str, Int]
    next_instruction: int

    def step(self):
        self.program.code[self.next_instruction].execute(self.namespace)
        self.next_instruction += 1

    def show(self):
        int2str = lambda n: str(int(n)).ljust(ceil_log(256**n.size, 10) + 1)
        for ns in (self.registers.items(), self.variables.items()):
            print(" ".join(f"{n}:{s*8}={int2str(v)}" for (n, s), v in ns))

    @staticmethod
    def start(program):
        program.typecheck()
        variables, registers = program.variables.items(), generate_registers()
        variables = {n: Int(*v) for (n, v) in variables}
        variables = {(n, v.size): v for (n, v) in variables.items()}
        registers = {(n, v.size): v for (n, v) in registers.items()}
        consts = {const for line in program.code for const in line.constants}
        consts = {(str(c[0]), c[1]): Int(*c) for c in consts}
        namespace = ChainDict(consts, registers, variables)
        return Process(program, consts, registers, variables, namespace, 0)

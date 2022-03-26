import dataclasses
from typing import Any
from mymath import ceil_log
from distributed_integer import Int
from mycollections import ChainDict, FunDict
import typed_instructions
import typechecker
import executer
import parser


def generate_registers():
    regs = [(n, Int(-42, 2)) for n, s in zip("abcd", range(4))]
    subs = {n + e: s for n, r in regs for e, s in zip("lh", r.split(1, 1))}
    return {n + "x": r for n, r in regs} | subs


@dataclasses.dataclass
class Programm:
    code: list[typed_instructions.Statement]
    variables: dict[str, (int, int)]

    def show(self):
        print("\n".join(map(str, self.code)))

    def typecheck(self):
        self.typecheck = lambda x: None
        registers = {n: (None, v.size) for n, v in generate_registers().items()}
        for i, stmt in enumerate(self.code):
            if isinstance(stmt, typed_instructions.Operator):
                if not typechecker.typecheck(stmt, registers, self.variables):
                    raise ValueError(f"Failed to typecheck line #{i}: {instr}")

    @staticmethod
    def parse(source):
        lines = source.split("\n")
        code, variables = [], {}
        for line in lines:
            if not (statement := parser.parse_statement(line)):
                raise Exception(f"unknown instruction: {line}")
            if isinstance(statement, typed_instructions.Definition):
                name = statement.variable
                variables[name] = (statement.value, statement.size)
            code.append(statement)
        return Programm(code, variables)


@dataclasses.dataclass
class Process:
    program: Programm
    registers: dict[(str, int), Int]
    variables: dict[(str, int), Int]
    namespace: Any  #  ChainDict[str, Int]
    next_instruction: int

    def step(self):
        stmt = self.program.code[self.next_instruction]
        if isinstance(stmt, typed_instructions.Operator):
            executer.execute(stmt, self.namespace)
        self.next_instruction += 1

    def show(self):
        int2str = lambda n: str(n.i).ljust(ceil_log(256**n.size, 10) + 1)
        for ns in (self.registers.items(), self.variables.items()):
            print(" ".join(f"{n}:{s*8}={int2str(v)}" for (n, s), v in ns))

    @staticmethod
    def start(program):
        program.typecheck()
        constants = FunDict(lambda v: Int(int(v[0]), v[1]))
        variables, registers = program.variables.items(), generate_registers()
        variables = {n: Int(*v) for (n, v) in variables}
        variables = {(n, v.size): v for (n, v) in variables.items()}
        registers = {(n, v.size): v for (n, v) in registers.items()}
        namespace = ChainDict(registers, variables, constants)
        return Process(program, registers, variables, namespace, 0)

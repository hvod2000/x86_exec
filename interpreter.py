import dataclasses
from mymath import ceil_log
from string import ascii_lowercase, digits
from instructions import Instruction
from collections import ChainMap


@dataclasses.dataclass
class IntValue:
    value: int
    size: int

    def __init__(self, value, size):
        self.value = value % 2 ** (size * 8)
        self.size = size

    def sext(self, size):
        return IntValue(int(self), size)

    def split(self, *sizes):
        assert sum(sizes) == self.size
        offset = 0
        for size in sizes:
            yield IntValue(self.value >> 8 * offset, size)
            offset += size

    def __int__(self):
        t = 2 ** (self.size * 8 - 1)
        return (self.value + t) % (2 * t) - t

    def __str__(self):
        return f"{int(self)}:i{self.size*8}"

    def __add__(u, v):
        assert u.size == v.size
        return IntValue(u.value + v.value, u.size)

    def __sub__(u, v):
        assert u.size == v.size
        return IntValue(u.value - v.value, u.size)


@dataclasses.dataclass
class Int:
    mem: bytearray
    offset: int
    size: int

    def split(self, *sizes):
        assert sum(sizes) == self.size
        offset = 0
        for size in sizes:
            yield Int(self.mem, self.offset + offset, size)
            offset += size

    @staticmethod
    def from_value(value):
        self = Int(bytearray(value.size), 0, value.size)
        self.value = value
        return self

    @property
    def value(self):
        mem, offset, size = self.mem, self.offset, self.size
        value = int.from_bytes(mem[offset : offset + size], "little")
        return IntValue(value, size)

    @value.setter
    def value(self, value):
        assert value.size == self.size
        mem, offset, size = self.mem, self.offset, self.size
        mem[offset : offset + size] = (value.value).to_bytes(size, "little")

    def __int__(self):
        return int(self.value)


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

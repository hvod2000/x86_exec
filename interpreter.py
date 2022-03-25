import dataclasses
from mymath import ceil_log
from string import ascii_lowercase, digits


word_chars = ascii_lowercase + digits


def parse_tokens(line):
    source, comment = line.split(";", 1) if ";" in line else (line, None)
    source = source.strip().lower()
    tokens, in_word = [], False
    for char in source:
        if char in word_chars:
            if in_word:
                tokens[-1] += char
            else:
                tokens.append(char)
            in_word = True
        else:
            if char not in " \t":
                tokens.append(char)
            in_word = False
    return tokens, comment


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
        assert sum(bits) == self.size
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
        assert sum(bits) == self.size
        offset = 0
        for size in sizes:
            yield Int(self.mem, self.offset + offset, size)
            offset += size

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


@dataclasses.dataclass
class Instruction:
    operation: str
    args: list[str]

    def __str__(self):
        return f"{self.operation} {', '.join(self.args)}"


@dataclasses.dataclass
class Process:
    code: list[Instruction]
    variables: dict[str, Int] = dataclasses.field(default_factory=dict)
    instruction_ptr: int = 0

    def step(self):
        instr = self.code[self.instruction_ptr]
        self.instruction_ptr += 1
        if instr.operation == "mov":
            target, source = map(lambda name: self.variables[name], instr.args)
            target.value = source.value
        elif instr.operation == "cbw":
            self.variables["ax"].value = self.variables["al"].value.sext(2)
        elif instr.operation == "cwd":
            low, hieght = self.variables["ax"].value.sext(4).split(2, 2)
            self.variables["dx"] = hieght
        elif instr.operation == "add":
            target, source = map(lambda name: self.variables[name], instr.args)
            target.value += source.value
        elif instr.operation == "sub":
            target, source = map(lambda name: self.variables[name], instr.args)
            target.value -= source.value

    def show(self):
        int2str = lambda n: str(int(n)).ljust(ceil_log(256**n.size, 10) + 1)
        variables = sorted(self.variables.items())
        print(" ".join(f"{n}={int2str(v)}" for n, v in variables))

    def initialize_registers(self):
        mem = bytearray([0] * 8)
        al, ax, ah = Int(mem, 0, 1), Int(mem, 0, 2), Int(mem, 1, 1)
        bl, bx, bh = Int(mem, 2, 1), Int(mem, 2, 2), Int(mem, 3, 1)
        cl, cx, ch = Int(mem, 4, 1), Int(mem, 4, 2), Int(mem, 5, 1)
        dl, dx, dh = Int(mem, 6, 1), Int(mem, 6, 2), Int(mem, 7, 1)
        self.variables |= {"al": al, "ax": ax, "ah": ah}
        self.variables |= {"bl": bl, "bx": bx, "bh": bh}
        self.variables |= {"cl": cl, "cx": cx, "ch": ch}
        self.variables |= {"dl": dl, "dx": dx, "dh": dh}

    @staticmethod
    def from_program(program):
        code = program.code
        mem_size = sum(w for v, w in program.variables.values())
        mem = bytearray([0] * mem_size)
        variables, offset = {}, 0
        for name, (value, size) in program.variables.items():
            variables[name] = Int(mem, offset, size)
            variables[name].value = IntValue(value, size)
            offset += size
        process = Process(code, variables)
        process.initialize_registers()
        return process


@dataclasses.dataclass
class Programm:
    code: list[Instruction]
    variables: dict[str, (int, int)]
    labels: dict[str, int]

    def show(self):
        labels = {i: label for label, i in self.labels.items()}
        for line_number, line in enumerate(self.code):
            if line_number in labels:
                print(labels[line_number] + ":")
            print("\t" + str(line))

    @staticmethod
    def parse(source):
        lines = source.split("\n")
        code, variables, labels = [], {}, {}
        for line in lines:
            tokens, comment = parse_tokens(line)
            if not tokens:
                continue
            elif tokens[0] in {"mov", "cbw", "cwd", "add", "sub"}:
                code.append(Instruction(tokens[0], tokens[1::2]))
            elif tokens[1] in {"dw", "db"}:
                code.append(Instruction("undefined_behavour", []))
                name, value = tokens[0], tokens[2]
                assert name not in variables
                size = 2 if tokens[1] == "dw" else 1
                variables[name] = (int(value), size)
            else:
                raise Exception(f"unknown instruction: {line}")
        return Programm(code, variables, labels)

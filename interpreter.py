import dataclasses
from mymath import ceil_log
from string import ascii_lowercase


@dataclasses.dataclass
class Register:
    value: int

    @property
    def low(self):
        return self.value % 256

    @property
    def hieght(self):
        return (self.value // 256) % 256

    @property
    def value32(self):
        return self.value % 2**32

    @low.setter
    def low(self, value):
        self.value += (value % 256) - self.low

    @hieght.setter
    def hieght(self, value):
        self.value += (value % 256 - self.hieght) * 256

    @value32.setter
    def value32(self, value):
        self.value += value % 2**32 - self.value32

    def __str__(self):
        return f"R({self.value})"


@dataclasses.dataclass
class IntValue:
    value: int
    size: int

    def __init__(self, value, size):
        self.value = value % 2 ** (size * 8)
        self.size = size

    def sext(self, size):
        return IntValue(int(self), size)

    def split(self, low, hight):
        low = IntValue(self.value, low)
        hight = IntValue(self.value >> (self.size - hight), hight)
        return low, hight

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


def get_subreg(reg, i):
    if i == "low":
        return reg.low
    elif i == "hig":
        return reg.hieght
    elif i == "v32":
        return reg.value32


def set_subreg(reg, i, value):
    if i == "low":
        reg.low = value
    elif i == "hig":
        reg.hieght = value
    elif i == "v32":
        reg.value32 = value


@dataclasses.dataclass
class State:
    registers: tuple[Register]

    def move_reg(self, source, sd, target, td):
        source, target = self.registers[source], self.registers[target]
        set_subreg(target, td, get_subreg(source, td))

    def show(self):
        print("registers:")
        for i, name in enumerate("ABCD"):
            print(f"\t{name} : {self.registers[i].value}")


@dataclasses.dataclass
class Instruction:
    operation: str
    args: list[str]

    def __str__(self):
        return f"{self.operation} {' '.join(self.args)}"

    @staticmethod
    def parse(source):
        source = source.split(";", 1)[0] if ";" in source else source
        source = source.strip(" \t").lower()
        if not source:
            return None
        instr = []
        j = 0
        while j < len(source):
            i = j
            while i < len(source) and source[i] in ascii_lowercase:
                i += 1
            instr.append(source[j:i])
            while i < len(source) and source[i] not in ascii_lowercase:
                i += 1
            j = i
        operation, args = instr[0], [a.strip(',') for a in instr[1:]]
        return Instruction(operation, args)


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
        int2str = lambda n: str(int(n)).ljust(ceil_log(256**n.size, 10))
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
        for line in map(lambda s: s.strip(" \t"), lines):
            instruction = Instruction.parse(line)
            if not instruction:
                continue
            if instruction.operation in ["mov", "cbw", "cwd", "add", "sub"]:
                code.append(instruction)
            elif len(instruction.args) and instruction.args[0] in ("dw", "db"):
                code.append(None)
                name, value = instruction.operation, instruction.args[1]
                assert name not in variables
                size = 2 if instruction.args[0] == "dw" else 1
                variables[name] = (value, size)
            else:
                raise Exception(f"unknown instruction: {line}")
        return Programm(code, variables, labels)

from dataclasses import dataclass


@dataclass
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


@dataclass
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


@dataclass
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


@dataclass
class State:
    registers: tuple[Register]

    def move_reg(self, source, sd, target, td):
        source, target = self.registers[source], self.registers[target]
        set_subreg(target, td, get_subreg(source, td))

    def show(self):
        print("registers:")
        for i, name in enumerate("ABCD"):
            print(f"\t{name} : {self.registers[i].value}")


@dataclass
class Instruction:
    operation: str
    args: list[str]

    def __str__(self):
        return f"{self.operation} {' '.join(self.args)}"


@dataclass
class Programm:
    code: list[Instruction]
    variables: dict[str, (int, int)]
    labels: dict[str, int]
    entry: int = 0

    def show(self):
        labels = {i: label for label, i in self.labels.items()}
        for line_number, line in enumerate(self.code):
            if line_number in labels:
                print(labels[line_number] + ":")
            print("\t" + str(line))

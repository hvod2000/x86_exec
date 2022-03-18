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

    def show(self):
        print("registers:")
        for i, name in enumerate("ABCD"):
            print(f"\t{name} : {self.registers[i].value}")

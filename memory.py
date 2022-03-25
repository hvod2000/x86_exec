import dataclasses


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

    def __init__(self, *args):
        if len(args) == 3:
            self.mem, self.offset, self.size = args
        elif len(args) == 2:
            value, size = args
            self.mem, self.offset, self.size = bytearray(size), 0, size
            self.value = IntValue(value, size)
        else:
            value = args[0]
            size = value.size
            self.mem, self.offset, self.size = bytearray(size), 0, size
            self.value = value

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

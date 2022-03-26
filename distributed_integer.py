import dataclasses


def uint2bytes(num, size):
    mem = bytearray((num % 256**size).to_bytes(size, "little"))
    return [(mem, i) for i in range(len(mem))]


def int2bytes(num, size):
    return uint2bytes(num, size)


def bytes2uint(bts):
    return int.from_bytes([b[i] for b, i in bts], "little")


def bytes2int(bts):
    num = bytes2uint(bts)
    return num - 256 ** len(bts) if num >> (8 * len(bts) - 1) else num


@dataclasses.dataclass
class Int:
    location: list[bytearray, int]
    size: int

    def __init__(self, *args):
        if len(args) == 2:
            value, size = args
            value = int2bytes(value, size) if isinstance(value, int) else value
        elif len(args) == 1:
            value, size = args[0].value, args[0].size
        else:
            raise ValueError(f"Wrong number of arguments for Int(): {args}")
        self.location, self.size = value, size

    def split(self, *sizes):
        assert sum(sizes) == self.size
        offset = 0
        for size in sizes:
            yield Int(self.location[offset : offset + size], size)
            offset += size

    def __matmul__(self, other):
        return Int(self.location + other.location, self.size + other.size)

    def __imatmul__(self, value):
        value = value.u if isinstance(value, Int) else value
        for i, (b, j) in enumerate(self.location):
            b[j] = (value >> (i * 8)) % 256
        return self

    def __str__(self):
        return f"{self.i}:{self.size * 8}"

    def __add__(self, other):
        return self.i + other.i

    def __iadd__(self, other):
        self @= self + other
        return self

    def __sub__(self, other):
        return self.i - other.i

    def __isub__(self, other):
        self @= self - other
        return self

    @property
    def i(self):
        return bytes2int(self.location)

    @property
    def u(self):
        return bytes2uint(self.location)

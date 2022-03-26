from typed_instructions import *
from itertools import product


def execute(instruction, namespace):
    regs = product("ad", zip("xlh", (2, 1, 1)))
    ax, al, ah, dx, dl, dh = (namespace[n + m, s] for n, (m, s) in regs)
    a, d = [None, al, ax, ax @ dl, ax @ dx], [None, ah, dx]
    match instruction:
        case OperatorMov(_, operand1, operand2, size):
            namespace[operand1, size] @= namespace[operand2, size]
        case OperatorCbw(_):
            ax @= al.i
        case OperatorCwd(_):
            a[3] @= ax.i
        case OperatorAdd(_, operand1, operand2, size):
            namespace[operand1, size] += namespace[operand2, size]
        case OperatorSub(_, operand1, operand2, size):
            namespace[operand1, size] -= namespace[operand2, size]
        case OperatorMul(_, operand, size):
            a[2 * size] @= a[size].u * namespace[operand, size].u
        case OperatorImul(_, operand, size):
            a[2 * size] @= a[size].i * namespace[operand, size].i
        case OperatorDiv(_, operand, size):
            q, r = divmod(a[size * 2].u, namespace[operand, size].u)
            a[size] @= q
            d[size] @= r
        case OperatorIdiv(_, operand, size):
            q, r = divmod(a[size * 2].i, namespace[operand, size].i)
            a[size] @= q
            d[size] @= r
        case _:
            raise NotImplementedError(f"Unsupported operation: {repr(op)}")

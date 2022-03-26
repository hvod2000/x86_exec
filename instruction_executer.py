from itertools import product


def execute(instruction, namespace):
    if instruction.operation in ("define", ""):
        return
    regs = product("ad", zip("xlh", (2, 1, 1)))
    ax, al, ah, dx, dl, dh = (namespace[n + m, s] for n, (m, s) in regs)
    a, d = [None, al, ax, ax @ dl, ax @ dx], [None, ah, dx]
    size = next(iter(arg[1] for arg in instruction.args), None)
    args = list(namespace[arg] for arg in instruction.args)
    operand1, operand2, *_ = args + [None] * 2
    match instruction.operation:
        case "mov":
            operand1 @= operand2
        case "cbw":
            ax @= al.i
        case "cwd":
            ax_dx @= ax.i
        case "add":
            operand1 += operand2
        case "sub":
            operand1 -= operand2
        case "mul":
            a[2 * size] @= a[size].u * operand1.u
        case "imul":
            a[2 * size] @= a[size].i * operand1.i
        case "div":
            q, r = divmod(a[size * 2].u, operand1.u)
            a[size] @= q
            d[size] @= r
        case "idiv":
            q, r = divmod(a[size * 2].i, operand1.i)
            a[size] @= q
            d[size] @= r
        case _:
            raise NotImplementedError(f"Unsupported operation: {repr(op)}")

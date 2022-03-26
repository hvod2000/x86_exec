from itertools import product


def execute(instruction, namespace):
    op, args = instruction.operation, instruction.args
    get_var = lambda var: namespace[var]
    get_sized = lambda var: (namespace[var], var[1])
    regs = product("ad", zip("xlh", (2, 1, 1)))
    ax, al, ah, dx, dl, dh = (namespace[n + m, s] for n, (m, s) in regs)
    a, d = [None, al, ax, ax @ dl, ax @ dx], [None, ah, dx]
    match op:
        case "mov":
            target, source = map(get_var, args)
            target @= source
        case "cbw":
            ax @= al.i
        case "cwd":
            ax_dx @= ax.i
        case "add":
            target, source = map(get_var, args)
            target @= target.i + source.i
        case "sub":
            target, source = map(get_var, args)
            target @= target.i - source.i
        case "mul":
            operand, size = get_sized(args[0])
            a[2 * size] @= a[size].u * operand.u
        case "imul":
            operand, size = get_sized(args[0])
            a[2 * size] @= a[size].i * operand.i
        case "div":
            operand, size = get_sized(args[0])
            q, r = divmod(a[size * 2].u, operand.u)
            a[size] @= q
            d[size] @= r
        case "define" | "":
            pass
        case _:
            raise NotImplementedError(f"Unsupported operation: {repr(op)}")

dict2fun = lambda dct: lambda name: dct[name]


def execute(instruction, vars):
    op, args, get_var = instruction.operation, instruction.args, dict2fun(vars)
    ax, al, dx = get_var(("ax", 2)), get_var(("al", 1)), get_var(("dx", 2))
    ax_dx = ax @ dx
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
            operand = get_var(args[0])
            if operand.size == 2:
                ax_dx @= ax.u * operand.u
            else:
                ax @= al.u * operand.u
        case "imul":
            operand = get_var(args[0])
            if operand.size == 2:
                ax_dx @= ax.i * operand.i
            else:
                ax @= al.i * operand.i

dict2fun = lambda dct: lambda name: dct[name]


def execute(instruction, vars):
    op, args, get_var = instruction.operation, instruction.args, dict2fun(vars)
    ax, al, dx = get_var(("ax", 2)), get_var(("al", 1)), get_var(("dx", 2))
    match op:
        case "mov":
            target, source = map(get_var, args)
            target.value = source.value
        case "cbw":
            ax.value = al.value.sext(2)
        case "cwd":
            dx.value = ax.value.sext(4).split(2, 2)[1]
        case "add":
            target, source = map(get_var, args)
            target.value += source.value
        case "sub":
            target, source = map(get_var, args)
            target.value -= source.value
        case "mul":
            operand = get_var(args[0])
            if operand.size == 2:
                ax.value, dx.value = (ax.value.mul(operand.value)).split(2, 2)
            else:
                ax.value = (al.value.mul(operand.value))
        case "imul":
            operand = get_var(args[0])
            if operand.size == 2:
                ax.value, dx.value = (ax.value * operand.value).split(2, 2)
            else:
                ax.value = al.value * operand.value

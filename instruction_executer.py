dict2fun = lambda dct: lambda name: dct[name]


def execute(instruction, vars):
    op, args, get_var = instruction.operation, instruction.args, dict2fun(vars)
    match op:
        case "mov":
            target, source = map(get_var, args)
            target.value = source.value
        case "cbw":
            vars["ax"].value = vars["al"].value.sext(2)
        case "cwd":
            vars["dx"] = vars["ax"].value.sext(4).split(2, 2)[1]
        case "add":
            target, source = map(get_var, args)
            target.value += source.value
        case "sub":
            target, source = map(get_var, args)
            target.value -= source.value

is_int = lambda num: num.removeprefix("-").isdigit()


def typecheck(instruction, vars, regs):
    operation, args = instruction.operator, instruction.args
    if operator == "mov" and len(args) == 2:
        if (
            args[0] in vars
            and args[1] in regs
            and vars[args[0]][1] == regs[args[1]][1]
        ):
            size = vars[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

    if operator == "mov" and len(args) == 2:
        if (
            args[0] in regs
            and args[1] in regs
            and regs[args[0]][1] == regs[args[1]][1]
        ):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

        if (
            args[0] in regs
            and args[1] in vars
            and regs[args[0]][1] == vars[args[1]][1]
        ):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

    if operation == "cbw":
        return not len(args)

    if operation == "cwd":
        return not len(args)

    if operator == "add" and len(args) == 2:
        if (
            args[0] in regs
            and args[1] in regs
            and regs[args[0]][1] == regs[args[1]][1]
        ):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

        if (
            args[0] in regs
            and args[1] in vars
            and regs[args[0]][1] == vars[args[1]][1]
        ):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

        if args[0] in regs and is_int(args[1]):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

    if operator == "add" and len(args) == 2:
        if (
            args[0] in vars
            and args[1] in regs
            and vars[args[0]][1] == regs[args[1]][1]
        ):
            size = vars[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

        if args[0] in vars and is_int(args[1]):
            size = vars[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

    if operator == "sub" and len(args) == 2:
        if (
            args[0] in regs
            and args[1] in regs
            and regs[args[0]][1] == regs[args[1]][1]
        ):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

        if (
            args[0] in regs
            and args[1] in vars
            and regs[args[0]][1] == vars[args[1]][1]
        ):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

        if args[0] in regs and is_int(args[1]):
            size = regs[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

    if operator == "sub" and len(args) == 2:
        if (
            args[0] in vars
            and args[1] in regs
            and vars[args[0]][1] == regs[args[1]][1]
        ):
            size = vars[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

        if args[0] in vars and is_int(args[1]):
            size = vars[args[0]][1]
            args[0] = (args[0], size)
            args[1] = (args[1], size)
            return True

    return False
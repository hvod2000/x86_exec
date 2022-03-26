from typed_instructions import *
is_int = lambda num: num.removeprefix("-").isdigit()
def typecheck(instr, registers, memory):
    match instr:
        case OperatorMov(_, operand0, operand1, _) if operand0 in memory and is_int(operand1):
            instr.size = memory[operand0][1]
            return True

        case OperatorMov(_, operand0, operand1, _) if operand0 in memory and operand1 in registers and memory[operand0][1] == registers[operand1][1]:
            instr.size = memory[operand0][1]
            return True

        case OperatorMov(_, operand0, operand1, _) if operand0 in registers and is_int(operand1):
            instr.size = registers[operand0][1]
            return True

        case OperatorMov(_, operand0, operand1, _) if operand0 in registers and operand1 in memory and registers[operand0][1] == memory[operand1][1]:
            instr.size = registers[operand0][1]
            return True

        case OperatorMov(_, operand0, operand1, _) if operand0 in registers and operand1 in registers and registers[operand0][1] == registers[operand1][1]:
            instr.size = registers[operand0][1]
            return True

        case OperatorCbw(_):
            return True

        case OperatorCwd(_):
            return True

        case OperatorAdd(_, operand0, operand1, _) if operand0 in memory and is_int(operand1):
            instr.size = memory[operand0][1]
            return True

        case OperatorAdd(_, operand0, operand1, _) if operand0 in memory and operand1 in registers and memory[operand0][1] == registers[operand1][1]:
            instr.size = memory[operand0][1]
            return True

        case OperatorAdd(_, operand0, operand1, _) if operand0 in registers and is_int(operand1):
            instr.size = registers[operand0][1]
            return True

        case OperatorAdd(_, operand0, operand1, _) if operand0 in registers and operand1 in memory and registers[operand0][1] == memory[operand1][1]:
            instr.size = registers[operand0][1]
            return True

        case OperatorAdd(_, operand0, operand1, _) if operand0 in registers and operand1 in registers and registers[operand0][1] == registers[operand1][1]:
            instr.size = registers[operand0][1]
            return True

        case OperatorSub(_, operand0, operand1, _) if operand0 in memory and is_int(operand1):
            instr.size = memory[operand0][1]
            return True

        case OperatorSub(_, operand0, operand1, _) if operand0 in memory and operand1 in registers and memory[operand0][1] == registers[operand1][1]:
            instr.size = memory[operand0][1]
            return True

        case OperatorSub(_, operand0, operand1, _) if operand0 in registers and is_int(operand1):
            instr.size = registers[operand0][1]
            return True

        case OperatorSub(_, operand0, operand1, _) if operand0 in registers and operand1 in memory and registers[operand0][1] == memory[operand1][1]:
            instr.size = registers[operand0][1]
            return True

        case OperatorSub(_, operand0, operand1, _) if operand0 in registers and operand1 in registers and registers[operand0][1] == registers[operand1][1]:
            instr.size = registers[operand0][1]
            return True

        case OperatorMul(_, operand0, _) if operand0 in memory:
            instr.size = memory[operand0][1]
            return True

        case OperatorMul(_, operand0, _) if operand0 in registers:
            instr.size = registers[operand0][1]
            return True

        case OperatorImul(_, operand0, _) if operand0 in memory:
            instr.size = memory[operand0][1]
            return True

        case OperatorImul(_, operand0, _) if operand0 in registers:
            instr.size = registers[operand0][1]
            return True

        case OperatorDiv(_, operand0, _) if operand0 in memory:
            instr.size = memory[operand0][1]
            return True

        case OperatorDiv(_, operand0, _) if operand0 in registers:
            instr.size = registers[operand0][1]
            return True

        case OperatorIdiv(_, operand0, _) if operand0 in memory:
            instr.size = memory[operand0][1]
            return True

        case OperatorIdiv(_, operand0, _) if operand0 in registers:
            instr.size = registers[operand0][1]
            return True

        case _:
            return False

from tokenizer import tokenize
from typed_instructions import *

is_int = lambda num: num.removeprefix("-").isdigit()


def parse_statement(source):
    tokens, comment = tokenize(source)
    match tokens:
        case []:
            return Statement(comment)
        case ["mov", operand1, ",", operand2]:
            return OperatorMov(comment, operand1, operand2)
        case ["cbw"]:
            return OperatorCbw(comment)
        case ["cwd"]:
            return OperatorCwd(comment)
        case ["add", operand1, ",", operand2]:
            return OperatorAdd(comment, operand1, operand2)
        case ["sub", operand1, ",", operand2]:
            return OperatorSub(comment, operand1, operand2)
        case ["mul", operand]:
            return OperatorMul(comment, operand)
        case ["imul", operand]:
            return OperatorImul(comment, operand)
        case ["div", operand]:
            return OperatorDiv(comment, operand)
        case ["idiv", operand]:
            return OperatorIdiv(comment, operand)
        case [variable, "db", value] if is_int(value):
            return DefinitionByte(comment, variable, int(value))
        case [variable, "dw", value] if is_int(value):
            return DefinitionWord(comment, variable, int(value))
        case _:
            return None

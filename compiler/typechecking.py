from nodes import *
from errors import DslSyntaxError
from collections import namedtuple

Type = namedtuple("Type", "sign elements byte_lvl")

# type -- (signed/unsigned, number_of elements)


def ilog(x, b=2):
    result = 0
    while b**result < x:
        result += 1
    return result


def unify_types(typ, *types):
    for t in types:
        typ = Type(map(max, zip(typ, t)))
    return typ


def classify_number(number):
    sign = "s" if number < 0 or number.bit_length() % 8 else "u"
    bits, byte_lvl = number.bit_length(), 0
    while 8 * 2**byte_lvl < bits:
        byte_lvl += 1
    return Type(sign, 1, byte_lvl)


def derive_type(expression, scopes):
    match expression:
        case Byte(_):
            return Type("u", 1, 0)
        case Number(_, number):
            return classify_number(int(number))
        case Array(_, items):
            typ = unify_types(*(derive_type(item, scopes) for item in items))
            assert typ.elements != 1, "I don't support arrays of arrays"
            return Type(typ.sign, len(items), typ.bits)
        case Variable(pos, variable):
            for scope in scopes:
                if variable in scope:
                    break
            else:
                raise DslSyntaxError(pos, f"Undefined variable {variable}")
            return scope[variable]
        case Function(_):
            raise NotImplementedError()
        case Application(_):
            raise NotImplementedError()
        case BinaryOperation(_, operation, x, y):
            x, y = (derive_type(v, scopes) for v in (x, y))
            match operation:
                case "and" | "or":
                    return Type("s", 1, 0)
                case op:
                    return Type(*map(max, zip(x, y)))
        case UnaryOperation(_, _, argument):
            return derive_type(argument, scopes)
        case TypeCast(_, _, typ):
            assert typ.name[0] in "iu"
            return Type(typ.name[0], 1, ilog((int(typ.name[1:]) + 7) // 8, 2))
        case Indexing(_, array, _):
            array = derive_type(array, scopes)
            return Type(array.sign, 1, array.byte_lvl)


def typecheck(programm, scopes=()):
    scope = {}
    scopes += (scope,)
    for statement in programm:
        match statement:
            case Assignment(_, variables, values):
                new_variables = {
                    v: derive_type(e, scopes) for v, e in zip(variables, values)
                }
                scope.update(new_variables)
            case _:
                raise ValueError("0_0")
    return scope

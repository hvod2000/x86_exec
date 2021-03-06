from nodes import *
from errors import DslSyntaxError
from collections import namedtuple
from itertools import zip_longest

Type = namedtuple("Type", "sign elements byte_lvl")
Type.__str__ = lambda typ: typ.sign + str(8 * 2**typ.byte_lvl) + f"[{typ.elements}]" * (typ.elements != 1)


# type -- (signed/unsigned, number_of elements)


def ilog(x, b=2):
    result = 0
    while b**result < x:
        result += 1
    return result


def unify_types(typ, *types):
    for t in types:
        typ = Type(*map(max, zip(typ, t)))
    return typ


def classify_number(number):
    sign = "i" if number <= 0 or number.bit_length() % 8 else "u"
    bits, byte_lvl = number.bit_length(), 0
    while 8 * 2**byte_lvl < bits:
        byte_lvl += 1
    return Type(sign, 1, byte_lvl)


def derive_type(expression, scopes):
    match expression:
        case Object(_, typ):
            return typ
        case Byte(_):
            return Type("u", 1, 0)
        case Number(_, number):
            return classify_number(int(number))
        case Array(_, items):
            typ = unify_types(*(derive_type(item, scopes) for item in items))
            assert typ.elements == 1, "I don't support arrays of arrays"
            return Type(typ.sign, len(items), typ.byte_lvl)
        case Variable(pos, variable):
            for scope in scopes:
                if variable in scope:
                    break
            else:
                raise DslSyntaxError(pos, f"Undefined variable {variable}")
            return scope[variable].type
        case Function(_):
            raise NotImplementedError()
        case Application(_):
            raise NotImplementedError()
        case BinaryOperation(_, operation, x, y):
            x, y = (derive_type(v, scopes) for v in (x, y))
            match operation:
                case "and" | "or":
                    return Type("i", max(x.elements, y.elements), 0)
                case op:
                    return Type(*map(max, zip(x, y)))
        case UnaryOperation(_, _, argument):
            return derive_type(argument, scopes)
        case TypeCast(_, expr, typ):
            derive_type(expr, scopes)
            return str2type(typ)
        case Indexing(_, array, index):
            array = derive_type(array, scopes)
            index = derive_type(index, scopes)
            return Type(array.sign, index.elements, array.byte_lvl)


def str2type(typ):
    var = typ.name if isinstance(typ, Variable) else typ.array.name
    assert var[0] in "iu"
    sign = var[0]
    byte_lvl = ilog((int(var[1:]) + 7) // 8, 2)
    elements = int(typ.index.value) if isinstance(typ, Indexing) else 1
    return Type(sign, elements, byte_lvl)


def typecheck(programm, scopes=(), scope=None):
    if scope is None:
        scope = {}
    scopes = (scope,) + scopes
    for statement in programm:
        match statement:
            case Assignment(_, variables, expressions):
                new_types = {}
                for target, expr in zip(variables, expressions):
                    var = target.name if isinstance(target, Variable) else target.array.name
                    new_types[target] = derive_type(expr, scopes)
                for target, typ in new_types.items():
                    if isinstance(target, Variable):
                        var = target.name
                        value = scope[var].value if var in scope else (0,) * typ.elements
                        scope[var] = Object(value, typ)
                    else:
                        var = target.array.name
                        typ = unify_types(scope[var].type, typ)
                        value = scope[var].value if var in scope else (0,) * typ.elements
                        scope[var] = Object(value, typ)
            case Declaration(_, var, typ):
                var = var.name
                typ = str2type(typ)
                assert var not in scope
                value = (0,) * typ.elements
                scope[var] = Object(value, typ)
            case IfBlock(_, condition, body):
                derive_type(condition, scopes)
                typecheck(body, scopes[1:], scope)
            case IfElseBlock(_, condition, body1, body2):
                derive_type(condition, scopes)
                typecheck(body1, scopes[1:], scope)
                typecheck(body2, scopes[1:], scope)
            case WhileLoop(_, condition, body):
                derive_type(condition, scopes)
                typecheck(body, scopes[1:], scope)
            case _:
                raise ValueError("0_0")
    return scope

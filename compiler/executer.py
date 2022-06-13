from nodes import *
from typechecking import derive_type, Type
from itertools import zip_longest

LOGICAL = {"and", "or", "not"}


def get_value(obj: Object):
    base = 256 ** (2**obj.type.byte_lvl)
    if obj.type.sign == "u":
        values = [v % base for v in obj.value]
    else:
        values = [(v + base // 2) % base - base // 2 for v in obj.value]
    if obj.type.elements <= len(values):
        return tuple(values[: obj.type.elements])
    return tuple(values + [0] * (obj.type.elements - len(values)))


def gen_obj(it, typ):
    return Object(get_value(Object(it, typ)), typ)


def evaluate(expression, scopes):
    typ = derive_type(expression, scopes)
    match expression:
        case Byte(_, value) | Number(_, value):
            return Object((int(value),), typ)
        case Array(pos, items):
            items = tuple(get_value(evaluate(item, scopes))[0] for item in items)
            return Object(items, typ)
        case Variable(pos, var):
            return next(scope[var] for scope in scopes if var in scope)
        case Function(_):
            raise NotImplementedError()
        case Application(_):
            raise NotImplementedError()
        case BinaryOperation(pos, operation, x, y) if operation in LOGICAL:
            x = get_value(evaluate(x, scopes))
            if all(x) and operation == "or":
                return Object((1,) * typ.elements, typ)
            if not any(x) and operation == "and":
                return Object((0,) * typ.elements, typ)
            y = get_value(evaluate(y, scopes))
            if operation == "or":
                xy = zip_longest(x, y, fillvalue=0)
                return gen_obj([bool(x or y) for x, y in xy], typ)
            xy = zip_longest(x, y, fillvalue=1)
            return gen_obj([bool(x and y) for x, y in xy], typ)
        case BinaryOperation(pos, operation, x, y):
            x, y = (get_value(evaluate(z, scopes)) for z in (x, y))
            match operation:
                case "+":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x + y for x, y in xy], typ)
                case "-":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x - y for x, y in xy], typ)
                case "*":
                    xy = zip_longest(x, y, fillvalue=1)
                    return gen_obj([x * y for x, y in xy], typ)
                case "/":
                    xy = zip_longest(x, y, fillvalue=1)
                    return gen_obj([x // y for x, y in xy], typ)
                case ">":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x > y for x, y in xy], typ)
                case ">=":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x >= y for x, y in xy], typ)
                case "<=":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x <= y for x, y in xy], typ)
                case "<":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x < y for x, y in xy], typ)
                case "==":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x == y for x, y in xy], typ)
                case "!=":
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x != y for x, y in xy], typ)
                case op:
                    raise Exception(f"unsupported operation: {op}")
        case UnaryOperation(_, operation, argument):
            x = evaluate(argument, scopes)
            match operation:
                case "(":
                    return x
                case "-":
                    return gen_obj(tuple(-x for x in get_value(x)), typ)
                case op:
                    raise Exception(f"unsupported operation: {op}")
        case TypeCast(_, expr, _):
            return gen_obj(get_value(evaluate(expr, scopes)), typ)
        case Indexing(_, array, index):
            array = get_value(evaluate(array, scopes))
            index = get_value(evaluate(index, scopes))
            return gen_obj([array[i] for i in index], typ)


def execute(statement, scopes):
    match statement:
        case Assignment(_, variables, values):
            values = [get_value(evaluate(value, scopes)) for value in values]
            for target, value in zip(variables, values):
                var = target.name if isinstance(target, Variable) else target.array.name
                scope = next(scope for scope in scopes if var in scope)
                if isinstance(target, Variable):
                    scope[var] = gen_obj(value, scope[var].type)
                else:
                    assert len(value) == 1
                    indexes = get_value(evaluate(target.index, scopes))
                    array = list(get_value(scope[var]))
                    value = value[0]
                    for index in indexes:
                        array[index] = value
                    scope[var] = gen_obj(array, scope[var].type)
        case Declaration(_, _, _):
            pass
        case IfBlock(_, condition, body):
            if any(get_value(evaluate(condition, scopes))):
                execute(body, scopes)
        case IfElseBlock(_, condition, body1, body2):
            if any(get_value(evaluate(condition, scopes))):
                execute(body1, scopes)
            else:
                execute(body2, scopes)
        case WhileLoop(_, condition, body):
            while any(get_value(evaluate(condition, scopes))):
                execute(body, scopes)
        case tuple(statements):
            for statement in statements:
                execute(statement, scopes)
        case unsupported_thing:
            raise Exception(f"{unsupported_thing}")

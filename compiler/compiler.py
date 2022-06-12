from nodes import *
from typechecking import derive_type, Type, typecheck, unify_types
from itertools import zip_longest

LOGICAL = {"and", "or", "not"}

UNIQUE_ID_COUNTER = hash(None) % (10**6)


def get_uid():
    global UNIQUE_ID_COUNTER
    uid = str(UNIQUE_ID_COUNTER).zfill(6)
    UNIQUE_ID_COUNTER += 1
    return uid


def get_value(obj: Object):
    base = 256 ** (2**obj.type.byte_lvl)
    if obj.type.sign == "u":
        values = [v % base for v in obj.value]
    values = [(v + base // 2) % base - base // 2 for v in obj.value]
    if obj.type.elements <= len(values):
        return tuple(values[: obj.type.elements])
    return tuple(values + [0] * (obj.type.elements - len(values)))


def gen_obj(it, typ):
    return Object(get_value(Object(it, typ)), typ)


def compile_get(var, typ):
    var = compile_var_name(var)
    assert typ.elements == 1
    if typ.byte_lvl == 0:
        return f"mov al, {var}\npush ax\n"
    if typ.byte_lvl == 1:
        return f"mov ax, {var}\npush ax\n"
    if typ.byte_lvl == 2:
        return f"lea si, {var}\nmov ax, [si]\nadd si, 2\n" + "mov dx, [si]\npush dx\npush ax"
    raise NotImplementedError()

def compile_compare(typ, operation):
    assert typ.elements == 1
    label = "l" + get_uid()
    end = f"mov ax, 0\npush ax\njmp {label}_end\n" + f"{label}_true:\nmov ax, 1\npush ax\n" + f"{label}_end:\n"
    if typ.byte_lvl < 2:
        cmp = "pop ax\npop bx\n"
        cmp += "cmp al, bl\n" if typ.byte_lvl == 0 else "cmp ax, bx\n"
        match (operation, typ.sign):
            case "!=", _:
                return cmp + f"jne {label}_true\n" + end
            case "==", _:
                return cmp + f"je {label}_true\n" + end
            case ">", "i":
                return cmp + f"jg {label}_true\n" + end
            case ">=", "i":
                return cmp + f"jge {label}_true\n" + end
            case "<", "i":
                return cmp + f"jl {label}_true\n" + end
            case "<=", "i":
                return cmp + f"jle {label}_true\n" + end
            case ">", "u":
                return cmp + f"ja {label}_true\n" + end
            case ">=", "u":
                return cmp + f"jae {label}_true\n" + end
            case "<", "u":
                return cmp + f"jb {label}_true\n" + end
            case "<=", "u":
                return cmp + f"jbe {label}_true\n" + end
    raise NotImplementedError

def compile_expression(expression, scopes):
    typ = derive_type(expression, scopes)
    match expression:
        case Byte(_, value) | Number(_, value):
            return f"mov al, {value}\npush ax\n"
        case Array(pos, items):
            raise NotImplementedError()
            items = tuple(get_value(compile_expression(item, scopes))[0] for item in items)
            return Object(items, typ)
        case Variable(pos, var):
            obj = next(scope[var] for scope in scopes if var in scope)
            return compile_get(var, obj.type)
        case Function(_):
            raise NotImplementedError()
        case Application(_):
            raise NotImplementedError()
        case BinaryOperation(pos, operation, x, y) if operation in LOGICAL:
            raise NotImplementedError()
            x = get_value(compile_expression(x, scopes))
            if all(x) and operation == "or":
                return Object((1,) * typ.elements, typ)
            if not any(x) and operation == "and":
                return Object((0,) * typ.elements, typ)
            y = get_value(compile_expression(y, scopes))
            if operation == "or":
                xy = zip_longest(x, y, fillvalue=0)
                return gen_obj([bool(x or y) for x, y in xy], typ)
            xy = zip_longest(x, y, fillvalue=1)
            return gen_obj([bool(x and y) for x, y in xy], typ)
        case BinaryOperation(pos, operation, x, y):
            x_type, y_type = (derive_type(z, scopes) for z in (x, y))
            x, y = (compile_expression(z, scopes) for z in (x, y))
            match operation:
                case "+":
                    assert typ.elements == 1
                    xy = ( (y + compile_cast(y_type, typ)) + (x + compile_cast(x_type, typ)))
                    if typ.byte_lvl == 0:
                        return xy + "pop ax\npop bx\nadd al, bl\npush ax\n"
                    if typ.byte_lvl == 1:
                        return xy + "pop ax\npop bx\nadd ax, bx\npush ax\n"
                    raise NotImplementedError()
                case "-":
                    raise NotImplementedError()
                    xy = zip_longest(x, y, fillvalue=0)
                    return gen_obj([x - y for x, y in xy], typ)
                case "*":
                    raise NotImplementedError()
                    xy = zip_longest(x, y, fillvalue=1)
                    return gen_obj([x * y for x, y in xy], typ)
                case "/":
                    raise NotImplementedError()
                    xy = zip_longest(x, y, fillvalue=1)
                    return gen_obj([x // y for x, y in xy], typ)
                case cmp if cmp in {">", ">=", "<", "<=", "!=", "=="}:
                    typ = unify_types(x_type, y_type)
                    return ( (y + compile_cast(y_type, typ)) + (x + compile_cast(x_type, typ)) + compile_compare(typ, cmp))
                case op:
                    raise Exception(f"unsupported operation: {op}")
        case UnaryOperation(_, operation, argument):
            x = compile_expression(argument, scopes)
            match operation:
                case "(":
                    return x
                case "-":
                    raise NotImplementedError()
                    return gen_obj(tuple(-x for x in get_value(x)), typ)
                case op:
                    raise Exception(f"unsupported operation: {op}")
        case TypeCast(_, expr, _):
            raise NotImplementedError()
            return gen_obj(get_value(compile_expression(expr, scopes)), typ)
        case Indexing(_, array, index):
            arr_type = derive_type(array, scopes)
            ind_type = derive_type(index, scopes)
            assert ind_type.elements == 1
            assert ind_type.byte_lvl == 0
            var = compile_var_name(array.name)
            _, elements, byte_lvl = next(scope[var].type for scope in scopes if var in scope)
            index_push = compile_expression(index, scopes)
            get_target = index_push + f"lea si, {var}\npop ax\nmov ah, 0\n" + "add si, ax\n" * (2**byte_lvl)
            load = ["mov al, [si]", "mov ax, [si]"][byte_lvl] + "\n"
            push = ["push ax", "push ax", "push dx\push ax"][byte_lvl] + "\n"
            return get_target + load + push


def compile_statement(statement, scopes):
    match statement:
        case Assignment(_, variables, values):
            values = [compile_expression(value, scopes) for value in values]
            code = ["".join(reversed(values))]
            for target in variables:
                if isinstance(target, Variable):
                    var = target.name
                    scope = next(scope for scope in scopes if var in scope)
                    _, elements, byte_lvl = scope[var].type
                    var = compile_var_name(target.name)
                    assert elements == 1
                    pop = ["pop ax", "pop ax", "pop ax\npop dx"][byte_lvl] + "\n"
                    move = [f"mov {var}, al", f"mov {var}, ax"][byte_lvl] + "\n"
                    code.append(pop + move)
                else:
                    var = target.array.name
                    scope = next(scope for scope in scopes if var in scope)
                    _, elements, byte_lvl = scope[var].type
                    var = compile_var_name(target.array.name)
                    index_push = compile_expression(target.index, scopes)
                    get_target = index_push + f"lea si, {var}\npop ax\nmov ah, 0\nadd si, ax\n"
                    pop = ["pop ax", "pop ax", "pop ax\npop dx"][byte_lvl] + "\n"
                    move = ["mov [si], al", "mov [si], ax"][byte_lvl] + "\n"
                    code.append(get_target + pop + move)
            return "".join(code)
        case Declaration(_, _, _):
            return ""
        case IfBlock(_, condition, body):
            label = "if" + get_uid()
            _, elements, byte_lvl = derive_type(condition, scopes)
            assert elements == 1
            assert byte_lvl == 0
            return (
                f"{label}:\n"
                + compile_expression(condition, scopes)
                + "pop ax\ntest al, al\n"
                + f"jnz {label}_body\njmp {label}_end\n"
                + (f"{label}_body:\n" + compile_statements(body, scopes) + f"{label}_end:\n")
            )
        case WhileLoop(_, condition, body):
            label = "while" + get_uid()
            _, elements, byte_lvl = derive_type(condition, scopes)
            assert elements == 1
            assert byte_lvl == 0
            return (
                f"{label}:\n"
                + compile_expression(condition, scopes)
                + "pop ax\ntest al, al\n"
                + f"jnz {label}_body\njmp {label}_end\n"
                + (f"{label}_body:\n" + compile_statements(body, scopes) + f"jmp {label}\n{label}_end:\n")
            )
        case unsupported_thing:
            raise Exception(f"{unsupported_thing}")


def compile_cast(typ1, typ2):
    assert typ1.elements == 1
    assert typ2.elements == 1
    if typ1.byte_lvl == typ2.byte_lvl:
        return ""
    if typ1.byte_lvl < typ2.byte_lvl:
        return {
                ("s", 0, 1) : "pop ax\ncbw\npush ax\n",
                ("u", 0, 1) : "pop ax\nmov ah, 0\npush ax\n",
                ("s", 1, 2) : "pop ax\ncwd\npush dx\npush ax\n",
                ("u", 1, 2) : "pop ax\nmov dx, 0\npush dx\npush ax\n",
                }[typ1.sign, typ1.byte_lvl, typ2.byte_lvl]
    raise NotImplementedError()

def compile_var_name(variable):
    return "".join(char if char == char.lower() else "big_" + char.lower() for char in variable)


def compile_scope(scope):
    code = []
    for var, obj in scope.items():
        _, elements, byte_lvl = obj.type
        typ = ["db", "dw", "dd"][byte_lvl]
        var = compile_var_name(var)
        value = ",".join("0" for _ in range(elements))
        code.append(f"{var} {typ} " + value + "\n")
    return "".join(code)


def compile_statements(statements, scopes):
    code = []
    for statement in statements:
        code.append(compile_statement(statement, scopes))
    return "".join(code)


def prettify_assembly(assembly: str):
    lines = []
    for line in assembly.strip().split("\n"):
        if line and not line.endswith(":") and not line.startswith("halt:") and not line == "jmp begin":
            line = "\t" + line
        lines.append(line)
    return "\n".join(lines)


def compile(program):
    scope = typecheck(program)
    code = "jmp begin\n" + compile_scope(scope) + "begin:\n" + compile_statements(program, (scope,)) + "halt:jmp halt;$E\n"
    return prettify_assembly(code)

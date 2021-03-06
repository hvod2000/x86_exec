from nodes import *
from parser import *


def ast2str(node):
    match node:
        case Byte(_, value):
            return repr(chr(value))
        case Number(_, value):
            return str(value)
        case Variable(_, value):
            return str(value)
        case BinaryOperation(_, op, x, y):
            return ast2str(x) + f" {op} " + ast2str(y)
        case UnaryOperation(_, "(", x):
            return "(" + ast2str(x) + ")"
        case UnaryOperation(_, op, x):
            return f" {op} " + ast2str(x)
        case Indexing(_, arr, index):
            return ast2str(arr) + "[" + ast2str(index) + "]"
        case Array(_, items):
            return "[" + ", ".join(map(ast2str, items)) + "]"
        case TypeCast(_, expr, typ):
            return ast2str(expr) + " : " + ast2str(typ)
        case IfBlock(_, condition, body):
            body = ("    " + line for line in ast2str(body).split("\n"))
            return "if " + ast2str(condition) + "\n" + "\n".join(body)
        case IfElseBlock(_, condition, body1, body2):
            body1 = ("    " + line for line in ast2str(body1).split("\n"))
            body2 = ("    " + line for line in ast2str(body2).split("\n"))
            return "if " + ast2str(condition) + "\n" + "\n".join(body1) + "\nelse\n" + "\n".join(body2) + "\n"
        case WhileLoop(_, condition, body):
            body = ("    " + line for line in ast2str(body).split("\n"))
            return "while " + ast2str(condition) + "\n" + "\n".join(body)
        case Declaration(_, var, typ):
            return ast2str(var) + " : " + ast2str(typ)
        case Assignment(pos=_, variables=vrbls, values=vals):
            vrbls = ", ".join(map(ast2str, vrbls))
            vals = ", ".join(map(ast2str, vals))
            return f"{vrbls} = {vals}"
        case tuple(xs):
            return "\n".join(map(ast2str, xs))
        case unrecognized_shit:
            raise ValueError(f"{unrecognized_shit}?")

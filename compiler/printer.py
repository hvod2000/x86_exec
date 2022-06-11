from nodes import *
from parser import *

def ast2str(node):
    match node:
        case (_, value):
            return str(value)
        case BinaryOperation(_, op, x, y):
            return ast2str(x) + f" {op} " + ast2str(y)
        case UnaryOperation(_, op, x):
            return f" {op} " + ast2str(x)
        case Indexing(_, arr, index):
            return f"{arr}[{index}]"
        case Assignment(pos=_, variables=vrbls, values=vals):
            vrbls = ", ".join(map(ast2str, vrbls))
            vals = ", ".join(map(ast2str, vals))
            return  f"{vrbls} = {vals}"
        case list(xs):
            return  "\n".join(map(ast2str, xs))
        case unrecognized_shit:
            raise ValueError(f"{unrecognized_shit}?")
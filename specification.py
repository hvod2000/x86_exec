from tokenizer import tokenize
from itertools import product
import pathlib

dict2fun = lambda dct: lambda name: dct.get(name, name)
ARGUMENT_TYPES = {"r": "registers", "m": "memory", "imm": "immediate"}


def parse_operators_specification(specification):
    lines = (line.split("#")[0].strip() for line in specification.split("\n"))
    source = [tokenize(line)[0] for line in lines if line]
    operators, order = {}, []
    for operator, *tokens in source:
        if operator not in operators:
            operators[operator] = set()
            order.append(operator)
        args = [[]]
        for token in tokens:
            if token == "/":
                continue
            elif token == ",":
                args.append([])
            else:
                args[-1].append(token)
        if not args[-1]:
            args.pop()
        for args in product(*args):
            operators[operator].add(tuple(map(dict2fun(ARGUMENT_TYPES), args)))
    return {k: operators[k] for k in order}


operators = pathlib.Path("operations").read_text()
operators = parse_operators_specification(operators)

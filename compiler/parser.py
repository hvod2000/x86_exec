from typing import List
from collections import namedtuple
from nodes import *
from errors import *

#LONG_JUMPS = False
#REGISTERS = {"ax", "bx", "al", "bl"}
OPERATORS = set("+-*/%()[]<>=") | {"<=", ">=", "!=", "=="}
NAME_CHARS = set("qfuyzxkcwboheaidrtnsmjglpv0123456789")
NAME_CHARS |= {char.upper() for char in NAME_CHARS}
Token = namedtuple("Token", "pos literal")


def get_indent(line):
    i = 0
    while i < len(line) and line[i] in " \t":
        i += 1
    return i

def next_token(source, i=0):
    if source[i:i+2] in OPERATORS:
        return i + 2, source[i:i+2]
    if source[i:i+1] in OPERATORS:
        return i + 1, source[i:i+1]
    j = i
    while j < len(source) and source[j] in NAME_CHARS:
        j += 1
    return j, source[i:j]

def tokenize(source: str):
    indents, tokens = [0], []
    for line_no, line in enumerate(source.split("\n")):
        indent = get_indent(line)
        line = (line.split("#", 1)[0] if "#" in line else line).strip()
        if indent > indents[-1]:
            indents.append(indent)
            tokens.append(Token((line_no, indent // 2), "INDENT"))
        while indent < indents[-1]:
            tokens.append(Token((line_no, indent // 2), "DEINDENT"))
            indents.pop()
        assert indents[-1] == indent
        i = 0
        while i < len(line):
            j, (i, literal) = i, next_token(line, i)
            tokens.append(Token((line_no, indent + j), literal))
            while i < len(line) and line[i] in " \t":
                i += 1
    for _ in range(len(indents) - 1):
        tokens.append(Token((line_no + 1, 0), "DEINDENT"))
    return tokens + [Token(None, "END")]

def parse(source, i=0):
    return parse_statements(tokenize(source), i)[1]

def parse_statements(tokens, i):
    statements = []
    while tokens[i] != Token(None, "END"):
        i, statement = parse_statement(tokens, i)
        statements.append(statement)
    return i, statements

def parse_statement(tokens, i):
    if tokens[i].literal == "while" and tokens[i + 1].literal not in ",=":
        return parse_while(tokens, i)
    return parse_assignment(tokens, i)

def parse_assignment(tokens, i):
    i, variable = parse_variable(tokens, i)
    variables = [variable]
    while tokens[i] == ",":
        i, variable = parse_variable(tokens, i + 1)
        variables.append(variable)
    if tokens[i].literal != "=":
        raise DslSyntaxError(tokens[i].pos, '"=" was expected here')
    j, expr = parse_expression(tokens, i + 1)
    expressions = [expr]
    while tokens[j].literal == ",":
        j, expr = parse_expression(tokens, j + 1)
        expressions.append(expr)
    return j, Assignment(tokens[i].pos, variables, expressions)

def parse_variable(tokens, i):
    print("parse var:", tokens[i-1:i+2])
    variable = tokens[i].literal
    if variable.isdigit() or not all(char in NAME_CHARS for char in variable):
        raise DslSyntaxError(tokens[i].pos, 'It does not look like variable name')
    if tokens[i + 1].literal == "[":
        return parse_indexing(tokens, i)
    variable = Variable(tokens[i].pos, variable)
    return i + 1, variable

def parse_expression(tokens, i):
    return parse_dijunction(tokens, i)

def parse_dijunction(tokens, i):
    i, result = parse_conjunction(tokens, i)
    while tokens[i].literal == "or":
        j, (i, conjunction) = i, parse_conjunction(tokens, i + 1)
        result = BinaryOperation(tokens[j].pos, "or", result, conjunction)
    return i, result

def parse_conjunction(tokens, i):
    i, result = parse_unary_boolean(tokens, i)
    while tokens[i].literal == "and":
        j, (i, element) = i, parse_unary_boolean(tokens, i + 1)
        result = BinaryOperation(tokens[j].pos, "and", result, element)
    return i, result

def parse_unary_boolean(tokens, i):
    if tokens[i].literal == "not":
        j, argument = parse_comparison(tokens, i + 1)
        return UnaryOperation(tokens[i].pos, "not", argument)
    return parse_comparison(tokens, i)

def parse_comparison(tokens, i):
    i, result = parse_arithmetic(tokens, i)
    if tokens[i].literal not in {"<=", "<", ">", ">=", "!=", "=="}:
        return i, result
    j, right = parse_arithmetic(tokens, i + 1)
    return i, BinaryOperation(tokens[i].pos, tokens[i].liter, result, right)
    

def parse_arithmetic(tokens, i):
    if tokens[i].literal == "-":
        j, (i, result) = i, parse_product(tokens, i + 1)
        resulc = UnaryOperation(tokens[j], "-", result)
    else:
        i, result = parse_product(tokens, i)
    while tokens[i].literal in "+-":
        j, (i, right) = i, parse_product(tokens, i + 1)
        result = BinaryOperation(tokens[j].pos, tokens[j].literal, result, right)
    return i, result

def parse_product(tokens, i):
    i, result = parse_exponent(tokens, i)
    while tokens[i].literal in {"*", "/", "%", "//"}:
        j, (i, right) = i, parse_exponent(tokens, i + 1)
        result = BinaryOperation(tokens[j].pos, tokens[j].literal, result, right)
    return i, result

def parse_exponent(tokens, i):
    i, result = parse_unary(tokens, i)
    while tokens[i].literal == "^":
        j, (i, right) = i, parse_unary(tokens, i + 1)
        result = BinaryOperation(tokens[j].pos, "^", result, right)
    return i, result

def parse_unary(tokens, i):
    print("unary", tokens[i-1:])
    if tokens[i].literal == "(":
        i, expr = parse_expression(tokens, i + 1)
        assert tokens[i].literal == ")"
        return i + 1, expr
    if tokens[i].literal.isdigit():
        return parse_number(tokens, i)
    if tokens[i].literal == "[":
        return parse_array(tokens, i)
    return parse_variable(tokens, i)

def parse_number(tokens, i):
    return i + 1, Number(tokens[i].pos, tokens[i].literal)

def parse_array(tokens, i):
    raise NotImplementedError()
def parse_indexing(tokens, i):
    raise NotImplementedError()
def parse_while(tokens, i):
    raise NotImplementedError()
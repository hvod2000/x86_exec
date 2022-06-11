from collections import namedtuple

Char = namedtuple("Char", "pos value")
Array = namedtuple("Array", "pos items")
Number = namedtuple("Number", "pos value")
Variable = namedtuple("Variable", "pos name")
Function = namedtuple("Function", "pos parameters body")

BinaryOperation = namedtuple("BinaryOperation", "pos operation arg1 arg2")
UnaryOperation = namedtuple("UnaryOperation", "pos operation argument")
Application = namedtuple("Application", "pos function arguments")
TypeCast = namedtuple("TypeCast", "pos argument type")
Indexing = namedtuple("Indexing", "pos array index")

Assignment = namedtuple("Aassignment", "pos variables values")
WhileLoop = namedtuple("WhileLoop", "pos condition body")
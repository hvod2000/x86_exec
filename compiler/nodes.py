from collections import namedtuple

Byte = namedtuple("Byte", "pos value")
Array = namedtuple("Array", "pos items")
Number = namedtuple("Number", "pos value")
Variable = namedtuple("Variable", "pos name")
Function = namedtuple("Function", "pos parameters body")

BinaryOperation = namedtuple("BinaryOperation", "pos operation arg1 arg2")
UnaryOperation = namedtuple("UnaryOperation", "pos operation argument")
Application = namedtuple("Application", "pos function arguments")
TypeCast = namedtuple("TypeCast", "pos argument type")
Indexing = namedtuple("Indexing", "pos array index")

Declaration = namedtuple("Declaration", "pos variable type")
Assignment = namedtuple("Aassignment", "pos variables values")
WhileLoop = namedtuple("WhileLoop", "pos condition body")
IfBlock = namedtuple("IfBlock", "pos condition body")

# runtime
Object = namedtuple("Object", "value type")

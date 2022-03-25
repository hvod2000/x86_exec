import dataclasses
from string import ascii_lowercase, digits

OPERATIONS = {"mov", "cbw", "cwd", "add", "sub"}


def is_int(number):
    try:
        int(number)
    except ValueError:
        return False
    return True


dict2fun = lambda dct: lambda name: dct[name]


@dataclasses.dataclass
class Instruction:
    operation: str
    args: list[str]
    comment: str = ""

    @classmethod
    def parse(line):
        word_chars = set(ascii_lowercase + digits)
        line, comment = line.split(";", 1) if ";" in line else (line, "")
        source, tokens, in_word = line.strip().lower(), [], False
        for char in source:
            if char in word_chars:
                if in_word:
                    tokens[-1] += char
                else:
                    tokens.append(char)
            else:
                if char not in " \t":
                    tokens.append(char)
            in_word = char in word_chars
        if not tokens:
            return Instruction("", [], comment)
        if tokens[0] in OPERATIONS:
            if not all(comma == "," for comma in tokens[2::2]):
                return None
            return Instruction(tokens[0], tokens[1::2], comment)
        if len(tokens) == 3 and tokens[1] in {"dw", "db"}:
            return Instruction("define", tokens, comment)
        return None

    def typecheck(self, regs, vars):
        op, args = self.operation, self.args
        if op not in OPERATIONS:
            return op == "" and not args or op == "define"
        match op:
            case "mov":
                if len(tokens) != 2:
                    return False
                x, y = tokens
                if x in vars and y in regs:
                    return True
                return x in vars and y in (regs | vars)
            case "cbw", "cwd":
                return not len(tokens)
            case "add", "sub":
                if len(tokens) != 2:
                    return False
                x, y = tokens
                if x in regs and (y in (regs | vars) or is_int(y)):
                    return True
                return x in vars and (y in regs or is_int(y))

    def execute(self, vars):
        op, args, get_var = self.operation, self.args, dict2fun(vars)
        match op:
            case "mov":
                target, source = map(get_var, args)
                target.value = source.value
            case "cbw":
                vars["ax"].value = vars["al"].value.sext(2)
            case "cwd":
                vars["dx"] = vars["ax"].value.sext(4).split(2, 2)[1]
            case "add":
                target, source = map(get_var, args)
                target.value += source.value
            case "sub":
                target, source = map(get_var, args)
                target.value -= source.value

    def __str__(self):
        args = ",".join(" " + arg for arg in self.args)
        comment = ";" + self.comment if self.comment else ""
        if self.operation == "define":
            return " ".join(self.args) + comment
        return f"{self.operation}{args}{comment}"

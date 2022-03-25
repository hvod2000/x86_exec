import dataclasses
from string import ascii_lowercase, digits

OPERATIONS = {"mov", "cbw", "cwd", "add", "sub"}


def is_int(number):
    try:
        int(number)
    except ValueError:
        return False
    return True


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

    def __str__(self):
        args = ",".join(" " + arg for arg in self.args)
        comment = ";" + self.comment if self.comment else ""
        return f"{self.operation}{args}{comment}"

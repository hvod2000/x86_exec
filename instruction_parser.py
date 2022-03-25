from string import ascii_lowercase, digits

WORD_CHARS = set(ascii_lowercase + digits + "-")
OPERATIONS = set("mov cbw cwd add sub".split())


def parse_instruction(source):
    source, comment = source.split(";", 1) if ";" in source else (source, "")
    source, tokens, in_word = source.strip().lower(), [], False
    for char in source:
        if char in WORD_CHARS:
            if in_word:
                tokens[-1] += char
            else:
                tokens.append(char)
        else:
            if char not in " \t":
                tokens.append(char)
        in_word = char in WORD_CHARS
    if not tokens:
        return "", [], comment
    if tokens[0] in OPERATIONS:
        if not all(comma == "," for comma in tokens[2::2]) or tokens[-1] == ",":
            return None
        return tokens[0], tokens[1::2], comment
    if len(tokens) == 3 and tokens[1] in {"dw", "db"}:
        return "define", tokens, comment
    return None

from string import ascii_lowercase, digits

WORD_CHARS = set(ascii_lowercase + digits + "-")


def tokenize(source):
    source, comment = source.split(";", 1) if ";" in source else (source, None)
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
    return tokens, comment

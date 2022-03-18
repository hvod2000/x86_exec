def ceil_log(n, base=2):
    if n < 0:
        return ceil_log(-n, base) + 1
    result = 0
    while n:
        result += 1
        n //= base
    return result

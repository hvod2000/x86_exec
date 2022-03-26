from collections import ChainMap


class ChainDict:
    def __init__(self, *dicts):
        self.dicts = dicts

    def __getitem__(self, i):
        for d in self.dicts:
            if i in d:
                return d[i]
        raise KeyError(i)

    def __setitem__(self, i, value):
        try:
            next(d for d in self.dicts if i in d)[i] = value
        except StopIteration:
            raise KeyError(i)

    def items(self):
        visited = set()
        for d in self.dicts:
            for k, v in d.items():
                if k in visited:
                    continue
                visited.add(k)
                yield k, v


class FunDict:
    def __init__(self, f):
        self.f = f

    def __getitem__(self, i):
        return self.f[i]

    def items(self):
        pass

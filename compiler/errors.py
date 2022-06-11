def warnging(msg):
    print(f"\033[33mWARNING: {msg}\033[0m")


def error(msg):
    print(f"\033[31m ERRROR: {msg}\033[0m")
    exit(42)

class DslSyntaxError(Exception):
    def __init__(self, pos, msg):
        self.pos = pos
        self.msg = msg
        super().__init__(msg)
    def __str__(self):
        return super().__str__() +":"+ str(self.pos)

import dataclasses


@dataclasses.dataclass
class Instruction:
    operation: str
    args: list[str]
    comment: str = ""

    def __str__(self):
        args = ",".join(" " + arg for arg in self.args)
        comment = ";" + self.comment if self.comment else ""
        return f"{self.operation}{args}{comment}"
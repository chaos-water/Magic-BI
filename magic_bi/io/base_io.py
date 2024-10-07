

class BaseIo():
    def input(self) -> str:
        raise NotImplementedError("Method should be implementd")

    def output(self, content: str):
        raise NotImplementedError("Method should be implementd")

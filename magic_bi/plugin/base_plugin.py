class BasePlugin():
    def __init__(self):
        self.max_context_size: int = 8000

    def run(self, argument: str, context: str):
        raise NotImplementedError("this method shold ")




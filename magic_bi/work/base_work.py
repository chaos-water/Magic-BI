from loguru import logger


from magic_bi.work.work import Work
from magic_bi.work.work import WorkInput, WorkOutput


class BaseWork(Work):
    def __init__(self):
        pass

    def execute(self, work_input: WorkInput) -> WorkOutput:
        logger.error("this method should be overridden")
        raise NotImplementedError("this method should be overridden")

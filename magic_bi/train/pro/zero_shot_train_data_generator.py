from loguru import logger


class ZeroShotTrainDataGenerator(object):
    def init(self) -> int:
        logger.debug("ZeroShotTrainDataGenerator init suc")
        return 0

    def resume(self) -> int:
        raise NotImplementedError("This method is not implemented")

    def start(self) -> int:
        raise NotImplementedError("This method is not implemented")

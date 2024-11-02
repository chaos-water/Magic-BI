from loguru import logger


class FewShotTrainDataGenerator:

    def init(self) -> int:
        logger.debug("FewShotTrainDataGenerator init suc")
        return 0

    def start(self) -> int:
        raise NotImplementedError("This method is not implemented")

    def resume(self, train_data_id: str):
        raise NotImplementedError("This method is not implemented")
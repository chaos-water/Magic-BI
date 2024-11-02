from threading import Lock
from loguru import logger
import numpy as np
from sentence_transformers import SentenceTransformer, util
from magic_bi.config.model_config import ModelConfig


class TextEmbedding():
    _model: any = None
    _get_lock: Lock = Lock()

    def init(self, model_config: ModelConfig):
        self._model = SentenceTransformer(model_config.model, trust_remote_code=True, local_files_only=True)

        logger.debug("TextEmbedding init suc")
        return 0

    def get(self, text: str) -> list:
        try:
            self._get_lock.acquire()
            embedding = self._model.encode(text)
            vector = np.array(embedding)
            normalized_vector = vector / np.sqrt(np.sum(vector ** 2))

            logger.debug("TextEmbedding get suc")
            return normalized_vector.tolist()
        finally:
            self._get_lock.release()

    def calculate_distance(self, vector1: list, vector2: list) -> float:
        cos_score = util.cos_sim(vector1, vector2)
        return cos_score

    def get_model(self) -> SentenceTransformer:
        return self._model

if __name__ == '__main__':
    model_config = ModelConfig()
    model_config.model_path = "/home/luguanglong/Codes/mojing/Magic-Vision/model.md/distiluse-base-multilingual-cased-v1"
    text_embedding = TextEmbedding()
    text_embedding.init(model_config)
    ret = text_embedding.get("你好")
    pass
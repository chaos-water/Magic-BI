from loguru import logger
from magic_bi.oss.minio_adapter import MinioAdapter
from magic_bi.config.oss_config import OssConfig


class OssFactory:
    def __init__(self):
        self._storage_adapter: MinioAdapter = None

    def init(self, oss_config: OssConfig) -> int:
        if oss_config.type == "minio":
            self._storage_adapter: MinioAdapter = MinioAdapter()
            self._storage_adapter.init(oss_config)
        else:
            logger.error("init failed, unsupportd oss type:%s" % oss_config.type)
            return -1

        # if self._storage_adapter.has_bucket(oss_config.default_bucket) is False:
        #     self._storage_adapter.add_bucket(oss_config.default_bucket)

        logger.debug("OssFactory init suc")
        return 0

    def has_bucket(self, bucket_name: str="default") -> bool:
        return self._storage_adapter.has_bucket(bucket_name)

    def add_bucket(self, bucket_name: str="default") -> int:
        return self._storage_adapter.add_bucket(bucket_name)

    def delete_bucket(self, bucket_name: str="default") -> int:
        return self._storage_adapter.delete_bucket(bucket_name)

    def add_file(self, file_id: str, file_bytes: bytes, bucket_name: str= "default") -> int:

        return self._storage_adapter.add_file(file_id, file_bytes, bucket_name)

    def add_file_without_id(self, file_bytes: bytes, bucket_name: str= "default") -> int:
        return self._storage_adapter.add_file_without_id(file_bytes, bucket_name)

    def get_file(self, file_id: str, bucket_name: str="default") -> (bytes, int):
        return self._storage_adapter.get_file(bucket_name, file_id)

    def del_file(self, file_id: str, bucket_name: str="default") -> int:
        return self._storage_adapter.del_file(bucket_name, file_id)

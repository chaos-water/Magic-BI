import io
from loguru import logger
from minio import Minio

from magic_bi.config.oss_config import OssConfig


class MinioAdapter():
    def __init__(self):
        self._default_location = "cn-north-1"
        self._client: Minio = None

    def init(self, oss_config: OssConfig) -> int:
        self._client = Minio(oss_config.endpoint, access_key=oss_config.access_key, secret_key=oss_config.secret_key,
                             secure=False)
        logger.debug("init MinioAdapter suc")
        return 0

    def add_file(self, file_id: str, file_bytes: bytes, bucket_name: str) -> int:
        try:
            try:
                ret = self._client.stat_object(bucket_name, file_id)
                if ret.size > 0:
                    logger.debug("add_file suc, file already exixsted, bucket_name:%s, file_id:%s" % (
                        bucket_name, file_id))
                    return 0
            except Exception as e:
                pass

            object_data_io = io.BytesIO(file_bytes)
            self._client.put_object(bucket_name, file_id, object_data_io, object_data_io.getbuffer().nbytes,
                                    content_type='application/octet-stream')
            logger.debug("add_file suc, bucket_name:%s, file_id:%s" % (bucket_name, file_id))
            return 0
        except Exception as e:
            logger.error("catch Exception: " + str(e))
            return -1

    def add_file_without_id(self, file_bytes: bytes, bucket_name: str) -> str:
        import uuid
        file_id = uuid.uuid1().hex
        ret = self.add_file(file_id=file_id, file_bytes=file_bytes, bucket_name=bucket_name)
        if ret == 0:
            logger.debug("add_file suc, bucket_name:%s, file_id:%s" % (bucket_name, file_id))
            return file_id
        else:
            logger.error("add_file failed, bucket_name:%s, file_id:%s" % (bucket_name, file_id))
            return ""

    def del_file(self, file_id: str, bucket_name: str) -> int:
        try:
            ret = self._client.stat_object(bucket_name, file_id)
            if ret.size > 0:
                self._client.remove_object(bucket_name, file_id)

            logger.debug("del_file suc, bucket_name:%s, file_id:%s" % (bucket_name, file_id))
        except Exception as e:
            logger.error("catch Exception: " + str(e))
            return -1

    def get_file(self, file_id: str, bucket_name: str) -> (bytes, int):
        try:
            object_ret = self._client.stat_object(bucket_name, file_id)
            if object_ret.size > 0:
                data = self._client.get_object(bucket_name, file_id).read()
                logger.debug("get_file suc, bucket_name:%s, file_id:%s, object_size:%d" % (
                    bucket_name, file_id, object_ret.size))
                return data, object_ret.size
        except Exception as e:
            logger.error("catch Exception: " + str(e))
            return "".encode(), 0

    def has_bucket(self, bucket_name: str) -> bool:
        try:
            return self._client.bucket_exists(bucket_name)
        except Exception as e:
            logger.error("catch Exception: " + str(e))
            return False

    def add_bucket(self, bucket_name: str) -> int:
        try:
            buckets = self._client.list_buckets()
            for bucket in buckets:
                if bucket.name == bucket_name:
                    logger.debug("add_bucket suc, bucket:%s already existed" % (bucket_name))
                    return 0
            self._client.make_bucket(bucket_name, location=self._default_location)
            logger.debug("add_bucket suc, bucket_name:%s" % (bucket_name))
            return 0
        except Exception as e:
            logger.error("catch Exception: " + str(e))
            return -1

    def delete_bucket(self, bucket_name: str) -> int:
        try:
            # 列出 bucket 中的所有对象
            objects = self._client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                self._client.remove_object(bucket_name, obj.object_name)

            # 删除 bucket
            self._client.remove_bucket(bucket_name)
            logger.debug("deleted bucket: {bucket_name}")
            return 0
        except Exception as e:
            logger.error(f"Error occurred: %s" % str(e))
            return -1

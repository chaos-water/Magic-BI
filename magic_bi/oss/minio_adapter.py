import io
from loguru import logger
from minio import Minio
import urllib3

from magic_bi.config.oss_config import OssConfig
# 这段代码中的get_file会报错，请分析并解决
class MinioAdapter():
    def __init__(self):
        self._default_location = "cn-north-1"
        self._client: Minio = None

    def init(self, oss_config: OssConfig) -> int:
        self._client = Minio(oss_config.endpoint, access_key=oss_config.access_key, secret_key=oss_config.secret_key,
                             secure=False, http_client=urllib3.PoolManager(timeout=6000))
        logger.debug("init MinioAdapter suc")
        return 0

    def add_file_by_path(self, file_id: str, file_path: str, bucket_name: str) -> int:
        try:
            try:
                ret = self._client.stat_object(bucket_name, file_id)
                if ret.size > 0:
                    logger.debug("add_file suc, file already exixsted, bucket_name:%s, file_id:%s" % (
                        bucket_name, file_id))
                    return 0
            except Exception as e:
                pass

            self._client.fput_object(bucket_name, file_id, file_path)
            logger.debug("add_file_by_path suc, bucket_name:%s, file_id:%s" % (bucket_name, file_id))
            return 0
        except Exception as e:
            logger.error("catch Exception: " + str(e))
            return -1

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
            return 0
        except Exception as e:
            logger.error("catch Exception: " + str(e))
            return -1

    def stream_file(self, bucket_name: str, file_id: str, chunk_size: int = 10 * 1024 * 1024):
        try:
            object_stat = self._client.stat_object(bucket_name, file_id)
            if object_stat.size > 0:
                offset = 0
                total_size = object_stat.size

                while offset < total_size:
                    length = min(chunk_size, total_size - offset)
                    response = self._client.get_object(bucket_name, file_id, offset=offset, length=length)
                    chunk_data = response.read()  # 读取当前块数据

                    yield chunk_data  # 使用 yield 返回数据块，供 StreamingResponse 逐块发送

                    offset += len(chunk_data)

        except Exception as e:
            logger.error(f"Error streaming file: {str(e)}")
            raise Exception("stream_file failed")

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
            logger.error("file_id:%s, bucket_name:%s" % (file_id, bucket_name))
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

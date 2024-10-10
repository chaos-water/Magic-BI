import json
from typing import Any
import asyncio
from loguru import logger
import hashlib
from PIL import Image
from io import BytesIO
import base64
import numpy as np


def init_log(level="DEBUG"):
    logger.remove(handler_id=None)
    logger.add('./log/{time:YYYY-MM-DD}.log', level=level, rotation='1024 MB', encoding='utf-8')

def get_http_rsp(code=0, msg="suc", data={}):
    """
    get_http_rsp
    """
    rsp = {"code": code, "data": data, "msg": msg}
    return rsp

def syn_execute_asyn_func(future) -> Any:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    return future.result()

def get_bytes_hash(input_bytes: bytes) -> str:
    sha256 = hashlib.sha256()
    sha256.update(input_bytes)
    return sha256.hexdigest()

def generate_formatted_time():
    from datetime import datetime
    # 获取当前时间
    now = datetime.now()
    # 格式化时间，例如：2024-08-22 14:45:30
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def image_bytes_to_base64(image_bytes) -> str:
    image_base64 = base64.b64encode(image_bytes)
    return image_base64.decode('utf-8')

def image_ndarray_to_base64(image_ndarray) -> str:
    image_bytes = image_ndarray_to_bytes(image_ndarray)
    image_base64 = base64.b64encode(image_bytes)
    return image_base64.decode('utf-8')

def image_ndarray_to_bytes(image_ndarray) -> bytes:
    image = Image.fromarray(image_ndarray)

    # 创建一个 BytesIO 对象，用于保存图像的字节数据
    image_bytes = BytesIO()

    # 将图像保存为字节数据
    image.save(image_bytes, format='JPEG')  # 你可以根据需要选择其他图像格式

    # 获取字节数据
    image_bytes_data = image_bytes.getvalue()
    return image_bytes_data

def image_bytes_to_ndarray(image_bytes: bytes) -> np.ndarray:
    # 使用BytesIO将字节数据转换为PIL Image对象
    image = Image.open(BytesIO(image_bytes))

    # 将PIL Image对象转换为NumPy数组
    image_array = np.array(image)
    return image_array

def format_db_url(db_url: str) -> str:
    if db_url.startswith("mysql://"):
        converted_url = db_url.replace('mysql://', 'mysql+pymysql://')
        return converted_url
    else:
        return db_url
import json

import asyncio
from loguru import logger
import hashlib
from PIL import Image
from io import BytesIO
import base64
import numpy as np
import zipfile
import os

def init_log(level="DEBUG"):

    logger.remove(handler_id=None)
    logger.add('./log/{time:YYYY-MM-DD}.log', level=level, rotation='1024 MB', encoding='utf-8', format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

def get_http_rsp(code=0, msg="suc", data={}):
    """
    get_http_rsp
    """
    rsp = {"code": code, "data": data, "msg": msg}
    return rsp

def syn_execute_asyn_func(future) -> any:
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
    import imghdr
    # 创建一个 BytesIO 对象，以便 imghdr 识别图片类型
    image_file = BytesIO(image_bytes)
    img_type = imghdr.what(image_file)

    if img_type:
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        data_uri = f"data:image/{img_type};base64,{base64_data}"
    else:
        data_uri = ""
        raise ValueError("无法识别图片类型")

    return data_uri

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

def base64_to_image_bytes(base64_string: str):
    # 去掉头部的元数据
    if base64_string.startswith('data:image/png;base64,'):
        base64_string = base64_string.replace('data:image/png;base64,', '')
    elif base64_string.startswith('data:image/jpeg;base64,'):
        base64_string = base64_string.replace('data:image/jpeg;base64,', '')

    # 将 Base64 字符串解码为二进制数据
    image_bytes = base64.b64decode(base64_string)

    return image_bytes

def format_db_url(db_url: str) -> str:
    if db_url.startswith("mysql://"):
        converted_url = db_url.replace('mysql://', 'mysql+pymysql://')
        return converted_url
    else:
        return db_url

def stop_process_by_pid(pid: int, timeout: int = 30) -> int:
    import os
    import signal
    import psutil
    import time

    try:
        # 尝试正常终止进程 (SIGTERM)
        os.kill(pid, signal.SIGTERM)
        logger.debug(f"Sent SIGTERM to process {pid}. Waiting for it to terminate...")

        # 等待并检查进程是否终止
        for _ in range(timeout):
            if not psutil.pid_exists(pid):
                logger.debug(f"Process {pid} has been successfully terminated.")
                return 0
            time.sleep(1)  # 每隔1秒检查一次进程是否退出

        # 如果10秒后进程仍然存在，强制终止
        if psutil.pid_exists(pid):
            logger.debug(f"Process {pid} is still running. Forcibly terminating it now...")
            os.kill(pid, signal.SIGKILL)
            logger.debug(f"Process {pid} has been forcibly terminated.")

    except ProcessLookupError:
        logger.error(f"Process with PID {pid} does not exist.")
        return -1

    except PermissionError:
        logger.error(f"No permission to terminate process {pid}.")
        return -1

    except Exception as e:
        logger.error(f"Failed to terminate process {pid}: {e}")
        return -1

def next_multiple_of_1024(n: int) -> int:
    # 计算下一个1024的倍数
    if n % 1024 == 0:
        return n  # 如果n已经是1024的倍数，返回n
    else:
        return (n // 1024 + 1) * 1024  # 向上取整到下一个1024的倍数

def zip_directory(folder_path):
    zip_filename = f"{folder_path}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_STORED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    return zip_filename

def get_env_info() -> str:
    env_info = ""

    from magic_bi.utils.utils import generate_formatted_time
    env_info += "Current Time: " + generate_formatted_time()

    return env_info

def clean_llm_output(flag: str, llm_output: str) -> str:
    import re
    if f"```{flag}" in llm_output:
        pattern = re.compile(rf'```{flag}(.*?)```', re.DOTALL)

        # 提取并清理代码块
        matches = pattern.findall(llm_output)
        if matches:
            cleaned_code = [match.strip() for match in matches]
            # 返回代码块，合并成字符串或保持原始列表格式都可行
            return '\n'.join(cleaned_code)
        else:
            return ""
    else:
        return llm_output


import pandas as pd
from io import BytesIO


def generate_excel_file(sheet_name: str, column_names: list, column_data: list):
    import openpyxl
    # 创建一个新的 Excel 工作簿
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = sheet_name

    # 写入标题行
    # sheet.append(["问题", "SQL"])
    sheet.append(column_names)

    # 写入数据行
    for item in column_data:
        sheet.append(item)

    # 将工作簿保存到内存中的二进制流
    excel_stream = BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)  # 重置流的位置以便后续读取

    return excel_stream.getvalue()

def decode_json_list_from_llm_output(input_str: str):
    if input_str.find("```json") != -1:
        import re
        pattern = re.compile(rf'```json(.*?)```', re.DOTALL)
        matches = pattern.findall(input_str)
        try:
            output = json.loads(matches[0].strip())
            return output
        except Exception as e:
            logger.error("catch exception: %s" % str(e))
            logger.error("decode_json_list failed")
    else:
        try:
            output = json.loads(input_str)
            return output
        except Exception as e:
            logger.error("catch exception: %s" % str(e))
            logger.error("decode_json_list failed")

    return []
# 这个函数可以正常工作么？
# def clean_llm_output(flag: str, llm_output: str) -> str:
#     import re
#     if f"```{flag}" in llm_output:
#         pattern = re.compile(rf'```{flag}(.*?)```', re.DOTALL)
#
#         # 提取并清理代码块
#         matches = pattern.findall(llm_output)
#         cleaned_code = [match.strip() for match in matches]
#
#         # 将提取到的代码合并为一个字符串
#         extracted_code = '\n'.join(cleaned_code)
#         return extracted_code
#     else:
#         return llm_output
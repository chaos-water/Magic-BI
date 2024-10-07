import asyncio
import json
from typing import Dict
from loguru import logger
from fastapi.websockets import WebSocket
from magic_bi.io.base_io import BaseIo
from magic_bi.utils.utils import syn_execute_asyn_func


class WebsocketIo(BaseIo):
    def __init__(self, websocket: WebSocket):
        self._websocket: WebSocket = websocket

    def input(self) -> str:
        role = "USER"

        syn_execute_asyn_func(self._websocket.send_text(f"[bold]{role}: "))
        receive_data = syn_execute_asyn_func(self._websocket.send_text(f"[bold]{role}: "))

        if "text" in receive_data:
            receive_data_str: str = receive_data.get("text", "")
        else:
            logger.error("input failed, invalid person_input type")
            return ""

        receive_data = json.loads(receive_data_str)
        content = receive_data.get("content", "")
        logger.debug("input suc, content:%s" % content)
        return content

    def output(self, content: str):
        role = "MAGIC_ASSISTANT"

        syn_execute_asyn_func(self._websocket.send_text(f"[bold]{role}:"))
        syn_execute_asyn_func(self._websocket.send_text(f"{content}"))

        logger.debug("output suc, input:%s" % input)
        return 0

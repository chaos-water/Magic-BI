"""
MqAdapter module
"""
import time
import threading
from loguru import logger
import pika
from magic_bi.config.rabbitmq_config import RabbitmqConfig


def mq_request(prompt: str, callback: str):
    output = {"prompt": {}, callback: callback}
    pass


class RabbitmqProducer():
    def __init__(self):
        self._config: RabbitmqConfig = None
        self.parameters = None

    def init(self, rabbitmq_config: RabbitmqConfig):
        self._config = rabbitmq_config
        credentials = pika.PlainCredentials(username=rabbitmq_config.user, password=rabbitmq_config.password)
        self.parameters = pika.ConnectionParameters(host=rabbitmq_config.host, credentials=credentials)
        # self._connection = pika.BlockingConnection(parameters)
        # self._channel = self._connection.channel()
        logger.debug("init rabbitmq producer suc")
        return 0

    def declare_queue(self, queue: str):
        if self._channel.is_closed:
            self._channel = self._connection.channel()
        self._channel.queue_declare(queue=queue, durable=True)
        logger.debug("declare_queue suc")

    def produce(self, queue:str, msg: str):
        # if self._connection.is_closed:
        #     self.init(self._config)
        #
        # if self._channel.is_closed:
        #     self._channel = self._connection.channel()

        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()

        channel.basic_publish(exchange='', routing_key=queue, body=msg)
        logger.debug("produce suc")

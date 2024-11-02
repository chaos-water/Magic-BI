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

def callback(channel, method, properties, body):
    # 手动标记消息已接收并处理完毕，RabbitMQ可以从queue中移除该条消息
    channel.basic_ack(delivery_tag=method.delivery_tag)

# 这段代码有个问题，callback函数中，通过lorugu输出的log，头部信息是： pika.adapters.blocking_connection:_dispatch_events:1510。
# 而不是log所在的文件、函数和代码行数，请解决。
class RabbitmqConsumer(object):
    def __init__(self, max_retries=None):
        self.max_retries = max_retries
        self._connection = None
        self._callback = None
        self._consumer_tag = ""

    def init(self, config: RabbitmqConfig, callback: callable, queue: str):
        credentials = pika.PlainCredentials(username=config.user, password=config.password)
        parameters = pika.ConnectionParameters(host=config.host, credentials=credentials)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        self._channel.basic_qos(prefetch_count=1)
        self._callback = callback

        self._channel.queue_declare(queue=queue, durable=True)
        self._consumer_tag = self._channel.basic_consume(queue=queue, on_message_callback=self._callback, arguments={"consumer_index": 1})

        self.t = threading.Thread(target=self.keep_connection)
        self.t.start()

        logger.debug("init rabbbitmq consumer suc, consumer_tag:%s" % self._consumer_tag)
        return 0

    def start(self):
        logger.debug("Starting consuming in a new thread, consumer_tag:%s" % self._consumer_tag)
        consuming_thread = threading.Thread(target=self._start_consuming)
        consuming_thread.start()

    def _start_consuming(self):
        self._channel.start_consuming()

    def keep_connection(self):
        logger.debug(f'keep_connection thread id: {threading.get_ident()}')
        time.sleep(10)
        while self._connection.is_open:
            logger.debug("keep_connection")
            # channel.connection.sleep(5.0)
            self._connection.process_data_events()
            time.sleep(10)
            # channel.basic_publish(exchange='', routing_key=dl_queue_name, body="1")
        logger.debug("keep_connection close")


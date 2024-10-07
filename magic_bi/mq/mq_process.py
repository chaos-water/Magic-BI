
from magic_bi.config.rabbitmq_config import RabbitmqConfig
from magic_bi.mq.rabbitmq_consumer import RabbitmqConsumer


def init_mq_process(rabbitmq_config: RabbitmqConfig, func_callback) -> int:
    rabbitmq_consumer = RabbitmqConsumer()
    rabbitmq_consumer.init(rabbitmq_config, func_callback,
                           "analyse_file_collection")

    rabbitmq_consumer.start()
    return 0
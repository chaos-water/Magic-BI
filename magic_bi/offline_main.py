from loguru import logger
from magic_bi.utils.globals import GLOBAL_CONFIG, GLOBALS
from magic_bi.mq.mq_process import init_mq_process
from magic_bi.mq.mq_msg import MqMsg, MQ_MSG_TYPE
# from magic_bi.train.train_manager_mq_func import execute_train_model, execute_deploy_model
from magic_bi.train.model_deployer import ModelDeployer
from magic_bi.train.model_trainer import ModelTrainer
from magic_bi.train.pro.few_shot_train_data_generator import FewShotTrainDataGenerator
from magic_bi.train.pro.zero_shot_train_data_generator import ZeroShotTrainDataGenerator
from magic_bi.train.pure_conversion_train_data_generator import PureConversionTrainDataGenerator


def execute_mq_func(channel, method, properties, body):
    from magic_bi.train.train_data_type import TRAIN_DATA_GENERATE_METHOD
    channel.basic_ack(delivery_tag=method.delivery_tag)

    mq_msg: MqMsg = MqMsg()
    mq_msg.from_json_str(body.decode())
    if mq_msg.msg_type == MQ_MSG_TYPE.START_GENERATE_TRAIN_DATA.value:
        generate_method = mq_msg.msg_json.get("generate_method", "")
        if generate_method == TRAIN_DATA_GENERATE_METHOD.PURE_CONVERSION.value:
            pure_conversion_train_data_generator: PureConversionTrainDataGenerator = PureConversionTrainDataGenerator()
            pure_conversion_train_data_generator.init(GLOBALS)

            pure_conversion_train_data_generator.start(mq_msg.msg_json.get("user_id"),
                                                mq_msg.msg_json.get("train_qa_file_id"),
                                                mq_msg.msg_json.get("sheet_name"),
                                                 mq_msg.msg_json.get("train_data_name"),
                                                 mq_msg.msg_json.get("data_source_id"),
                                                 mq_msg.msg_json.get("table_list"))

        elif generate_method == TRAIN_DATA_GENERATE_METHOD.FEW_SHOT.value:
            few_shot_train_data_generator: FewShotTrainDataGenerator = FewShotTrainDataGenerator()
            few_shot_train_data_generator.init(GLOBALS)

            few_shot_train_data_generator.start(mq_msg.msg_json.get("user_id"),
                                                mq_msg.msg_json.get("train_qa_file_id"),
                                                mq_msg.msg_json.get("sheet_name"),
                                                 mq_msg.msg_json.get("train_data_name"),
                                                 mq_msg.msg_json.get("data_source_id"),
                                                 mq_msg.msg_json.get("table_list"),
                                                 mq_msg.msg_json.get("to_reach_item_cnt"))

        elif generate_method == TRAIN_DATA_GENERATE_METHOD.ZERO_SHOT.value:
            zero_shot_train_data_generator: ZeroShotTrainDataGenerator = ZeroShotTrainDataGenerator()
            zero_shot_train_data_generator.init(GLOBALS)
            zero_shot_train_data_generator.start(mq_msg.msg_json.get("user_id"),
                                                 mq_msg.msg_json.get("train_data_name"),
                                                 mq_msg.msg_json.get("data_source_id"),
                                                 mq_msg.msg_json.get("table_list"),
                                                 mq_msg.msg_json.get("relevant_business", ""),
                                                 mq_msg.msg_json.get("to_reach_item_cnt"),
                                                 mq_msg.msg_json.get("temperature", 0.3))

    elif mq_msg.msg_type == MQ_MSG_TYPE.RESUME_GENERATE_TRAIN_DATA.value:
        train_data_id = mq_msg.msg_json.get("train_data_id", "")
        from magic_bi.train.entity.train_data import TrainData
        from magic_bi.train.utils import get_train_data
        train_data: TrainData = get_train_data(train_data_id)

        if train_data.generate_method == TRAIN_DATA_GENERATE_METHOD.PURE_CONVERSION.value:
            pure_conversion_train_data_generator: PureConversionTrainDataGenerator = PureConversionTrainDataGenerator()
            pure_conversion_train_data_generator.init(GLOBALS)

            pure_conversion_train_data_generator.resume(mq_msg.msg_json.get("train_data_id"))

        elif train_data.generate_method == TRAIN_DATA_GENERATE_METHOD.FEW_SHOT.value:
            few_shot_train_data_generator: FewShotTrainDataGenerator = FewShotTrainDataGenerator()
            few_shot_train_data_generator.init(GLOBALS)

            few_shot_train_data_generator.resume(mq_msg.msg_json.get("train_data_id"))

        elif train_data.generate_method == TRAIN_DATA_GENERATE_METHOD.ZERO_SHOT.value:
            zero_shot_train_data_generator: ZeroShotTrainDataGenerator = ZeroShotTrainDataGenerator()
            zero_shot_train_data_generator.init(GLOBALS)
            zero_shot_train_data_generator.resume(mq_msg.msg_json.get("train_data_id"),
                                                 mq_msg.msg_json.get("temperature", 0.3))

    elif mq_msg.msg_type == MQ_MSG_TYPE.TRAIN_MODEL.value:
        model_trainer: ModelTrainer = ModelTrainer()
        ret = model_trainer.execute(mq_msg.msg_json.get("domain_model_id"),
                                   mq_msg.msg_json.get("train_data_id"),
                                   mq_msg.msg_json.get("cuda_devices", ""),
                                   mq_msg.msg_json.get("train_epochs", 1.0))

        if ret == 0:
            logger.debug("execute_train_model suc")
        else:
            logger.error("execute_train_model fail")

    elif mq_msg.msg_type == MQ_MSG_TYPE.DEPLOY_MODEL.value:
        model_deployer: ModelDeployer = ModelDeployer()
        ret = model_deployer.execute(mq_msg.msg_json.get("model_server_host_ip"),
                                     mq_msg.msg_json.get("model_deploy_ip"),
                                     mq_msg.msg_json.get("domain_model_id"),
                                     mq_msg.msg_json.get("username"),
                                     mq_msg.msg_json.get("password"),
                                     mq_msg.msg_json.get("deploy_model_name", ""),
                                     mq_msg.msg_json.get("force", False))

        if ret == 0:
            logger.debug("deploy_model suc")
        else:
            logger.error("deploy_model fail")

    else:
        logger.error(f"unknown message type {mq_msg.msg_type}")

    logger.debug("execute_mq_func suc")


def offline_main():
    init_mq_process(rabbitmq_config=GLOBAL_CONFIG.rabbitmq_config, func_callback=execute_mq_func)

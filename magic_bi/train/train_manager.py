
from loguru import logger
from sqlalchemy.orm import Session


from magic_bi.utils.globals import Globals, GLOBALS
from magic_bi.config.global_config import GlobalConfig
from magic_bi.train.entity.domain_model import DomainModel
from magic_bi.train.entity.train_data import TrainData
from magic_bi.train.entity.train_qa_file import TrainQaFile
from magic_bi.train.train_data_type import TRAIN_DATA_GENERATE_METHOD
from magic_bi.mq.mq_msg import MqMsg, MQ_MSG_TYPE
from magic_bi.train.entity.domain_model import DOMAIN_MODEL_STATE
from magic_bi.train.entity.train_data_original_item import TrainDataOriginalItem
from magic_bi.train.entity.train_data_prompted_item import TrainDataPromptedItem
from magic_bi.train.utils import parse_excel_to_json


class TrainManager():
    def __init__(self, global_config: GlobalConfig, globals: Globals):
        self.globals: Globals = globals
        self.global_config = global_config

    def import_qa_file(self, input_train_qa_file: TrainQaFile) -> str:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                existed_train_qa_file: TrainQaFile = session.query(TrainQaFile).filter(TrainQaFile.hash == input_train_qa_file.hash,
                                                          TrainQaFile.name == input_train_qa_file.name).one_or_none()
                if existed_train_qa_file is not None:
                    return existed_train_qa_file.id
                session.add(input_train_qa_file)
                session.commit()

            ret = self.globals.oss_factory.add_file(input_train_qa_file.id, input_train_qa_file.file_bytes)
            if ret < 0:
                logger.error("import_qa_file failed")
                return ""

            # question_2_sql_dict = parse_excel_to_dict(train_qa_file.file_bytes, train_qa_file.sheet_name)
            # for question, sql_statement in question_2_sql_dict.items():
            #     train_data_original_item: TrainDataOriginalItem = TrainDataOriginalItem()
            #     train_data_original_item.input = question
            #     train_data_original_item.output = sql_statement
            #     train_data_original_item.generate_method = TRAIN_DATA_GENERATE_METHOD.PURE_CONVERSION.value
            #     train_data_original_item.train_qa_file_id = train_qa_file.id

            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                session.add(input_train_qa_file)
                session.commit()

        except Exception as e:
            logger.error("add import_qa_file failed")
            logger.error("catch exception:%s" % str(e))
            return ""

        logger.debug("import_qa_file suc")
        return input_train_qa_file.id

    def delete_train_qa_file(self, id: str) -> int:
        try:
            self.globals.oss_factory.del_file(id)

            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                session.query(TrainQaFile).filter(TrainQaFile.id == id).delete()
                session.commit()

        except Exception as e:
            logger.error("delete_qa_file failed")
            logger.error("catch exception:%s" % str(e))
            return -1

        logger.debug("delete_qa_file suc")
        return 0

    def get_train_qa_file(self, user_id: str) -> list[TrainQaFile]:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                train_qa_file_list = session.query(TrainQaFile).filter(TrainQaFile.user_id == user_id).all()

                logger.debug("get_qa_file suc, ")
                return train_qa_file_list
        except Exception as e:
            logger.error("add data failed")
            logger.error("catch exception:%s" % str(e))
            return []

    def get_train_data(self, user_id: str) -> list[TrainData]:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                train_data_list: list[TrainData] = session.query(TrainData).filter(TrainData.user_id == user_id).all()

                logger.debug("get_train_data suc, train_data_list cnt:%d" % len(train_data_list))
                return train_data_list
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return []

    def get_train_data_by_id(self, train_data_id: str) -> TrainData:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                train_data: TrainData = session.query(TrainData).filter(TrainData.id == train_data_id).one_or_none()

                logger.debug("get_train_data_by_id suc")
                return train_data
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return None

    def get_train_data_original_item(self, train_data_id: str, valid_filter_flag: str) -> list[TrainDataOriginalItem]:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                if valid_filter_flag == "valid" or valid_filter_flag == "invalid":
                    train_data_original_item_list: list[TrainDataOriginalItem] = \
                        session.query(TrainDataOriginalItem).filter(TrainDataOriginalItem.train_data_id == train_data_id,
                                                                    TrainDataOriginalItem.valid_result == valid_filter_flag).all()
                else:
                    train_data_original_item_list: list[TrainDataOriginalItem] = \
                        session.query(TrainDataOriginalItem).filter(TrainDataOriginalItem.train_data_id == train_data_id).all()

                logger.debug("get_original_train_original_item suc")
                return train_data_original_item_list
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("get_original_train_original_item failed")
            return []


    # def train_domain_model(self, domain_model_id: str, train_data_id: str, cuda_devices: str, train_epochs: float) -> int:
    #     with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
    #         domain_model: DomainModel = session.query(DomainModel).filter(DomainModel.id == domain_model_id).one_or_none()
    #         if domain_model is None:
    #             logger.error(f"train_domain_model failed, domain_model {domain_model_id} not existed")
    #             return -1
    #
    #         if domain_model.state != DOMAIN_MODEL_STATE.NOT_TRAINED.value:
    #             logger.error(f"train_domain_model failed, domain_model state is {domain_model.state}")
    #             return -1
    #
    #     mq_msg: MqMsg = MqMsg()
    #     mq_msg.msg_type: str = MQ_MSG_TYPE.TRAIN_DOMAIN_MODEL.value
    #     mq_msg.msg_json: dict = {"domain_model_id": domain_model_id, "train_data_id": train_data_id, "cuda_devices": cuda_devices,
    #                              "train_epochs": train_epochs}
    #
    #     ret = self.globals.rabbitmq_producer.produce(self.global_config.rabbitmq_config.internal_mq_queue, mq_msg.to_json_str())
    #
    #     logger.debug("generate_train_data suc")
    #     return ret

    def stop_generate_train_data(self, train_id: str) -> int:
        return 0
        # with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
        #     train: Train = session.query(Train).filter(Train.id == train_id).one_or_none()
        #     if train is None:
        #         logger.error("stop_enhance_train_data failed")
        #         return -1
        #
        #     ret = stop_process_by_pid(train.enhance_train_data_process_id)
        #     if ret == 0:
        #         logger.debug("stop_enhance_train_data suc")
        #     else:
        #         logger.error("stop_enhance_train_data failed")
        #
        #     return ret

    def stop_train_model(self, train_id: str) -> int:
        return 0
        # with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
        #     train: Train = session.query(Train).filter(Train.id == train_id).one_or_none()
        #     if train is None:
        #         logger.error("stop_enhance_train_data failed")
        #         return -1
        #
        #     ret = stop_process_by_pid(train.train_model_process_id)
        #     if ret == 0:
        #         logger.debug("stop_train_model suc")
        #     else:
        #         logger.error("stop_train_model failed")
        #
        #     return ret

    def add_model(self, domain_model: DomainModel) -> int:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                session.add(domain_model)
                session.commit()
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("add_model failed")
            return -1

        logger.debug("add_model scu")
        return 0

    def get_domain_model(self, user_id: str) -> list[DomainModel]:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                train_model_list = session.query(DomainModel).filter(DomainModel.user_id == user_id).all()

                logger.debug("get_model suc")
                return train_model_list
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("get_model failed")
            return []

    def get_domain_model_by_id(self, domain_model_id: str) -> DomainModel:
        try:
            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                domain_model: DomainModel = session.query(DomainModel).filter(DomainModel.id == domain_model_id).one_or_none()

                logger.debug("get_domain_model_by_id suc")
                return domain_model
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("domain_model failed")
            return None

    def delete_model(self, domain_model_id: str) -> int:
        try:
            ret = self.globals.oss_factory.del_file(domain_model_id)
            if ret < 0:
                logger.error(f"delete_file {domain_model_id} failed")

            with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
                session.query(DomainModel).filter(DomainModel.id == domain_model_id).delete()
                session.commit()

                logger.debug("delete_model suc")
                return 0
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            logger.error("delete_model failed")
            return -1

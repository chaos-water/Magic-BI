from typing import List
from loguru import logger
from sqlalchemy.orm import Session
import pandas as pd

from magic_bi.db.qdrant_adapter import QdrantPoint
from magic_bi.utils.globals import Globals
from magic_bi.data.data_source import DataSourceOrm
from magic_bi.data.data_source_knowledge.qa_template import QaTemplate
from magic_bi.data.data_source_knowledge.table_description import TableDescription
from magic_bi.data.data_source_knowledge.table_column_description import TableColumnDescription
from magic_bi.data.data_source_knowledge.domain_knowledge import DomainKnowledge
from magic_bi.data.data_source import get_qa_template_embedding_collection_id, get_domain_knowledge_embedding_collection_id, get_table_description_embedding_collection_id
from magic_bi.utils.error import ERROR_CODE, get_error_message
from magic_bi.config.language_config import LanguageConfig

class DataSourceManager():
    def __init__(self, globals: Globals, lanuage_config: LanguageConfig):
        self.globals: Globals = globals
        self.language_config: LanguageConfig = lanuage_config

    def add(self, data_source_orm: DataSourceOrm) -> (int, str):
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            count = session.query(DataSourceOrm).filter(DataSourceOrm.user_id == data_source_orm.user_id,
                                                        DataSourceOrm.url == data_source_orm.url).count()
            if count > 0:
                logger.error("add data source, the same data %s already exists" % data_source_orm.name)
                return ERROR_CODE.DUPLICATE_ADD.value, get_error_message(ERROR_CODE.DUPLICATE_ADD)

        qa_template_collection_id = get_qa_template_embedding_collection_id(data_source_orm.id)
        table_description_collection_id = get_table_description_embedding_collection_id(data_source_orm.id)
        domain_knowledge_collection_id = get_domain_knowledge_embedding_collection_id(data_source_orm.id)

        ret1 = self.globals.qdrant_adapter.add_collection(qa_template_collection_id, 768)
        ret2 = self.globals.qdrant_adapter.add_collection(table_description_collection_id, 768)
        ret3 = self.globals.qdrant_adapter.add_collection(domain_knowledge_collection_id, 768)

        if ret1 != 0 or ret2 != 0 or ret3 != 0:
            logger.error("add data source failed, update qdrant failed")
            return ERROR_CODE.UNKNOWN_ERROR.value, get_error_message(ERROR_CODE.UNKNOWN_ERROR)

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            ret = session.query(DataSourceOrm).filter(DataSourceOrm.user_id == data_source_orm.user_id, \
                                                      DataSourceOrm.url == data_source_orm.url).count()
            if ret > 0:
                logger.error("add data source failed, the same connector has already been added")
                return ERROR_CODE.DUPLICATE_ADD.value, get_error_message(ERROR_CODE.DUPLICATE_ADD)

            session.add(data_source_orm)
            session.commit()

        logger.debug("add dataset suc")
        return ERROR_CODE.SUC.value, get_error_message(ERROR_CODE.SUC)

    def delete(self, data_source_orm: DataSourceOrm) -> int:
        with Session(self.globals.sql_orm.engine) as session:
            session.query(DataSourceOrm).filter(DataSourceOrm.id == data_source_orm.id).delete()
            session.commit()

        logger.debug("delete data_source suc")
        return ERROR_CODE.SUC.value

    def get(self, user_id: str = "", id: str = "", page_index: int = 1, page_size: int = 10) -> List[DataSourceOrm]:
        if page_index < 1:
            page_index = 1
        offset = (page_index - 1) * page_size
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            data_source_list: List[DataSourceOrm] = []
            if user_id != "":
                data_source_list = session.query(DataSourceOrm).filter(DataSourceOrm.user_id == user_id).\
                    offset(offset).limit(page_size).all()
            elif id != "":
                data_source_list = session.query(DataSourceOrm).filter(DataSourceOrm.id == id).offset(offset).\
                    limit(page_size).all()

        logger.debug("get data_source suc, data_source_cnt:%d" % len(data_source_list))
        return data_source_list

    def count(self, user_id: str = "") -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            count = session.query(DataSourceOrm).filter(DataSourceOrm.user_id == user_id).count()

        logger.debug("count suc, count:%d" % count)
        return count

    def add_qa_template(self, qa_template: QaTemplate) -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            ret = session.query(QaTemplate).filter(QaTemplate.data_source_id == qa_template.data_source_id, QaTemplate.question == qa_template.question).count()
            if ret > 0:
                logger.error("add qa template failed, the same qa template has already been added")
                return -1

            session.add(qa_template)
            session.commit()

        question_vector = self.globals.text_embedding.get(qa_template.question)
        collection_id = get_qa_template_embedding_collection_id(qa_template.data_source_id)

        from magic_bi.db.qdrant_adapter import QdrantPoint
        qdrant_point = QdrantPoint()
        qdrant_point.vector = question_vector
        qdrant_point.payload = {"question": qa_template.question, "answer": qa_template.answer}

        ret = self.globals.qdrant_adapter.upsert(collection_id, qdrant_point)
        if ret == 0:
            logger.debug("add_qa_template suc")
        else:
            logger.error("add_qa_template failed")

        return ret

    def update_qa_template(self, qa_template: QaTemplate) -> int:
        from sqlalchemy import update

        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            stmt = update(QaTemplate).where(QaTemplate.id == qa_template.id).values(
                question=qa_template.question).values(answer=qa_template.answer)
            # 执行更新

            session.execute(stmt)
            session.commit()

        logger.debug("update_qa_template suc")
        return 0

    def get_qa_template(self, data_source_id: str) -> List[QaTemplate]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            from typing import List
            qa_template_list: List[QaTemplate] = session.query(QaTemplate).filter(
                QaTemplate.data_source_id == data_source_id).all()

        logger.debug("get_qa_template suc, qa_template_list_cnt:%d" % len(qa_template_list))
        return qa_template_list


    def export_qa_template(self, data_source_id: str) -> pd.DataFrame:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            qa_template_list = session.query(QaTemplate).filter(QaTemplate.data_source_id == data_source_id).all()

        question_list = [qa_template.question for qa_template in qa_template_list]
        answer_list = [qa_template.answer for qa_template in qa_template_list]

        data = {"question": question_list, "answer": answer_list}
        df = pd.DataFrame(data)

        logger.debug("export_qa_template suc")
        return df

    def import_qa_template(self, df: pd.DataFrame, data_source_id: str) -> int:
        if 'question' not in df.columns or 'answer' not in df.columns:
            logger.error("import_qa_template failed")
            return -1

        question_answer_list = df[['question', 'answer']].to_dict(orient='records')
        for question_answer in question_answer_list:
            body = {"data_source_id": data_source_id, "question": question_answer.get("question"), "answer": question_answer.get("answer")}
            qa_template = QaTemplate()
            qa_template.from_dict(body)
            self.add_qa_template(qa_template)

        logger.debug("import_qa_template suc")
        return 0

    def add_table_description(self, table_description: TableDescription) -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            ret = session.query(TableDescription).filter(TableDescription.data_source_id == table_description.data_source_id, TableDescription.table_name == table_description.table_name).count()
            if ret > 0:
                logger.error("add table description failed, the same table description has already been added")
                return -1

            session.add(table_description)
            session.commit()

        table_description_vector = self.globals.text_embedding.get(table_description.table_description)
        collection_id = get_table_description_embedding_collection_id(table_description.data_source_id)

        qdrant_point = QdrantPoint()
        qdrant_point.vector = table_description_vector
        qdrant_point.payload = {"table_name": table_description.table_name, "table_description": table_description.table_description}

        ret = self.globals.qdrant_adapter.upsert(collection_id, qdrant_point)
        if ret == 0:
            logger.debug("add_table_description suc")
            return 0
        else:
            logger.error("add_table_description failed")
            return -1

    def delete_table_description(self, data_source_id: str, id: str) -> int:
        with Session(self.globals.sql_orm.engine) as session:
            session.query(TableDescription).filter(TableDescription.id == id).delete()
            session.commit()

        collection_id = get_table_description_embedding_collection_id(data_source_id)

        ret = self.globals.qdrant_adapter.delete_point(collection_id, [id])
        if ret == 0:
            logger.debug("delete_table_description suc")
            return 0
        else:
            logger.error("delete_table_description failed")
            return -1

    def get_table_description(self, data_source_id: str) -> List[TableDescription]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            table_description_list = session.query(TableDescription).filter(TableDescription.data_source_id == data_source_id).all()

        logger.debug("get_table_description suc")
        return table_description_list

    def add_table_column_description(self, table_column_description: TableColumnDescription) -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            session.add(table_column_description)
            session.commit()

        logger.debug("add_table_column_description suc")
        return 0

    def delete_table_column_description(self, id: str) -> int:
        with Session(self.globals.sql_orm.engine) as session:
            session.query(TableColumnDescription).filter(TableColumnDescription.id == id).delete()
            session.commit()

        logger.debug("delete_table_column_description suc")
        return 0

    def get_table_column_description(self, data_source_id: str, table_name: str) -> List[TableColumnDescription]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            table_column_description_list = session.query(TableColumnDescription).\
                filter(TableColumnDescription.data_source_id == data_source_id, table_name == table_name).all()

        logger.debug("get_table_column_description suc")
        return table_column_description_list

    def add_domain_knowledge(self, domain_knowledge: DomainKnowledge) -> int:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            ret = session.query(DomainKnowledge).filter(DomainKnowledge.data_source_id == domain_knowledge.data_source_id, DomainKnowledge.content == domain_knowledge.content).count()
            if ret > 0:
                logger.error("add domain knowledge failed, the same domain knowledge has already been added")
                return -1

            session.add(domain_knowledge)
            session.commit()

        domain_knowledge_vector = self.globals.text_embedding.get(domain_knowledge.content)
        collection_id = get_domain_knowledge_embedding_collection_id(domain_knowledge.data_source_id)

        qdrant_point = QdrantPoint()
        qdrant_point.vector = domain_knowledge_vector
        qdrant_point.payload = {"content": domain_knowledge.content}

        ret = self.globals.qdrant_adapter.upsert(collection_id, qdrant_point)
        if ret == 0:
            logger.debug("add_domain_knowledge suc")
            return 0
        else:
            logger.error("add_domain_knowledge failed")
            return -1

    def delete_domain_knowledge(self, data_source_id: str, id: str) -> int:
        with Session(self.globals.sql_orm.engine) as session:
            session.query(DomainKnowledge).filter(DomainKnowledge.id == id).delete()
            session.commit()

        collection_id = get_domain_knowledge_embedding_collection_id(data_source_id)
        ret = self.globals.qdrant_adapter.delete_point(collection_id, [id])
        if ret == 0:
            logger.debug("delete_domain_knowledge suc")
            return 0
        else:
            logger.error("delete_domain_knowledge failed")
            return -1
        return 0


    def get_domain_knowledge(self, data_source_id: str) -> List[DomainKnowledge]:
        with Session(self.globals.sql_orm.engine, expire_on_commit=False) as session:
            domain_knowledge_list = session.query(DomainKnowledge).filter(DomainKnowledge.data_source_id == data_source_id).all()

        logger.debug("get_domain_knowledge suc")
        return domain_knowledge_list

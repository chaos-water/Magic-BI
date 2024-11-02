from loguru import logger
from sqlalchemy.orm import Session


from magic_bi.data.data_source import DataSource
from magic_bi.utils.globals import Globals

data_zero_recommend_prompt_template = '''
[DATA CONTENT]:
{data_content}

[USER PROFILE]:
{user_profile}

[EXAMPLE OUTPUTS]
xxx
xxx
xxx

Based on the above, generate 10 relevant questions in Chinese for BI purpose. 
The questions can be answered by sql queries.
The question should be ranked by its business value.
The list of questions should be diverse, and the questions should be prioritized according to their business value.
You just need to output the questions, no others(including explanations and sql queries) needed.
'''

data_source_zero_recommend_prompt_template = '''
[OPTIONAL DATA CONNECTORS]:
data_source_name | data_source_url ｜ table descriptions
-----------------------
{provided_data_sources}

[USER PROFILE]:
{user_profile}

[EXAMPLE OUTPUTS]
xxx
xxx
xxx

Based on the above, generate {count} relevant questions in Chinese for BI purpose. 
The questions can be answered by sql queries.
The question should be ranked by its business value.
The list of questions should be diverse, and the questions should be prioritized according to their business value.
You just need to output the questions, no others(including explanations and sql queries) needed.
'''

relevant_prompt_template = '''
[OPTIONAL DATA CONNECTORS]:
data_source_name | data_source_url ｜ table descriptions
-----------------------
{provided_data_sources}

[USER PROFILE]:
{user_profile}

[PREVIOUS USER QUESTION]:
{previous_user_question}

[EXAMPLE OUTPUTS]
xxx
xxx
xxx
......

Based on the above, generate 10 relevant questions in Chinese for BI purpose. 
The questions can be answered by sql queries.
The question should be ranked by its bi
The list of questions should be relevant with [PREVIOUS USER QUESTION] and diverse, and the questions should be prioritized according to their relevance and business value.
You just need to output the questions, no others(including explanations and sql queries) needed.
'''

class Recommender():
    def __init__(self):
        self.globals: Globals = None

    def _get_user_profile(self, user_id: str) -> str:

        logger.debug("_get_user_profile suc")
        return ""

    def init(self, globals: Globals) -> int:
        self.globals = globals

        return 0

    def zero_recommend(self, user_id: str, data_source_id: str, dataset_id: str, data_id: str, count: int) -> list[str]:
        recomendation_list = []
        if data_source_id != "":
            recomendation_list = self.zero_recommend_by_data_source(user_id, data_source_id, count)
        elif dataset_id != "":
            recomendation_list = self.zero_recommend_by_dataset(user_id, dataset_id)
        elif data_id != "":
            recomendation_list = self.zero_recommend_by_data(user_id, data_id)
        else:
            logger.error("zero_recommend failed, data_source_id:%s dataset_id:%s" % (data_source_id, dataset_id))

        logger.debug("zero_recommend suc, recomendation_list cnt:%d" % len(recomendation_list))
        return recomendation_list

    def zero_recommend_by_data_source(self, user_id: str, data_source_id: str, count: int) -> list[str]:
        relevant_data_source = self.get_relevant_data_source_from_input(user_id, data_source_id)
        provided_data_sources = ""
        for data_source in relevant_data_source:
            data_source.generate_meta_info()
            provided_data_sources += data_source.get_meta_info()

        recommend_prompt = (data_source_zero_recommend_prompt_template.replace("{provided_data_sources}", provided_data_sources).\
                            replace("{user_profile}", self._get_user_profile(user_id))).\
                            replace("{count}", str(count))
        llm_output = self.globals.general_llm_adapter.process(recommend_prompt)

        recomendation_list = llm_output.split("\n")

        logger.debug("zero_recommend suc, recomendation cnt:%d" % len(recomendation_list))
        return recomendation_list

    def zero_recommend_by_dataset(self, user_id: str, dataset_id: str) -> list[str]:
        relevant_data_source = self.get_relevant_data_source_from_input(user_id, dataset_id)
        provided_data_sources = ""
        for data_source in relevant_data_source:
            data_source.generate_meta_info()
            provided_data_sources += data_source.get_meta_info()

        recommend_prompt = data_source_zero_recommend_prompt_template.format(provided_data_sources=provided_data_sources, user_profile=self._get_user_profile(user_id))
        llm_output = self.globals.general_llm_adapter.process(recommend_prompt)

        recomendation_list = llm_output.split("\n")

        logger.debug("zero_recommend suc, recomendation cnt:%d" % len(recomendation_list))
        return recomendation_list

    def zero_recommend_by_data(self, user_id: str, data_id: str) -> list[str]:
        data_bytes, ret = self.globals.oss_factory.get_file()
        if ret > 0:
            pass

        # relevant_data_source = self.get_relevant_data_source_from_input(user_id, dataset_id)
        # provided_data_sources = ""
        # for data_source in relevant_data_source:
        #     data_source.generate_meta_info()
        #     provided_data_sources += data_source.to_str_with_meta_info()

        # recommend_prompt = data_source_zero_recommend_prompt_template.format(provided_data_sources=provided_data_sources, user_profile=self._get_user_profile(user_id))
        # llm_output = self.globals.llm_adapter.process(recommend_prompt)
        #
        # recomendation_list = llm_output.split("\n")

        # logger.debug("zero_recommend suc, recomendation cnt:%d" % len(recomendation_list))
        # return recomendation_list

    def relevant_recommend(self, user_id: str, previous_user_input: str, data_source_id: str, dataset_id: str, data_id: str) -> list[str]:
        recomendation_list = []
        if data_source_id != "":
            recomendation_list = self.relevant_recommend_by_data_source(user_id, data_source_id, previous_user_input)
        elif dataset_id != "":
            recomendation_list = self.relevant_recommend_by_dataset(user_id, dataset_id, previous_user_input)
        elif data_id != "":
            recomendation_list = self.relevant_recommend_by_data(user_id, data_id, previous_user_input)
        else:
            logger.error("zero_recommend failed, data_source_id:%s dataset_id:%s" % (data_source_id, dataset_id))

        logger.debug("zero_recommend suc, recomendation_list cnt:%d" % len(recomendation_list))
        return recomendation_list

    def relevant_recommend_by_data_source(self, user_id: str, data_source_id: str, previous_user_input: str) -> list[str]:
        relevant_data_source = self.get_relevant_data_source_from_input(user_id, data_source_id)
        provided_data_sources = ""
        for data_source_id in relevant_data_source:
            provided_data_sources += data_source_id.get_meta_info()

        recommend_prompt = relevant_prompt_template.format(provided_data_sources=provided_data_sources,
                                                           user_profile=self._get_user_profile(user_id),
                                                           previous_user_question=previous_user_input)
        llm_output = self.globals.general_llm_adapter.process(recommend_prompt)

        recomendation_list = llm_output.split("\n")
        logger.debug("relevant_recommend suc")
        return recomendation_list

    def relevant_recommend_by_dataset(self, user_id: str, dataset_id: str, previous_user_input: str) -> list[str]:
        relevant_data_source = self.get_relevant_data_source_from_input(user_id, dataset_id)
        provided_data_sources = ""
        for dataset_id in relevant_data_source:
            provided_data_sources += dataset_id.get_meta_info()

        recommend_prompt = relevant_prompt_template.format(provided_data_sources=provided_data_sources,
                                                           user_profile=self._get_user_profile(user_id),
                                                           previous_user_question=previous_user_input)
        llm_output = self.globals.general_llm_adapter.process(recommend_prompt)

        recomendation_list = llm_output.split("\n")
        logger.debug("relevant_recommend suc")
        return recomendation_list

    def relevant_recommend_by_data(self, user_id: str, data_id: str, previous_user_input: str) -> list[str]:
        relevant_data_source = self.get_relevant_data_source_from_input(user_id, data_id)
        provided_data_sources = ""
        for data_id in relevant_data_source:
            provided_data_sources += data_id.get_meta_info()

        recommend_prompt = relevant_prompt_template.format(provided_data_sources=provided_data_sources,
                                                           user_profile=self._get_user_profile(user_id),
                                                           previous_user_question=previous_user_input)
        llm_output = self.globals.general_llm_adapter.process(recommend_prompt)

        recomendation_list = llm_output.split("\n")
        logger.debug("relevant_recommend suc")
        return recomendation_list

    def get_relevant_data_source_from_input(self, user_id, data_source) -> list[DataSource]:
        authorized_data_source_list: list[DataSource] = []

        if data_source == "all":
            with Session(self.globals.sql_orm.engine) as session:
                authorized_data_source_list: list[DataSource] = session.query(DataSource).filter(DataSource.user_id == user_id).all()
        else:
            with Session(self.globals.sql_orm.engine) as session:
                authorized_data_source_list: list[DataSource] = session.query(DataSource).filter(DataSource.id == data_source).all()

        for authorized_data_source in authorized_data_source_list:
            authorized_data_source.generate_meta_info()

        return authorized_data_source_list


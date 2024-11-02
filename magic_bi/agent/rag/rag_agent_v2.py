
import json

from magic_bi.agent.memmory import Memmory
from loguru import logger

from magic_bi.agent.base_agent import BaseAgent
from magic_bi.message.message import Message
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.config.agent_config import AgentConfig


rag_prompt_template = \
"""{relevant_knowledge}

[User Question]
    {user_question}

[Instructions]:
    1、基于上诉文档片段，言简意赅的回答用户问题，不需要任何多余的信息，如建议和语气词等；
    2、不要提及你引用的文档名，也不用提及你用了哪个文档片段；
    3、如果你认为在已经选择的文档片段中部分与用户问题无关，则忽略就可以，只基于与用户问题相关的文档片段回答用户问题；
    4、不要超出选择的文档片段范围回答用户问题，如果选择的文档片段无法回答用户问题，则礼貌拒绝回答并说明原因，而不是自己捏造答案；
    5、尽可能直接引用原文回答问题，而不是自己基于原文做改写和总结；
    6、输出纯文本格式，不需要markdown格式。

首先分析给定的条件，然后逐步解决问题，不要输出推理中间步骤，直接输出推理结果。"""


merge_answer_prompt_template = \
"""[Answer 1]:
{answer1}

[Answer 2]:
{answer2}

[User Question]
    {user_question}

[Instructions]:
    1, 合并上诉独立答案，来回答用户问题；
    2，按照{"merge_answer": "$merge_answer", "reason": "$reason"}格式回答。

首先分析给定的条件，然后逐步解决问题，不要输出推理中间步骤，直接输出推理结果。"""

extract_keyword_prompt_template = \
"""[User Question]:
    {user_question}
    
[Instructions]:
    1, extract key words from User Question;
    2, The sorting of keywords is consistent with the order in the original text;
    3, output in json list format [] in {language_name} directly without other explanations.
    
First, analyze the given conditions, then solve the problem step by step. Do not output the intermediate steps of reasoning; directly provide the reasoning result.
"""


class RagAgentV2(BaseAgent):
    def __init__(self):
        self.memmory: Memmory = Memmory()
        self.polite_refuse = "对不起，知识库中没有检索到相关知识，请换个其它问题。"
        super().__init__()

    def init(self, agent_meta: AgentMeta, agent_config: AgentConfig, globals: Globals, io: BaseIo, language_name: str) -> int:
        super().init(agent_meta, agent_config, globals, io, language_name)

        logger.debug("init suc")
        return 0


    def get_relevant_file_list(self, user_input_embedding: list, dataset_id: str) ->list[str]:
        summary_search_results = self.globals.qdrant_adapter.search(dataset_id + "_summary", user_input_embedding, cnt=2)
        if len(summary_search_results) == 0:
            return []

        score = summary_search_results[0].score
        if score < 0.3:
            print("illegal file_id:%s, score:%s" % (summary_search_results[0].payload["file_id"], score))
            return []

        file_list = []
        for search_result in summary_search_results:
            file_list.append({"file_id": search_result.payload["file_id"], "file_name": search_result.payload["file_name"]})

        return file_list


    def process(self, message: Message):
        extract_keyword_prompt = extract_keyword_prompt_template.replace("{user_question}", message.person_input).\
                                        replace("{language_name}", self.language_name)
        try:
            llm_output = self.globals.general_llm_adapter.process(extract_keyword_prompt)
            llm_output_json = json.loads(llm_output)
            user_question_keywords_str = " ".join(llm_output_json)
        except Exception as e:
            user_question_keywords_str = ""

        es_answer, es_file_2_relevant_chunk_list = self.process_by_elasticsearch(message, user_question_keywords_str)
        qdrant_answer, qdrant_file_2_relevant_chunk_list = self.process_by_qdrant(message, user_question_keywords_str)

        merge_answer_prompt = merge_answer_prompt_template.replace("{answer1}", es_answer).replace("{answer2}",
                                                                                                     qdrant_answer).replace(
            "{user_question}", message.person_input)
        llm_output = self.globals.general_llm_adapter.process(merge_answer_prompt)
        llm_output_json = json.loads(llm_output)
        merge_answer = llm_output_json.get("merge_answer")

        file_2_relevant_chunk_set = {}
        file_2_relevant_chunk_list = {}

        for file_name, chunk_list in qdrant_file_2_relevant_chunk_list.items():
            if file_name not in file_2_relevant_chunk_set:
                file_2_relevant_chunk_set[file_name] = set(chunk_list)
            else:
                file_2_relevant_chunk_set[file_name].update(set(chunk_list))

        for file_name, chunk_list in es_file_2_relevant_chunk_list.items():
            if file_name not in file_2_relevant_chunk_set:
                file_2_relevant_chunk_set[file_name] = set(chunk_list)
            else:
                file_2_relevant_chunk_set[file_name].update(set(chunk_list))

        for file_name, chunk_set in file_2_relevant_chunk_set.items():
            file_2_relevant_chunk_list[file_name] = list(chunk_set)

        logger.debug("RagAgent process suc")
        return merge_answer, file_2_relevant_chunk_list


    def process_by_elasticsearch(self, message: Message, user_question_keywords_str: str) -> (str, dict):
        if user_question_keywords_str != "":
            relevant_chunk_content_str, output_file_2_chunk_content_dict = self.get_relevant_knowledge_by_elasticsearch(
                message.dataset_id, user_question_keywords_str)
        else:
            relevant_chunk_content_str, output_file_2_chunk_content_dict = self.get_relevant_knowledge_by_elasticsearch(
                message.dataset_id, message.person_input)

        rag_prompt = rag_prompt_template.replace("{relevant_knowledge}", relevant_chunk_content_str).replace("{user_question}", message.person_input)
        rag_llm_output = self.globals.general_llm_adapter.process(rag_prompt)

        return rag_llm_output, output_file_2_chunk_content_dict

    def process_by_qdrant(self, message: Message, user_question_keywords_str: str) -> (str, dict):
        if user_question_keywords_str != "":
            relevant_chunk_content_str, output_file_2_chunk_content_dict = self.get_relevant_knowledge_by_qdrant(
                message.dataset_id, user_question_keywords_str, message.file_id)
        else:
            relevant_chunk_content_str, output_file_2_chunk_content_dict = self.get_relevant_knowledge_by_qdrant(
                message.dataset_id, message.person_input, message.file_id)

        rag_prompt = rag_prompt_template.replace("{relevant_knowledge}", relevant_chunk_content_str).replace(
            "{user_question}", message.person_input)
        rag_llm_output = self.globals.general_llm_adapter.process(rag_prompt)

        return rag_llm_output, output_file_2_chunk_content_dict

    def max_key_by_value_count(self, input_dict: dict):
        max_key = None
        max_count = -1

        for key, value in input_dict.items():
            count = len(value)  # 计算值的计数
            if count > max_count:
                max_count = count
                max_key = key

        return max_key

    def get_relevant_knowledge_by_qdrant(self, dataset_id: str, user_question: str, file_id: str) -> (str, dict):
        user_input_embedding = self.globals.text_embedding.get(user_question)

        if file_id != "":
            relevant_file_list = [file_id]
        else:
            relevant_file_list = self.get_relevant_file_list(user_input_embedding, dataset_id)

        filter_dict = {}
        relevant_chunk_content_str = ""
        output_file_2_chunk_content_dict = {}
        for file_dict in relevant_file_list:
            relevant_chunk_content_str += "[%s]:\n" % file_dict["file_name"]
            filter_dict["file_id"] = file_dict["file_id"]

            search_results = self.globals.qdrant_adapter.search(collection_id=dataset_id + "_chunk",
                                                                input_vector=user_input_embedding,
                                                                score_threshold=0.1, cnt=30, filter_dict=filter_dict)

            chunk_content_list_v1 = []
            for search_result in search_results:
                chunk_content_list_v1.append(search_result.payload["chunk_content"])

            chunk_content_list_v2 = self.globals.text_rerank_adapter.process(user_question,
                                                                             chunk_content_list_v1)

            if len(search_results) == 0:
                return self.polite_refuse, []

            output_chunk_content_list = []

            for chunk_content_and_relevant_score_tuple in chunk_content_list_v2:
                chunk_content = chunk_content_and_relevant_score_tuple[0]
                relevant_score = chunk_content_and_relevant_score_tuple[1]
                if relevant_score < 0.001:
                    break

                output_chunk_content_list.append(chunk_content)
                relevant_chunk_content_str += "\t" + chunk_content + "\n\n"
                if len(output_chunk_content_list) > 10:
                    break

            output_file_2_chunk_content_dict[file_dict["file_name"]] = output_chunk_content_list

        return relevant_chunk_content_str, output_file_2_chunk_content_dict

    def get_relevant_knowledge_by_elasticsearch(self, dataset_id: str, user_question: str) -> (str, dict):
        query = {
            "query": {
                "multi_match": {
                    "query": user_question,
                    "fields": ["chunk_content"],  # 替换为实际的字段名
                    "fuzziness": "AUTO"  # 启用模糊匹配
                }
            }
        }

        ret = self.globals.elasticsearch_adapter.search(dataset_id, query)
        file_name_2_chunk_content_dic = {}
        for hit in ret.get("hits", {}).get("hits", []):
            file_name = hit["_source"]["file_name"]
            chunk_content = hit["_source"]["chunk_content"]
            if file_name in file_name_2_chunk_content_dic:
                file_name_2_chunk_content_dic[file_name].append(chunk_content)
            else:
                file_name_2_chunk_content_dic[file_name] = [chunk_content]

        output_content = ""
        for file_name, chunk_content_list in file_name_2_chunk_content_dic.items():
            output_content += f"[{file_name}]:\n"
            output_content += ''.join(chunk_content_list)
            output_content += f"\n\n"
            pass

        logger.debug("get_content_by_elasticsearch")
        return output_content, file_name_2_chunk_content_dic

from loguru import logger

from magic_bi.utils.globals import Globals, GLOBALS, GLOBAL_CONFIG


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


from magic_bi.work.base_work import BaseWork
from magic_bi.work.work import WorkInput, WorkOutput

class SummarizeContextWork(BaseWork):
    def __init__(self):
        self.polite_refuse = "对不起，知识库中没有检索到相关知识，请换个其它问题。"
        super().__init__()


    def execute(self, work_input: WorkInput) -> WorkOutput:
        prompt = rag_prompt_template.replace("{relevant_knowledge}", work_input.previous_work_output).replace("{relevant_knowledge}", work_input.previous_work_output)

        try:
            llm_output = GLOBALS.general_llm_adapter.process(prompt)
            work_output: WorkOutput = WorkOutput()
            work_output.data = llm_output

            logger.debug("SummarizeContextWork executed successfully")
            return work_output
        except Exception as e:
            logger.error("catch exception: %s")
            return None

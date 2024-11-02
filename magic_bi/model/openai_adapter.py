from magic_bi.config.model_config import ModelConfig
from loguru import logger
# from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI
from magic_bi.model.base_llm_adapter import BaseLlmAdapter


class OpenaiAdapter(BaseLlmAdapter):
    def __init__(self):
        self.client = None
        self.model_config: ModelConfig = None

    def init(self, model_config: ModelConfig) -> int:
        self.model_config = model_config
        self.client = OpenAI(
            api_key=model_config.api_key,
            base_url=model_config.base_url,
        )

        logger.debug("OpenaiAdapter init suc")
        return 0

    def process(self, user_input: str, image_base64: str = "", temperature = 0) -> str:
        try:
            if image_base64 == "":
                messages = [
                    {
                        "role": "system",
                        "content": self.model_config.system_prompt  # 你可以自定义系统消息
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            else:
                messages=[
                            {
                                "role": "system",
                                "content": self.model_config.system_prompt  # 你可以自定义系统消息
                            },
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": user_input},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": image_base64},
                                    },
                                ],
                            }
                        ]


            completion = self.client.chat.completions.create(
                model=self.model_config.model,
                messages=messages,
                temperature=temperature,
            )

            response = completion.choices[0].message.content
            logger.debug("process suc, text_content_cnt: %d" % len(response))
            return response
        except Exception as e:
            logger.error("catch exception:%s" % str(e))
            return ""

    def get_model_config(self) -> ModelConfig:
        return self.model_config

"""
[Table daily_reports Data Preview]:
--------------------
id | updated_at | dataid | title | event_time | send_dept_name | associated_ent | swrs | ssrs | miss_person | zhsgjbxx | sgdj | province | city | county | disaster_type | event_type | state
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
2356 | 2024-09-03 15:06:54 | None | 关于华泰龙矿业公司果朗沟尾矿库尾砂外溢情况的报告（续报一） | None | 西藏自治区应急厅 | None | 0 | 0 | 0 | 西藏华泰龙矿业开发有限公司果朗沟尾矿库存在尾砂外溢现象。 | 一般 | 西藏自治区 | 拉萨市 | None | 事故灾难,金属非金属矿山事故 | 事故 | None
487 | 2024-09-03 15:06:54 | None | 保定涿州市辖区河道内发现两具尸体 | 2023-08-11 | 河北省应急厅 | None | 2 | 0 | 0 | 8月8日上午，涿州市在灾后重建过程中在拒马河河边两处地点发现两具尸体，一处位于百尺竿镇葱园村附近，另一处位于旅游大道京港澳高速桥涵附近，并于8月10日晚确认两人身份，分别为。 | 一般 | 河北省 | 保定市 | 涿州市 | 自然灾害,水旱灾害,洪水 | 灾害 | None
1076 | 2024-09-03 15:06:54 | None | 陇南市成县黄渚镇发生一起森林火灾（续报三）无人员伤亡 | 2024-03-30 | 甘肃省应急厅 | None | 0 | 0 | 0 | 2024年3月30日14时30分，陇南市成县黄渚镇王庄村黑潭沟发生一起森林火灾。 | 一般 | 甘肃省 | 陇南市 | 成县 | 自然灾害,森林火灾,境内森林火灾 | 灾害 | None
[Table daily_reports Data Preview End]
"""

if __name__ == "__main__":
    model_config: ModelConfig = ModelConfig()
    model_config.base_url = "http://192.168.68.96:12434/v1/"
    model_config.model = "qwen2.5:72b"
    model_config.api_key = "ollama"
    openai_adapter = OpenaiAdapter()
    openai_adapter.init(model_config)
    prompt = \
"""
[Relevant Business]
    应急、事故、灾害、事件
    
[Table 0]
	Table Name: daily_reports
	Column Name | Column Comment
	id              | 自增主键                
	updated_at      | 数据更新时间              
	dataid          | dataid              
	title           | 发生灾害或事故的信息标题信息      
	event_time      | 灾害或事故的发生的日期，数据格式为：yyyy-MM-dd
	send_dept_name  | 灾害或事故信息上报的部门名称，比如：广东省应急厅、北京市应急局
	associated_ent  | 灾害或事故发生的企业名称        
	swrs            | 灾害或事故引起的死亡人数        
	ssrs            | 灾害或事故引起的受伤人数        
	miss_person     | 灾害或事故引起的失踪人数        
	zhsgjbxx        | 灾害或事故详细描述信息         
	sgdj            | 灾害或事故的等级，只包括“特别重大”、“重大”、“较大”、“一般”四种类型
	province        | 灾害或事故发生的省份地域行政单位，如：广东省、湖南省
	city            | 灾害或事故发生的城市（地市级行政单位），如：长沙市、广州市
	county          | 灾害或事故发生的区县（区县级行政单位），如：海淀区、天河区
	disaster_type   | 灾害或事故的类型，如：天然地震、内涝  
	event_type      | 事故类型分类，有且只有两种确定的类型，一种是灾害，一种是事故
	state           | 事件状态 0=已发布 1=未发布    

[Table daily_reports Data Preview]:
    --------------------
    id | updated_at | dataid | title | event_time | send_dept_name | associated_ent | swrs | ssrs | miss_person | zhsgjbxx | sgdj | province | city | county | disaster_type | event_type | state
    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    2356 | 2024-09-03 15:06:54 | None | 关于华泰龙矿业公司果朗沟尾矿库尾砂外溢情况的报告（续报一） | None | 西藏自治区应急厅 | None | 0 | 0 | 0 | 西藏华泰龙矿业开发有限公司果朗沟尾矿库存在尾砂外溢现象。 | 一般 | 西藏自治区 | 拉萨市 | None | 事故灾难,金属非金属矿山事故 | 事故 | None
    487 | 2024-09-03 15:06:54 | None | 保定涿州市辖区河道内发现两具尸体 | 2023-08-11 | 河北省应急厅 | None | 2 | 0 | 0 | 8月8日上午，涿州市在灾后重建过程中在拒马河河边两处地点发现两具尸体，一处位于百尺竿镇葱园村附近，另一处位于旅游大道京港澳高速桥涵附近，并于8月10日晚确认两人身份，分别为。 | 一般 | 河北省 | 保定市 | 涿州市 | 自然灾害,水旱灾害,洪水 | 灾害 | None
    1076 | 2024-09-03 15:06:54 | None | 陇南市成县黄渚镇发生一起森林火灾（续报三）无人员伤亡 | 2024-03-30 | 甘肃省应急厅 | None | 0 | 0 | 0 | 2024年3月30日14时30分，陇南市成县黄渚镇王庄村黑潭沟发生一起森林火灾。 | 一般 | 甘肃省 | 陇南市 | 成县 | 自然灾害,森林火灾,境内森林火灾 | 灾害 | None

First analyze the given conditions, then solve the problem step by step.

Generate 5 questions which you think the above database can answer and the relevant tables.

The question and table name must meet the following conditions:
    1, The question should have business significance, the above Relevant Business can be referenced but is not limited.
    2, The question can be answered by a single table, or it can be addressed by a combination of two or three tables.
    3, The questions should be as diverse as possible to cover different fields.
    4, The table must be mentioned in the tables above, do not create yourself!
    5, The questions and reasons are in Chinese.

Output in the following format [{"question": "$question", "table": ["$table_name"...], "reason": "$reason"}...] without other explanations.
"""
    llm_output = openai_adapter.process(prompt)
    print(llm_output)
    pass
    # with open("./test.jpg", "rb") as f:
    #     image_bytes = f.read()
    #     ret = openai_adapter.process(user_input="describe the image detailly", image_bytes=image_bytes)

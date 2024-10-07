from magic_bi.config.base_config import BaseConfig


class AgentConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        # self.max_loop_count: int = 0
        # self.output_intermediate_steps: bool = True
        # self.user_confirm_and_adjust: bool = False
        # self.memory_size: int = 0
        self.memmory_enabled: bool = False
        self.llm_type: str = "public"
        self.try_decompose_user_question: bool = False
        pass
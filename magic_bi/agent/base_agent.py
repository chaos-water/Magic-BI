from typing import Any
from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.agent.memmory import Memmory
from magic_bi.config.agent_config import AgentConfig

class BaseAgent():
    def __init__(self):
        self.agent_meta: AgentMeta = None
        self.globals: Globals = None
        self.io: BaseIo = None
        self.memmory: Memmory = Memmory()
        self.agent_config: AgentConfig = None
        self.language_name: str = ""

    def init(self, agent_meta: AgentMeta, agent_config: AgentConfig, globals: Globals, io: BaseIo, language_name: str) -> int:
        self.agent_config = agent_config
        self.agent_meta: AgentMeta = agent_meta

        self.globals: Globals = globals
        self.io: BaseIo = io
        self.language_name: str = language_name

        self.memmory.init(globals=globals, agent_id=agent_meta.id, memmory_enabled=agent_config.memmory_enabled)
        return 0

    # def init(self):
    #     raise NotImplementedError("Should be implemented")

    def run(self):
        raise NotImplementedError("Should be implemented")

    def process(self, person_input: str) -> Any:
        raise NotImplementedError("Should be implemented")

    def output_intermediate_steps(self, output: str):
        if self.agent_config.output_intermediate_steps:
            self.io.output(output)

# if __name__ == "__main__":
#     AGENT_TYPE.to_list()

from magic_bi.utils.globals import Globals
from magic_bi.io.base_io import BaseIo
from magic_bi.agent.agent_meta import AgentMeta
from magic_bi.config.system_config import SystemConfig

class BaseAgent():
    def __init__(self):
        self.agent_meta: AgentMeta = None
        self.globals: Globals = None
        self.io: BaseIo = None
        self.language_name: str = ""

    def init(self, agent_meta: AgentMeta, globals: Globals, io: BaseIo, system_config: SystemConfig) -> int:
        self.agent_meta: AgentMeta = agent_meta

        self.globals: Globals = globals
        self.io: BaseIo = io
        self.system_config: SystemConfig = system_config
        return 0

    def run(self):
        raise NotImplementedError("Should be implemented")

    def process(self, person_input: str) -> any:
        raise NotImplementedError("Should be implemented")

    def output_intermediate_steps(self, output: str):
        if self.agent_config.output_intermediate_steps:
            self.io.output(output)

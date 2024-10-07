# from pydantic import BaseModel

# class BaseConfig(BaseModel):
class BaseConfig():
    def __init__(self):
        self.loaded: bool = False

    def parse(self, web_config_dict: dict):
        if len(web_config_dict) == 0:
            return

        for key, value in web_config_dict.items():
            if key in self.__dict__ and value is not None:
                self.__dict__[key] = value

        self.loaded = True

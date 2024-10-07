from typing import Dict, Any
import yaml

def get_yaml_content(config_file_path: str) -> Dict[str, Any]:
    try:
        with open(config_file_path, 'r') as f:
            file_content = f.read()
            yaml_config_content = yaml.load(file_content, yaml.Loader)
            return yaml_config_content
    except Exception as e:
        return {}
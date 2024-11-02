from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import update
import os
import paramiko
import subprocess

from magic_bi.train.entity.domain_model import DomainModel
from magic_bi.utils.globals import GLOBALS, GLOBAL_CONFIG
from magic_bi.train.entity.domain_model import DOMAIN_MODEL_STATE


ollama_modelfile_template = \
'''FROM {model_file_path}

# set the temperature to 1 [higher is more creative, lower is more coherent]
PARAMETER temperature 0.7
PARAMETER top_p 0.8

PARAMETER repeat_penalty 1.05
PARAMETER top_k 20

TEMPLATE """{{ if .Messages }}
{{- if or .System .Tools }}<|im_start|>system
{{ .System }}
{{- if .Tools }}

# Tools

You are provided with function signatures within <tools></tools> XML tags:
<tools>{{- range .Tools }}
{"type": "function", "function": {{ .Function }}}{{- end }}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>
{{- end }}<|im_end|>
{{ end }}
{{- range $i, $_ := .Messages }}
{{- $last := eq (len (slice $.Messages $i)) 1 -}}
{{- if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{ else if eq .Role "assistant" }}<|im_start|>assistant
{{ if .Content }}{{ .Content }}
{{- else if .ToolCalls }}<tool_call>
{{ range .ToolCalls }}{"name": "{{ .Function.Name }}", "arguments": {{ .Function.Arguments }}}
{{ end }}</tool_call>
{{- end }}{{ if not $last }}<|im_end|>
{{ end }}
{{- else if eq .Role "tool" }}<|im_start|>user
<tool_response>
{{ .Content }}
</tool_response><|im_end|>
{{ end }}
{{- if and (ne .Role "assistant") $last }}<|im_start|>assistant
{{ end }}
{{- end }}
{{- else }}
{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ end }}{{ .Response }}{{ if .Response }}<|im_end|>{{ end }}"""

# set the system message
SYSTEM """You are {model_name}, created by {model_creator}. You are a helpful assistant."""
'''


class ModelDeployer():
    def execute(self, model_server_host_ip: str, model_deploy_ip: str, domain_model_id: str, username: str, password: str,
                deploy_model_name: str="", force: bool=False) -> int:

        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            stmt = update(DomainModel).where(DomainModel.id == domain_model_id).values(
                state=DOMAIN_MODEL_STATE.DEPLOYING.value)
            session.execute(stmt)
            session.commit()

        version_postfix = ""
        current_host = subprocess.getoutput("hostname -I | awk '{print $1}'").strip()
        model_root_path = os.path.join(GLOBAL_CONFIG.system_config.root_dir, "models")
        model_name = f" {version_postfix}"
        model_download_url = f"http://{model_server_host_ip}:50000/{GLOBAL_CONFIG.system_config.url_prefix}/train/model/export?id={domain_model_id}"

        model_file_name = model_name + ".gguf"

        ollama_modelfile = ollama_modelfile_template.replace("{model_file_path}", model_file_name) \
            .replace("{model_identity}", GLOBAL_CONFIG.system_config.model_identity) \
            .replace("{model_creator}", GLOBAL_CONFIG.system_config.model_creator)

        command = f"""
        MODEL_LIST=$(ollama list)
        if echo "$MODEL_LIST" | grep -q {model_name}; then
          echo "模型 '$MODEL_NAME' 已存在，脚本退出。"
          exit 0
        fi

        if [ ! -d "{model_root_path}" ]; then
          mkdir -p "{model_root_path}"
        fi

        cd {model_root_path} || exit

        log=$(wget --content-disposition "{model_download_url}" 2>&1)

        # 从日志中提取下载的文件名
        filename=$(echo "$log" | grep 'Saving to:' | awk -F"‘|’" '{{print $2}}')

        rm -rf Modelfile
        echo {ollama_modelfile} > Modelfile
        ollama create {model_name} -f Modelfile
        """

        logger.debug("command:%s" % command)
        if current_host != model_deploy_ip:
            logger.debug("ssh in")

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(model_deploy_ip, username=username, password=password)

            stdin, stdout, stderr = ssh.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()  # 等待命令完成
            logger.debug(f"exit_status:{exit_status}, command:{command}, stdout:{stdout}, stderr:{stderr}")

            ssh.close()

        else:
            logger.debug("locale in")
            logger.debug(f"command:{command}")
            os.system(command)

        with Session(GLOBALS.sql_orm.engine, expire_on_commit=False) as session:
            stmt = update(DomainModel).where(DomainModel.id == domain_model_id).values(
                state=DOMAIN_MODEL_STATE.DEPLOYED.value)
            session.execute(stmt)
            session.commit()

        logger.debug("execute_deploy_model suc")
        return 0

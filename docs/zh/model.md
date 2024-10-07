# 小模型
智能体中，推荐采用本地部署的方式，相关模型的下载可以通过执行./script/download_models.sh来完成，如果用户有模型API的需要，可以自行替换，或在社区中提出需求。
## 向量模型
向量模型用于对文本进行向量化，在文本问答功能中，召回与用户问题相关的文本。目前Magic-BI采用的是本地向量模型，模型下载方式如下。用户要采用向量模型云服务，也可自行修改，或向社区提出需求。
## 重排模型
重排模型用于在文本问答功能中，对向量模型召回的文本片段进行重排序。
# 大模型
不论是通用语言大模型还是微调大模型，上下文都要求128K及以上，通常选用128K的就可以。
## 通用大语言模型
通用大语言模型，为整Magic-BI提供智力，通常采用70B以上的开源模型或大模型云服务，用户可以根据自己的情况选择70B以上的开源大模型或大模型云服务。
### 本地大语言模型
当采用开源模型时，目前采用qwen2.5:72B。模型可以通过执行./script/download_models.sh来完成部署。该脚本会从huggingface上下载模型，如果遇到网络阻断，
可以执行执行 export HF_ENDPOINT=https://hf-mirror.com 后再执行./script/download_models.sh脚本。
### 大模型云服务
目前Magic-BI采用openai api的方式，接入所有大模型（包括通用大语言模型、微调大语言模型和多模态大模型）。几乎所有主流的大模型云服务，都提供openai api兼容的服务。
用户可以根据自己的实际情况选择，比如openai、claude、kimi或qwen等。
用户只需自行在大模型云服务厂商申请获得key后，在配置文件magic_bi.yml配置url和key即可。
## 微调大语言模型
微调大语言模型，目前主要用在数据库问答功能中，该模型主要通过训练领域数据生成。模型的微调方式，请参考finetuned_llm。
微调模型通过执行如下命令部署：
```
nohup python -m vllm.entrypoints.openai.api_server --model $finetuned_model_path  --api-key ollama --host $host_ip --port $port --tensor-parallel-size 1 --max_model_len 40192 > nohup.txt &
```
其中的$finetuned_model_path、$host_ip和$port根据实际情况进行修改。
# 组件
Magic-BI运行，也依赖其它组件，比如数据库、对象存储和文本搜索等等。可以通过执行
```
docker compose -f deployment/docker-compsoe-components.yml up -d
curl -fsSL https://ollama.com/install.sh | sh
```
下载和启动组件。

组件解释
## ollama
ollama用于部署本地大模型，包括通用大语言模型、多模态大语言模型和微调领域模型。
## postgre
Magic-BI采用postgre作为SQL数据库，存储必要的配置信息。
## minio
Magic-BI采用minio作为对象存储，存储用户上传的文件。用户也可以采用其它对象存储或对象存储服务API，需自行修改代码或在社区中提出需求。
## timescale
Magic-BI采用timescale作为时序数据库，存储用户对话记录。
## qdrant
Magic-BI采用qdrant作为向量数据库，存储文本和图像向量及向量召回。
## elasticsearch
Magic-BI采用elasticsearch存储文本片段，实现关键词召回文本片段。

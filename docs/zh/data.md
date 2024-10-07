# 小模型
智能体中，推荐采用本地部署的方式，如果用户有模型API的需要，可以自行替换，或在社区中提出需求。
## 向量模型

```
huggingface-cli download --resume-download sentence-transformers/paraphrase-multilingual-mpnet-base-v2 --local-dir ./models/paraphrase-multilingual-mpnet-base-v2
```
## 重排模型
```
huggingface-cli download --resume-download BAAI/bge-reranker-v2-m3 --local-dir ./models/bge-reranker-v2-m3
```

# 大模型
## 大语言模型


huggingface-cli download --resume-download sentence-transformers/paraphrase-multilingual-mpnet-base-v2 --local-dir ./models/paraphrase-multilingual-mpnet-base-v2
huggingface-cli download --resume-download BAAI/bge-reranker-v2-m3 --local-dir ./models/bge-reranker-v2-m3
ollama pull qwen2.5:72b
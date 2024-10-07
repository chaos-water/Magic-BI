FROM ubuntu:22.04

SHELL ["/bin/bash", "-c"]

RUN apt update -y
RUN apt install -y gcc libpq-dev python3-pip
RUN #apt install -y gcc libpq-dev python3-pip python3-venv

ADD magic_bi ./magic_bi
#ADD pyproject.toml ./
#ADD poetry.lock ./
ADD README.md ./
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

#RUN python3 -m venv magic_bi
RUN pip install "uvicorn>=0.31.0"
RUN pip install "loguru>=0.7.2"
RUN pip install "fastapi>=0.115.0"
RUN pip install "pillow>=10.4.0"
RUN pip install "numpy>=2.1.1"
RUN pip install "openai>=1.51.0"
RUN pip install "sqlalchemy>=2.0.35"
RUN pip install "SQLAlchemy-Utils>=0.41.2"
RUN pip install "minio>=7.2.9"
RUN pip install "sentence-transformers>=3.1.1"
RUN pip install "qdrant-client>=1.11.3"
RUN pip install "flagembedding>=1.2.11"
RUN pip install "peft>=0.13.0"
RUN pip install "elasticsearch>=8.15.1"
RUN pip install "pika>=1.3.2"
RUN pip install "python-docx>=1.1.2"
RUN pip install "fitz>=0.0.1.dev"
RUN pip install "pymupdf>=1.24.10"
RUN pip install "pytesseract>=0.3.13"
RUN pip install "psycopg2>=2.9.9"
RUN pip install "python-multipart>=0.0.12"

WORKDIR ./

CMD python3 -m magic_bi.main

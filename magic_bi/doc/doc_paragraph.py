from loguru import logger


from magic_bi.model import openai_adapter
# from sentence_transformers import SentenceTransformer, util

from magic_bi.model.text_embedding import TextEmbedding
from magic_bi.model.openai_adapter import OpenaiAdapter
from magic_bi.doc.text_splitter import split_by_embedding, split_by_llm

class DocParagraph():
    def __init__(self, text_embedding: TextEmbedding = None, openai_adapter: OpenaiAdapter = None, max_chunk_size: int = 512):
        self.title: str = ""
        self.content: str = ""
        self.splitted_content: list[str] = []
        self.sub_paragraphs: list[DocParagraph] = []

        self.text_embedding: TextEmbedding = text_embedding
        self.openai_adapter: OpenaiAdapter = openai_adapter
        self.max_chunk_size: int = max_chunk_size

    def to_json(self):
        sub_paragraphs = []
        for sub_paragraph in self.sub_paragraphs:
            if isinstance(sub_paragraph, dict):
                sub_paragraphs.append(sub_paragraph)
            elif isinstance(sub_paragraph, DocParagraph):
                sub_paragraphs.append(sub_paragraph.to_json())
            else:
                logger.error("unsupported sub_paragraph type:%s" % type(sub_paragraph))

        return {
            "title": self.title,
            "content": self.content,
            "splitted_content": self.splitted_content,
            "sub_paragraphs": sub_paragraphs
        }

    def try_split_content_v2(self) -> int:
        if self.text_embedding is not None and len(self.content) > self.max_chunk_size:
            self.splitted_content = split_by_llm(self.content, self.openai_adapter)
            if self.splitted_content == []:
                self.splitted_content = split_by_embedding(self.content, self.text_embedding)

        return 0


    # def execute_split_content(self, input_content: str, depth_cnt: int=0) -> list:
    #     chunk_list = []
    #     if len(input_content) < self.max_chunk_size or depth_cnt == 0:
    #         # if len(input_content) < self.max_chunk_size or similarity_threshold >= 0.9:
    #         logger.debug("execute_split_content suc, input_content can not be splitted again")
    #         return [input_content]
    #
    #     chunk_content_list = split_by_embedding(input_content, self.text_embedding)
    #     for chunk_content in chunk_content_list:
    #         if len(chunk_content) > self.max_chunk_size:
    #             # similarity_threshold += 0.05
    #             chunk_list.extend(self.execute_split_content(chunk_content, similarity_threshold))
    #         else:
    #             chunk_list.append(chunk_content)
    #
    #     logger.debug("execute_split_content suc, chunk_list cnt:%d, similarity_threshold:%f" % (len(chunk_list), similarity_threshold))
    #     return chunk_list

    def execute_split_content(self, input_content: str, depth_cnt: int=0) -> list:
        depth_cnt += 1
        chunk_list = []
        if len(input_content) < self.max_chunk_size or depth_cnt > 10:
            # if len(input_content) < self.max_chunk_size or similarity_threshold >= 0.9:
            logger.debug("execute_split_content suc, input_content can not be splitted again")
            return [input_content]

        chunk_content_list = split_by_embedding(input_content, self.text_embedding)
        # logger.debug("execute_split_content suc, chunk_list cnt:%d, depth_cnt:%d" % (len(chunk_list), depth_cnt))
        # return chunk_content_list
        for chunk_content in chunk_content_list:
            if len(chunk_content) > self.max_chunk_size:
                chunk_list.extend(self.execute_split_content(chunk_content, depth_cnt))
            else:
                chunk_list.append(chunk_content)

        logger.debug("execute_split_content suc, chunk_list cnt:%d, depth_cnt:%d" % (len(chunk_list), depth_cnt))
        return chunk_list

    def try_split_content(self) -> int:
        import re
        self.content = re.sub(r'\n+', '\n', self.content)
        self.splitted_content = self.execute_split_content(self.content, 0)

        return 0

def trans_doc_paragraph_list_to_content_list(doc_paragraph_list: list[DocParagraph]) -> list[str]:
    content_list = []
    for doc_paragraph in doc_paragraph_list:
        if len(doc_paragraph.splitted_content) > 0:
            content_list.extend(doc_paragraph.splitted_content)
        elif len(doc_paragraph.content.strip()) > 0:
            content_list.append(doc_paragraph.content)

        if len(doc_paragraph.sub_paragraphs) > 0:
            content_list.extend(trans_doc_paragraph_list_to_content_list(doc_paragraph.sub_paragraphs))

    logger.debug("trans_doc_paragraph_list_to_content_list suc, content_list_cnt:%d" % len(content_list))
    return content_list

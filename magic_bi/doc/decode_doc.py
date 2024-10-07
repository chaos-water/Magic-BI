from loguru import logger
from typing import List
from magic_bi.model.text_embedding import TextEmbedding
from magic_bi.model.openai_adapter import OpenaiAdapter
from magic_bi.doc.decode_docx import decode_docx
from magic_bi.doc.decode_pdf import decode_pdf
from magic_bi.doc.decode_txt import decode_txt
from magic_bi.doc.doc_paragraph import trans_doc_paragraph_list_to_content_list


def decode_doc(file_name: str, file_data: [bytes, str], max_chunk_size: int=512, text_embedding: TextEmbedding=None,
               openai_adapter: OpenaiAdapter=None) ->(List, str):
    if file_name.endswith('.docx'):
        doc_paragraph_list, full_content = decode_docx(file_data, max_chunk_size, text_embedding, openai_adapter)
    elif file_name.endswith('.pdf'):
        doc_paragraph_list, full_content = decode_pdf(file_data, max_chunk_size, text_embedding, openai_adapter)
    elif file_name.endswith('.txt'):
        doc_paragraph_list, full_content = decode_txt(file_data, max_chunk_size, text_embedding, openai_adapter)
    else:
        doc_paragraph_list: List = []
        full_content = ""

    output_list = trans_doc_paragraph_list_to_content_list(doc_paragraph_list)

    logger.debug("decode_doc suc")
    return output_list, full_content
    



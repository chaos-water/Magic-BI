
from magic_bi.model.text_embedding import TextEmbedding
from magic_bi.model.openai_adapter import OpenaiAdapter
from magic_bi.doc.doc_paragraph import DocParagraph

def decode_txt(file_name: str, file_data: [bytes, str], max_chunk_size: int=512, text_embedding: TextEmbedding=None, \
               openai_adapter: OpenaiAdapter=None) -> list:
    doc_paragraph: DocParagraph = DocParagraph(text_embedding=text_embedding, openai_adapter=openai_adapter)
    doc_paragraph.content = file_data
    doc_paragraph.try_split_content()

    return [doc_paragraph]

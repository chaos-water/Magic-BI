import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

import os
from magic_bi.doc.doc_paragraph import DocParagraph
from magic_bi.model.text_embedding import TextEmbedding
from magic_bi.model.openai_adapter import OpenaiAdapter

def decode_pdf(pdf_bytes: bytes, max_chunk_size: int, text_embedding: TextEmbedding, openai_adapter: OpenaiAdapter) -> list:
    doc_paragraph = DocParagraph(text_embedding=text_embedding, openai_adapter=openai_adapter, max_chunk_size=max_chunk_size)
    # 打开 PDF 文件

    try:
        pdf_stream = io.BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        # doc = fitz.open(pdf_path)
        # text = ""

        import uuid
        temp_dir = './%s' % (uuid.uuid1().hex)
        os.makedirs(temp_dir, exist_ok=True)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # 1. 尝试提取文本
            page_text = page.get_text()
            if page_text.strip():
                # text += f"\n--- Page {page_num + 1} ---\n"

                doc_paragraph.content += page_text

                # 查找页面中的所有图片
                img_list = page.get_images(full=True)

                for img_index, img in enumerate(img_list):
                    xref = img[0]  # 图像引用 ID
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]  # 获取图像的字节流

                    # 将字节流转换为 PIL 图像
                    img = Image.open(io.BytesIO(image_bytes))

                    # 保存图片到临时目录
                    file_name = os.path.join(temp_dir, f"page_{page_num + 1}_img_{img_index + 1}.jpg")
                    img.save(file_name)

                    # 使用 pytesseract 提取图像中的文本
                    ocr_text = pytesseract.image_to_string(img)
                    if ocr_text.strip():
                        # text += f"\n--- OCR Image {page_num + 1}_{img_index + 1} ---\n"
                        doc_paragraph.content += ocr_text

        doc_paragraph.try_split_content()
        return [[doc_paragraph], doc_paragraph.content]
    finally:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# # 使用示例
# pdf_file_path = "./H3C iNode智能客户端安装指导(macOS)-7.3-5PW102-整本手册.pdf"
# extracted_text = decode_pdf(pdf_file_path)
# print(extracted_text)

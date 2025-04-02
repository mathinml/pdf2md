import os
from converters import PDFToImageConverter, ImageToMarkdownConverter

"""
整合 PDF 转图像和图像转 Markdown 的主处理器，支持断点续传
"""
class PDFMarkdownProcessor:
    
    def __init__(self, pdf_converter=None, image_converter=None, md_output_dir="markdown_output"):
        self.pdf_converter = pdf_converter or PDFToImageConverter()
        self.image_converter = image_converter or ImageToMarkdownConverter()
        self.md_output_dir = md_output_dir
        if not os.path.exists(self.md_output_dir):
            os.makedirs(self.md_output_dir)
    
    def process(self, pdf_path, output_md_path="output.md"):
        image_paths = self.pdf_converter.convert(pdf_path)
        markdown_texts = []
        
        for i, image_path in enumerate(image_paths):
            page_num = i + 1
            md_file = os.path.join(self.md_output_dir, f"page_{page_num}.md")
            markdown_text = self.image_converter.convert(image_path, md_file)
            
            # 检查内容是否有效
            if markdown_text.startswith("Conversion failed"):
                print(f"Warning: Page {page_num} failed to convert.")
                markdown_texts.append(f"## Page {page_num}\n{markdown_text}\n")
            else:
                markdown_texts.append(f"## Page {page_num}\n{markdown_text}\n")
        
        # 合并所有 Markdown 到最终文件
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_texts))
        print(f"Combined Markdown saved to: {output_md_path}")
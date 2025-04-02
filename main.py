import os
import torch
from converters import PDFToImageConverter, ImageToMarkdownConverter
from processor import PDFMarkdownProcessor
from cli import parse_args


"""
确保 vLLM 配置目录可写，兼容 Linux 和 macOS
"""
def ensure_config_dir():

    config_dir = os.path.expanduser("~/.config/vllm")
    try:
        os.makedirs(config_dir, exist_ok=True)
    except PermissionError:
        alt_dir = os.path.expanduser("~/vllm_config")
        os.makedirs(alt_dir, exist_ok=True)
        os.environ["XDG_CONFIG_HOME"] = alt_dir
        print(f"Using {alt_dir} as config directory.")


def main():
    ensure_config_dir()
    args = parse_args()
    
    # 根据设备调整参数
    cuda_available = torch.cuda.is_available()
    pdf_converter = PDFToImageConverter(dpi=args.dpi)
    # 使用本地模型路径
    image_converter = ImageToMarkdownConverter(
        model_path=args.model,  # 传入本地路径
        max_model_len=8192 if cuda_available else 4096,
        dtype="half" if cuda_available else "float16"
    )
    processor = PDFMarkdownProcessor(pdf_converter, image_converter)
    
    processor.process(args.pdf, args.output)

if __name__ == "__main__":
    main()    
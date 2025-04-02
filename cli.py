import argparse

"""
解析命令行参数
"""
def parse_args():

    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using Qwen2.5-VL-3B-Instruct")
    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.md",
        help="Path to the output Markdown file (default: output.md)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="DPI for PDF to image conversion (default: 200)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-VL-3B-Instruct",
        help="Model name or path (default: Qwen/Qwen2.5-VL-3B-Instruct)"
    )
    return parser.parse_args()
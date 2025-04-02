# 文件结构

project/
├── converters.py      # 包含 PDFToImageConverter 和 ImageToMarkdownConverter 类
├── processor.py       # 包含 PDFMarkdownProcessor 类
├── cli.py             # 包含命令行解析函数 parse_args
├── main.py            # 主程序，整合所有模块
└── requirements.txt   # 依赖列表（可选）

# 安装步骤

pdf2image 库依赖下面这个，因此先安装一下。

```python
sudo apt-get update
sudo apt-get install poppler-utils
```

# 模型下载

```python
pip install modelscope
modelscope download --model Qwen/Qwen2.5-VL-3B-Instruct --local_dir ../local_models/Qwen2.5-VL-3B-Instruct
```

# 使用方法

python main.py --pdf ./test_ocr.pdf --model ../local_models/Qwen2.5-VL-3B-Instruct --output output.md
import os
import shutil
import torch
from pdf2image import convert_from_path
from transformers import AutoProcessor
from vllm import LLM, SamplingParams
from qwen_vl_utils import process_vision_info

"""
将 PDF 文件转换为低分辨率 JPEG 图像的类
"""
class PDFToImageConverter:
    
    def __init__(self, output_dir="png_output", dpi=200, fmt="jpeg", size=(1024, None)):
        self.output_dir = output_dir
        self.dpi = dpi
        self.fmt = fmt.upper()
        self.size = size
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def convert(self, pdf_path):
        print(f"Converting {pdf_path} to {self.fmt}...")
        image_paths = convert_from_path(
            pdf_path,
            dpi=self.dpi,
            fmt=self.fmt,
            output_folder=self.output_dir,
            size=self.size,
            paths_only=True
        )
        if not image_paths:
            raise ValueError("No images generated.")
        for path in image_paths:
            print(f"Saved: {path}")
        return image_paths
    
    def set_dpi(self, dpi):
        self.dpi = dpi
        print(f"DPI set to {dpi}")


"""
使用 Qwen2.5-VL 和 vLLM 将图像转换为 Markdown 的类，支持 GPU 和 CPU
"""        
class ImageToMarkdownConverter:
    
    def __init__(self, model_path="../local_models/Qwen2.5-VL-3B-Instruct", **kwargs):
        self.model_path = model_path
        
        # 动态选择设备
        if torch.cuda.is_available():
            self.device = "cuda"
            print("Using NVIDIA GPU (CUDA)")
        elif torch.backends.mps.is_available():
            self.device = "cpu"
            print("有待 vllm 优化 Apple M3 MPS")
        else:
            self.device = "cpu"
            kwargs["gpu_memory_utilization"] = 0  # 强制使用 CPU
            print("Using CPU")
        
        # 设置默认参数，适配 GPU/CPU
        default_kwargs = {
            "dtype": "auto",  # 让 vLLM 自动选择 dtype
            "max_model_len": 8192 if self.device == "cuda" else 4096,
            "trust_remote_code": True,
            "device": self.device
        }
        default_kwargs.update(kwargs)  # 允许用户覆盖默认值
        
        # 从本地路径加载 vLLM 模型
        print(f"Loading model from local path: {self.model_path}")
        self.llm = LLM(model=self.model_path, quantization=None, **default_kwargs)
        
        # 从本地路径加载处理器
        self.processor = AutoProcessor.from_pretrained(self.model_path)
    
    def convert(self, image_path, output_md_path, prompt=None, sampling_params=None):
        """将图像转换为 Markdown 并保存到指定路径"""
        if os.path.exists(output_md_path):
            print(f"Skipping {image_path}: {output_md_path} already exists.")
            with open(output_md_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content and not content.startswith("Conversion failed"):
                    return content
        
        print(f"Processing {image_path} on {self.device}...")
        image_path = os.path.abspath(image_path)
        
        if sampling_params is None:
            sampling_params = SamplingParams(
                temperature=0.1,
                min_p=0.1,
                max_tokens=8192,
                stop_token_ids=[]
            )
        if prompt is None:
            prompt = "Convert the provided image of a PDF document strictly into valid Markdown. If there are mathematical formulas in the document, use Mathjax."
        
        message = [
            {"role": "system", "content": "You are a tool to parse documents."},
            {"role": "user", "content": [{"type": "image", "image": f"file://{image_path}"}, {"type": "text", "text": prompt}]},
        ]
        
        prompt_text = self.processor.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
        image_input, _ = process_vision_info(message)
        
        mm_data = {}
        if image_input is not None:
            if isinstance(image_input, list):
                image_input = image_input[0]
            mm_data["image"] = image_input
        else:
            raise ValueError(f"Failed to process image from {image_path}")
        
        llm_inputs = {"prompt": prompt_text, "multi_modal_data": mm_data}
        print(f"LLM Inputs: {llm_inputs}")
        
        try:
            outputs = self.llm.generate([llm_inputs], sampling_params=sampling_params)
            markdown_text = outputs[0].outputs[0].text.strip()
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            markdown_text = "Conversion failed due to processing error."
        
        if not markdown_text or markdown_text == "```markdown" or markdown_text.isspace():
            markdown_text = "Conversion failed: No valid content generated."
        
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"Saved Markdown to: {output_md_path}")
        
        return markdown_text
"""
OCR 引擎模块（正确版本）
使用 trust_remote_code=True 加载自定义模型
支持 local_files_only 参数强制使用本地模型
"""
import torch
from pathlib import Path
from typing import Union, List, Dict, Optional
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText


class OCREngine:
    """OCR 引擎类"""

    def __init__(self, model_path: str = "zai-org/GLM-OCR", device: str = "auto", use_local_only: bool = False):
        """
        初始化 OCR 引擎

        Args:
            model_path: 模型路径或 HuggingFace 模型名称
            device: 设备 (auto, cpu, cuda, cuda:0, etc.)
            use_local_only: 是否仅使用本地模型，不连接 HuggingFace
        """
        self.model_path = model_path
        self.device = device
        self.use_local_only = use_local_only
        self.processor = None
        self.model = None
        self._is_loaded = False

    def load_model(self, progress_callback=None) -> bool:
        """
        加载模型

        Args:
            progress_callback: 进度回调函数 callback(message: str, progress: float)

        Returns:
            是否加载成功
        """
        try:
            if progress_callback:
                progress_callback("正在加载处理器...", 0.1)

            # 根据 use_local_only 设置是否仅使用本地文件
            local_mode_msg = " (仅本地模式)" if self.use_local_only else ""
            print(f"加载模式: {'仅本地' if self.use_local_only else '在线/本地'}{local_mode_msg}")

            # 关键：添加 trust_remote_code=True 和 local_files_only
            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                local_files_only=self.use_local_only  # 强制仅使用本地文件
            )

            if progress_callback:
                progress_callback("正在加载模型...", 0.5)

            # 关键：添加 trust_remote_code=True 和 local_files_only
            self.model = AutoModelForImageTextToText.from_pretrained(
                pretrained_model_name_or_path=self.model_path,
                torch_dtype=torch.float16,
                device_map=self.device,
                trust_remote_code=True,  # 必须添加这个
                local_files_only=self.use_local_only  # 强制仅使用本地文件
            )

            if progress_callback:
                progress_callback("模型加载完成", 1.0)

            self._is_loaded = True
            print(f"✓ 模型加载成功")
            print(f"✓ 设备: {self.model.device}")
            print(f"✓ 模式: {'仅本地' if self.use_local_only else '在线/本地'}")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"加载失败: {str(e)}", 0.0)
            print(f"✗ 模型加载失败: {e}")
            
            if self.use_local_only:
                print(f"\n可能的解决方案:")
                print(f"1. 确认本地模型路径正确: {self.model_path}")
                print(f"2. 检查模型文件是否完整")
                print(f"3. 如需从 HuggingFace 下载，请设置 use_local_only=False")
            else:
                print(f"\n可能的解决方案:")
                print(f"1. 升级 transformers: pip install --upgrade transformers")
                print(f"2. 安装开发版: pip install git+https://github.com/huggingface/transformers.git")
                print(f"3. 检查网络连接")
            return False

    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self._is_loaded

    def recognize_image(
        self,
        image: Union[str, Path, Image.Image],
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 8192
    ) -> Optional[str]:
        """
        识别单张图片

        Args:
            image: 图片路径或 PIL Image 对象
            prompt: 识别提示词
            max_new_tokens: 最大生成 token 数

        Returns:
            识别结果文本，失败返回 None
        """
        if not self._is_loaded:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        try:
            # 处理图片输入
            if isinstance(image, Image.Image):
                # 如果是 PIL Image，保存为临时文件
                import tempfile
                import os

                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, "temp_ocr_image.png")
                image.save(temp_path)
                image_url = temp_path
            else:
                # 如果是路径，直接使用
                image_url = str(image)

            # 按官方文档构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "url": image_url
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ]

            # 处理输入
            inputs = self.processor.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt"
            ).to(self.model.device)

            inputs.pop("token_type_ids", None)

            # 关闭梯度计算，减少显存占用
            with torch.inference_mode():
                generated_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)

            # 解码输出
            input_len = inputs["input_ids"].shape[1]
            output_text = self.processor.decode(
                generated_ids[0][input_len:],
                skip_special_tokens=False
            )

            # 释放中间张量
            del inputs, generated_ids
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # 清理临时文件
            if isinstance(image, Image.Image):
                try:
                    os.remove(temp_path)
                except:
                    pass

            return output_text

        except Exception as e:
            print(f"识别失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def recognize_batch(
        self,
        images: List[Union[str, Path, Image.Image]],
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 8192,
        progress_callback=None
    ) -> List[Dict[str, Union[str, bool]]]:
        """
        批量识别图片

        Args:
            images: 图片路径或对象列表
            prompt: 识别提示词
            max_new_tokens: 最大生成 token 数
            progress_callback: 进度回调 callback(current: int, total: int, result: str)

        Returns:
            识别结果列表 [{"image": path, "text": result, "success": bool}, ...]
        """
        results = []
        total = len(images)

        for i, image in enumerate(images):
            try:
                image_path = str(image) if isinstance(image, (str, Path)) else "clipboard"
                text = self.recognize_image(image, prompt, max_new_tokens)

                results.append({
                    "image": image_path,
                    "text": text if text else "",
                    "success": text is not None
                })

                if progress_callback:
                    progress_callback(i + 1, total, text if text else "识别失败")

            except Exception as e:
                results.append({
                    "image": str(image) if isinstance(image, (str, Path)) else "unknown",
                    "text": f"错误: {str(e)}",
                    "success": False
                })

                if progress_callback:
                    progress_callback(i + 1, total, f"错误: {str(e)}")

        return results

    def unload_model(self):
        """卸载模型释放内存"""
        if self._is_loaded:
            del self.model
            del self.processor
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self._is_loaded = False
            print("✓ 模型已卸载")

    def get_supported_prompts(self) -> Dict[str, str]:
        """获取支持的提示词类型"""
        return {
            "text_recognition": "Text Recognition:",
            "document_parsing": "Document Parsing:",
            "table_recognition": "Table Recognition:",
            "formula_recognition": "Formula Recognition:"
        }

    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        if not self._is_loaded:
            return {"status": "未加载"}

        return {
            "status": "已加载",
            "model_path": self.model_path,
            "device": str(self.model.device),
            "dtype": str(self.model.dtype) if hasattr(self.model, 'dtype') else "unknown",
            "mode": "仅本地" if self.use_local_only else "在线/本地"
        }

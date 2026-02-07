"""
OCR 引擎模块
使用 trust_remote_code=True 加载自定义模型
支持 local_files_only 参数强制使用本地模型
包含内存优化：低内存加载、推理后回收、可选量化
"""
import gc
import torch
from pathlib import Path
from typing import Union, List, Dict, Optional
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText


class OCREngine:
    """OCR 引擎类"""

    # 超过此尺寸的图片会在预处理时等比缩放，避免浪费内存
    MAX_IMAGE_LONG_EDGE = 4096

    def __init__(self, model_path: str = "zai-org/GLM-OCR", device: str = "auto",
                 use_local_only: bool = False, quantization: str = "none"):
        """
        初始化 OCR 引擎

        Args:
            model_path: 模型路径或 HuggingFace 模型名称
            device: 设备 (auto, cpu, cuda, cuda:0, etc.)
            use_local_only: 是否仅使用本地模型，不连接 HuggingFace
            quantization: 量化模式 ("none", "8bit", "4bit")
        """
        self.model_path = model_path
        self.device = device
        self.use_local_only = use_local_only
        self.quantization = quantization
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

            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                local_files_only=self.use_local_only
            )

            if progress_callback:
                progress_callback("正在加载模型...", 0.5)

            # 构建加载参数
            load_kwargs = dict(
                pretrained_model_name_or_path=self.model_path,
                torch_dtype=torch.float16,
                device_map=self.device,
                trust_remote_code=True,
                local_files_only=self.use_local_only,
                # 逐片加载权重，避免峰值内存翻倍（最关键的优化）
                low_cpu_mem_usage=True,
            )

            # 可选量化：进一步降低内存占用
            if self.quantization in ("8bit", "4bit"):
                try:
                    from transformers import BitsAndBytesConfig
                    if self.quantization == "8bit":
                        load_kwargs["quantization_config"] = BitsAndBytesConfig(
                            load_in_8bit=True
                        )
                    elif self.quantization == "4bit":
                        load_kwargs["quantization_config"] = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_quant_type="nf4"
                        )
                    print(f"使用 {self.quantization} 量化加载模型")
                except ImportError:
                    print("bitsandbytes 未安装，跳过量化，使用 float16")

            self.model = AutoModelForImageTextToText.from_pretrained(**load_kwargs)

            # 加载完成后立即回收加载过程中的临时内存
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            if progress_callback:
                progress_callback("模型加载完成", 1.0)

            self._is_loaded = True
            print(f"✓ 模型加载成功")
            print(f"✓ 设备: {self.model.device}")
            print(f"✓ 模式: {'仅本地' if self.use_local_only else '在线/本地'}")
            if self.quantization != "none":
                print(f"✓ 量化: {self.quantization}")
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

    def _prepare_image(self, image: Union[str, Path, Image.Image]) -> str:
        """
        预处理图片：限制超大图片尺寸以节省内存，返回可用的图片路径。

        对于超过 MAX_IMAGE_LONG_EDGE 的图片，等比缩放后保存到临时文件。
        普通尺寸图片直接返回原始路径。
        """
        import tempfile
        import os

        if isinstance(image, Image.Image):
            pil_image = image
        else:
            pil_image = Image.open(str(image))

        w, h = pil_image.size
        needs_temp = isinstance(image, Image.Image)

        # 超大图片等比缩放
        if max(w, h) > self.MAX_IMAGE_LONG_EDGE:
            pil_image.thumbnail(
                (self.MAX_IMAGE_LONG_EDGE, self.MAX_IMAGE_LONG_EDGE),
                Image.LANCZOS
            )
            needs_temp = True

        if needs_temp:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "temp_ocr_image.png")
            # 转为 RGB 避免 PNG 保存 RGBA 浪费空间
            if pil_image.mode not in ("RGB", "L"):
                pil_image = pil_image.convert("RGB")
            pil_image.save(temp_path)
            pil_image.close()
            return temp_path
        else:
            pil_image.close()
            return str(image)

    def recognize_image(
        self,
        image: Union[str, Path, Image.Image],
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 2048
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

        temp_path = None
        try:
            # 预处理图片（限制超大图片尺寸）
            image_url = self._prepare_image(image)
            if isinstance(image, Image.Image):
                import os
                temp_path = image_url  # 记录临时文件以便清理

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
                skip_special_tokens=True
            )

            # 立即释放中间张量
            del inputs, generated_ids

            # 强制回收内存，防止碎片累积
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            return output_text

        except Exception as e:
            print(f"识别失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 清理临时文件
            if temp_path:
                try:
                    import os
                    os.remove(temp_path)
                except OSError:
                    pass

    def recognize_batch(
        self,
        images: List[Union[str, Path, Image.Image]],
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 2048,
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
            self.model = None
            self.processor = None
            self._is_loaded = False

            # 强制回收 Python 对象和 CUDA 显存
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

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
            "mode": "仅本地" if self.use_local_only else "在线/本地",
            "quantization": self.quantization
        }

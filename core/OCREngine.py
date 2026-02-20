"""
OCR 引擎模块
使用 trust_remote_code=True 加载自定义模型
支持 local_files_only 参数强制使用本地模型
包含内存优化：低内存加载、推理后回收、可选量化
"""
import gc
import torch
from pathlib import Path
from typing import Union, List, Dict, Optional, Callable
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText


# 旧版推理模式名称 → 新版迁移表（兼容已保存的旧配置文件）
_MODE_MIGRATION = {
    "accurate_fast": "high_quality",
    "accurate_save": "balanced",
    "fast_save":     "memory_save",
}


def normalize_performance_mode(mode: str) -> str:
    """将旧版推理模式名迁移到当前版本，未知名称原样返回。"""
    return _MODE_MIGRATION.get(mode, mode)


# 三种推理模式对应的 token 上限（max）。下限统一为 512，不再强制最低值。
# 上限由模式决定，防止省显存模式因 token 过高导致 OOM。
PERFORMANCE_MODE_TOKEN_LIMITS = {
    "high_quality": (512, 8192),  # 高质量：无量化，token 上限 8192
    "balanced":     (512, 4096),  # 推荐：8bit 量化，token 上限 4096
    "memory_save":  (512, 2048),  # 省显存：4bit 量化，token 上限 2048
}


def get_token_limits_for_performance_mode(mode: str) -> tuple:
    """
    返回当前推理模式允许的 token 范围 (min_tokens, max_tokens)。
    用于界面滑块范围与有效 token 计算。自动迁移旧版模式名。
    """
    return PERFORMANCE_MODE_TOKEN_LIMITS.get(normalize_performance_mode(mode), (512, 4096))


def get_effective_max_new_tokens(performance_mode: str, user_value: int, global_limit: int) -> int:
    """
    按推理模式上限钳位用户设置的 token 数。
    只限制上限（避免 OOM），不再强制最低值，用户可自由设低。
    """
    min_t, max_t = get_token_limits_for_performance_mode(performance_mode)
    cap = min(max_t, global_limit)
    return max(min_t, min(user_value, cap))


def get_performance_mode_params(mode: str) -> tuple:
    """
    根据性能模式返回 (quantization, max_image_long_edge)。
    未知模式回退到 balanced（8bit, 4096）。

    三种推理模式的具体区别：

    - high_quality（高质量）
      量化: 无量化(none)；显存不足时由 get_smart_performance_params 自动降级
      长边: 4096
      适用: 显存 ≥14GB，长文档/大图，追求最高识别质量

    - balanced（推荐）
      量化: 8bit
      长边: 4096
      适用: 显存 7-14GB，质量与资源占用的最佳平衡

    - memory_save（省显存）
      量化: 4bit
      长边: 2048（大图缩小，识别可能略差）
      适用: 显存 <7GB，优先保证能跑起来
    """
    mode = normalize_performance_mode(mode)
    modes = {
        "high_quality": ("none", 4096),
        "balanced":     ("8bit", 4096),
        "memory_save":  ("4bit", 2048),
    }
    return modes.get(mode, ("8bit", 4096))


def get_recommended_batch_concurrency() -> int:
    """
    根据当前显卡显存推荐批量并发数（供 API 服务端与客户端参考）。
    无 CUDA 或异常时返回 1。8G 显存给 3 以利用富余显存。
    """
    if not torch.cuda.is_available():
        return 1
    try:
        total_bytes = torch.cuda.get_device_properties(0).total_memory
        total_gb = total_bytes / (1024 ** 3)
        if total_gb >= 24:
            return 4
        if total_gb >= 16:
            return 3
        if total_gb >= 12:
            return 3
        if total_gb >= 7.0:
            return 3   # 7G 及以上（含 8G 卡若系统报 7.x）给 3 并发
        return 2
    except Exception:
        return 1


def get_smart_performance_params(mode: str) -> tuple:
    """
    根据性能模式与当前显卡显存返回 (quantization, max_image_long_edge)。
    仅对 high_quality 做智能降级，其余模式直接返回固定参数。
    用于避免 high_quality 在显存不足时 OOM。
    """
    mode = normalize_performance_mode(mode)
    if mode != "high_quality":
        return get_performance_mode_params(mode)
    if not torch.cuda.is_available():
        return "8bit", 4096
    try:
        total_bytes = torch.cuda.get_device_properties(0).total_memory
        total_gb = total_bytes / (1024 ** 3)
        if total_gb >= 24:
            q, edge = "none", 4096
        elif total_gb >= 16:
            q, edge = "8bit", 4096
        elif total_gb >= 12:
            q, edge = "8bit", 4096
        elif total_gb >= 7.0:
            # 7-8GB：降级量化但保留 4096 长边，维持图片质量
            q, edge = "8bit", 4096
        else:
            # 严重不足：量化 + 缩图双管齐下
            q, edge = "8bit", 2048
        print(f"[推理模式] 显存 {total_gb:.1f} GB，high_quality 实际使用: {q} 量化, 长边 {edge}")
        return q, edge
    except Exception:
        return "8bit", 4096


class OCREngine:
    """OCR 引擎类"""

    # 默认超过此尺寸的图片会在预处理时等比缩放（可由 performance_mode 覆盖）
    MAX_IMAGE_LONG_EDGE = 4096

    # dtype 配置值到实际类型的映射
    DTYPE_MAP = {
        "float16": torch.float16,
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
        "auto": "auto",
    }

    def __init__(self, model_path: str = "zai-org/GLM-OCR", device: str = "auto",
                 use_local_only: bool = False, quantization: str = "none",
                 dtype: str = "float16", max_image_long_edge: int = None):
        """
        初始化 OCR 引擎

        Args:
            model_path: 模型路径或 HuggingFace 模型名称
            device: 设备 (auto, cpu, cuda, cuda:0, etc.)
            use_local_only: 是否仅使用本地模型，不连接 HuggingFace
            quantization: 量化模式 ("none", "8bit", "4bit")
            dtype: 模型精度 ("float16", "float32", "bfloat16", "auto")
            max_image_long_edge: 图片长边上限（超过则等比缩放），None 则用类默认 4096
        """
        self.model_path = model_path
        self.device = device
        self.use_local_only = use_local_only
        self.quantization = quantization
        self.dtype = self.DTYPE_MAP.get(dtype, torch.float16)
        self.max_image_long_edge = max_image_long_edge if max_image_long_edge is not None else self.MAX_IMAGE_LONG_EDGE
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
                local_files_only=self.use_local_only,
                use_fast=False
            )

            if progress_callback:
                progress_callback("正在加载模型...", 0.5)

            # 构建加载参数
            load_kwargs = dict(
                pretrained_model_name_or_path=self.model_path,
                dtype=self.dtype,
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

    def _prepare_image(self, image: Union[str, Path, Image.Image]) -> tuple:
        """
        预处理图片：限制超大图片尺寸以节省内存，返回可用的图片路径。

        对于超过 MAX_IMAGE_LONG_EDGE 的图片，等比缩放后保存到临时文件。
        普通尺寸图片直接返回原始路径。

        Returns:
            (image_url, is_temp): 图片路径和是否为临时文件
        """
        import tempfile
        import os

        opened_by_me = False
        if isinstance(image, Image.Image):
            pil_image = image
        else:
            pil_image = Image.open(str(image))
            opened_by_me = True

        try:
            w, h = pil_image.size
            needs_temp = isinstance(image, Image.Image)

            # 超大图片等比缩放
            if max(w, h) > self.max_image_long_edge:
                pil_image.thumbnail(
                    (self.max_image_long_edge, self.max_image_long_edge),
                    Image.LANCZOS
                )
                needs_temp = True

            if needs_temp:
                fd, temp_path = tempfile.mkstemp(suffix=".png", prefix="ocr_")
                os.close(fd)
                # 转为 RGB 避免 PNG 保存 RGBA 浪费空间
                if pil_image.mode not in ("RGB", "L"):
                    pil_image = pil_image.convert("RGB")
                pil_image.save(temp_path)
                if not opened_by_me:
                    # 由调用方传入的 PIL Image，保存后即可关闭
                    pil_image.close()
                return temp_path, True
            else:
                # 非 PIL 输入且无需临时文件，由 finally 负责关闭
                return str(image), False
        finally:
            # 由本函数打开的文件句柄，在任何路径（正常/异常）下都确保关闭
            if opened_by_me:
                try:
                    pil_image.close()
                except Exception:
                    pass

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
            image_url, is_temp = self._prepare_image(image)
            if is_temp:
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
        progress_callback=None,
        stop_check: Optional[Callable[[], bool]] = None,
        wait_if_paused: Optional[Callable[[], None]] = None
    ) -> List[Dict[str, Union[str, bool]]]:
        """
        批量识别图片

        Args:
            images: 图片路径或对象列表
            prompt: 识别提示词
            max_new_tokens: 最大生成 token 数
            progress_callback: 进度回调 (current, total, result_text_or_msg)
            stop_check: 返回 True 时停止
            wait_if_paused: 阻塞直到恢复或停止

        Returns:
            识别结果列表 [{"image": path, "text": result, "success": bool}, ...]
        """
        results = []
        total = len(images)

        for i, image in enumerate(images):
            if stop_check and stop_check():
                break
            if wait_if_paused:
                wait_if_paused()
            if stop_check and stop_check():
                break
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

"""
本地 OCR 服务实现
直接调用本地 OCREngine
"""
from typing import Optional, Dict
from services.base import OCRService
from core.OCREngine import OCREngine


class LocalOCRService(OCRService):
    """本地 OCR 服务（直接使用 OCREngine）"""

    def __init__(self, engine: OCREngine):
        """
        初始化本地服务

        Args:
            engine: OCREngine 实例
        """
        self.engine = engine

    def recognize_image(
        self,
        image,
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 2048
    ) -> Optional[str]:
        """
        识别单张图片

        Args:
            image: 图片（PIL Image、文件路径或 Path 对象）
            prompt: 识别类型提示词
            max_new_tokens: 最大生成 token 数

        Returns:
            识别结果文本，失败返回 None
        """
        if not self.engine or not self.engine.is_loaded():
            return None

        return self.engine.recognize_image(image, prompt, max_new_tokens)

    def is_loaded(self) -> bool:
        """
        检查模型是否已加载

        Returns:
            模型是否可用
        """
        return self.engine is not None and self.engine.is_loaded()

    def get_supported_prompts(self) -> Dict[str, str]:
        """
        获取支持的识别类型

        Returns:
            提示词映射字典
        """
        if self.engine and self.engine.is_loaded():
            return self.engine.get_supported_prompts()
        return {
            "text_recognition": "Text Recognition:",
            "document_parsing": "Document Parsing:",
            "table_recognition": "Table Recognition:",
            "formula_recognition": "Formula Recognition:"
        }

    def recognize_batch(
        self,
        images,
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 2048,
        progress_callback=None
    ):
        """
        批量识别（使用 OCREngine 的批量方法）

        Args:
            images: 图片列表
            prompt: 识别类型提示词
            max_new_tokens: 最大生成 token 数
            progress_callback: 进度回调函数

        Returns:
            识别结果列表
        """
        if not self.engine or not self.engine.is_loaded():
            return []

        return self.engine.recognize_batch(
            images,
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            progress_callback=progress_callback
        )

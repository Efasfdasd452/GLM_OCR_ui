"""
OCR 服务抽象基类
定义统一的 OCR 服务接口
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from PIL import Image


class OCRService(ABC):
    """OCR 服务抽象基类"""

    @abstractmethod
    def recognize_image(
        self,
        image,  # Union[str, Path, Image.Image]
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
        pass

    @abstractmethod
    def is_loaded(self) -> bool:
        """
        检查模型是否已加载

        Returns:
            模型是否可用
        """
        pass

    @abstractmethod
    def get_supported_prompts(self) -> Dict[str, str]:
        """
        获取支持的识别类型

        Returns:
            提示词映射字典
        """
        pass

    def recognize_batch(
        self,
        images: List,  # List[Union[str, Path, Image.Image]]
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 2048,
        progress_callback=None
    ) -> List[Dict]:
        """
        批量识别（默认实现：顺序调用单图识别）

        Args:
            images: 图片列表
            prompt: 识别类型提示词
            max_new_tokens: 最大生成 token 数
            progress_callback: 进度回调函数

        Returns:
            识别结果列表
        """
        results = []
        total = len(images)

        for i, image in enumerate(images, 1):
            try:
                text = self.recognize_image(image, prompt, max_new_tokens)
                result = {
                    "image": str(image),
                    "text": text if text else "",
                    "success": text is not None
                }
            except Exception as e:
                result = {
                    "image": str(image),
                    "text": f"错误: {e}",
                    "success": False
                }

            results.append(result)

            # 进度回调
            if progress_callback:
                progress_callback(i, total, result)

        return results

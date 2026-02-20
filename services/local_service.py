"""
本地 OCR 服务实现
直接调用本地 OCREngine，批量时按显存推荐并发数并发识别并保证结果顺序
"""
from typing import Optional, Dict, List, Callable
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path

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
        images: List,
        prompt: str = "Text Recognition:",
        max_new_tokens: int = 2048,
        progress_callback: Optional[Callable] = None,
        stop_check: Optional[Callable[[], bool]] = None,
        wait_if_paused: Optional[Callable[[], None]] = None
    ) -> List[Dict]:
        """
        批量识别：按显存推荐并发数并发调用引擎，保证结果与 images 顺序一致。
        支持 stop_check 与 wait_if_paused。
        """
        if not self.engine or not self.engine.is_loaded():
            return []

        total = len(images)
        if total == 0:
            return []

        # 单 GPU 单模型实例不支持并发推理，强制串行避免 CUDA 错误/OOM
        concurrency = 1
        results = [None] * total
        next_index = 0
        in_flight = {}
        executor = ThreadPoolExecutor(max_workers=concurrency)

        def recognize_one(img, idx):
            try:
                text = self.engine.recognize_image(img, prompt, max_new_tokens)
                image_path = str(img) if isinstance(img, (str, Path)) else "clipboard"
                return idx, {
                    "image": image_path,
                    "text": text if text else "",
                    "success": text is not None
                }
            except Exception as e:
                image_path = str(img) if isinstance(img, (str, Path)) else "unknown"
                return idx, {
                    "image": image_path,
                    "text": f"错误: {e}",
                    "success": False
                }

        try:
            while next_index < total or in_flight:
                if wait_if_paused:
                    wait_if_paused()
                if stop_check and stop_check():
                    break
                while len(in_flight) < concurrency and next_index < total:
                    if wait_if_paused:
                        wait_if_paused()
                    if stop_check and stop_check():
                        break
                    idx = next_index
                    next_index += 1
                    img = images[idx]
                    future = executor.submit(recognize_one, img, idx)
                    in_flight[future] = idx
                if not in_flight:
                    break
                # 带超时等待，便于定期检查停止/暂停（否则会阻塞到有任务完成才响应）
                done, _ = wait(in_flight.keys(), return_when=FIRST_COMPLETED, timeout=1.0)
                for f in done:
                    in_flight.pop(f)
                    idx, result = f.result()
                    results[idx] = result
                    if progress_callback:
                        completed = sum(1 for r in results if r is not None)
                        progress_callback(completed, total, result)
                if stop_check and stop_check():
                    break
        finally:
            # wait=False：停止时立刻返回，不阻塞等待在途推理完成
            executor.shutdown(wait=False)

        for i in range(total):
            if results[i] is None:
                img = images[i]
                image_path = str(img) if isinstance(img, (str, Path)) else "unknown"
                results[i] = {
                    "image": image_path,
                    "text": "已停止",
                    "success": False
                }
        return results

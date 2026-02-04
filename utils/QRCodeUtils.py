"""
二维码识别工具模块
使用 pyzbar 解码图片中的二维码
"""
from pathlib import Path
from typing import Union, List, Dict
from PIL import Image


class QRCodeUtils:
    """二维码工具类"""

    @staticmethod
    def decode_qrcodes(image: Union[str, Path, Image.Image]) -> List[Dict[str, str]]:
        """
        解码图片中的二维码

        Args:
            image: 图片路径或 PIL Image 对象

        Returns:
            解码结果列表 [{"data": "https://...", "type": "QRCODE"}, ...]
        """
        try:
            from pyzbar import pyzbar
        except ImportError:
            print("请安装 pyzbar: pip install pyzbar")
            return []

        try:
            if isinstance(image, (str, Path)):
                image = Image.open(str(image))

            decoded = pyzbar.decode(image)
            results = []
            for obj in decoded:
                results.append({
                    "data": obj.data.decode("utf-8", errors="replace"),
                    "type": obj.type
                })
            return results
        except Exception as e:
            print(f"二维码解码失败: {e}")
            return []

    @staticmethod
    def format_results(qr_results: List[Dict[str, str]]) -> str:
        """
        格式化二维码解码结果为可读文本

        Args:
            qr_results: decode_qrcodes 返回的结果列表

        Returns:
            格式化后的文本
        """
        if not qr_results:
            return ""

        lines = ["[二维码识别结果]"]
        for i, result in enumerate(qr_results, 1):
            lines.append(f"二维码 {i}: {result['data']}")
        return "\n".join(lines)

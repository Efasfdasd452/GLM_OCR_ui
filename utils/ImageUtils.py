"""
图片编解码工具
提供 Base64 编码/解码功能用于 API 图片传输
"""
import base64
import io
from PIL import Image
from typing import Union
from pathlib import Path


def encode_image_to_base64(image: Union[Image.Image, str, Path]) -> str:
    """
    将图片编码为 Base64 字符串

    Args:
        image: PIL Image 对象或文件路径

    Returns:
        Base64 编码的字符串
    """
    if isinstance(image, (str, Path)):
        # 从文件读取
        with open(str(image), 'rb') as f:
            image_bytes = f.read()
        return base64.b64encode(image_bytes).decode('utf-8')
    else:
        # PIL Image 对象
        buffer = io.BytesIO()
        # 保存为 PNG 格式
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')


def decode_base64_image(base64_string: str) -> Image.Image:
    """
    将 Base64 字符串解码为 PIL Image

    Args:
        base64_string: Base64 编码的图片字符串

    Returns:
        PIL Image 对象

    Raises:
        ValueError: 如果解码失败
    """
    try:
        # 解码 Base64
        image_bytes = base64.b64decode(base64_string)
        # 从字节流创建图片
        buffer = io.BytesIO(image_bytes)
        image = Image.open(buffer)
        # 立即加载图片数据（避免延迟加载问题）
        image.load()
        return image
    except Exception as e:
        raise ValueError(f"无法解码 Base64 图片: {e}")


def validate_image_size(base64_string: str, max_size_mb: int = 10) -> bool:
    """
    验证 Base64 图片大小

    Args:
        base64_string: Base64 编码的图片
        max_size_mb: 最大允许大小（MB）

    Returns:
        是否在限制内
    """
    # Base64 编码后大小约为原始大小的 4/3
    encoded_size = len(base64_string)
    decoded_size_mb = (encoded_size * 3 / 4) / (1024 * 1024)
    return decoded_size_mb <= max_size_mb

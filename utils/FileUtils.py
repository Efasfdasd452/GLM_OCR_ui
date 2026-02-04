"""
文件处理工具模块
处理文件和目录操作
"""
import os
import json
from pathlib import Path
from typing import List, Union
from datetime import datetime
from PIL import Image


class FileUtils:
    """文件工具类"""

    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff'}

    @staticmethod
    def get_images_from_directory(
            directory: Union[str, Path],
            recursive: bool = False
    ) -> List[Path]:
        """
        从目录获取所有图片文件

        Args:
            directory: 目录路径
            recursive: 是否递归搜索子目录

        Returns:
            图片文件路径列表
        """
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            return []

        images = []

        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in FileUtils.SUPPORTED_IMAGE_FORMATS:
                        images.append(file_path)
        else:
            for file in directory.iterdir():
                if file.is_file() and file.suffix.lower() in FileUtils.SUPPORTED_IMAGE_FORMATS:
                    images.append(file)

        return sorted(images)

    @staticmethod
    def validate_image(image_path: Union[str, Path]) -> bool:
        """
        验证图片是否有效

        Args:
            image_path: 图片路径

        Returns:
            是否为有效图片
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    @staticmethod
    def save_result(
            text: str,
            output_path: Union[str, Path],
            format: str = "txt"
    ) -> bool:
        """
        保存识别结果

        Args:
            text: 识别结果文本
            output_path: 输出文件路径
            format: 输出格式 (txt, json, markdown)

        Returns:
            是否保存成功
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if format == "txt":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)

            elif format == "json":
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "text": text
                }
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            elif format == "markdown":
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# OCR Result\n\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"## Content\n\n{text}\n")

            return True

        except Exception as e:
            print(f"保存文件失败: {e}")
            return False

    @staticmethod
    def generate_output_filename(
            original_name: str,
            format_template: str = "[OCR]_{name}_{date}",
            date_format: str = "%Y%m%d_%H%M%S",
            extension: str = "txt"
    ) -> str:
        """
        生成输出文件名

        Args:
            original_name: 原始文件名
            format_template: 文件名格式模板
            date_format: 日期格式
            extension: 文件扩展名

        Returns:
            生成的文件名
        """
        name_without_ext = Path(original_name).stem
        current_date = datetime.now().strftime(date_format)

        filename = format_template.replace("{name}", name_without_ext)
        filename = filename.replace("{date}", current_date)

        return f"{filename}.{extension}"

    @staticmethod
    def ensure_directory(directory: Union[str, Path]) -> Path:
        """
        确保目录存在，不存在则创建

        Args:
            directory: 目录路径

        Returns:
            目录路径对象
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def get_file_size_mb(file_path: Union[str, Path]) -> float:
        """
        获取文件大小（MB）

        Args:
            file_path: 文件路径

        Returns:
            文件大小（MB）
        """
        return Path(file_path).stat().st_size / (1024 * 1024)

    @staticmethod
    def is_image_file(file_path: Union[str, Path]) -> bool:
        """
        判断是否为图片文件

        Args:
            file_path: 文件路径

        Returns:
            是否为图片文件
        """
        return Path(file_path).suffix.lower() in FileUtils.SUPPORTED_IMAGE_FORMATS
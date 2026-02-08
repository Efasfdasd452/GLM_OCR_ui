"""
PDF 处理工具模块
将 PDF 文档转换为图片，供 OCR 引擎识别
内置 Poppler，无需用户额外安装
"""
import sys
from pathlib import Path
from typing import List, Union, Optional
from PIL import Image


class PDFUtils:
    """PDF 工具类"""

    @staticmethod
    def _get_poppler_path() -> Optional[str]:
        """
        获取内置 Poppler 的 bin 目录路径

        优先使用程序自带的 poppler/Library/bin，
        找不到时返回 None（让 pdf2image 从系统 PATH 查找）。
        """
        # PyInstaller 打包后的基础目录
        if getattr(sys, 'frozen', False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent.parent

        poppler_bin = base / "poppler" / "Library" / "bin"
        if poppler_bin.exists() and (poppler_bin / "pdftoppm.exe").exists():
            return str(poppler_bin)

        return None

    @staticmethod
    def pdf_to_images(pdf_path: Union[str, Path], dpi: int = 200) -> List[Image.Image]:
        """
        将 PDF 文件转换为 PIL Image 列表

        Args:
            pdf_path: PDF 文件路径
            dpi: 渲染分辨率，越高越清晰但越慢

        Returns:
            PIL Image 对象列表，每页一个
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("请安装 pdf2image 库: pip install pdf2image")

        poppler_path = PDFUtils._get_poppler_path()

        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=dpi,
                poppler_path=poppler_path
            )
            return images
        except Exception as e:
            if "poppler" in str(e).lower() or "pdftoppm" in str(e).lower():
                raise RuntimeError(
                    f"找不到 Poppler，请确认程序目录下存在 poppler/Library/bin/pdftoppm.exe\n"
                    f"原始错误: {e}"
                )
            raise

    @staticmethod
    def get_pdf_page_count(pdf_path: Union[str, Path]) -> int:
        """
        获取 PDF 页数

        Args:
            pdf_path: PDF 文件路径

        Returns:
            页数
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        try:
            from pdf2image import pdfinfo_from_path
        except ImportError:
            raise ImportError("请安装 pdf2image: pip install pdf2image")

        poppler_path = PDFUtils._get_poppler_path()

        try:
            info = pdfinfo_from_path(str(pdf_path), poppler_path=poppler_path)
            return info["Pages"]
        except Exception:
            images = PDFUtils.pdf_to_images(pdf_path, dpi=72)
            count = len(images)
            for img in images:
                img.close()
            return count

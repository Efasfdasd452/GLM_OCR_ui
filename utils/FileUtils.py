"""
文件处理工具模块
处理文件和目录操作
"""
import os
import json
import zipfile
from pathlib import Path
from typing import List, Union, Tuple
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
        except (OSError, SyntaxError):
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

    # 批量输出方式
    BATCH_SAVE_SINGLE_MD = "single_md"
    BATCH_SAVE_SINGLE_TXT = "single_txt"
    BATCH_SAVE_ZIP_MD = "zip_md"
    BATCH_SAVE_ZIP_TXT = "zip_txt"
    BATCH_SAVE_SINGLE_PDF = "single_pdf"

    @staticmethod
    def _batch_result_content(text: str, as_markdown: bool) -> str:
        """单条结果写入文件时的内容（md 带简单标题，txt 纯文本）。"""
        if as_markdown:
            return f"# OCR Result\n\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## Content\n\n{text}\n"
        return text

    @staticmethod
    def save_batch_results(
        results: List[dict],
        output_dir: Union[str, Path],
        save_mode: str,
        filename_format: str = "[OCR]_{name}_{date}",
        date_format: str = "%Y%m%d_%H%M%S",
    ) -> Tuple[int, str]:
        """
        按选定方式保存批量识别结果。

        Args:
            results: 列表，每项 {"image": path, "text": str, "success": bool}
            output_dir: 输出目录（单文件时落在此目录，ZIP/PDF 也在此目录生成）
            save_mode: single_md / single_txt / zip_md / zip_txt / single_pdf
            filename_format: 文件名模板
            date_format: 日期格式

        Returns:
            (成功保存条数, 说明文字，如 "已保存到 xxx" 或 "已保存 3 个文件")
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        success_list = [r for r in results if r.get("success") and r.get("text") is not None]
        success_count = 0
        base_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if save_mode == FileUtils.BATCH_SAVE_SINGLE_MD:
            ext = "md"
            as_md = True
        elif save_mode == FileUtils.BATCH_SAVE_SINGLE_TXT:
            ext = "txt"
            as_md = False
        elif save_mode == FileUtils.BATCH_SAVE_ZIP_MD:
            ext = "md"
            as_md = True
        elif save_mode == FileUtils.BATCH_SAVE_ZIP_TXT:
            ext = "txt"
            as_md = False
        elif save_mode == FileUtils.BATCH_SAVE_SINGLE_PDF:
            ext = "pdf"
            as_md = False
        else:
            ext = "md"
            as_md = True

        if save_mode in (FileUtils.BATCH_SAVE_SINGLE_MD, FileUtils.BATCH_SAVE_SINGLE_TXT):
            for r in success_list:
                name = Path(r["image"]).name
                fname = FileUtils.generate_output_filename(name, filename_format, date_format, ext)
                path = output_dir / fname
                content = FileUtils._batch_result_content(r["text"], as_md)
                try:
                    path.write_text(content, encoding="utf-8")
                    success_count += 1
                except Exception as e:
                    print(f"保存失败 {path}: {e}")
            return success_count, str(output_dir.absolute())

        if save_mode in (FileUtils.BATCH_SAVE_ZIP_MD, FileUtils.BATCH_SAVE_ZIP_TXT):
            zip_path = output_dir / f"OCR_batch_{base_ts}.zip"
            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for r in success_list:
                        name = Path(r["image"]).name
                        fname = FileUtils.generate_output_filename(name, filename_format, date_format, ext)
                        content = FileUtils._batch_result_content(r["text"], as_md)
                        zf.writestr(fname, content.encode("utf-8"))
                        success_count += 1
                return success_count, str(zip_path.absolute())
            except Exception as e:
                print(f"打包失败: {e}")
                return 0, ""

        if save_mode == FileUtils.BATCH_SAVE_SINGLE_PDF:
            pdf_path = output_dir / f"OCR_batch_{base_ts}.pdf"
            ok, msg = FileUtils._write_batch_pdf(pdf_path, [r["text"] for r in success_list])
            if ok:
                return len(success_list), str(pdf_path.absolute())
            return 0, msg

        return success_count, str(output_dir.absolute())

    @staticmethod
    def _write_batch_pdf(pdf_path: Path, texts: List[str]) -> Tuple[bool, str]:
        """将多段文本写入一个 PDF，每段一页。成功返回 (True, path)，失败 (False, error_msg)。"""
        if not texts:
            return False, "无内容"
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
            import html
        except ImportError:
            return False, "请安装 reportlab: pip install reportlab"

        try:
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                leftMargin=72,
                rightMargin=72,
                topMargin=72,
                bottomMargin=72,
            )
            styles = getSampleStyleSheet()
            style = styles["Normal"]
            story = []
            for i, text in enumerate(texts):
                if i > 0:
                    story.append(PageBreak())
                plain = (text or "").strip()
                if not plain:
                    plain = "(无内容)"
                escaped = html.escape(plain).replace("\n", "<br/>")
                story.append(Paragraph(escaped, style))
            doc.build(story)
            return True, str(pdf_path.absolute())
        except Exception as e:
            return False, str(e)
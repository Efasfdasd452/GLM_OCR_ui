"""
剪贴板工具模块
处理剪贴板图片和文本
"""
import io
from PIL import Image, ImageGrab
from typing import Optional


class ClipboardUtils:
    """剪贴板工具类"""

    @staticmethod
    def get_image_from_clipboard() -> Optional[Image.Image]:
        """
        从剪贴板获取图片

        Returns:
            PIL Image 对象，如果剪贴板没有图片则返回 None
        """
        try:
            # 尝试从剪贴板获取图片
            image = ImageGrab.grabclipboard()

            if image is None:
                return None

            # 如果是图片对象，直接返回
            if isinstance(image, Image.Image):
                return image.convert('RGB')

            # 如果是文件路径列表（Windows 复制文件）
            elif isinstance(image, list):
                # 尝试打开第一个文件
                if len(image) > 0 and isinstance(image[0], str):
                    try:
                        return Image.open(image[0]).convert('RGB')
                    except Exception:
                        return None

            return None

        except Exception as e:
            print(f"从剪贴板获取图片失败: {e}")
            return None

    @staticmethod
    def has_image() -> bool:
        """
        检查剪贴板是否包含图片

        Returns:
            是否包含图片
        """
        try:
            image = ImageGrab.grabclipboard()
            if image is None:
                return False

            if isinstance(image, Image.Image):
                return True

            # 检查是否是图片文件路径
            if isinstance(image, list) and len(image) > 0:
                from pathlib import Path
                file_path = Path(image[0])
                return file_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'}

            return False

        except Exception:
            return False

    @staticmethod
    def set_text_to_clipboard(text: str) -> bool:
        """
        设置文本到剪贴板

        Args:
            text: 要复制的文本

        Returns:
            是否成功
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"复制到剪贴板失败: {e}")
            return False

    @staticmethod
    def set_image_to_clipboard(image: Image.Image) -> bool:
        """
        设置图片到剪贴板

        Args:
            image: PIL Image 对象

        Returns:
            是否成功
        """
        try:
            # 使用 win32clipboard (Windows)
            import win32clipboard
            from io import BytesIO

            output = BytesIO()
            image.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]  # BMP 文件头是 14 字节
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True

        except ImportError:
            # 如果没有 win32clipboard，尝试使用 PIL 的方法
            try:
                import subprocess
                import platform

                if platform.system() == 'Darwin':  # macOS
                    # 使用 pbcopy
                    process = subprocess.Popen(
                        ['osascript', '-e', 'set the clipboard to (read (POSIX file "' +
                         str(image) + '") as JPEG picture)'],
                        stdin=subprocess.PIPE
                    )
                    return True
                else:
                    print("不支持的操作系统")
                    return False

            except Exception as e:
                print(f"设置剪贴板图片失败: {e}")
                return False

        except Exception as e:
            print(f"设置剪贴板图片失败: {e}")
            return False
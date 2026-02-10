"""
远程 OCR 服务实现
通过 HTTP API 调用其他 GLM-OCR 客户端
"""
from typing import Optional, Dict
import httpx
from PIL import Image
from pathlib import Path

from services.base import OCRService
from utils.ImageUtils import encode_image_to_base64


class RemoteOCRService(OCRService):
    """远程 OCR 服务（通过 HTTP API 调用）"""

    def __init__(self, base_url: str, timeout: int = 60):
        """
        初始化远程服务

        Args:
            base_url: 远程 API 基础 URL（如 http://192.168.1.100:8000）
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = None

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
        try:
            # 转换为 Base64
            if isinstance(image, (str, Path)):
                image_b64 = encode_image_to_base64(str(image))
            elif isinstance(image, Image.Image):
                image_b64 = encode_image_to_base64(image)
            else:
                print(f"不支持的图片类型: {type(image)}")
                return None

            # 发送 HTTP 请求
            response = self.client.post(
                f"{self.base_url}/api/recognize",
                json={
                    "image_base64": image_b64,
                    "prompt": prompt,
                    "max_new_tokens": max_new_tokens
                }
            )

            # 检查响应
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data.get("text")
            else:
                error = data.get("error", "未知错误")
                print(f"远程识别失败: {error}")
                return None

        except httpx.TimeoutException:
            print(f"远程请求超时（{self.timeout}秒）")
            return None
        except httpx.HTTPStatusError as e:
            print(f"远程 API 错误: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"远程连接失败: {e}")
            return None
        except Exception as e:
            print(f"远程识别异常: {e}")
            return None

    def is_loaded(self) -> bool:
        """
        检查远程模型是否可用

        Returns:
            远程服务是否可用
        """
        try:
            response = self.client.get(
                f"{self.base_url}/api/status",
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("loaded", False)
        except Exception as e:
            print(f"无法连接到远程服务: {e}")
            return False

    def get_supported_prompts(self) -> Dict[str, str]:
        """
        获取远程服务支持的识别类型

        Returns:
            提示词映射字典
        """
        # 远程服务暂不提供此接口，返回默认值
        return {
            "text_recognition": "Text Recognition:",
            "document_parsing": "Document Parsing:",
            "table_recognition": "Table Recognition:",
            "formula_recognition": "Formula Recognition:"
        }

    def test_connection(self) -> tuple[bool, str]:
        """
        测试远程连接

        Returns:
            (是否成功, 状态消息)
        """
        try:
            # 健康检查
            response = self.client.get(
                f"{self.base_url}/api/health",
                timeout=5.0
            )
            response.raise_for_status()
            health_data = response.json()

            if health_data.get("status") == "ok":
                # 检查模型状态
                status_response = self.client.get(
                    f"{self.base_url}/api/status",
                    timeout=5.0
                )
                status_response.raise_for_status()
                status_data = status_response.json()

                if status_data.get("loaded"):
                    return True, "连接成功，远程模型已加载"
                else:
                    return True, "连接成功，但远程模型未加载"
            else:
                return False, "远程服务状态异常"

        except httpx.TimeoutException:
            return False, "连接超时"
        except httpx.HTTPStatusError as e:
            return False, f"HTTP 错误: {e.response.status_code}"
        except httpx.RequestError:
            return False, "无法连接到远程服务"
        except Exception as e:
            return False, f"未知错误: {e}"

    @property
    def client(self) -> httpx.Client:
        """懒初始化 HTTP 客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def close(self):
        """显式关闭 HTTP 客户端"""
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None

    def __del__(self):
        """析构时关闭 HTTP 客户端"""
        try:
            self.close()
        except (httpx.HTTPError, RuntimeError, OSError):
            pass

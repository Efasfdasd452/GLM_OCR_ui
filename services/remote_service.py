"""
远程 OCR 服务实现
通过 HTTP API 调用其他 GLM-OCR 客户端
- 单图识别：httpx 同步请求
- 批量识别：线程池 + 同步 httpx 请求，结果顺序与 images 严格一致
"""
from concurrent.futures import ThreadPoolExecutor, wait as futures_wait, FIRST_COMPLETED
from typing import Optional, Dict, List, Callable
import httpx
from PIL import Image
from pathlib import Path

from services.base import OCRService
from utils.ImageUtils import encode_image_to_base64


def _image_to_base64_sync(image) -> Optional[str]:
    """同步将图片转为 Base64，供批量异步里在 run_in_executor 或同步调用。"""
    try:
        if isinstance(image, (str, Path)):
            return encode_image_to_base64(str(image))
        if isinstance(image, Image.Image):
            return encode_image_to_base64(image)
    except Exception:
        pass
    return None


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
        识别单张图片（同步，供单次调用）

        Args:
            image: 图片（PIL Image、文件路径或 Path 对象）
            prompt: 识别类型提示词
            max_new_tokens: 最大生成 token 数

        Returns:
            识别结果文本，失败返回 None
        """
        try:
            image_b64 = _image_to_base64_sync(image)
            if not image_b64:
                print("不支持的图片类型")
                return None
            response = self.client.post(
                f"{self.base_url}/api/recognize",
                json={
                    "image_base64": image_b64,
                    "prompt": prompt,
                    "max_new_tokens": max_new_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                return data.get("text")
            print(f"远程识别失败: {data.get('error', '未知错误')}")
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
        """检查远程模型是否可用"""
        try:
            response = self.client.get(
                f"{self.base_url}/api/status",
                timeout=5.0
            )
            response.raise_for_status()
            return response.json().get("loaded", False)
        except Exception as e:
            print(f"无法连接到远程服务: {e}")
            return False

    def get_supported_prompts(self) -> Dict[str, str]:
        """获取远程服务支持的识别类型"""
        return {
            "text_recognition": "Text Recognition:",
            "document_parsing": "Document Parsing:",
            "table_recognition": "Table Recognition:",
            "formula_recognition": "Formula Recognition:"
        }

    def _fetch_recommended_concurrency(self) -> int:
        """从远程 /api/status 获取推荐批量并发数，失败时返回 2。"""
        try:
            response = self.client.get(
                f"{self.base_url}/api/status",
                timeout=5.0
            )
            response.raise_for_status()
            info = (response.json().get("model_info") or {})
            n = info.get("recommended_batch_concurrency")
            if isinstance(n, int) and n >= 1:
                return min(n, 8)
        except Exception:
            pass
        return 2

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
        批量识别：线程池 + 同步 httpx 请求，返回列表与 images 顺序严格一致（第 i 个结果对应第 i 张图）。
        """
        total = len(images)
        if total == 0:
            return []

        concurrency = max(1, self._fetch_recommended_concurrency())
        print(f"[批量识别] 后端推荐并发数: {concurrency}")
        results = [None] * total
        next_index = 0
        in_flight = {}  # future -> idx
        base_url = self.base_url.rstrip("/")
        timeout = self.timeout

        def recognize_one(idx: int, img) -> tuple:
            """单张识别（在线程池中执行，每个线程自建 httpx 客户端）。"""
            try:
                image_b64 = _image_to_base64_sync(img)
                if not image_b64:
                    return idx, {
                        "image": str(img),
                        "text": "不支持的图片类型",
                        "success": False,
                    }
                with httpx.Client(timeout=timeout) as client:
                    resp = client.post(
                        f"{base_url}/api/recognize",
                        json={
                            "image_base64": image_b64,
                            "prompt": prompt,
                            "max_new_tokens": max_new_tokens,
                        },
                    )
                    data = resp.json()
                    text = data.get("text") if data.get("success") else None
            except Exception as e:
                print(f"远程识别失败 [{idx}]: {e}")
                text = None
            return idx, {
                "image": str(img),
                "text": text if text else "",
                "success": text is not None,
            }

        executor = ThreadPoolExecutor(max_workers=concurrency)
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
                    future = executor.submit(recognize_one, idx, images[idx])
                    in_flight[future] = idx
                if not in_flight:
                    break
                # 带超时等待，便于定期检查停止/暂停（否则会阻塞到有任务完成才响应）
                done, _ = futures_wait(in_flight.keys(), return_when=FIRST_COMPLETED, timeout=1.0)
                for f in done:
                    idx = in_flight.pop(f)
                    try:
                        _, result = f.result()
                        results[idx] = result
                        if progress_callback:
                            completed = sum(1 for r in results if r is not None)
                            progress_callback(completed, total, result)
                    except Exception as e:
                        results[idx] = {
                            "image": str(images[idx]),
                            "text": f"错误: {e}",
                            "success": False,
                        }
                        if progress_callback:
                            completed = sum(1 for r in results if r is not None)
                            progress_callback(completed, total, results[idx])
                if stop_check and stop_check():
                    break
        except Exception as e:
            print(f"批量远程识别异常: {e}")
            for i in range(total):
                if results[i] is None:
                    results[i] = {
                        "image": str(images[i]),
                        "text": f"错误: {e}",
                        "success": False,
                    }
        finally:
            # wait=False：停止时立刻返回，不阻塞等待在途 HTTP 请求完成
            executor.shutdown(wait=False)

        for i in range(total):
            if results[i] is None:
                results[i] = {
                    "image": str(images[i]),
                    "text": "已停止",
                    "success": False,
                }
        return results

    def test_connection(self) -> tuple[bool, str]:
        """测试远程连接"""
        try:
            response = self.client.get(
                f"{self.base_url}/api/health",
                timeout=5.0
            )
            response.raise_for_status()
            if response.json().get("status") != "ok":
                return False, "远程服务状态异常"
            status_response = self.client.get(
                f"{self.base_url}/api/status",
                timeout=5.0
            )
            status_response.raise_for_status()
            if status_response.json().get("loaded"):
                return True, "连接成功，远程模型已加载"
            return True, "连接成功，但远程模型未加载"
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
        """懒初始化同步 HTTP 客户端（单图与状态查询）"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def close(self):
        """显式关闭 HTTP 客户端"""
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None

    def __del__(self):
        try:
            self.close()
        except (httpx.HTTPError, RuntimeError, OSError):
            pass

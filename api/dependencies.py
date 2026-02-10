"""
API 依赖注入
全局管理 OCREngine 实例
"""
from typing import Optional
from core.OCREngine import OCREngine
from core.Config import Config
from pathlib import Path
import time
import threading


class ModelManager:
    """单例模式管理 OCREngine"""

    def __init__(self):
        self.engine: Optional[OCREngine] = None
        self.start_time: float = time.time()
        self.config: Optional[Config] = None
        self._load_lock = threading.Lock()

    def load_model(self, config: Config) -> bool:
        """
        加载模型（线程安全）

        Args:
            config: 配置对象

        Returns:
            是否成功加载
        """
        if self.engine is not None and self.engine.is_loaded():
            print("模型已加载")
            return True

        with self._load_lock:
            # 双重检查：拿到锁后再确认一次
            if self.engine is not None and self.engine.is_loaded():
                return True

            self.config = config

            try:
                # 从配置读取参数
                quantization = config.get("model.quantization", "none")
                dtype = config.get("model.dtype", "float16")

                if config.get("model.use_local_only"):
                    self.engine = OCREngine(
                        model_path=config.get("model.local_path"),
                        device=config.get("model.device"),
                        use_local_only=config.get("model.use_local_only"),
                        quantization=quantization,
                        dtype=dtype
                    )
                else:
                    self.engine = OCREngine(
                        model_path=config.get("model.name"),
                        device=config.get("model.device"),
                        quantization=quantization,
                        dtype=dtype
                    )

                # 加载模型
                success = self.engine.load_model(
                    progress_callback=lambda msg, prog: print(f"[模型加载] {msg}")
                )

                if success:
                    print("✓ 模型加载成功")
                    self.start_time = time.time()
                else:
                    print("✗ 模型加载失败")
                    self.engine = None

                return success
            except Exception as e:
                print(f"✗ 模型加载异常: {e}")
                self.engine = None
                return False

    def unload_model(self):
        """卸载模型"""
        if self.engine:
            self.engine.unload_model()
            self.engine = None
            print("模型已卸载")

    def get_engine(self) -> Optional[OCREngine]:
        """获取 OCREngine 实例"""
        return self.engine

    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.engine is not None and self.engine.is_loaded()

    def get_uptime(self) -> float:
        """获取运行时间（秒）"""
        return time.time() - self.start_time

    def get_model_info(self) -> dict:
        """获取模型信息"""
        if not self.is_loaded() or not self.engine:
            return {}

        info = self.engine.get_model_info()
        if self.config:
            info.update({
                "quantization": self.config.get("model.quantization", "none"),
                "max_new_tokens_limit": self.config.get("model.max_new_tokens_limit", 8192)
            })
        return info


# 全局单例
model_manager = ModelManager()


def get_model_manager() -> ModelManager:
    """依赖注入：获取 ModelManager"""
    return model_manager

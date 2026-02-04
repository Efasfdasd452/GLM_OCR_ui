"""
配置管理模块（支持本地模型路径）
"""
import os
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """配置管理类"""

    # 默认配置
    DEFAULT_CONFIG = {
        "model": {
            # 优先使用本地模型路径
            "name": "zai-org/GLM-OCR",
            "local_path": None,  # 本地模型路径，优先级高于 name
            "device": "auto",
            "torch_dtype": "auto",
            "max_new_tokens": 2048
        },
        "ocr": {
            "language": "简体中文",
            "prompt_type": "text_recognition",
            "output_format": "txt"
        },
        "batch": {
            "enabled": False,
            "recursive": False,
            "output_dir": "./output",
            "filename_format": "[OCR]_{name}_{date}",
            "date_format": "%Y%m%d_%H%M%S"
        },
        "ui": {
            "theme": "light",
            "font_size": 12,
            "window_size": "1200x800"
        }
    }

    def __init__(self, config_path: str = None):
        """初始化配置"""
        if config_path is None:
            config_path = Path.home() / "config.json"

        self.config_path = Path(config_path)
        self.config = self.load_config()

        # 自动检测本地模型
        self.detect_local_model()

    def detect_local_model(self):
        """自动检测本地模型路径"""
        # 检测顺序：
        # 1. 配置文件中的 local_path
        # 2. 程序同目录下的 models/GLM-OCR
        # 3. 上级目录的 models/GLM-OCR

        if self.config["model"]["local_path"]:
            local_path = Path(self.config["model"]["local_path"])
            if local_path.exists():
                print(f"✓ 使用配置的本地模型: {local_path}")
                return

        # 检测程序同目录
        exe_dir = Path(__file__).parent.parent  # 回到项目根目录
        local_model_paths = [
            exe_dir / "models" / "GLM-OCR",  # ./models/GLM-OCR
            exe_dir.parent / "models" / "GLM-OCR",  # ../models/GLM-OCR
            Path("./models/GLM-OCR"),  # 相对路径
            Path("../models/GLM-OCR"),  # 上级目录
        ]

        for path in local_model_paths:
            if path.exists() and (path / "model.safetensors").exists():
                print(f"✓ 自动检测到本地模型: {path.absolute()}")
                self.config["model"]["local_path"] = str(path.absolute())
                return

        print("⚠ 未检测到本地模型，将从 HuggingFace 下载")

    def get_model_path(self) -> str:
        """获取模型路径（优先返回本地路径）"""
        local_path = self.config["model"].get("local_path")
        if local_path and Path(local_path).exists():
            return str(Path(local_path).absolute())
        return self.config["model"]["name"]

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                return self._merge_config(self.DEFAULT_CONFIG.copy(), loaded_config)
            except Exception as e:
                print(f"加载配置失败: {e}, 使用默认配置")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()

    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """递归合并配置"""
        for key, value in loaded.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                default[key] = self._merge_config(default[key], value)
            else:
                default[key] = value
        return default

    def get(self, key_path: str, default=None):
        """获取配置值"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value):
        """设置配置值"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value

    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
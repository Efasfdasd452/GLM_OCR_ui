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
    "name": "zai-org/GLM-OCR",
    "local_path": "./models/GLM-OCR",
    "device": "auto",
    "torch_dtype": "float16",
    "max_new_tokens": 2048,
    "use_local_only": True
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
    README_STR = """
     ===========================================                                                                                                                 
       GLM-OCR 配置说明 (config.json)                                                                                                                         
  ===========================================

  【模型设置 model】

    name          HuggingFace 模型名称
                  默认: zai-org/GLM-OCR
                  仅在 use_local_only 为 false 时生效

    local_path    本地模型文件夹路径（优先级高于 name）
                  默认: ./models/GLM-OCR
                  支持相对路径或绝对路径
                  示例: D:/my_models/GLM-OCR

    device        运行设备
                  auto  - 自动选择（有显卡用显卡，没有用CPU）
                  cuda  - 强制使用显卡
                  cpu   - 强制使用CPU

    torch_dtype   模型精度
                  float16 - 半精度（推荐，省显存）
                  auto    - 自动选择
                  float32 - 全精度（更准但占用翻倍）

    max_new_tokens  最大生成字数
                    默认: 2048
                    识别长文档时可适当增大

    use_local_only  是否仅使用本地模型
                    true  - 离线模式，不连接网络（推荐）
                    false - 允许从 HuggingFace 在线下载

  【识别设置 ocr】

    language      识别语言
                  默认: 简体中文

    prompt_type   默认识别类型
                  text_recognition - 文本识别
                  document_parsing - 文档解析
                  table_recognition - 表格识别
                  formula_recognition - 公式识别

    output_format 输出格式
                  txt      - 纯文本
                  json     - JSON（含时间等元数据）
                  markdown - Markdown 格式

  【批量处理 batch】

    output_dir       结果保存目录
                     默认: ./output
                     示例: D:/OCR结果

    recursive        是否扫描子文件夹
                     true / false

    filename_format  输出文件名格式
                     {name} = 原文件名, {date} = 日期时间
                     默认: [OCR]_{name}_{date}

    date_format      日期格式
                     默认: %Y%m%d_%H%M%S
                     效果: 20260204_153012

  【界面设置 ui】

    theme         主题: light（浅色）/ dark（深色）
    font_size     字体大小，默认 12
    window_size   窗口尺寸，默认 1200x800
    """


    def __init__(self, config_path: str = None, base_dir: Path = None):
        """初始化配置"""
        # 基础目录（兼容 PyInstaller 打包）
        if base_dir is None:
            import sys
            if getattr(sys, 'frozen', False):
                self.base_dir = Path(sys.executable).parent
            else:
                self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)

        if config_path is None:
            config_path = self.base_dir / "config.json"
        readme_path_utf8 = self.base_dir / "readme_utf8.txt"
        readme_path_gbk = self.base_dir / "readme_gbk.txt"

        self.config_path = Path(config_path)
        self.readme_path_utf8 = Path(readme_path_utf8)
        self.readme_path_gbk = Path(readme_path_gbk)
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
        local_model_paths = [
            self.base_dir / "models" / "GLM-OCR",  # 程序目录/models/GLM-OCR
            self.base_dir.parent / "models" / "GLM-OCR",  # 上级目录/models/GLM-OCR
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
                with open(self.readme_path_utf8, 'w', encoding='utf-8') as f:
                    f.write(self.README_STR)
                with open(self.readme_path_gbk, 'w', encoding='gbk') as f:
                    f.write(self.README_STR)
                print(f"✓ 已加载配置文件: {self.config_path}")
                return self._merge_config(self.DEFAULT_CONFIG.copy(), loaded_config)
            except Exception as e:
                print(f"加载配置失败: {e}, 使用默认配置")
                return self.DEFAULT_CONFIG.copy()
        else:
            print(f"⚠ 未找到配置文件: {self.config_path}，自动创建默认配置")
            config = self.DEFAULT_CONFIG.copy()
            # 自动生成默认配置文件到程序目录
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                with open(self.readme_path_utf8,'w',encoding='utf-8') as f:
                    f.write(self.README_STR)
                with open(self.readme_path_gbk,'w',encoding='gbk') as f:
                    f.write(self.README_STR)
                print(f"✓ 已创建默认配置文件: {self.config_path}")
            except Exception as e:
                print(f"⚠ 创建配置文件失败: {e}")
            return config

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
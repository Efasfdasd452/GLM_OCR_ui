# GLM-OCR 本地模型配置说明

## 修改内容

为了支持完全离线使用本地模型，添加了一个新的配置项 `use_local_only`。

### 修改的文件：

1. **core/Config.py**
   - 在 `DEFAULT_CONFIG["model"]` 中添加了 `"use_local_only": False` 配置项
   
2. **core/OCREngine.py**
   - 在 `__init__` 方法中添加了 `use_local_only` 参数
   - 在 `load_model` 方法中，调用 `from_pretrained` 时添加了 `local_files_only=self.use_local_only` 参数

3. **ui/MainWindow.py**
   - 修改 OCREngine 初始化，使用 `config.get_model_path()` 替代直接获取 `model.name`
   - 添加 `use_local_only` 参数传递

## 使用方法

### 方法1: 修改配置文件（推荐）

编辑配置文件 `~/.glm_ocr_config.json`（Linux/Mac）或 `C:\Users\你的用户名\.glm_ocr_config.json`（Windows）:

```json
{
  "model": {
    "name": "zai-org/GLM-OCR",
    "local_path": "/path/to/your/local/GLM-OCR",
    "use_local_only": true,
    "device": "auto",
    "torch_dtype": "auto",
    "max_new_tokens": 8192
  }
}
```

**参数说明：**
- `local_path`: 本地模型的完整路径（优先级最高）
- `use_local_only`: 
  - `true` - 强制只使用本地模型，不连接 HuggingFace（离线模式）
  - `false` - 允许从 HuggingFace 下载（默认）

### 方法2: 自动检测

程序会自动检测以下位置的本地模型：
1. 配置文件中指定的 `local_path`
2. `./models/GLM-OCR`（程序同目录）
3. `../models/GLM-OCR`（上级目录）

如果检测到本地模型，会自动使用。

### 方法3: 程序化设置

```python
from core.Config import Config

config = Config()
config.set("model.local_path", "/path/to/your/local/GLM-OCR")
config.set("model.use_local_only", True)
config.save_config()
```

## 配置组合说明

| local_path | use_local_only | 行为 |
|------------|----------------|------|
| 未设置 | False | 从 HuggingFace 下载模型 |
| 未设置 | True | 错误（没有本地模型） |
| 已设置 | False | 优先使用本地，缺失文件时从 HuggingFace 下载 |
| 已设置 | True | **仅使用本地，完全离线（推荐）** |

## 完全离线使用步骤

1. 首先在有网络的环境下载模型到本地：
   ```bash
   # 使用 huggingface-cli 下载
   huggingface-cli download zai-org/GLM-OCR --local-dir ./models/GLM-OCR
   ```

2. 修改配置文件：
   ```json
   {
     "model": {
       "local_path": "./models/GLM-OCR",
       "use_local_only": true
     }
   }
   ```

3. 运行程序，现在会完全使用本地模型，不会尝试连接 HuggingFace

## 错误排查

### 错误：OSError: Can't load tokenizer for '...'

**原因：** 设置了 `use_local_only: true` 但本地模型路径不正确或文件不完整

**解决方案：**
1. 检查 `local_path` 路径是否正确
2. 确认模型文件完整（应包含 config.json, tokenizer_config.json, model.safetensors 等）
3. 如需下载，临时设置 `use_local_only: false`

### 提示：未检测到本地模型

**原因：** 程序在预设位置没找到模型

**解决方案：**
1. 将模型放到 `./models/GLM-OCR` 目录
2. 或在配置文件中明确指定 `local_path`

## 优势

- ✅ 完全离线运行，不依赖网络
- ✅ 避免 HuggingFace 连接超时问题
- ✅ 加载速度更快（无需检查远程更新）
- ✅ 保护隐私，不向外部发送请求

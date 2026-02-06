# GLM-OCR

基于 [GLM-OCR](https://huggingface.co/zai-org/GLM-OCR) 模型的本地图像文字识别工具，提供现代化的图形用户界面。
如果需要弄打包版，则需要下载源代码和模型(./models)以后，执行exe.py打包
## 功能特性

- **多种识别模式**
  - 文本识别 - 通用文字提取
  - 文档解析 - 结构化文档识别
  - 表格识别 - 表格内容提取
  - 公式识别 - 数学公式识别

- **便捷的输入方式**
  - 单图识别 - 选择图片文件
  - 剪贴板识别 - 直接粘贴截图
  - 批量识别 - 多文件处理
  - 文件夹扫描 - 批量处理整个目录

- **二维码功能**
  - 二维码生成
  - 二维码识别

- **离线运行**
  - 完全本地化，无需联网
  - 支持 GPU 加速

## 安装

### 环境要求

- Python 3.8+
- CUDA（可选，用于 GPU 加速）

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/your-username/glm-ocr.git
cd glm-ocr
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 下载模型

首次运行时会自动从 HuggingFace 下载模型（约 3-4GB）。

如需手动下载，可以使用：

```bash
python export.py
# 选择选项 1：导出模型到本地
```

## 使用方法

### 启动程序

```bash
python main.py
```

或使用启动脚本：
- Windows: 双击 `start.bat`
- Linux/macOS: `bash start.sh`

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Q` | 快速识别 |
| `Ctrl+V` | 剪贴板识别 |
| `Ctrl+O` | 选择图片 |

### 离线模式

修改 `config.json` 启用离线模式：

```json
{
  "model": {
    "use_local_only": true,
    "local_path": "./models/GLM-OCR"
  }
}
```

## 模型信息

本项目使用 HuggingFace 上的 [zai-org/GLM-OCR](https://huggingface.co/zai-org/GLM-OCR) 模型。

| 项目 | 说明 |
|------|------|
| 模型名称 | GLM-OCR |
| 来源 | HuggingFace |
| 模型大小 | ~3-4GB |
| 支持设备 | CPU / CUDA |

## 项目结构

```
glm_ocr/
├── core/                   # 核心模块
│   ├── Config.py          # 配置管理
│   └── OCREngine.py       # OCR 引擎
├── ui/                     # 用户界面
│   └── MainWindow.py      # 主窗口
├── utils/                  # 工具模块
│   ├── FileUtils.py       # 文件处理
│   ├── ClipboardUtils.py  # 剪贴板操作
│   └── QRCodeUtils.py     # 二维码处理
├── models/                 # 本地模型存储
├── output/                 # 输出目录
├── main.py                 # 程序入口
├── export.py               # 模型导出工具
├── config.json             # 配置文件
└── requirements.txt        # 依赖列表
```

## 配置说明

`config.json` 主要配置项：

```json
{
  "model": {
    "name": "zai-org/GLM-OCR",
    "local_path": "./models/GLM-OCR",
    "device": "auto",
    "torch_dtype": "float16",
    "use_local_only": true
  },
  "ocr": {
    "prompt_type": "text_recognition",
    "output_format": "txt"
  },
  "batch": {
    "output_dir": "./output",
    "recursive": false
  },
  "ui": {
    "theme": "light"
  }
}
```

## 依赖项

主要依赖：

- `torch` - 深度学习框架
- `transformers` - HuggingFace 模型库
- `customtkinter` - GUI 框架
- `Pillow` - 图像处理
- `pyzbar` - 二维码识别

完整列表见 [requirements.txt](requirements_old.txt)。

## 创建便携版

```bash
python export.py
# 选择选项 2：创建完整的便携版程序包
```

便携版包含所有源代码和模型文件，可直接运行。

## 致谢

- [GLM-OCR](https://huggingface.co/zai-org/GLM-OCR) - OCR 模型
- [HuggingFace Transformers](https://github.com/huggingface/transformers) - 模型加载框架
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - GUI 框架

## 许可证

MIT License

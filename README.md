# GLM-OCR 图片文字识别工具

基于 GLM-4V-9B 模型的高精度 OCR 图片文字识别工具，支持前后端分离架构，提供 GUI 界面和 RESTful API 服务。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## ✨ 主要特性

### 核心功能
- 🖼️ **多种识别模式**：文本识别、文档解析、表格识别、公式识别、二维码识别
- 📄 **PDF 文档识别**：支持将 PDF 文档逐页转换并识别
- 📸 **截图识别**：快捷键 `Ctrl+Shift+S` 快速截图识别
- 📋 **剪贴板识别**：直接识别剪贴板中的图片
- 📁 **批量处理**：支持批量识别多张图片或整个文件夹
- 🎨 **二维码生成**：支持生成二维码图片

### 前后端分离架构 (v2.0 新增)
- 🔌 **API 服务器**：提供 RESTful API 供外部程序调用
- 🌐 **远程模式**：UI 可调用其他机器的 OCR 服务
- 🖥️ **本地模式**：传统的本地模型直接推理
- 🔄 **混合模式**：GUI + API 服务器同时运行
- 📚 **自动文档**：Swagger UI 自动生成 API 文档

### 用户体验
- 🌍 **多语言支持**：简体中文、繁体中文、English、Français、Deutsch、日本語、Italiano、Русский
- 🎛️ **动态配置**：实时调整 Token 数量、识别类型
- 💾 **自动保存**：设置自动保存，无需手动点击
- 🔔 **提示通知**：Toast 风格提示信息
- 🎨 **现代化 UI**：基于 CustomTkinter 的美观界面

### 性能优化
- ⚡ **量化支持**：8bit/4bit 量化降低内存占用
- 🧠 **智能缓存**：推理后自动清理显存
- 🔀 **并发控制**：API 服务器支持并发处理，防止 OOM
- 📊 **进度反馈**：批量识别实时显示进度

---

## 📦 安装

### 系统要求
- Python 3.8 或更高版本
- Windows / Linux / macOS
- （可选）NVIDIA GPU 支持 CUDA 12.6

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/glm-ocr.git
cd glm-ocr
```

### 2. 安装依赖

**基础依赖**（GUI 模式）：
```bash
pip install -r requirements.txt
```

**完整依赖**（包含 API 服务器）：
```bash
pip install -r requirements.txt
pip install fastapi uvicorn[standard] httpx pydantic python-multipart
```

### 3. 下载模型

**方式 1：自动下载**（首次运行时自动从 HuggingFace 下载）
```bash
python main.py
# 点击"加载模型"按钮，程序会自动下载
```

**方式 2：手动下载**（推荐，支持离线使用）
```bash
# 下载到 ./models/GLM-OCR 目录
git lfs clone https://huggingface.co/zai-org/GLM-OCR ./models/GLM-OCR
```

修改 `config.json`：
```
{
  "model": {
    "use_local_only": true,
    "local_path": "./models/GLM-OCR"
  }
}
```

---

## 🚀 快速开始

### GUI 模式（默认）

```bash
python main.py
```

启动后：
1. 点击"加载模型"按钮加载 GLM-OCR 模型
2. 选择识别模式（文本识别/文档解析/表格识别/公式识别）
3. 使用以下方式之一识别图片：
   - 点击"截图 OCR"或按 `Ctrl+Shift+S` 截图识别
   - 点击"剪贴板 OCR"或按 `Ctrl+V` 识别剪贴板图片
   - 点击"选择图片"或按 `Ctrl+O` 选择本地图片

### API 服务器模式

**启动服务器**：
```bash
python main.py --server
```

服务器启动后访问：
- **API 文档**：http://127.0.0.1:8000/docs
- **健康检查**：http://127.0.0.1:8000/api/health

**自定义地址和端口**：
```bash
python main.py --server --host 0.0.0.0 --port 8080
```

### 混合模式（GUI + API）

```bash
python main.py --with-server
```

同时启动 GUI 界面和 API 服务器，适合个人使用时对外提供 API 服务。

---

## 📡 API 使用

### 端点列表

| 端点 | 方法 | 功能 | 说明 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | 返回服务状态 |
| `/api/status` | GET | 模型状态 | 返回模型是否已加载 |
| `/api/recognize` | POST | 单图识别 | 识别单张图片 |
| `/api/model/load` | POST | 加载模型 | 手动触发模型加载 |
| `/api/model/unload` | POST | 卸载模型 | 释放内存 |

### 识别请求示例

**Python 示例**：
```
import requests
import base64

# 读取图片
with open("test.png", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# 发送识别请求
response = requests.post("http://127.0.0.1:8000/api/recognize", json={
    "image_base64": image_b64,
    "prompt": "Text Recognition:",
    "max_new_tokens": 2048
})

result = response.json()
if result["success"]:
    print("识别结果:", result["text"])
    print("处理时间:", result["processing_time"], "秒")
else:
    print("识别失败:", result["error"])
```

**curl 示例**：
```bash
# Linux/macOS
IMAGE_B64=$(base64 -w 0 test.png)

# Windows PowerShell
$IMAGE_B64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("test.png"))

# 发送请求
curl -X POST http://127.0.0.1:8000/api/recognize \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$IMAGE_B64\", \"prompt\": \"Text Recognition:\", \"max_new_tokens\": 2048}"
```

**JavaScript 示例**：
```javascript
// 读取图片文件
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

// 转换为 Base64
const reader = new FileReader();
reader.onload = async function(e) {
    const base64 = e.target.result.split(',')[1];

    // 发送请求
    const response = await fetch('http://127.0.0.1:8000/api/recognize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_base64: base64,
            prompt: 'Text Recognition:',
            max_new_tokens: 2048
        })
    });

    const result = await response.json();
    console.log('识别结果:', result.text);
};
reader.readAsDataURL(file);
```

### 响应格式

**成功响应**：
```
{
  "success": true,
  "text": "识别出的文本内容",
  "error": null,
  "processing_time": 1.23,
  "timestamp": "2026-02-09T12:34:56"
}
```

**失败响应**：
```
{
  "success": false,
  "text": null,
  "error": "模型未加载",
  "processing_time": 0.01,
  "timestamp": "2026-02-09T12:34:56"
}
```

### 识别类型（Prompt）

| Prompt | 说明 | 适用场景 |
|--------|------|----------|
| `Text Recognition:` | 文本识别 | 普通文字、手写文字 |
| `Document Parsing:` | 文档解析 | 结构化文档、段落识别 |
| `Table Recognition:` | 表格识别 | 表格数据提取 |
| `Formula Recognition:` | 公式识别 | 数学公式、化学式 |

---

## 🔧 配置说明

配置文件：`config.json`

### 模型配置
```
{
  "model": {
    "name": "zai-org/GLM-OCR",          // HuggingFace 模型名称
    "local_path": "./models/GLM-OCR",  // 本地模型路径（优先级更高）
    "device": "auto",                  // 运行设备：auto/cuda/cpu
    "quantization": "none",            // 量化：none/8bit/4bit
    "max_new_tokens": 2048,            // 默认最大生成 Token 数
    "max_new_tokens_limit": 8192,      // Token 上限
    "use_local_only": true             // 离线模式
  }
}
```

### API 配置
```
{
  "api": {
    "enabled": false,                      // 是否启用 API 服务器
    "host": "127.0.0.1",                   // 监听地址
    "port": 8000,                          // 监听端口
    "mode": "local",                       // 客户端模式：local/remote
    "remote_url": "http://127.0.0.1:8000", // 远程服务地址
    "auto_load_model": true,               // API 启动时自动加载模型
    "max_image_size_mb": 10                // 最大图片大小（MB）
  }
}
```

### UI 配置
```
{
  "ui": {
    "language": "简体中文",                 // 界面语言
    "screenshot_reminder_disabled": false  // 禁用截图成功提示
  }
}
```

### 批量识别配置
```
{
  "batch": {
    "output_dir": "./output",                         // 输出目录
    "filename_format": "[OCR]_{name}_{date}",        // 文件名格式
    "date_format": "%Y%m%d_%H%M%S"                   // 日期格式
  }
}
```

---

## 🌐 远程模式使用

### 场景说明
- **服务器**：性能强劲的机器（如 GPU 工作站）运行 API 服务器
- **客户端**：轻量级机器（如笔记本）运行 GUI，通过 API 调用服务器

### 配置步骤

#### 1. 服务器端
```bash
# 启动 API 服务器（允许局域网访问）
python main.py --server --host 0.0.0.0 --port 8000
```

#### 2. 客户端
打开 GUI 设置界面：
1. **客户端模式** → 选择 `remote`
2. **远程地址** → 输入 `http://192.168.1.100:8000`（替换为服务器 IP）
3. 点击 **测试连接** 验证连接状态
4. 保存设置

现在客户端的所有识别操作都会通过网络调用服务器的 API。

### 安全提示
⚠️ 使用 `0.0.0.0` 监听时会弹出安全警告：
- **127.0.0.1**：仅本机访问（推荐）
- **0.0.0.0**：局域网可访问（需要确认）

建议：
- 仅在可信网络环境下使用 0.0.0.0
- 生产环境建议使用反向代理（Nginx）+ HTTPS
- 可选添加 API Token 认证

---

## ⚙️ 高级功能

### 量化模式（降低内存占用）

在 `config.json` 中配置：
```
{
  "model": {
    "quantization": "8bit"  // none/8bit/4bit
  }
}
```

| 模式 | 内存占用 | 速度 | 精度 |
|------|---------|------|------|
| none | 100% | 最快 | 最高 |
| 8bit | ~50% | 略慢 | 几乎无损 |
| 4bit | ~25% | 较慢 | 略有下降 |

**注意**：8bit/4bit 模式需要安装 `bitsandbytes` 库：
```bash
pip install bitsandbytes
```

### 自定义快捷键

当前快捷键：
- `Ctrl+Shift+S` - 截图识别
- `Ctrl+V` - 剪贴板识别
- `Ctrl+O` - 选择图片
- `Ctrl+Q` - 快速识别

### 批量识别

1. 切换到"批量 OCR"标签页
2. 点击"添加文件"或"添加文件夹"
3. （可选）勾选"递归子目录"
4. 点击"开始批量识别"
5. 结果自动保存到 `./output` 目录

### PDF 文档识别

1. 切换到"PDF OCR"标签页
2. 点击"选择 PDF 文件"
3. 等待转换和识别完成
4. 点击"保存结果"导出为 Markdown 或 TXT

---

## 🛠️ 开发指南

### 项目结构
```
glm_ocr/
├── api/                    # API 服务模块
│   ├── server.py          # FastAPI 应用
│   ├── models.py          # Pydantic 数据模型
│   └── dependencies.py    # 依赖注入
├── core/                  # 核心模块
│   ├── Config.py         # 配置管理
│   └── OCREngine.py      # OCR 引擎
├── services/             # 服务抽象层
│   ├── base.py          # OCRService 基类
│   ├── local_service.py # 本地服务
│   └── remote_service.py # 远程服务
├── ui/                   # UI 模块
│   ├── MainWindow.py    # 主窗口
│   ├── LanguageManager.py # 多语言
│   └── ToastNotification.py # 提示通知
├── utils/                # 工具模块
│   ├── ImageUtils.py    # 图片编解码
│   ├── FileUtils.py     # 文件操作
│   ├── ClipboardUtils.py # 剪贴板
│   ├── QRCodeUtils.py   # 二维码
│   ├── PDFUtils.py      # PDF 处理
│   └── ScreenCapture.py # 截图工具
├── main.py              # 程序入口
├── config.json          # 配置文件
└── requirements.txt     # 依赖列表
```

### 扩展识别类型

在 `core/OCREngine.py` 中添加新的 Prompt：
```
def get_supported_prompts(self) -> Dict[str, str]:
    return {
        "text_recognition": "Text Recognition:",
        "document_parsing": "Document Parsing:",
        "table_recognition": "Table Recognition:",
        "formula_recognition": "Formula Recognition:",
        "custom_type": "Your Custom Prompt:"  # 新增
    }
```

### 添加新语言

在 `ui/LanguageManager.py` 中添加翻译：
```
self.translations = {
    "window_title": {
        "zh_CN": "GLM-OCR 图片识别",
        "en": "GLM-OCR Image Recognition",
        "your_lang": "Your Translation"  # 新增
    },
    # ... 其他翻译
}
```

---

## 📊 性能参考

测试环境：
- CPU: Intel i7-12700K
- GPU: NVIDIA RTX 4060 Ti 16GB
- RAM: 32GB DDR4
- 模型：GLM-4V-9B（float16）

| 场景          | 图片尺寸      | 识别时间  | GPU 显存 |
|-------------|-----------|-------|--------|
| 单张文字图片      | 1920x1080 | ~2-3秒 | ~6GB   |
| 复杂表格        | 2560x1440 | ~4-5秒 | ~7GB   |
| PDF 文档（10页） | A4        | ~30秒  | ~6GB   |
| 批量识别（100张）  | 混合        | ~5分钟  | ~6GB   |

**网络延迟**（远程模式，局域网）：
- 上传图片（2MB）：~100ms
- 识别处理：~2-3秒
- 下载结果：~10ms
- **总计**：~2.5秒

---

## ❓ 常见问题

### 1. 模型加载失败
**原因**：模型文件缺失或路径错误

**解决**：
```bash
# 检查模型路径
ls ./models/GLM-OCR

# 重新下载模型
git lfs clone https://huggingface.co/zai-org/GLM-OCR ./models/GLM-OCR
```

### 2. CUDA Out of Memory
**原因**：GPU 显存不足

**解决**：
1. 启用量化模式：`"quantization": "8bit"`
2. 减少 Token 数量：`"max_new_tokens": 1024`
3. 关闭其他占用 GPU 的程序

### 3. API 服务器无法访问
**原因**：防火墙阻止或地址配置错误

**解决**：
```bash
# Windows 防火墙添加规则
netsh advfirewall firewall add rule name="GLM-OCR API" dir=in action=allow protocol=TCP localport=8000

# Linux iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

### 4. 远程模式连接超时
**原因**：网络不通或服务器未启动

**解决**：
1. 检查服务器是否运行：`curl http://192.168.1.100:8000/api/health`
2. 检查防火墙规则
3. 尝试使用 IP 地址而非域名

### 5. 识别结果为空
**原因**：图片质量差或类型不匹配

**解决**：
1. 使用更清晰的图片
2. 尝试不同的识别类型（文本识别/文档解析）
3. 增加 Token 数量

---

## 🔄 更新日志

### v2.0.0 (2026-02-09)
- ✨ 新增前后端分离架构
- ✨ 新增 RESTful API 服务器
- ✨ 新增远程模式支持
- ✨ 新增并发控制和线程池
- ✨ 新增 Swagger API 文档
- 🌍 完善多语言支持（9种语言）
- 🎨 优化设置界面布局
- 🔧 添加 API 配置选项
- ⚠️ 添加 0.0.0.0 监听安全警告

### v1.0.0 (2025-XX-XX)
- 🎉 首次发布
- 支持文本识别、文档解析、表格识别、公式识别
- 支持截图、剪贴板、批量识别
- 支持 PDF 文档识别
- 支持二维码生成和识别
- 多语言界面

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 🙏 致谢

- [GLM-4V-9B](https://huggingface.co/zai-org/GLM-OCR) - 核心 OCR 模型
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化 UI 库
- [Transformers](https://github.com/huggingface/transformers) - 模型推理框架

---

## 📧 联系方式

- **问题反馈**：GitHub Issues
- **功能建议**：GitHub Discussions

---

<p align="center">Made with ❤️ by GLM-OCR-ui Team</p>

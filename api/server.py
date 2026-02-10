"""
GLM-OCR API 服务器
基于 FastAPI 的 RESTful API
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from typing import Optional

from api.models import RecognizeRequest, RecognizeResponse, ModelStatusResponse, HealthResponse
from api.dependencies import ModelManager, get_model_manager
from utils.ImageUtils import decode_base64_image, validate_image_size
from core.Config import Config
from pathlib import Path
import sys


# 创建 FastAPI 应用（禁用默认 CDN 文档，改用本地静态文件）
app = FastAPI(
    title="GLM-OCR API",
    description="GLM-OCR 图片识别 API 服务",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# 挂载本地静态文件（Swagger UI JS/CSS/favicon）
_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# CORS 中间件（允许跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 自定义 /docs 页面（使用本地静态文件，无需联网）
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
    )


# 自定义 /redoc 页面（使用本地静态文件）
@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico",
    )


# 根路径跳转到 API 文档
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


# 线程池（用于并发推理）
executor = ThreadPoolExecutor(max_workers=4)

# 并发控制（防止 GPU OOM）
inference_semaphore = asyncio.Semaphore(2)  # 最多 2 个并发推理


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    import threading

    print("=" * 60)
    print("GLM-OCR API 服务器启动中...")
    print("=" * 60)

    # 加载配置
    manager = get_model_manager()

    # 查找配置文件
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent.parent

    config_path = base_dir / "config.json"
    config = Config(str(config_path), base_dir=base_dir)

    # 如果配置要求自动加载模型，在后台线程中加载（不阻塞端口启动）
    if config.get("api.auto_load_model", True):
        def _load_model_background():
            print("正在后台加载模型...")
            success = manager.load_model(config)
            if success:
                print("✓ 模型加载成功，API 已就绪")
            else:
                print("⚠ 模型加载失败，请手动调用 /api/model/load")

        threading.Thread(target=_load_model_background, daemon=True).start()
    else:
        print("自动加载已禁用，请手动调用 /api/model/load")

    print("=" * 60)
    print("API 服务器已启动，端口已开放")
    print(f"API 文档: http://127.0.0.1:8000/docs")
    print("模型正在后台加载中..." if config.get("api.auto_load_model", True) else "")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    print("正在关闭 API 服务器...")
    manager = get_model_manager()
    manager.unload_model()
    executor.shutdown(wait=False)
    print("✓ API 服务器已关闭")


@app.get("/api/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """
    健康检查

    返回服务状态和版本信息
    """
    return HealthResponse(status="ok", version="1.0.0")


@app.get("/api/status", response_model=ModelStatusResponse, tags=["模型"])
async def get_status(manager: ModelManager = Depends(get_model_manager)):
    """
    获取模型状态

    返回模型是否已加载、模型信息和运行时间
    """
    return ModelStatusResponse(
        loaded=manager.is_loaded(),
        model_info=manager.get_model_info() if manager.is_loaded() else None,
        uptime=manager.get_uptime()
    )


@app.post("/api/model/load", tags=["模型"])
async def load_model(manager: ModelManager = Depends(get_model_manager)):
    """
    加载模型

    手动触发模型加载
    """
    if manager.is_loaded():
        return {"success": True, "message": "模型已加载"}

    # 重新加载配置
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent.parent

    config_path = base_dir / "config.json"
    config = Config(str(config_path), base_dir=base_dir)

    success = manager.load_model(config)
    if success:
        return {"success": True, "message": "模型加载成功"}
    else:
        raise HTTPException(status_code=500, detail="模型加载失败")


@app.post("/api/model/unload", tags=["模型"])
async def unload_model(manager: ModelManager = Depends(get_model_manager)):
    """
    卸载模型

    释放 GPU/CPU 内存
    """
    manager.unload_model()
    return {"success": True, "message": "模型已卸载"}


@app.post("/api/recognize", response_model=RecognizeResponse, tags=["识别"])
async def recognize(
    request: RecognizeRequest,
    manager: ModelManager = Depends(get_model_manager)
):
    """
    单图识别

    接收 Base64 编码的图片，返回识别结果

    **参数**:
    - image_base64: Base64 编码的图片
    - prompt: 识别类型（默认: "Text Recognition:"）
    - max_new_tokens: 最大生成 token 数（默认: 2048）

    **返回**:
    - success: 是否成功
    - text: 识别结果文本
    - error: 错误信息（如果失败）
    - processing_time: 处理时间（秒）
    """
    # 检查模型是否已加载
    if not manager.is_loaded():
        raise HTTPException(status_code=503, detail="模型未加载，请先调用 /api/model/load")

    # 验证图片大小（默认最大 10MB）
    max_size_mb = 10
    if not validate_image_size(request.image_base64, max_size_mb):
        raise HTTPException(
            status_code=413,
            detail=f"图片过大，最大允许 {max_size_mb}MB"
        )

    # 使用并发控制
    async with inference_semaphore:
        # 在线程池中运行同步推理
        loop = asyncio.get_running_loop()
        start_time = time.time()

        try:
            result = await loop.run_in_executor(
                executor,
                _recognize_sync,
                request.image_base64,
                request.prompt,
                request.max_new_tokens,
                manager
            )
            processing_time = time.time() - start_time

            return RecognizeResponse(
                success=True,
                text=result,
                error=None,
                processing_time=processing_time
            )
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            print(f"✗ 识别失败: {error_msg}")

            return RecognizeResponse(
                success=False,
                text=None,
                error=error_msg,
                processing_time=processing_time
            )


def _recognize_sync(
    image_base64: str,
    prompt: str,
    max_new_tokens: int,
    manager: ModelManager
) -> Optional[str]:
    """
    同步推理函数（在线程池中执行）

    Args:
        image_base64: Base64 编码的图片
        prompt: 识别提示词
        max_new_tokens: 最大生成 token 数
        manager: 模型管理器

    Returns:
        识别结果文本

    Raises:
        Exception: 推理失败时抛出异常
    """
    try:
        # Base64 -> PIL Image
        image = decode_base64_image(image_base64)

        # 调用 OCREngine
        engine = manager.get_engine()
        if engine is None:
            raise RuntimeError("OCREngine 未初始化")

        text = engine.recognize_image(image, prompt, max_new_tokens)

        if text is None:
            raise RuntimeError("识别失败，返回结果为空")

        return text
    except Exception as e:
        raise RuntimeError(f"推理异常: {e}")


@app.exception_handler(413)
async def request_entity_too_large_handler():
    """处理请求过大异常"""
    return JSONResponse(
        status_code=413,
        content={
            "success": False,
            "text": None,
            "error": "请求过大，图片大小不能超过限制",
            "processing_time": 0
        }
    )


# 用于直接运行（调试）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

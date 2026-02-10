"""
API 数据模型
使用 Pydantic 进行请求/响应验证
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RecognizeRequest(BaseModel):
    """识别请求"""
    image_base64: str = Field(..., description="Base64 编码的图片")
    prompt: str = Field("Text Recognition:", description="识别类型提示词")
    max_new_tokens: int = Field(2048, ge=512, le=32768, description="最大生成 token 数")

    class Config:
        json_schema_extra = {
            "example": {
                "image_base64": "iVBORw0KGgoAAAANS...",
                "prompt": "Text Recognition:",
                "max_new_tokens": 2048
            }
        }


class RecognizeResponse(BaseModel):
    """识别响应"""
    success: bool = Field(..., description="是否成功")
    text: Optional[str] = Field(None, description="识别结果文本")
    error: Optional[str] = Field(None, description="错误信息")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "text": "识别结果文本",
                "error": None,
                "processing_time": 1.23,
                "timestamp": "2026-02-09T12:34:56"
            }
        }


class ModelStatusResponse(BaseModel):
    """模型状态响应"""
    loaded: bool = Field(..., description="模型是否已加载")
    model_info: Optional[dict] = Field(None, description="模型信息")
    uptime: Optional[float] = Field(None, description="运行时间（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "loaded": True,
                "model_info": {
                    "model_path": "zai-org/GLM-OCR",
                    "device": "cuda:0",
                    "quantization": "none"
                },
                "uptime": 3600.5
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field("ok", description="服务状态")
    version: str = Field("1.0.0", description="API 版本")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "version": "1.0.0"
            }
        }

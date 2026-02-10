"""
OCR 服务抽象层
提供本地和远程两种服务实现
"""
from services.base import OCRService
from services.local_service import LocalOCRService
from services.remote_service import RemoteOCRService

__all__ = ['OCRService', 'LocalOCRService', 'RemoteOCRService']

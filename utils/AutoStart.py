"""
开机自动启动管理模块
使用 Windows 注册表 HKCU\Software\Microsoft\Windows\CurrentVersion\Run
"""
import sys
from pathlib import Path

REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "GLM-OCR"


def is_auto_start_enabled() -> bool:
    """检查是否已设置开机自启

    Returns:
        是否已启用开机自启
    """
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def set_auto_start(enable: bool) -> bool:
    """设置/取消开机自启

    Args:
        enable: True 启用开机自启，False 取消

    Returns:
        是否设置成功
    """
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, winreg.KEY_SET_VALUE)
        try:
            if enable:
                cmd = _get_startup_command()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            return True
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        print(f"设置开机自启失败: {e}")
        return False


def _get_startup_command() -> str:
    """获取启动命令（带 --minimized 参数，启动后最小化到托盘）

    Returns:
        完整的启动命令字符串
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包：直接用 EXE 路径
        exe_path = sys.executable
        return f'"{exe_path}" --minimized'
    else:
        # 开发环境：用 pythonw.exe 避免控制台窗口
        python_exe = sys.executable
        pythonw = Path(python_exe).parent / "pythonw.exe"
        if pythonw.exists():
            python_exe = str(pythonw)
        main_py = Path(__file__).parent.parent / "main.py"
        return f'"{python_exe}" "{main_py}" --minimized'

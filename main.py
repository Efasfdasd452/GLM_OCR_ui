"""
GLM-OCR 主程序入口
支持 GUI 模式和 API 服务器模式

"""
import sys
from pathlib import Path
import os
import argparse
import threading

# 修复 PyInstaller --windowed/--noconsole 模式：
# stdout/stderr 可能为 None、无 buffer 属性、或使用 GBK 编码导致 Unicode 字符输出崩溃
# 无控制台时将日志写入程序目录下的 glm_ocr.log，方便排查问题
def _fix_stdio():
    import io

    # 判断是否需要重定向（stdout 为 None 说明没有控制台）
    needs_redirect = sys.stdout is None or sys.stderr is None

    if needs_redirect:
        # 确定日志文件路径：EXE 同目录
        if getattr(sys, 'frozen', False):
            log_dir = Path(sys.executable).parent
        else:
            log_dir = Path(__file__).parent
        log_path = log_dir / "glm_ocr.log"

        try:
            log_file = open(log_path, 'a', encoding='utf-8', buffering=1)
        except OSError:
            log_file = open(os.devnull, 'w', encoding='utf-8')

        if sys.stdout is None:
            sys.stdout = log_file
        if sys.stderr is None:
            sys.stderr = log_file
    else:
        # 有控制台但编码不是 UTF-8（如 GBK），包装为 UTF-8 流
        for name in ('stdout', 'stderr'):
            stream = getattr(sys, name)
            try:
                encoding = getattr(stream, 'encoding', None) or ''
                if encoding.lower().replace('-', '') != 'utf8':
                    buf = getattr(stream, 'buffer', None)
                    if buf is not None:
                        setattr(sys, name, io.TextIOWrapper(
                            buf, encoding='utf-8', errors='replace', line_buffering=True))
            except Exception:
                pass

    if sys.stdin is None:
        sys.stdin = open(os.devnull, 'r')
_fix_stdio()
del _fix_stdio

# 启动日志标记（方便在 glm_ocr.log 中区分不同次运行）
from datetime import datetime as _dt
print(f"\n{'=' * 60}\nGLM-OCR 启动  {_dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'=' * 60}")
del _dt

os.environ["TORCH_DISABLE_TORCH_NP"] = "1"
# 减少 CUDA 显存碎片化（仅 Linux 支持 expandable_segments）
if sys.platform != "win32":
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# 判断是否为 PyInstaller 打包环境
if getattr(sys, 'frozen', False):
    # 打包后：EXE 所在目录
    BASE_DIR = Path(sys.executable).parent
else:
    # 开发环境：脚本所在目录
    BASE_DIR = Path(__file__).parent

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(BASE_DIR))

# 全局 API 服务器控制
_api_server = None
_api_thread = None


class APIServerManager:
    """API 服务器管理器，支持启动和停止"""

    def __init__(self):
        """初始化 API 服务器管理器"""
        self.server = None
        self.thread = None
        self.running = False
        self.host = None
        self.port = None
        self.port_changed = False
        self.original_port = None

    @staticmethod
    def _is_port_free(host: str, port: int) -> bool:
        """检测端口是否空闲

        Args:
            host: 主机地址
            port: 端口号

        Returns:
            端口是否空闲
        """
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.bind((host, port))
                return True
        except OSError:
            return False

    def _find_free_port(self, host: str, port: int, max_tries: int = 20) -> int:
        """从指定端口开始，找到第一个空闲端口

        Args:
            host: 主机地址
            port: 起始端口号
            max_tries: 最大尝试次数

        Returns:
            可用端口号，未找到返回 -1
        """
        for offset in range(max_tries):
            candidate = port + offset
            if candidate > 65535:
                break
            if self._is_port_free(host, candidate):
                return candidate
        return -1

    def start(self, host: str, port: int):
        """在后台线程中启动 API 服务器，自动检测端口冲突

        Args:
            host: 监听地址
            port: 监听端口

        Returns:
            是否启动成功
        """
        if self.running:
            print(f"API 服务器已在运行 ({self.host}:{self.port})")
            return True

        # 检测端口是否被占用
        original_port = port
        if not self._is_port_free(host, port):
            print(f"⚠ 端口 {port} 已被占用，正在寻找可用端口...")
            port = self._find_free_port(host, original_port + 1)
            if port == -1:
                print(f"✗ 无法找到可用端口 ({original_port}-{original_port + 20})")
                return False
            print(f"⚠ 端口已切换: {original_port} -> {port}")
            self.port_changed = True
            self.original_port = original_port
        else:
            self.port_changed = False

        self.host = host
        self.port = port

        try:
            import uvicorn
            from api.server import app

            # --windowed 模式下禁用 uvicorn 默认日志配置，避免其内部
            # 创建 StreamHandler 时因 stdout/stderr 异常而崩溃
            log_cfg = None if getattr(sys, 'frozen', False) else uvicorn.config.LOGGING_CONFIG
            config = uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level="info",
                log_config=log_cfg
            )
            self.server = uvicorn.Server(config)

            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            self.running = True
            print(f"✓ API 服务器已启动: {host}:{port}")
            return True
        except ImportError as e:
            print(f"✗ API 启动失败: 缺少依赖库 - {e}")
            return False
        except Exception as e:
            print(f"✗ API 服务器启动失败: {e}")
            return False

    def _run(self):
        """运行服务器（在线程中）"""
        try:
            self.server.run()
        except Exception as e:
            print(f"✗ API 服务器异常退出: {e}")
        finally:
            self.running = False

    def stop(self):
        """停止 API 服务器"""
        if self.server and self.running:
            self.server.should_exit = True
            self.running = False
            print("✓ API 服务器已停止")

    def is_running(self):
        """检查 API 服务器是否正在运行

        Returns:
            是否运行中
        """
        return self.running


# 全局单例
api_server_manager = APIServerManager()


def start_gui(minimized=False):
    """启动 GUI 模式

    Args:
        minimized: 是否启动后最小化到托盘（开机自启使用）
    """
    try:
        from core.Config import Config
        config = Config(str(BASE_DIR / "config.json"), base_dir=BASE_DIR)

        # 根据启动模式决定是否启动 API 服务器
        startup_mode = config.get("app.startup_mode", "ui")
        # 兼容旧版本：如果 startup_mode 未设置，回退到 api.enabled
        should_start_api = (startup_mode == "ui+api") or (
            startup_mode == "ui" and config.get("api.enabled", False)
        )
        if should_start_api:
            host = config.get("api.host", "127.0.0.1")
            port = config.get("api.port", 8000)
            print(f"启动模式: {startup_mode}，正在后台启动 API 服务器 ({host}:{port})...")
            api_server_manager.start(host, port)

        from ui.MainWindow import MainWindow
        app = MainWindow(base_dir=BASE_DIR, api_manager=api_server_manager)

        # 如果端口发生了切换，在 GUI 启动后提醒用户
        if api_server_manager.is_running() and getattr(api_server_manager, 'port_changed', False):
            app.after(1000, lambda: app.log(
                f"⚠ 端口 {api_server_manager.original_port} 已被占用，"
                f"API 服务已切换到端口 {api_server_manager.port}"
            ))

        # 开机自启时最小化到托盘
        if minimized:
            app.after(100, app.hide_window)

        app.mainloop()
    except KeyboardInterrupt:
        print("\n用户中断 (Ctrl+C)，正在退出...")
    except Exception as e:
        print(f"GUI 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按任意键退出...")
    finally:
        # 确保退出时停止 API 服务器（KeyboardInterrupt 和 Exception 均触发）
        api_server_manager.stop()


def start_api_server(host: str, port: int):
    """启动 API 服务器模式（独立运行，阻塞）

    Args:
        host: 监听地址
        port: 监听端口
    """
    try:
        import uvicorn
        from api.server import app

        print("=" * 60)
        print("GLM-OCR API 服务器模式")
        print("=" * 60)
        print(f"监听地址: {host}:{port}")
        print(f"API 文档: http://{host}:{port}/docs")
        print("=" * 60)

        log_cfg = None if getattr(sys, 'frozen', False) else uvicorn.config.LOGGING_CONFIG
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            log_config=log_cfg
        )
    except ImportError as e:
        print(f"✗ 启动失败: 缺少依赖库")
        print(f"  错误: {e}")
        print(f"\n请安装 FastAPI 和 Uvicorn:")
        print("  pip install fastapi uvicorn httpx")
        input("\n按任意键退出...")
    except Exception as e:
        print(f"✗ API 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按任意键退出...")


def start_mixed_mode(host: str, port: int):
    """启动混合模式（GUI + API 服务器）

    Args:
        host: API 监听地址
        port: API 监听端口
    """
    import time

    print("=" * 60)
    print("GLM-OCR 混合模式 (GUI + API 服务器)")
    print("=" * 60)

    # 使用 APIServerManager 在后台启动
    api_server_manager.start(host, port)

    # 等待 API 服务器启动
    print("正在启动 API 服务器...")
    time.sleep(2)

    # 启动 GUI
    print("正在启动 GUI...")
    start_gui()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="GLM-OCR - 图片文字识别工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                        # GUI 模式（默认）
  python main.py --server               # API 服务器模式
  python main.py --server --host 0.0.0.0 --port 8080  # 自定义地址
  python main.py --with-server          # GUI + API 混合模式
  python main.py --minimized            # 启动后最小化到托盘
"""
    )

    parser.add_argument(
        "--server",
        action="store_true",
        help="启动 API 服务器模式（无 GUI）"
    )

    parser.add_argument(
        "--with-server",
        action="store_true",
        help="启动混合模式（GUI + API 服务器）"
    )

    parser.add_argument(
        "--minimized",
        action="store_true",
        help="启动后最小化到托盘（开机自启使用）"
    )

    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="API 监听地址（默认从配置读取）"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="API 监听端口（默认从配置读取）"
    )

    args = parser.parse_args()

    # 从配置读取默认值
    config = None
    try:
        from core.Config import Config
        config = Config(str(BASE_DIR / "config.json"), base_dir=BASE_DIR)
        default_host = config.get("api.host", "127.0.0.1")
        default_port = config.get("api.port", 8000)
    except (ImportError, OSError, RuntimeError):
        default_host = "127.0.0.1"
        default_port = 8000

    # 使用命令行参数或配置默认值
    host = args.host if args.host is not None else default_host
    port = args.port if args.port is not None else default_port

    # 根据参数启动不同模式（命令行参数优先于配置）
    if args.with_server:
        start_mixed_mode(host, port)
    elif args.server:
        start_api_server(host, port)
    else:
        # 读取配置的启动模式（配置加载失败时用 "ui"）
        startup_mode = config.get("app.startup_mode", "ui") if config else "ui"

        if startup_mode == "api":
            start_api_server(host, port)
        else:
            # "ui" 或 "ui+api" 都走 GUI 入口
            start_gui(minimized=args.minimized)


if __name__ == "__main__":
    main()

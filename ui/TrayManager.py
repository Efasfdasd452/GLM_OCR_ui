"""
系统托盘管理模块
使用 pystray 实现 Windows 系统托盘图标和菜单
"""
import threading
from pathlib import Path
from PIL import Image

try:
    import pystray
    from pystray import MenuItem as Item
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


class TrayManager:
    """系统托盘管理器"""

    def __init__(self, app, icon_path: str = None):
        """
        初始化托盘管理器

        Args:
            app: MainWindow 实例，需要提供以下方法/属性：
                - show_window()
                - hide_window()
                - quit_app()
                - api_server_running (bool)
                - start_api_server()
                - stop_api_server()
                - config
                - lang
            icon_path: 图标文件路径
        """
        self.app = app
        self.icon = None
        self._tray_thread = None
        self.api_running = False
        self._auto_start = False

        # 读取开机自启状态
        try:
            from utils.AutoStart import is_auto_start_enabled
            self._auto_start = is_auto_start_enabled()
        except (ImportError, OSError):
            pass

        # 加载图标
        if icon_path and Path(icon_path).exists():
            self._icon_image = Image.open(icon_path)
        else:
            # 创建一个简单的默认图标
            self._icon_image = Image.new('RGB', (64, 64), color=(52, 131, 235))

    def start(self):
        """启动托盘图标（在新线程中运行）"""
        if not PYSTRAY_AVAILABLE:
            print("⚠ pystray 未安装，跳过系统托盘")
            return

        if self.icon is not None:
            return

        self.icon = pystray.Icon(
            name="GLM-OCR",
            icon=self._icon_image,
            title="GLM-OCR",
            menu=self._build_menu()
        )

        self._tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self._tray_thread.start()

    def stop(self):
        """停止托盘图标"""
        if self.icon:
            try:
                self.icon.stop()
            except (RuntimeError, OSError):
                pass
            self.icon = None

    def update_menu(self):
        """更新托盘菜单（刷新 API 状态等）"""
        if self.icon:
            self.icon.menu = self._build_menu()
            self.icon.update_menu()

    def set_api_status(self, running: bool, port: int = None):
        """更新 API 服务状态

        Args:
            running: 是否正在运行
            port: API 服务端口号
        """
        self.api_running = running
        self._api_port = port
        self.update_menu()

    def _build_menu(self):
        """构建右键菜单

        Returns:
            pystray.Menu 菜单对象
        """
        api_status_text = self._get_api_status_text()
        auto_start_text = "✓ 开机自动启动" if self._auto_start else "  开机自动启动"

        return pystray.Menu(
            Item("显示主窗口", self._on_show, default=True),
            Item("隐藏主窗口", self._on_hide),
            pystray.Menu.SEPARATOR,
            Item(api_status_text, None, enabled=False),
            Item(
                "停止 API 服务" if self.api_running else "启动 API 服务",
                self._on_toggle_api
            ),
            pystray.Menu.SEPARATOR,
            Item(auto_start_text, self._on_toggle_auto_start),
            pystray.Menu.SEPARATOR,
            Item("退出", self._on_quit),
        )

    def _get_api_status_text(self):
        """获取 API 状态文本

        Returns:
            API 状态描述字符串
        """
        if self.api_running:
            port = getattr(self, '_api_port', None)
            if port:
                return f"API 服务运行中 (:{port})"
            return "API 服务运行中"
        return "API 服务已停止"

    def _on_show(self):
        """显示主窗口"""
        self.app.after(0, self.app.show_window)

    def _on_hide(self):
        """隐藏主窗口"""
        self.app.after(0, self.app.hide_window)

    def _on_toggle_api(self):
        """启动/停止 API 服务"""
        if self.api_running:
            self.app.after(0, self.app.stop_api_server)
        else:
            self.app.after(0, self.app.start_api_server)

    def _on_toggle_auto_start(self):
        """切换开机自启"""
        try:
            from utils.AutoStart import set_auto_start
            new_state = not self._auto_start
            success = set_auto_start(new_state)
            if success:
                self._auto_start = new_state
                self.update_menu()
                # 同步配置
                self.app.after(0, lambda: self._sync_auto_start_config(new_state))
        except Exception as e:
            print(f"切换开机自启失败: {e}")

    def _sync_auto_start_config(self, enabled: bool):
        """同步开机自启配置到 config

        Args:
            enabled: 是否启用开机自启
        """
        self.app.config.set("ui.auto_start", enabled)
        self.app.config.save_config()
        self.app.log(f"开机自动启动已{'启用' if enabled else '禁用'}")

    def set_auto_start_status(self, enabled: bool):
        """外部更新开机自启状态（如设置页面修改后同步到托盘）

        Args:
            enabled: 是否启用开机自启
        """
        self._auto_start = enabled
        self.update_menu()

    def _on_quit(self):
        """退出程序"""
        self.app.after(0, self.app.quit_app)

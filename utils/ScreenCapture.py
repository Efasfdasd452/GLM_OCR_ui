"""
截图工具模块
全屏暗色遮罩 → 框选区域 → 确认/取消
"""
import ctypes
import io
import tkinter as tk
from PIL import Image, ImageGrab, ImageTk
from pathlib import Path
from datetime import datetime


def _copy_image_to_clipboard(image: Image.Image):
    """使用 ctypes 将 PIL Image 复制到 Windows 剪贴板（无需 pywin32）"""
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    bmp_data = output.getvalue()[14:]  # 跳过 14 字节 BMP 文件头
    output.close()

    cf_dib = 8
    gmem_moveable = 0x0002

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # 64 位系统必须显式声明参数和返回类型，否则指针会被截断
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

    if not user32.OpenClipboard(0):
        raise OSError("OpenClipboard failed")

    user32.EmptyClipboard()

    h_mem = kernel32.GlobalAlloc(gmem_moveable, len(bmp_data))
    if not h_mem:
        user32.CloseClipboard()
        raise OSError("GlobalAlloc failed")

    p_mem = kernel32.GlobalLock(h_mem)
    ctypes.memmove(p_mem, bmp_data, len(bmp_data))
    kernel32.GlobalUnlock(h_mem)
    user32.SetClipboardData(cf_dib, h_mem)
    user32.CloseClipboard()


class ScreenCapture:
    """屏幕截图工具：全屏遮罩 + 框选 + 确认/取消"""

    def __init__(self, parent, save_dir="./screenshots", callback=None, lang_manager=None):
        """
        Args:
            parent:   父窗口 (tk.Tk / ctk.CTk)
            save_dir: 截图保存目录
            callback: 完成回调 callback(image, save_path)
                      取消时 image=None, save_path=None
            lang_manager: 语言管理器
        """
        self.parent = parent
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.callback = callback
        self.lang_manager = lang_manager

        # 内部状态
        self._screenshot = None          # 原始截图（物理分辨率）
        self._display_shot = None        # 用于显示的截图（逻辑分辨率）
        self._dark_display = None        # 暗化版
        self._scale_x = 1.0
        self._scale_y = 1.0

        self._overlay = None
        self._canvas = None
        self._tk_dark = None
        self._tk_bright = None

        self._start_x = 0
        self._start_y = 0
        self._end_x = 0
        self._end_y = 0
        self._has_selection = False
        self._selecting = False
        self._btn_frame = None

    # ==================== 公开接口 ====================

    def start(self):
        """开始截图流程：隐藏父窗口 → 截屏 → 显示遮罩"""
        self.parent.withdraw()
        # 等窗口真正隐藏后再截屏，避免把自身截进去
        self.parent.after(350, self._capture_and_show)

    # ==================== 截屏 & 遮罩 ====================

    def _capture_and_show(self):
        """截取全屏并弹出遮罩窗口"""
        # 截取全屏（物理分辨率）
        self._screenshot = ImageGrab.grab()
        phys_w, phys_h = self._screenshot.size

        # 使用物理分辨率，不缩小
        screen_w = phys_w
        screen_h = phys_h

        # 不需要缩放，直接使用 1:1 比例
        self._scale_x = 1.0
        self._scale_y = 1.0

        # 直接使用原始截图，不缩放
        self._display_shot = self._screenshot.copy()

        # 暗化版本
        dark = self._display_shot.copy().convert("RGBA")
        mask = Image.new("RGBA", (screen_w, screen_h), (0, 0, 0, 120))
        dark = Image.alpha_composite(dark, mask).convert("RGB")
        self._dark_display = dark

        # ---------- 创建全屏无边框窗口 ----------
        self._overlay = tk.Toplevel(self.parent)
        self._overlay.overrideredirect(True)
        self._overlay.geometry(f"{screen_w}x{screen_h}+0+0")
        self._overlay.attributes("-topmost", True)
        self._overlay.configure(cursor="cross")

        # 画布
        self._canvas = tk.Canvas(
            self._overlay,
            width=screen_w, height=screen_h,
            highlightthickness=0, bd=0,
        )
        self._canvas.pack()

        # 显示暗化截图做背景
        self._tk_dark = ImageTk.PhotoImage(self._dark_display)
        self._canvas.create_image(0, 0, anchor=tk.NW, image=self._tk_dark)

        # 顶部提示
        hint_text = "拖拽鼠标选择截图区域  |  按 ESC 取消  |  提示: Ctrl+Shift+S 可快速截图"
        if self.lang_manager:
            hint_text = self.lang_manager.get("screenshot_hint")

        self._canvas.create_text(
            screen_w // 2, 30,
            text=hint_text,
            fill="white",
            font=("Microsoft YaHei", 13, "bold"),
        )

        # 事件绑定
        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._overlay.bind("<Escape>", lambda e: self._cancel())
        self._overlay.bind("<Return>", lambda e: self._enter_confirm())

    # ==================== 鼠标事件 ====================

    def _clear_drawing(self):
        """清除画布上的选区、按钮等"""
        for tag in ("bright", "rect", "size_label", "btn_win"):
            self._canvas.delete(tag)
        if self._btn_frame:
            self._btn_frame.destroy()
            self._btn_frame = None
        self._has_selection = False

    def _on_press(self, event):
        self._clear_drawing()
        self._start_x = event.x
        self._start_y = event.y
        self._selecting = True
        self._overlay.configure(cursor="cross")

    def _on_drag(self, event):
        if not self._selecting:
            return

        self._end_x = event.x
        self._end_y = event.y

        # 每帧刷新选区
        self._canvas.delete("bright")
        self._canvas.delete("rect")
        self._canvas.delete("size_label")

        x1 = min(self._start_x, self._end_x)
        y1 = min(self._start_y, self._end_y)
        x2 = max(self._start_x, self._end_x)
        y2 = max(self._start_y, self._end_y)

        if x2 - x1 < 3 or y2 - y1 < 3:
            return

        # 亮区（从原图裁剪，让选中区域"透亮"）
        bright = self._display_shot.crop((x1, y1, x2, y2))
        self._tk_bright = ImageTk.PhotoImage(bright)
        self._canvas.create_image(
            x1, y1, anchor=tk.NW, image=self._tk_bright, tags="bright"
        )

        # 选区边框
        self._canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="#00aaff", width=2, tags="rect",
        )

        # 尺寸标注（显示物理像素尺寸）
        pw = int((x2 - x1) * self._scale_x)
        ph = int((y2 - y1) * self._scale_y)
        self._canvas.create_text(
            x1 + 5, y1 - 8,
            text=f"{pw} × {ph}",
            fill="#00aaff", anchor=tk.SW,
            font=("Microsoft YaHei", 10),
            tags="size_label",
        )

    def _on_release(self, event):
        if not self._selecting:
            return
        self._selecting = False
        self._end_x = event.x
        self._end_y = event.y

        x1 = min(self._start_x, self._end_x)
        y1 = min(self._start_y, self._end_y)
        x2 = max(self._start_x, self._end_x)
        y2 = max(self._start_y, self._end_y)

        # 选区太小，忽略
        if x2 - x1 < 5 or y2 - y1 < 5:
            return

        self._has_selection = True
        self._sel = (x1, y1, x2, y2)
        self._show_buttons(x1, y1, x2, y2)

    # ==================== 按钮 ====================

    def _show_buttons(self, x1, y1, x2, y2):
        """在选区下方显示确认/取消按钮"""
        self._overlay.configure(cursor="arrow")

        btn_x = (x1 + x2) // 2
        btn_y = y2 + 8

        # 如果下方空间不够，就放到选区上方
        screen_h = self._overlay.winfo_height()
        if btn_y + 50 > screen_h:
            btn_y = y1 - 48

        self._btn_frame = tk.Frame(self._canvas, bg="#2b2b2b", bd=0)

        # 获取翻译文本
        confirm_text = f" ✓ {self.lang_manager.get('confirm')} " if self.lang_manager else " ✓ 确认 "
        cancel_text = f" ✗ {self.lang_manager.get('cancel')} " if self.lang_manager else " ✗ 取消 "

        tk.Button(
            self._btn_frame, text=confirm_text,
            command=lambda: self._confirm(x1, y1, x2, y2),
            bg="#4CAF50", fg="white", activebackground="#45a049",
            font=("Microsoft YaHei", 10, "bold"),
            relief="flat", padx=12, pady=4, cursor="hand2",
        ).pack(side=tk.LEFT, padx=(4, 8), pady=4)

        tk.Button(
            self._btn_frame, text=cancel_text,
            command=self._cancel,
            bg="#f44336", fg="white", activebackground="#d32f2f",
            font=("Microsoft YaHei", 10, "bold"),
            relief="flat", padx=12, pady=4, cursor="hand2",
        ).pack(side=tk.LEFT, padx=(8, 4), pady=4)

        self._canvas.create_window(
            btn_x, btn_y,
            window=self._btn_frame, anchor=tk.N, tags="btn_win",
        )

    # ==================== 确认 / 取消 ====================

    def _enter_confirm(self):
        """按 Enter 确认当前选区"""
        if self._has_selection:
            self._confirm(*self._sel)

    def _confirm(self, x1, y1, x2, y2):
        """确认截图：裁剪 → 保存文件 → 复制到剪贴板"""
        # 用物理坐标从原始截图裁剪，保证清晰度
        px1 = int(x1 * self._scale_x)
        py1 = int(y1 * self._scale_y)
        px2 = int(x2 * self._scale_x)
        py2 = int(y2 * self._scale_y)
        cropped = self._screenshot.crop((px1, py1, px2, py2))

        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = self.save_dir / f"screenshot_{timestamp}.png"
        cropped.save(str(save_path))

        # 复制到剪贴板
        try:
            _copy_image_to_clipboard(cropped)
        except Exception as e:
            print(f"复制到剪贴板失败: {e}")

        # 关闭遮罩、恢复父窗口
        self._cleanup()

        if self.callback:
            self.callback(cropped, str(save_path))

    def _cancel(self):
        """取消截图"""
        self._cleanup()
        if self.callback:
            self.callback(None, None)

    def _cleanup(self):
        """销毁遮罩、恢复父窗口、释放资源"""
        if self._overlay:
            self._overlay.destroy()
            self._overlay = None
        self.parent.deiconify()

        self._screenshot = None
        self._display_shot = None
        self._dark_display = None
        self._tk_dark = None
        self._tk_bright = None

"""
主界面模块
使用 CustomTkinter 构建现代化 UI
"""
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import httpx
import customtkinter as ctk

from core.Config import Config
from core.OCREngine import OCREngine
from services.local_service import LocalOCRService
from services.remote_service import RemoteOCRService
from ui.LanguageManager import LanguageManager
from ui.ToastNotification import ToastNotification
from ui.TrayManager import TrayManager
from utils.ClipboardUtils import ClipboardUtils
from utils.FileUtils import FileUtils
from utils.PDFUtils import PDFUtils
from utils.QRCodeUtils import QRCodeUtils
from utils.ScreenCapture import ScreenCapture


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self, base_dir=None, api_manager=None):
        """初始化主窗口

        Args:
            base_dir: 程序基础目录，默认自动检测
            api_manager: API 服务器管理器实例
        """
        super().__init__()

        # 基础目录（兼容 PyInstaller 打包）
        if base_dir is None:
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)

        # 配置
        self.config = Config(str(self.base_dir / "config.json"), base_dir=self.base_dir)

        # 语言管理器
        self.lang = LanguageManager(self.config.get("ui.language", "简体中文"))

        # OCR 引擎和服务
        self.ocr_engine = None
        self.ocr_service = None
        self.model_loaded = False
        self._using_local_api = False  # 是否通过本地 API 调用（避免重复加载模型）
        self._api_poll_id = None
        self._api_poll_errors = 0  # 轮询连续失败次数

        # API 服务器管理器
        self.api_manager = api_manager

        # 字体设置
        self.font_family = self.config.get("ui.font_family", "Microsoft YaHei UI")
        self.font_size = self.config.get("ui.font_size", 12)

        # 动态 Token 设置
        self.current_tokens = self.config.get("model.max_new_tokens", 2048)

        # UI 初始化
        self.setup_window()
        self.create_widgets()

        # 识别状态
        self._recognizing = False
        self._loading_anim_id = None
        self._model_loading = False  # 防止并发加载模型

        # 绑定快捷键
        self.bind_shortcuts()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # 初始化系统托盘
        icon_path = self.base_dir / "icon.ico"
        self.tray_manager = TrayManager(self, str(icon_path))
        self.tray_manager.start()

        # 同步 API 状态到托盘
        if self.api_manager and self.api_manager.is_running():
            self.tray_manager.set_api_status(True, self.api_manager.port)
            # 本地 API 运行中，通过 API 调用避免重复加载模型
            self._connect_local_api()

    def setup_window(self):
        """设置窗口"""
        self.title(self.lang.get("window_title"))

        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 窗口尺寸
        window_width = 1200
        window_height = 800

        # 居中显示
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 设置主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _font(self, size_offset=0, bold=False):
        """返回统一字体元组

        Args:
            size_offset: 相对于基础字体大小的偏移量
            bold: 是否加粗

        Returns:
            字体元组 (family, size) 或 (family, size, "bold")
        """
        size = self.font_size + size_offset
        if bold:
            return self.font_family, size, "bold"
        return self.font_family, size

    def apply_font_settings(self):
        """应用字体设置到所有 UI 组件"""
        # 侧边栏
        self.logo_label.configure(font=self._font(12, bold=True))
        for btn in (self.btn_screenshot, self.btn_clipboard, self.btn_batch,
                     self.btn_folder, self.btn_pdf_ocr, self.btn_settings,
                     self.btn_load_model):
            btn.configure(font=self._font())
        self.model_status_label.configure(font=self._font())

        # 控制栏
        self.prompt_label.configure(font=self._font())
        self.prompt_type.configure(font=self._font())
        self.token_label.configure(font=self._font())
        self.token_entry.configure(font=self._font())

        # 单图 OCR
        self.image_label.configure(font=self._font())
        self.btn_select_image.configure(font=self._font())
        self.result_label.configure(font=self._font())
        self.btn_quick_ocr.configure(font=self._font(1))
        self.btn_copy_result.configure(font=self._font(1))
        self.result_text.configure(font=self._font())

        # 批量 OCR
        self.btn_add_files.configure(font=self._font())
        self.btn_add_folder.configure(font=self._font())
        self.recursive_checkbox.configure(font=self._font())
        self.btn_clear_list.configure(font=self._font())
        self.btn_start_batch.configure(font=self._font())
        self.file_list_label.configure(font=self._font())
        self.file_listbox.configure(font=self._font())
        self.progress_label.configure(font=self._font())

        # PDF OCR
        self.btn_select_pdf.configure(font=self._font())
        self.pdf_path_label.configure(font=self._font())
        self.btn_save_pdf_result.configure(font=self._font())
        self.pdf_progress_label.configure(font=self._font())
        self.pdf_result_text.configure(font=self._font())

        # 日志
        self.log_text.configure(font=self._font())
        self.btn_clear_log.configure(font=self._font())

    def update_ui_language(self):
        """更新所有界面元素的语言"""
        # 更新窗口标题
        self.title(self.lang.get("window_title"))

        # 更新侧边栏按钮
        self.btn_screenshot.configure(text=self.lang.get("screenshot_ocr"))
        self.btn_clipboard.configure(text=self.lang.get("clipboard_ocr"))
        self.btn_batch.configure(text=self.lang.get("batch_ocr"))
        self.btn_folder.configure(text=self.lang.get("folder_ocr"))
        self.btn_pdf_ocr.configure(text=self.lang.get("document_ocr"))
        self.btn_settings.configure(text=self.lang.get("settings"))

        # 更新模型状态
        if self.model_loaded:
            self.model_status_label.configure(text=self.lang.get("model_loaded"))
            self.btn_load_model.configure(text=self.lang.get("unload_model"))
        else:
            self.model_status_label.configure(text=self.lang.get("model_not_loaded"))
            self.btn_load_model.configure(text=self.lang.get("load_model"))

        # 更新控制栏
        self.prompt_label.configure(text=self.lang.get("recognition_type"))
        self.token_label.configure(text=self.lang.get("token_count"))

        # 更新识别类型选项
        self.prompt_type.configure(values=[
            self.lang.get("text_recognition"),
            self.lang.get("document_parsing"),
            self.lang.get("table_recognition"),
            self.lang.get("formula_recognition"),
            self.lang.get("qrcode_recognition")
        ])

        # 更新快速识别和复制结果按钮
        self.btn_quick_ocr.configure(text=self.lang.get("quick_recognition"))
        self.btn_copy_result.configure(text=self.lang.get("copy_result"))

        # 更新单图OCR标签页
        self.image_label.configure(text=self.lang.get("image_preview_hint"))
        self.btn_select_image.configure(text=self.lang.get("select_image"))
        self.result_label.configure(text=self.lang.get("recognition_result"))

        # 更新选项卡标题（需要重新创建，CustomTkinter 不支持直接修改）
        # 暂时跳过，因为需要重建整个 tabview

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 创建侧边栏
        self.create_sidebar()

        # 创建主内容区
        self.create_main_content()

        # 应用字体设置
        self.apply_font_settings()

    def create_sidebar(self):
        """创建侧边栏"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(7, weight=1)

        # Logo / 标题
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="GLM-OCR",
            font=self._font(12, bold=True)
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 功能按钮
        self.btn_screenshot = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get("screenshot_ocr"),
            command=self.screenshot_ocr,
            height=40
        )
        self.btn_screenshot.grid(row=1, column=0, padx=20, pady=10)

        self.btn_clipboard = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get("clipboard_ocr"),
            command=self.clipboard_ocr,
            height=40
        )
        self.btn_clipboard.grid(row=2, column=0, padx=20, pady=10)

        self.btn_batch = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get("batch_ocr"),
            command=self.batch_ocr,
            height=40
        )
        self.btn_batch.grid(row=3, column=0, padx=20, pady=10)

        self.btn_folder = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get("folder_ocr"),
            command=self.folder_ocr,
            height=40
        )
        self.btn_folder.grid(row=4, column=0, padx=20, pady=10)

        self.btn_pdf_ocr = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get("document_ocr"),
            command=self.pdf_ocr,
            height=40
        )
        self.btn_pdf_ocr.grid(row=5, column=0, padx=20, pady=10)

        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get("settings"),
            command=self.open_settings,
            height=40
        )
        self.btn_settings.grid(row=6, column=0, padx=20, pady=10)

        # 模型状态
        self.model_status_label = ctk.CTkLabel(
            self.sidebar,
            text=self.lang.get("model_not_loaded"),
            text_color="red"
        )
        self.model_status_label.grid(row=8, column=0, padx=20, pady=(10, 20))

        # 加载/卸载模型按钮
        self.btn_load_model = ctk.CTkButton(
            self.sidebar,
            text=self.lang.get("load_model"),
            command=self.toggle_model,
            fg_color="green",
            height=40
        )
        self.btn_load_model.grid(row=9, column=0, padx=20, pady=(10, 20))

    def create_main_content(self):
        """创建主内容区"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # 顶部控制栏
        self.create_control_bar()

        # 创建选项卡
        self.create_tabs()

    def create_control_bar(self):
        """创建控制栏"""
        self.control_frame = ctk.CTkFrame(self.main_frame, height=60)
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.control_frame.grid_columnconfigure(1, weight=1)

        # 提示词类型选择
        self.prompt_label = ctk.CTkLabel(self.control_frame, text=self.lang.get("recognition_type"))
        self.prompt_label.grid(row=0, column=0, padx=(10, 5), pady=10)

        recognition_types = [
            self.lang.get("text_recognition"),
            self.lang.get("document_parsing"),
            self.lang.get("table_recognition"),
            self.lang.get("formula_recognition"),
            self.lang.get("qrcode_recognition")
        ]
        self.prompt_type = ctk.CTkOptionMenu(
            self.control_frame,
            values=recognition_types,
            font=self._font(),
            command=self.on_prompt_change
        )
        self.prompt_type.set(recognition_types[0])  # 设置默认值
        self.prompt_type.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Token 调整控件
        # Token 标签
        self.token_label = ctk.CTkLabel(self.control_frame, text=self.lang.get("token_count"))
        self.token_label.grid(row=0, column=2, padx=(20, 5), pady=10)

        # Token 滑块
        max_limit = self.config.get("model.max_new_tokens_limit", 8192)
        self.token_slider = ctk.CTkSlider(
            self.control_frame,
            from_=512,
            to=max_limit,
            number_of_steps=None,
            width=200,
            command=self.on_token_change
        )
        self.token_slider.set(self.current_tokens)
        self.token_slider.grid(row=0, column=3, padx=5, pady=10)

        # Token 数值显示/输入框
        self.token_value_var = ctk.StringVar(value=str(self.current_tokens))
        self.token_entry = ctk.CTkEntry(
            self.control_frame,
            textvariable=self.token_value_var,
            width=80,
            justify="center"
        )
        self.token_entry.grid(row=0, column=4, padx=5, pady=10)
        self.token_entry.bind("<Return>", self.on_token_entry_change)
        self.token_entry.bind("<FocusOut>", self.on_token_entry_change)

    def create_tabs(self):
        """创建选项卡"""
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # 单图 OCR 标签页
        self.tab_single = self.tabview.add(self.lang.get("tab_single_ocr"))
        self.create_single_tab()

        # 批量 OCR 标签页
        self.tab_batch = self.tabview.add(self.lang.get("tab_batch_ocr"))
        self.create_batch_tab()

        # PDF OCR 标签页
        self.tab_pdf = self.tabview.add(self.lang.get("tab_pdf_ocr"))
        self.create_pdf_tab()

        # 二维码生成标签页
        self.tab_qrgen = self.tabview.add(self.lang.get("tab_qrcode_gen"))
        self.create_qrgen_tab()

        # 日志标签页
        self.tab_log = self.tabview.add(self.lang.get("tab_log"))
        self.create_log_tab()

    def create_single_tab(self):
        """创建单图OCR标签页"""
        self.tab_single.grid_columnconfigure(0, weight=1)
        self.tab_single.grid_rowconfigure(1, weight=1)

        # 图片预览区
        self.image_frame = ctk.CTkFrame(self.tab_single)
        self.image_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.image_frame.grid_columnconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text=self.lang.get("image_preview_hint"),
            height=200,
            fg_color="gray85"
        )
        self.image_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # 文件选择按钮
        self.btn_select_image = ctk.CTkButton(
            self.image_frame,
            text=self.lang.get("select_image"),
            command=self.select_image
        )
        self.btn_select_image.grid(row=1, column=0, padx=10, pady=(0, 10))

        # 结果显示区标题和按钮
        result_header_frame = ctk.CTkFrame(self.tab_single, fg_color="transparent")
        result_header_frame.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="ew")
        result_header_frame.grid_columnconfigure(0, weight=1)

        self.result_label = ctk.CTkLabel(result_header_frame, text=self.lang.get("recognition_result"), anchor="w")
        self.result_label.grid(row=0, column=0, sticky="w")

        # 快速识别按钮
        self.btn_quick_ocr = ctk.CTkButton(
            result_header_frame,
            text=self.lang.get("quick_recognition"),
            command=self.quick_ocr,
            width=160,
            height=35,
            font=self._font(1)
        )
        self.btn_quick_ocr.grid(row=0, column=1, padx=5)

        # 复制结果按钮
        self.btn_copy_result = ctk.CTkButton(
            result_header_frame,
            text=self.lang.get("copy_result"),
            command=self.copy_result,
            width=120,
            height=35,
            font=self._font(1),
            fg_color="#1f6aa5"
        )
        self.btn_copy_result.grid(row=0, column=2, padx=5)

        # 结果文本框
        self.result_text = ctk.CTkTextbox(self.tab_single, height=300)
        self.result_text.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.tab_single.grid_rowconfigure(3, weight=1)

    def create_batch_tab(self):
        """创建批量OCR标签页"""
        self.tab_batch.grid_columnconfigure(0, weight=1)
        self.tab_batch.grid_rowconfigure(2, weight=1)

        # 控制区
        self.batch_control_frame = ctk.CTkFrame(self.tab_batch)
        self.batch_control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.btn_add_files = ctk.CTkButton(
            self.batch_control_frame,
            text="添加文件",
            command=self.add_batch_files
        )
        self.btn_add_files.grid(row=0, column=0, padx=5, pady=5)

        self.btn_add_folder = ctk.CTkButton(
            self.batch_control_frame,
            text="添加文件夹",
            command=self.add_batch_folder
        )
        self.btn_add_folder.grid(row=0, column=1, padx=5, pady=5)

        self.recursive_var = ctk.BooleanVar(value=False)
        self.recursive_checkbox = ctk.CTkCheckBox(
            self.batch_control_frame,
            text="递归子目录",
            variable=self.recursive_var
        )
        self.recursive_checkbox.grid(row=0, column=2, padx=5, pady=5)

        self.btn_clear_list = ctk.CTkButton(
            self.batch_control_frame,
            text="清空列表",
            command=self.clear_batch_list
        )
        self.btn_clear_list.grid(row=0, column=3, padx=5, pady=5)

        self.btn_start_batch = ctk.CTkButton(
            self.batch_control_frame,
            text="开始批量识别",
            command=self.start_batch_ocr,
            fg_color="green"
        )
        self.btn_start_batch.grid(row=0, column=4, padx=5, pady=5)

        # 文件列表
        self.file_list_label = ctk.CTkLabel(self.tab_batch, text="待处理文件:")
        self.file_list_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")

        self.file_listbox = ctk.CTkTextbox(self.tab_batch, height=200)
        self.file_listbox.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # 进度条
        self.progress_label = ctk.CTkLabel(self.tab_batch, text="进度: 0/0")
        self.progress_label.grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self.tab_batch)
        self.progress_bar.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.progress_bar.set(0)

        # 批量文件列表
        self.batch_files = []

    def create_pdf_tab(self):
        """创建 PDF OCR 标签页"""
        self.tab_pdf.grid_columnconfigure(0, weight=1)
        self.tab_pdf.grid_rowconfigure(3, weight=1)

        # 控制区
        pdf_control_frame = ctk.CTkFrame(self.tab_pdf)
        pdf_control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        pdf_control_frame.grid_columnconfigure(1, weight=1)

        self.btn_select_pdf = ctk.CTkButton(
            pdf_control_frame,
            text="选择 PDF 文件",
            command=self.pdf_ocr,
            width=140
        )
        self.btn_select_pdf.grid(row=0, column=0, padx=(10, 5), pady=10)

        self.pdf_path_label = ctk.CTkLabel(
            pdf_control_frame,
            text="未选择文件",
            anchor="w"
        )
        self.pdf_path_label.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.btn_save_pdf_result = ctk.CTkButton(
            pdf_control_frame,
            text="保存结果",
            command=self.save_pdf_result,
            width=100
        )
        self.btn_save_pdf_result.grid(row=0, column=2, padx=(5, 10), pady=10)

        # 进度区
        self.pdf_progress_label = ctk.CTkLabel(self.tab_pdf, text="进度: 0/0")
        self.pdf_progress_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

        self.pdf_progress_bar = ctk.CTkProgressBar(self.tab_pdf)
        self.pdf_progress_bar.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.pdf_progress_bar.set(0)

        # 结果显示区
        self.pdf_result_text = ctk.CTkTextbox(self.tab_pdf)
        self.pdf_result_text.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # 保存当前 PDF 结果
        self._pdf_result_content = ""

    def create_qrgen_tab(self):
        """创建二维码生成标签页"""
        self.tab_qrgen.grid_columnconfigure(0, weight=1)
        self.tab_qrgen.grid_columnconfigure(1, weight=0)
        self.tab_qrgen.grid_rowconfigure(1, weight=1)

        # 输入区
        input_frame = ctk.CTkFrame(self.tab_qrgen)
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="输入内容:").grid(row=0, column=0, padx=(10, 5), pady=10)

        self.qrgen_entry = ctk.CTkEntry(input_frame, placeholder_text="输入文本或链接...")
        self.qrgen_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.qrgen_entry.bind("<Return>", lambda e: self.generate_qrcode())

        self.btn_generate_qr = ctk.CTkButton(
            input_frame,
            text="生成二维码",
            command=self.generate_qrcode,
            width=120
        )
        self.btn_generate_qr.grid(row=0, column=2, padx=(5, 10), pady=10)

        self.btn_save_qr = ctk.CTkButton(
            input_frame,
            text="保存图片",
            command=self.save_qrcode,
            width=100
        )
        self.btn_save_qr.grid(row=0, column=3, padx=(5, 10), pady=10)

        # 二维码预览区
        self.qr_preview_label = ctk.CTkLabel(
            self.tab_qrgen,
            text="二维码将显示在此处",
            width=400,
            height=400,
            fg_color="gray85"
        )
        self.qr_preview_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10))

        # 保存生成的二维码 PIL Image
        self._qr_image = None

    def generate_qrcode(self):
        """根据输入文本生成二维码"""
        text = self.qrgen_entry.get().strip()
        if not text:
            messagebox.showwarning("警告", "请输入要生成二维码的内容")
            return

        try:
            import qrcode

            qr = qrcode.QRCode(box_size=10, border=4)
            qr.add_data(text)
            qr.make(fit=True)
            self._qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            # 缩放到预览尺寸
            preview = self._qr_image.copy()
            preview.thumbnail((380, 380))
            w, h = preview.size

            ctk_image = ctk.CTkImage(light_image=preview, dark_image=preview, size=(w, h))
            self.qr_preview_label.configure(image=ctk_image, text="")
            self.qr_preview_label._ctk_image = ctk_image  # 防止被 GC 回收

            self.log(f"✓ 二维码已生成: {text[:50]}{'...' if len(text) > 50 else ''}")
        except ImportError:
            messagebox.showerror("错误", "请安装 qrcode 库: pip install qrcode")
        except Exception as e:
            self.log(f"✗ 二维码生成失败: {e}")
            messagebox.showerror("错误", f"生成失败: {e}")

    def save_qrcode(self):
        """保存生成的二维码图片"""
        if self._qr_image is None:
            messagebox.showwarning("警告", "请先生成二维码")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存二维码",
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("JPEG 图片", "*.jpg")]
        )

        if file_path:
            self._qr_image.save(file_path)
            self.log(f"✓ 二维码已保存: {file_path}")

    def create_log_tab(self):
        """创建日志标签页"""
        self.tab_log.grid_columnconfigure(0, weight=1)
        self.tab_log.grid_rowconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(self.tab_log)
        self.log_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 清空日志按钮
        self.btn_clear_log = ctk.CTkButton(
            self.tab_log,
            text="清空日志",
            command=self.clear_log
        )
        self.btn_clear_log.grid(row=1, column=0, padx=10, pady=(0, 10))

    def bind_shortcuts(self):
        """绑定快捷键"""
        self.bind("<Control-q>", lambda e: self.quick_ocr())
        self.bind("<Control-v>", lambda e: self.clipboard_ocr())
        self.bind("<Control-o>", lambda e: self.select_image())
        self.bind("<Control-Shift-s>", lambda e: self.screenshot_ocr())
        self.bind("<Control-Shift-S>", lambda e: self.screenshot_ocr())

    # ==================== 加载动画 ====================

    def _start_loading_animation(self):
        """开始识别加载动画，清空结果区并禁用按钮防止重复操作。"""
        self._recognizing = True
        self._loading_dots = 0
        # 清空结果区
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        # 禁用按钮防止重复点击
        self.btn_quick_ocr.configure(state="disabled", text="识别中...")
        self.btn_select_image.configure(state="disabled")
        # 启动动画
        self._animate_loading()

    def _animate_loading(self):
        """更新加载动画帧"""
        if not self._recognizing:
            return
        self._loading_dots = (self._loading_dots % 6) + 1
        dots = "." * self._loading_dots
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame = spinner[self._loading_dots % len(spinner)]
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", f"\n\n\t{frame}  正在识别中{dots}\n\n\t请稍候...")
        self._loading_anim_id = self.after(300, self._animate_loading)

    def _stop_loading_animation(self):
        """停止加载动画，恢复按钮"""
        self._recognizing = False
        if self._loading_anim_id:
            self.after_cancel(self._loading_anim_id)
            self._loading_anim_id = None
        # 恢复按钮
        self.btn_quick_ocr.configure(
            state="normal",
            text=self.lang.get("quick_recognition")
        )
        self.btn_select_image.configure(state="normal")

    # ==================== 窗口和托盘方法 ====================

    def on_close(self):
        """窗口关闭事件处理"""
        choice = self.config.get("ui.minimize_to_tray", None)

        if choice is None:
            # 首次关闭，弹出确认对话框
            self._show_close_confirm_dialog()
        elif choice is True:
            # 已设置最小化到托盘
            self.hide_window()
        else:
            # 已设置直接退出
            self.quit_app()

    def _show_close_confirm_dialog(self):
        """显示关闭确认对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("关闭确认")
        dialog.geometry("420x230")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.focus_force()

        # 居中显示
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 230) // 2
        dialog.geometry(f"+{x}+{y}")

        # 标题
        ctk.CTkLabel(
            dialog,
            text="关闭窗口",
            font=("Microsoft YaHei UI", 18, "bold")
        ).pack(pady=(20, 10))

        # 说明
        ctk.CTkLabel(
            dialog,
            text="请选择关闭方式：",
            font=("Microsoft YaHei UI", 13)
        ).pack(pady=(0, 10))

        # 记住选择复选框
        remember_var = ctk.BooleanVar(dialog, value=False)
        ctk.CTkCheckBox(
            dialog,
            text="记住我的选择",
            variable=remember_var
        ).pack(pady=(0, 15))

        # 按钮区
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))

        def minimize_to_tray():
            if remember_var.get():
                self.config.set("ui.minimize_to_tray", True)
                self.config.save_config()
            dialog.destroy()
            self.hide_window()

        def exit_app():
            if remember_var.get():
                self.config.set("ui.minimize_to_tray", False)
                self.config.save_config()
            dialog.destroy()
            self.quit_app()

        ctk.CTkButton(
            btn_frame,
            text="最小化到托盘",
            command=minimize_to_tray,
            width=140,
            height=38,
            fg_color="#1f6aa5"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="退出程序",
            command=exit_app,
            width=140,
            height=38,
            fg_color="#d32f2f"
        ).pack(side="left", padx=10)

        # ESC 关闭对话框（不退出）
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def show_window(self):
        """显示主窗口"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide_window(self):
        """隐藏主窗口到托盘"""
        self.withdraw()

    def quit_app(self):
        """完全退出程序"""
        # 取消 API 状态轮询
        if self._api_poll_id:
            self.after_cancel(self._api_poll_id)
            self._api_poll_id = None
        # 关闭本地 API 远程服务客户端
        if self._using_local_api and self.ocr_service and isinstance(self.ocr_service, RemoteOCRService):
            self.ocr_service.close()
        # 停止 API 服务器
        if self.api_manager:
            self.api_manager.stop()
        # 停止托盘图标
        if hasattr(self, 'tray_manager'):
            self.tray_manager.stop()
        # 卸载模型（仅本地模式需要）
        if not self._using_local_api and self.ocr_engine:
            try:
                self.ocr_engine.unload_model()
            except (RuntimeError, OSError):
                pass
        # 退出主循环
        self.destroy()

    def start_api_server(self):
        """启动 API 服务器，成功后自动切换到本地 API 模式以避免重复加载模型。"""
        if not self.api_manager:
            from main import api_server_manager
            self.api_manager = api_server_manager

        if self.api_manager.is_running():
            self.log("API 服务器已在运行")
            return

        host = self.config.get("api.host", "127.0.0.1")
        port = self.config.get("api.port", 8000)

        success = self.api_manager.start(host, port)
        if success:
            actual_port = self.api_manager.port
            self.log(f"✓ API 服务器已启动: {host}:{actual_port}")
            self.tray_manager.set_api_status(True, actual_port)

            # 如果当前没有通过本地 API 调用，自动切换
            if not self._using_local_api:
                # 卸载本地模型（如果已加载），避免占用显存
                if self.ocr_engine:
                    self.ocr_engine.unload_model()
                    self.ocr_engine = None
                self._connect_local_api()
                self.log("已自动切换到本地 API 模式")
        else:
            self.log("✗ API 服务器启动失败")

    def stop_api_server(self):
        """停止 API 服务器并重置本地 API 模式状态。"""
        if self.api_manager and self.api_manager.is_running():
            self.api_manager.stop()
            self.log("✓ API 服务器已停止")
            self.tray_manager.set_api_status(False)

            # 如果之前通过本地 API 调用，需要重置状态
            if self._using_local_api:
                # 取消轮询
                if self._api_poll_id:
                    self.after_cancel(self._api_poll_id)
                    self._api_poll_id = None
                # 关闭远程服务客户端
                if self.ocr_service and isinstance(self.ocr_service, RemoteOCRService):
                    self.ocr_service.close()
                self._using_local_api = False
                self._api_poll_errors = 0
                self.ocr_service = None
                self.model_loaded = False
                self.model_status_label.configure(text="请加载本地模型", text_color="red")
                self.btn_load_model.configure(text="加载模型", fg_color="green", state="normal")
                self.log("API 已关闭，请手动加载本地模型")
        else:
            self.log("API 服务器未在运行")

    @property
    def api_server_running(self):
        """API 服务器是否运行中"""
        return self.api_manager is not None and self.api_manager.is_running()

    # ==================== 功能方法 ====================

    def toggle_model(self):
        """根据当前模型状态切换加载或卸载操作。"""
        if not self.model_loaded:
            self.load_model()
        else:
            self.unload_model()

    def _init_ocr_service(self):
        """根据配置初始化 OCR 服务"""
        mode = self.config.get("api.mode", "local")

        if mode == "remote":
            # 远程模式：优先用 remote_host + remote_port 拼接
            r_host = self.config.get("api.remote_host", "")
            r_port = self.config.get("api.remote_port", 0)
            if r_host and r_port:
                bracket = f"[{r_host}]" if ":" in str(r_host) else r_host
                remote_url = f"http://{bracket}:{r_port}"
            else:
                remote_url = self.config.get("api.remote_url", "http://127.0.0.1:8000")
            self.ocr_service = RemoteOCRService(remote_url)
            self.log(f"使用远程 OCR 服务: {remote_url}")

            # 检查远程服务状态
            if self.ocr_service.is_loaded():
                self.model_loaded = True
                self.model_status_label.configure(text="远程模型已连接", text_color="green")
                self.btn_load_model.configure(text="断开连接", fg_color="red")
            else:
                self.model_loaded = False
                self.model_status_label.configure(text="远程服务未就绪", text_color="red")
                self.btn_load_model.configure(text="重新连接", fg_color="green")
        else:
            # 本地模式
            if self.ocr_engine and self.ocr_engine.is_loaded():
                self.ocr_service = LocalOCRService(self.ocr_engine)
                self.log("使用本地 OCR 服务")
            else:
                self.ocr_service = None
                self.log("本地模型未加载")

    def _connect_local_api(self):
        """连接到本地 API 服务（避免重复加载模型）"""
        port = self.api_manager.port
        base_url = f"http://127.0.0.1:{port}"

        self._using_local_api = True
        self._api_poll_errors = 0
        self.ocr_service = RemoteOCRService(base_url)

        # 更新 UI 状态
        self.model_status_label.configure(text="API 模型加载中...", text_color="orange")
        self.btn_load_model.configure(state="disabled", text="加载中...")
        self.log(f"已连接本地 API 服务 ({base_url})，等待模型加载...")

        # 开始轮询模型加载状态
        self._poll_api_model_status()

    def _poll_api_model_status(self):
        """轮询 API 模型加载状态"""
        if not self._using_local_api:
            return

        # 检测 API 进程是否已退出
        if not self.api_manager or not self.api_manager.is_running():
            self._api_poll_id = None
            self._api_poll_errors = 0
            self._using_local_api = False
            self.ocr_service = None
            self.model_loaded = False
            self.model_status_label.configure(text="API 服务已断开", text_color="red")
            self.btn_load_model.configure(text="加载模型", fg_color="green", state="normal")
            self.log("⚠ API 服务已断开，请手动加载本地模型")
            return

        try:
            loaded = self.ocr_service.is_loaded()
            if loaded:
                self.model_loaded = True
                self._api_poll_errors = 0
                self.model_status_label.configure(text="API 模型已加载", text_color="green")
                self.btn_load_model.configure(text="卸载模型", fg_color="red", state="normal")
                self.log("✓ API 模型已加载就绪")
                self._api_poll_id = None
                return
            # 模型尚未加载但 API 正常响应，重置错误计数
            self._api_poll_errors = 0
        except (httpx.HTTPError, OSError):
            self._api_poll_errors += 1
            # 连续失败超过 15 次（约 30 秒）则停止轮询
            if self._api_poll_errors >= 15:
                self._api_poll_id = None
                self.model_status_label.configure(text="API 无响应", text_color="red")
                self.btn_load_model.configure(text="重试", fg_color="green", state="normal")
                self.log("⚠ API 持续无响应，已停止轮询。可点击按钮重试")
                return

        # 继续轮询（每 2 秒）
        self._api_poll_id = self.after(2000, self._poll_api_model_status)

    def _load_model_via_api(self):
        """通过本地 API 触发模型加载，在后台线程中执行。"""
        def load_thread():
            self.after(0, lambda: self.btn_load_model.configure(state="disabled", text="加载中..."))
            self.after(0, lambda: self.model_status_label.configure(
                text="API 模型加载中...", text_color="orange"))
            self.log("正在通过 API 加载模型...")

            try:
                response = self.ocr_service.client.post(
                    f"{self.ocr_service.base_url}/api/model/load",
                    timeout=300.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    def on_success():
                        self.model_loaded = True
                        self.model_status_label.configure(text="API 模型已加载", text_color="green")
                        self.btn_load_model.configure(text="卸载模型", fg_color="red", state="normal")
                        self.log("✓ API 模型加载成功")
                    self.after(0, on_success)
                else:
                    msg = data.get("detail", "未知错误")
                    def on_fail():
                        self.model_status_label.configure(text="API 模型加载失败", text_color="red")
                        self.btn_load_model.configure(text="加载模型", fg_color="green", state="normal")
                        self.log(f"✗ API 模型加载失败: {msg}")
                    self.after(0, on_fail)
            except (httpx.HTTPError, OSError) as e:
                err = str(e)
                def on_error():
                    self.model_status_label.configure(text="API 模型加载失败", text_color="red")
                    self.btn_load_model.configure(text="加载模型", fg_color="green", state="normal")
                    self.log(f"✗ API 模型加载异常: {err}")
                self.after(0, on_error)

        threading.Thread(target=load_thread, daemon=True).start()

    def _unload_model_via_api(self):
        """向本地 API 发送卸载请求释放模型资源。"""
        try:
            response = self.ocr_service.client.post(
                f"{self.ocr_service.base_url}/api/model/unload",
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                self.model_loaded = False
                self.model_status_label.configure(text="API 模型未加载", text_color="red")
                self.btn_load_model.configure(text="加载模型", fg_color="green")
                self.log("✓ API 模型已卸载")
            else:
                self.log(f"✗ API 模型卸载失败: {data.get('detail', '未知错误')}")
        except (httpx.HTTPError, OSError) as e:
            self.log(f"✗ API 模型卸载失败: {e}")

    def load_model(self):
        """根据当前模式（本地 API / 远程 / 本地）加载 OCR 模型。"""
        # 如果通过本地 API 模式，调用 API 加载或重新轮询
        if self._using_local_api:
            self._api_poll_errors = 0
            # 如果 API 端模型未加载，尝试触发加载
            if not self.model_loaded:
                self._load_model_via_api()
            return

        # 如果是远程模式，重新初始化服务
        if self.config.get("api.mode") == "remote":
            self._init_ocr_service()
            return

        # 本地模式：加载模型（防止并发加载）
        if self._model_loading:
            self.log("模型正在加载中，请勿重复操作")
            return
        self._model_loading = True

        def load_thread():
            try:
                self.log("开始加载模型...")
                self.after(0, lambda: self.btn_load_model.configure(state="disabled", text="加载中..."))
                quantization = self.config.get("model.quantization", "none")
                dtype = self.config.get("model.dtype", "float16")
                if self.config.get("model.use_local_only"):
                    self.ocr_engine = OCREngine(
                        model_path=self.config.get("model.local_path"),
                        device=self.config.get("model.device"),
                        use_local_only=self.config.get("model.use_local_only"),
                        quantization=quantization,
                        dtype=dtype
                    )
                else:
                    self.ocr_engine = OCREngine(
                        model_path=self.config.get("model.name"),
                        device=self.config.get("model.device"),
                        quantization=quantization,
                        dtype=dtype
                    )

                success = self.ocr_engine.load_model(
                    progress_callback=lambda msg, prog: self.log(f"[模型加载] {msg}")
                )

                def on_done():
                    if success:
                        self.model_loaded = True
                        self.model_status_label.configure(text="模型已加载", text_color="green")
                        self.btn_load_model.configure(text="卸载模型", fg_color="red", state="normal")
                        self.log("✓ 模型加载成功")
                        self.ocr_service = LocalOCRService(self.ocr_engine)
                    else:
                        self.model_status_label.configure(text="加载失败", text_color="red")
                        self.btn_load_model.configure(text="加载模型", fg_color="green", state="normal")
                        self.log("✗ 模型加载失败")

                self.after(0, on_done)
            finally:
                self._model_loading = False

        threading.Thread(target=load_thread, daemon=True).start()

    def unload_model(self):
        """根据当前模式（本地 API / 远程 / 本地）卸载或断开 OCR 模型。"""
        # 本地 API 模式：通过 API 卸载
        if self._using_local_api:
            self._unload_model_via_api()
            return

        # 远程模式：断开连接
        if self.config.get("api.mode") == "remote":
            self.ocr_service = None
            self.model_loaded = False
            self.model_status_label.configure(text="远程服务未连接", text_color="red")
            self.btn_load_model.configure(text="重新连接", fg_color="green")
            self.log("已断开远程服务")
            return

        # 本地模式：卸载模型
        if self.ocr_engine:
            self.ocr_engine.unload_model()
        self.ocr_service = None
        self.model_loaded = False
        self.model_status_label.configure(text="模型未加载", text_color="red")
        self.btn_load_model.configure(text="加载模型", fg_color="green")
        self.log("模型已卸载")

    def screenshot_ocr(self):
        """启动截图工具进行屏幕截图，截图完成后自动进行 OCR 识别。"""
        screenshots_dir = self.base_dir / "screenshots"
        capture = ScreenCapture(
            parent=self,
            save_dir=str(screenshots_dir),
            callback=self._on_screenshot_done,
            lang_manager=self.lang
        )
        capture.start()

    def _show_screenshot_success_dialog(self, save_path):
        """显示截图成功对话框（带"下次不再提醒"选项）

        Args:
            save_path: 截图保存路径
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.lang.get("screenshot_success_title"))
        dialog.geometry("450x220")
        dialog.resizable(False, False)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 220) // 2
        dialog.geometry(f"+{x}+{y}")

        # 图标/标题
        title_label = ctk.CTkLabel(
            dialog,
            text=self.lang.get("screenshot_success_title"),
            font=("Microsoft YaHei UI", 18, "bold"),
            text_color="green"
        )
        title_label.pack(pady=(20, 10))

        # 消息内容
        message_text = self.lang.get("screenshot_success_message", save_path)
        message_label = ctk.CTkLabel(
            dialog,
            text=message_text,
            justify="left",
            wraplength=400
        )
        message_label.pack(pady=10, padx=20)

        # "下次不再提醒"复选框
        dont_show_var = ctk.BooleanVar(dialog, value=False)
        dont_show_checkbox = ctk.CTkCheckBox(
            dialog,
            text=self.lang.get("dont_show_again"),
            variable=dont_show_var
        )
        dont_show_checkbox.pack(pady=(10, 5))

        # 确认按钮
        def on_confirm():
            if dont_show_var.get():
                # 保存配置
                self.config.set("ui.screenshot_reminder_disabled", True)
                self.config.save_config()
                self.log("已禁用截图成功提示")
            dialog.destroy()

        confirm_btn = ctk.CTkButton(
            dialog,
            text=self.lang.get("confirm"),
            command=on_confirm,
            width=100,
            fg_color="green"
        )
        confirm_btn.pack(pady=(5, 20))

        # 按 Enter 键也能确认
        dialog.bind("<Return>", lambda e: on_confirm())

    def _on_screenshot_done(self, image, save_path):
        """截图完成回调

        Args:
            image: 截图的 PIL Image 对象，取消时为 None
            save_path: 截图保存路径，取消时为 None
        """
        if image is None:
            self.log("截图已取消")
            return

        self.log(f"截图已保存: {save_path}")
        self.log("截图已复制到剪贴板")
        self.show_image_preview(image)

        # 检查是否设置了不再提醒
        if not self.config.get("ui.screenshot_reminder_disabled", False):
            self._show_screenshot_success_dialog(save_path)

        # 自动识别截图内容
        if self.model_loaded:
            self.recognize_image(image)

    def clipboard_ocr(self):
        """从剪贴板获取图片并进行 OCR 识别。如果模型未加载会提示警告。"""
        if not self.model_loaded:
            messagebox.showwarning("警告", "请先加载模型")
            return

        self.log("正在从剪贴板获取图片...")
        image = ClipboardUtils.get_image_from_clipboard()

        if image is None:
            self.log("✗ 剪贴板中没有图片")
            messagebox.showwarning("警告", "剪贴板中没有图片")
            return

        self.log("✓ 成功获取剪贴板图片，开始识别...")
        self.show_image_preview(image)
        self.recognize_image(image)

    def batch_ocr(self):
        """切换到批量 OCR 标签页。"""
        self.tabview.set(self.lang.get("tab_batch_ocr"))

    def folder_ocr(self):
        """切换到批量 OCR 标签页并打开文件夹选择对话框。"""
        self.tabview.set(self.lang.get("tab_batch_ocr"))
        self.add_batch_folder()

    def pdf_ocr(self):
        """选择 PDF 文件并启动后台线程逐页进行 OCR 识别。"""
        if not self.model_loaded:
            messagebox.showwarning("警告", "请先加载模型")
            return

        file_path = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf")]
        )

        if not file_path:
            return

        self.tabview.set(self.lang.get("tab_pdf_ocr"))
        self.pdf_path_label.configure(text=file_path)
        self.pdf_result_text.delete("1.0", "end")
        self.pdf_progress_bar.set(0)
        self.pdf_progress_label.configure(text="正在转换 PDF...")
        self._pdf_result_content = ""
        self.log(f"开始处理 PDF: {file_path}")

        threading.Thread(
            target=self._pdf_ocr_thread,
            args=(file_path,),
            daemon=True
        ).start()

    def _pdf_ocr_thread(self, pdf_path):
        """PDF OCR 后台线程

        Args:
            pdf_path: PDF 文件路径
        """
        try:
            # 转换 PDF 为图片
            self.log("正在将 PDF 转换为图片...")
            images = PDFUtils.pdf_to_images(pdf_path)
            total = len(images)
            self.log(f"PDF 共 {total} 页，开始逐页识别...")
            self.after(0, lambda: self.pdf_progress_label.configure(text=f"进度: 0/{total}"))

            pdf_name = Path(pdf_path).name
            result_parts = [f"# {pdf_name} OCR 结果\n"]

            for i, page_image in enumerate(images, 1):
                self.after(0, lambda _i=i: self.pdf_progress_label.configure(
                    text=f"正在识别第 {_i}/{total} 页..."))
                self.log(f"正在识别第 {i}/{total} 页...")

                if not self.ocr_service:
                    self.log("✗ OCR 服务未就绪")
                    self.after(0, lambda: messagebox.showerror("错误", "OCR 服务未就绪"))
                    return

                text = self.ocr_service.recognize_image(
                    page_image,
                    prompt="Document Parsing:",
                    max_new_tokens=self.current_tokens
                )

                page_image.close()

                page_md = f"\n## 第 {i} 页\n\n"
                if text and text.strip():
                    page_md += text.strip()
                else:
                    page_md += "（此页未识别到内容）"
                if i < total:
                    page_md += "\n\n---\n"

                result_parts.append(page_md)

                # 实时更新结果显示（调度到主线程）
                self._pdf_result_content = "\n".join(result_parts)
                content_snapshot = self._pdf_result_content
                progress = i / total
                def _update_ui(_content=content_snapshot, _i=i, _prog=progress):
                    self.pdf_result_text.delete("1.0", "end")
                    self.pdf_result_text.insert("1.0", _content)
                    self.pdf_result_text.see("end")
                    self.pdf_progress_bar.set(_prog)
                    self.pdf_progress_label.configure(text=f"进度: {_i}/{total}")
                self.after(0, _update_ui)

            self.log(f"✓ PDF OCR 完成，共识别 {total} 页")
            self.after(0, lambda: messagebox.showinfo("完成", f"PDF OCR 完成！\n共识别 {total} 页"))

        except ImportError as e:
            self.log(f"✗ 依赖缺失: {e}")
            self.after(0, lambda _e=str(e): messagebox.showerror("依赖缺失", _e))
        except (RuntimeError, OSError) as e:
            self.log(f"✗ PDF OCR 失败: {e}")
            self.after(0, lambda _e=str(e): messagebox.showerror("错误", f"PDF OCR 失败:\n{_e}"))

    def save_pdf_result(self):
        """保存 PDF OCR 结果"""
        if not self._pdf_result_content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存 OCR 结果",
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("文本文件", "*.txt")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self._pdf_result_content)
                self.log(f"✓ 结果已保存: {file_path}")
                messagebox.showinfo("保存成功", f"结果已保存到:\n{file_path}")
            except OSError as e:
                self.log(f"✗ 保存失败: {e}")
                messagebox.showerror("错误", f"保存失败: {e}")

    def quick_ocr(self):
        """快速 OCR 入口：若剪贴板有图片则直接识别，否则弹出文件选择对话框。"""
        if ClipboardUtils.has_image():
            self.clipboard_ocr()
        else:
            self.select_image()

    def show_image_preview(self, image):
        """在预览区显示图片

        Args:
            image: PIL Image 对象或图片文件路径
        """
        from PIL import Image as PILImage

        if isinstance(image, (str, Path)):
            pil_image = PILImage.open(str(image))
        else:
            pil_image = image

        # 缩放到预览区大小，保持比例
        preview = pil_image.copy()
        preview.thumbnail((600, 200))
        w, h = preview.size

        ctk_image = ctk.CTkImage(light_image=preview, dark_image=preview, size=(w, h))
        self.image_label.configure(image=ctk_image, text="")
        self.image_label._ctk_image = ctk_image  # 防止 GC 回收

    def select_image(self):
        """选择图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.log(f"选择文件: {file_path}")
            self.show_image_preview(file_path)
            self.recognize_image(file_path)

    def _get_prompt_for_current_type(self) -> tuple:
        """根据当前选择的识别类型返回提示词信息

        Returns:
            (is_qrcode, prompt_string) 元组，is_qrcode 表示是否为二维码模式
        """
        current = self.prompt_type.get()
        # 通过对比翻译文本来反向查找识别类型 key
        type_key_map = {
            "text_recognition": "Text Recognition:",
            "document_parsing": "Document Parsing:",
            "table_recognition": "Table Recognition:",
            "formula_recognition": "Formula Recognition:",
            "qrcode_recognition": None,  # 二维码模式不需要 prompt
        }
        for key, prompt in type_key_map.items():
            if current == self.lang.get(key):
                if key == "qrcode_recognition":
                    return True, "Text Recognition:"
                return False, prompt
        # 兜底：默认文本识别
        return False, "Text Recognition:"

    def recognize_image(self, image):
        """识别图片（带加载动画）

        Args:
            image: PIL Image 对象或图片文件路径
        """
        is_qrcode_mode, selected_prompt = self._get_prompt_for_current_type()

        if not is_qrcode_mode and not self.model_loaded:
            messagebox.showwarning("警告", "请先加载模型或配置远程服务")
            return

        # 防止重复识别
        if self._recognizing:
            return

        # 开始加载动画
        self._start_loading_animation()

        def recognize_thread():
            try:
                self.log("开始识别...")
                output_parts = []

                if is_qrcode_mode:
                    # 二维码识别模式
                    self.log("正在扫描二维码...")
                    qr_results = QRCodeUtils.decode_qrcodes(image)
                    qr_text = QRCodeUtils.format_results(qr_results)

                    if qr_text:
                        output_parts.append(qr_text)
                        self.log(f"✓ 检测到 {len(qr_results)} 个二维码")

                    # 如果模型已加载，同时进行 OCR 识别（处理混合图片）
                    if self.model_loaded and self.ocr_service:
                        self.log("正在 OCR 识别文字...")
                        ocr_result = self.ocr_service.recognize_image(
                            image,
                            prompt="Text Recognition:",
                            max_new_tokens=self.current_tokens
                        )
                        if ocr_result and ocr_result.strip():
                            output_parts.append(f"[文字识别结果]\n{ocr_result}")
                            self.log("✓ 文字识别完成")

                    if output_parts:
                        self.after(0, lambda: self._show_result("\n\n".join(output_parts)))
                        self.log("✓ 识别完成")
                    else:
                        self.after(0, lambda: self._show_result(""))
                        self.log("✗ 未检测到二维码或文字")
                        messagebox.showinfo("提示", "未检测到二维码")
                else:
                    # 常规 OCR 模式
                    prompt = selected_prompt

                    if not self.ocr_service:
                        self.log("✗ OCR 服务未就绪")
                        self.after(0, lambda: self._show_result(""))
                        messagebox.showerror("错误", "OCR 服务未就绪")
                        return

                    result = self.ocr_service.recognize_image(
                        image,
                        prompt=prompt,
                        max_new_tokens=self.current_tokens
                    )

                    if result:
                        self.after(0, lambda r=result: self._show_result(r))
                        self.log("✓ 识别完成")
                    else:
                        self.after(0, lambda: self._show_result(""))
                        self.log("✗ 识别失败")
                        messagebox.showerror("错误", "识别失败")
            except Exception as e:
                self.log(f"✗ 识别异常: {e}")
                self.after(0, lambda: self._show_result(""))
            finally:
                self.after(0, self._stop_loading_animation)

        threading.Thread(target=recognize_thread, daemon=True).start()

    def _show_result(self, text: str):
        """在结果区显示识别结果（主线程调用）

        Args:
            text: 识别结果文本
        """
        self.result_text.delete("1.0", "end")
        if text:
            self.result_text.insert("1.0", text)

    def copy_result(self):
        """将识别结果文本复制到系统剪贴板。"""
        text = self.result_text.get("1.0", "end-1c")
        if text.strip():
            ClipboardUtils.set_text_to_clipboard(text)
            self.log("✓ 结果已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "没有可复制的内容")

    def add_batch_files(self):
        """打开文件选择对话框，添加图片文件到批量处理列表。"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("所有文件", "*.*")
            ]
        )

        if files:
            for file in files:
                if file not in self.batch_files:
                    self.batch_files.append(file)
            self.update_batch_list()
            self.log(f"添加了 {len(files)} 个文件")

    def add_batch_folder(self):
        """打开文件夹选择对话框，扫描并添加其中的图片文件到批量列表。"""
        folder = filedialog.askdirectory(title="选择文件夹")

        if folder:
            recursive = self.recursive_var.get()
            files = FileUtils.get_images_from_directory(folder, recursive)

            for file in files:
                file_str = str(file)
                if file_str not in self.batch_files:
                    self.batch_files.append(file_str)

            self.update_batch_list()
            self.log(f"从文件夹添加了 {len(files)} 个文件")

    def clear_batch_list(self):
        """清空批量处理的文件列表并更新显示。"""
        self.batch_files = []
        self.update_batch_list()
        self.log("已清空文件列表")

    def update_batch_list(self):
        """更新批量文件列表显示"""
        self.file_listbox.delete("1.0", "end")
        for i, file in enumerate(self.batch_files, 1):
            self.file_listbox.insert("end", f"{i}. {file}\n")

    def start_batch_ocr(self):
        """启动后台线程对批量文件列表中的所有图片依次进行 OCR 识别。"""
        if not self.model_loaded:
            messagebox.showwarning("警告", "请先加载模型")
            return

        if not self.batch_files:
            messagebox.showwarning("警告", "请先添加要处理的文件")
            return

        def batch_thread():
            total = len(self.batch_files)
            self.log(f"开始批量识别 {total} 个文件...")

            def progress_callback(current, totals):
                progress = current / totals
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"进度: {current}/{totals}")
                self.log(f"[{current}/{totals}] 识别完成")

            _, prompt = self._get_prompt_for_current_type()

            if not self.ocr_service:
                self.log("✗ OCR 服务未就绪")
                messagebox.showerror("错误", "OCR 服务未就绪")
                return

            results = self.ocr_service.recognize_batch(
                self.batch_files,
                prompt=prompt,
                progress_callback=progress_callback,
                max_new_tokens=self.current_tokens
            )

            # 保存结果
            output_dir = FileUtils.ensure_directory(self.config.get("batch.output_dir"))
            success_count = 0

            for result in results:
                if result["success"]:
                    filename = FileUtils.generate_output_filename(
                        Path(result["image"]).name,
                        self.config.get("batch.filename_format"),
                        self.config.get("batch.date_format"),
                        self.config.get("ocr.output_format")
                    )
                    output_path = output_dir / filename

                    if FileUtils.save_result(
                            result["text"],
                            output_path,
                            self.config.get("ocr.output_format")
                    ):
                        success_count += 1

            self.log(f"✓ 批量识别完成: {success_count}/{total} 成功")
            messagebox.showinfo("完成", f"批量识别完成\n成功: {success_count}/{total}")

        threading.Thread(target=batch_thread, daemon=True).start()

    def on_prompt_change(self, value):
        """提示词类型变化

        Args:
            value: 选中的识别类型名称
        """
        self.log(f"切换识别类型: {value}")

    def on_token_change(self, value):
        """Token 滑块值变化回调

        Args:
            value: 滑块当前值（浮点数）
        """
        # 滑块返回浮点数，转为整数
        token_value = int(value)

        # 更新当前值
        self.current_tokens = token_value

        # 同步更新输入框显示
        self.token_value_var.set(str(token_value))

        # 保存到配置
        self.config.set("model.max_new_tokens", token_value)
        self.config.save_config()

        # 显示 Toast 提示
        toast_text = self.lang.get("toast_token_saved")
        ToastNotification.show(self, f"{toast_text} {token_value}", duration=1500)

        # 记录日志
        self.log(f"Token 值调整为: {token_value}")

    def on_token_entry_change(self):
        """Token 输入框值变化回调"""
        try:
            # 获取用户输入
            input_value = self.token_value_var.get().strip()
            token_value = int(input_value)

            # 获取限制值
            min_tokens = 512
            max_tokens = self.config.get("model.max_new_tokens_limit", 8192)

            # 范围验证
            if token_value < min_tokens:
                token_value = min_tokens
                ToastNotification.show(self, f"⚠ Token 值不能小于 {min_tokens}，已自动调整", duration=2000)
            elif token_value > max_tokens:
                token_value = max_tokens
                ToastNotification.show(self, f"⚠ Token 值不能超过 {max_tokens}，已自动调整", duration=2000)

            # 更新值
            self.current_tokens = token_value
            self.token_value_var.set(str(token_value))

            # 同步滑块
            self.token_slider.set(token_value)

            # 保存到配置
            self.config.set("model.max_new_tokens", token_value)
            self.config.save_config()

            # 显示 Toast 提示
            toast_text = self.lang.get("toast_token_saved")
            ToastNotification.show(self, f"{toast_text} {token_value}", duration=1500)

            self.log(f"Token 值设置为: {token_value}")

        except ValueError:
            # 输入非数字，恢复为上次有效值
            self.token_value_var.set(str(self.current_tokens))
            ToastNotification.show(self, "✗ Invalid number", duration=2000)

    def open_settings(self):
        """打开设置窗口，包含语言、字体、输出目录、API 配置等选项。"""
        settings_win = ctk.CTkToplevel(self)
        settings_win.title(self.lang.get("settings_title"))
        settings_win.geometry("580x980")
        settings_win.resizable(False, False)
        settings_win.grab_set()

        # 居中显示
        settings_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 580) // 2
        y = self.winfo_y() + (self.winfo_height() - 980) // 2
        settings_win.geometry(f"+{x}+{y}")

        # 标题
        title_label = ctk.CTkLabel(
            settings_win,
            text=self.lang.get("settings"),
            font=("Microsoft YaHei UI", 20, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(20, 10))

        # 提示文本
        hint_label = ctk.CTkLabel(
            settings_win,
            text=self.lang.get("auto_save_hint"),
            font=("Microsoft YaHei UI", 11),
            text_color="gray"
        )
        hint_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))

        # ========== 语言设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("interface_language"), font=("Microsoft YaHei UI", 14)).grid(
            row=2, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        language_options = [
            "简体中文",
            "繁體中文（香港）",
            "繁體中文（台灣）",
            "English",
            "Français",
            "Deutsch",
            "日本語",
            "Italiano",
            "Русский"
        ]

        language_var = ctk.StringVar(settings_win, value=self.config.get("ui.language", "简体中文"))
        language_menu = ctk.CTkOptionMenu(

            settings_win,
            variable=language_var,
            values=language_options,
            width=250,
            font=("Microsoft YaHei UI", 12),
            command=lambda choice: self._save_language(choice, settings_win)
        )
        language_menu.grid(row=2, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        # ========== 字体设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("font_family"), font=("Microsoft YaHei UI", 14)).grid(
            row=3, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        font_options = [
            "Microsoft YaHei UI",
            "SimSun",
            "SimHei",
            "KaiTi",
            "FangSong",
            "Arial",
            "Consolas",
        ]
        font_family_var = ctk.StringVar(settings_win, value=self.font_family)

        def on_font_family_change(choice):
            self.font_family = choice
            self.config.set("ui.font_family", choice)
            self.config.save_config()
            self.apply_font_settings()
            toast_text = self.lang.get("toast_font_saved")
            ToastNotification.show(settings_win, f"{toast_text} {choice}", duration=1500)
            self.log(f"字体已设置为: {choice}")

        ctk.CTkOptionMenu(
            settings_win,
            variable=font_family_var,
            values=font_options,
            width=250,
            font=("Microsoft YaHei UI", 12),
            command=on_font_family_change
        ).grid(row=3, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        # ========== 字体大小设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("font_size_label"), font=("Microsoft YaHei UI", 14)).grid(
            row=4, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        font_size_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        font_size_frame.grid(row=4, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        font_size_var = ctk.StringVar(settings_win, value=str(self.font_size))

        font_size_slider = ctk.CTkSlider(
            font_size_frame,
            from_=10,
            to=20,
            number_of_steps=10,
            width=180,
            command=lambda val: _on_font_size_change(int(val))
        )
        font_size_slider.set(self.font_size)
        font_size_slider.pack(side="left", padx=(0, 8))

        font_size_entry = ctk.CTkEntry(font_size_frame, textvariable=font_size_var, width=60, justify="center")
        font_size_entry.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(font_size_frame, text="(10-20)", font=("Microsoft YaHei UI", 11), text_color="gray").pack(
            side="left", padx=5
        )

        def _on_font_size_change(val):
            val = max(10, min(20, val))
            self.font_size = val
            font_size_var.set(str(val))
            font_size_slider.set(val)
            self.config.set("ui.font_size", val)
            self.config.save_config()
            self.apply_font_settings()
            toast_text = self.lang.get("toast_font_saved")
            ToastNotification.show(settings_win, f"{toast_text} {val}px", duration=1500)

        def _on_font_size_entry():
            try:
                val = int(font_size_var.get().strip())
                _on_font_size_change(val)
            except ValueError:
                font_size_var.set(str(self.font_size))

        font_size_entry.bind("<Return>", _on_font_size_entry)
        font_size_entry.bind("<FocusOut>", _on_font_size_entry)

        # ========== 输出目录设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("output_directory"), font=("Microsoft YaHei UI", 14)).grid(
            row=5, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        output_dir_var = ctk.StringVar(settings_win, value=self.config.get("batch.output_dir", "./output"))
        output_dir_entry = ctk.CTkEntry(settings_win, textvariable=output_dir_var, width=250)
        output_dir_entry.grid(row=5, column=1, padx=10, pady=12)

        def browse_output_dir():
            folder = filedialog.askdirectory(title="选择输出目录", parent=settings_win)
            if folder:
                output_dir_var.set(folder)
                self.config.set("batch.output_dir", folder)
                self.config.save_config()
                toast_text = self.lang.get("toast_output_dir_saved")
                ToastNotification.show(settings_win, toast_text, duration=1500)
                self.log(f"输出目录已设置为: {folder}")

        ctk.CTkButton(settings_win, text=self.lang.get("browse"), command=browse_output_dir, width=70).grid(
            row=5, column=2, padx=10, pady=12
        )

        # ========== 最大 Token 限制设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("max_token_limit"), font=("Microsoft YaHei UI", 14)).grid(
            row=6, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        max_tokens_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        max_tokens_frame.grid(row=6, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        max_tokens_entry = ctk.CTkEntry(max_tokens_frame, width=120)
        max_tokens_entry.insert(0, str(self.config.get("model.max_new_tokens_limit", 8192)))
        max_tokens_entry.pack(side="left", padx=(0, 5))

        def confirm_max_tokens():
            try:
                new_value = int(max_tokens_entry.get().strip())
                if new_value < 512:
                    new_value = 512
                    ToastNotification.show(settings_win, "⚠ 最小值为 512，已自动调整", duration=1500)
                elif new_value > 32768:
                    new_value = 32768
                    ToastNotification.show(settings_win, "⚠ 最大值为 32768，已自动调整", duration=1500)

                max_tokens_entry.delete(0, "end")
                max_tokens_entry.insert(0, str(new_value))

                self.config.set("model.max_new_tokens_limit", new_value)
                self.config.save_config()

                # 更新主界面滑块
                self.token_slider.configure(to=new_value)
                if self.current_tokens > new_value:
                    self.current_tokens = new_value
                    self.token_slider.set(new_value)
                    self.token_value_var.set(str(new_value))

                toast_text = self.lang.get("toast_token_saved")
                ToastNotification.show(settings_win, f"{toast_text} {new_value}", duration=1500)
                self.log(f"最大 Token 限制已设置为: {new_value}")
            except ValueError:
                ToastNotification.show(settings_win, "⚠ 请输入有效数字", duration=1500)

        max_tokens_entry.bind("<Return>", lambda e: confirm_max_tokens())

        ctk.CTkButton(
            max_tokens_frame, text="确认", command=confirm_max_tokens, width=60, height=28
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            max_tokens_frame,
            text="(512-32768)",
            font=("Microsoft YaHei UI", 11),
            text_color="gray"
        ).pack(side="left", padx=5)

        # ========== 截图提示设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("screenshot_prompt"), font=("Microsoft YaHei UI", 14)).grid(
            row=7, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        screenshot_reminder_var = ctk.BooleanVar(
            settings_win,
            value=not self.config.get("ui.screenshot_reminder_disabled", False)
        )

        def save_screenshot_reminder():
            self.config.set("ui.screenshot_reminder_disabled", not screenshot_reminder_var.get())
            self.config.save_config()
            if screenshot_reminder_var.get():
                toast_text = self.lang.get("toast_screenshot_enabled")
            else:
                toast_text = self.lang.get("toast_screenshot_disabled")
            ToastNotification.show(settings_win, toast_text, duration=1500)
            self.log(f"截图提示已{'启用' if screenshot_reminder_var.get() else '禁用'}")

        screenshot_reminder_checkbox = ctk.CTkCheckBox(
            settings_win,
            text=self.lang.get("show_screenshot_success"),
            variable=screenshot_reminder_var,
            command=save_screenshot_reminder
        )
        screenshot_reminder_checkbox.grid(row=7, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        # ========== API 客户端模式设置 ==========
        ctk.CTkLabel(settings_win, text="客户端模式", font=("Microsoft YaHei UI", 14)).grid(
            row=8, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        api_mode_var = ctk.StringVar(settings_win, value=self.config.get("api.mode", "local"))

        def on_mode_change(mode):
            self.config.set("api.mode", mode)
            self.config.save_config()
            # 根据模式显示/隐藏远程 URL 框
            if mode == "remote":
                remote_frame.grid(row=9, column=0, columnspan=3, padx=40, pady=(0, 10), sticky="ew")
            else:
                remote_frame.grid_forget()
            # 重新初始化服务
            self._init_ocr_service()
            self.log(f"客户端模式已切换为: {mode}")

        ctk.CTkOptionMenu(
            settings_win,
            variable=api_mode_var,
            values=["local", "remote"],
            command=on_mode_change,
            width=200
        ).grid(row=8, column=1, padx=10, pady=12, sticky="w")

        # 远程地址配置框（仅远程模式显示）
        remote_frame = ctk.CTkFrame(settings_win, fg_color="transparent")

        # IP 地址
        ctk.CTkLabel(remote_frame, text="IP:", font=("Microsoft YaHei UI", 12)).grid(
            row=0, column=0, padx=(0, 5), sticky="w"
        )
        remote_ip_entry = ctk.CTkEntry(remote_frame, width=200,
                                        placeholder_text="例: 192.168.1.100 或 ::1")
        remote_ip_entry.insert(0, self.config.get("api.remote_host", "127.0.0.1"))
        remote_ip_entry.grid(row=0, column=1, padx=5)

        remote_ip_hint = ctk.CTkLabel(remote_frame, text="", font=("Microsoft YaHei UI", 10),
                                       text_color="gray")
        remote_ip_hint.grid(row=1, column=1, padx=5, sticky="w")

        # 端口
        ctk.CTkLabel(remote_frame, text="端口:", font=("Microsoft YaHei UI", 12)).grid(
            row=0, column=2, padx=(15, 5), sticky="w"
        )
        remote_port_entry = ctk.CTkEntry(remote_frame, width=80, placeholder_text="8000")
        remote_port_entry.insert(0, str(self.config.get("api.remote_port",
                                        self.config.get("api.port", 8000))))
        remote_port_entry.grid(row=0, column=3, padx=5)

        # 校验函数
        def _validate_ip(ip_str: str) -> tuple:
            """校验 IPv4/IPv6 地址，返回 (valid, type_str)"""
            import ipaddress
            ip_str = ip_str.strip()
            if not ip_str:
                return False, "不能为空"
            # 也允许域名（比如 localhost）
            if ip_str.lower() == "localhost":
                return True, "localhost"
            try:
                addr = ipaddress.ip_address(ip_str)
                if addr.version == 4:
                    return True, "IPv4"
                else:
                    return True, "IPv6"
            except ValueError:
                # 尝试当作域名
                import re
                domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
                if re.match(domain_pattern, ip_str):
                    return True, "域名"
                return False, "无效地址"

        def _validate_port(port_str: str) -> tuple:
            """校验端口号，返回 (valid, msg)"""
            port_str = port_str.strip()
            if not port_str:
                return False, "不能为空"
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    return False, "范围 1-65535"
                return True, str(port)
            except ValueError:
                return False, "必须为数字"

        # 实时 IP 校验提示
        def on_ip_input(*_):
            ip = remote_ip_entry.get()
            if not ip.strip():
                remote_ip_hint.configure(text="", text_color="gray")
                return
            valid, info = _validate_ip(ip)
            if valid:
                remote_ip_hint.configure(text=f"✓ {info}", text_color="green")
            else:
                remote_ip_hint.configure(text=f"✗ {info}", text_color="red")

        remote_ip_entry.bind("<KeyRelease>", on_ip_input)
        # 初始显示
        on_ip_input()

        # 按钮区
        btn_row_frame = ctk.CTkFrame(remote_frame, fg_color="transparent")
        btn_row_frame.grid(row=2, column=0, columnspan=4, pady=(5, 0), sticky="w")

        def save_remote_address():
            ip = remote_ip_entry.get().strip()
            port_str = remote_port_entry.get().strip()

            ip_valid, ip_info = _validate_ip(ip)
            if not ip_valid:
                ToastNotification.show(settings_win, f"⚠ IP 地址无效: {ip_info}", duration=2000)
                return

            port_valid, port_info = _validate_port(port_str)
            if not port_valid:
                ToastNotification.show(settings_win, f"⚠ 端口无效: {port_info}", duration=2000)
                return

            port = int(port_str)
            # IPv6 地址需要方括号
            bracket_ip = f"[{ip}]" if ":" in ip else ip
            url = f"http://{bracket_ip}:{port}"

            self.config.set("api.remote_host", ip)
            self.config.set("api.remote_port", port)
            self.config.set("api.remote_url", url)
            self.config.save_config()

            self._init_ocr_service()
            ToastNotification.show(settings_win, f"✓ 远程地址已保存: {url}", duration=1500)
            self.log(f"远程地址已设置为: {url}")

        ctk.CTkButton(btn_row_frame, text="保存", command=save_remote_address,
                       width=60, height=28).pack(side="left", padx=(0, 5))

        def test_connection():
            # 先保存再测试
            save_remote_address()
            if self.ocr_service and isinstance(self.ocr_service, RemoteOCRService):
                success, message = self.ocr_service.test_connection()
                if success:
                    messagebox.showinfo("连接测试", f"✓ {message}", parent=settings_win)
                else:
                    messagebox.showerror("连接测试", f"✗ {message}", parent=settings_win)
            else:
                messagebox.showwarning("提示", "请先切换到远程模式并保存", parent=settings_win)

        ctk.CTkButton(btn_row_frame, text="测试连接", command=test_connection,
                       width=80, height=28).pack(side="left", padx=5)

        # 根据当前模式决定是否显示
        if api_mode_var.get() == "remote":
            remote_frame.grid(row=9, column=0, columnspan=3, padx=40, pady=(0, 10), sticky="ew")

        # ========== API 服务器设置 ==========
        ctk.CTkLabel(settings_win, text="API 服务器", font=("Microsoft YaHei UI", 14)).grid(
            row=10, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        # API 状态和控制区
        api_control_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        api_control_frame.grid(row=10, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        # 状态标签
        api_running = self.api_server_running
        status_text = f"运行中 (:{self.api_manager.port})" if api_running else "已停止"
        status_color = "green" if api_running else "red"
        api_status_label = ctk.CTkLabel(
            api_control_frame,
            text=status_text,
            text_color=status_color,
            font=("Microsoft YaHei UI", 12)
        )
        api_status_label.pack(side="left", padx=(0, 10))

        # 启动/停止按钮
        def toggle_api_server():
            if self.api_server_running:
                self.stop_api_server()
                self.config.set("api.enabled", False)
                self.config.save_config()
                api_toggle_btn.configure(text="启动 API", fg_color="green")
                api_status_label.configure(text="已停止", text_color="red")
                ToastNotification.show(settings_win, "✓ API 服务器已停止", duration=1500)
            else:
                self.config.set("api.enabled", True)
                self.config.save_config()
                self.start_api_server()
                if self.api_server_running:
                    port = self.api_manager.port if self.api_manager else "?"
                    api_toggle_btn.configure(text="停止 API", fg_color="#d32f2f")
                    api_status_label.configure(text=f"运行中 (:{port})", text_color="green")
                    ToastNotification.show(settings_win, f"✓ API 服务器已启动 (:{port})", duration=1500)
                else:
                    self.config.set("api.enabled", False)
                    self.config.save_config()
                    ToastNotification.show(settings_win, "✗ API 服务器启动失败", duration=2000)

        btn_text = "停止 API" if api_running else "启动 API"
        btn_color = "#d32f2f" if api_running else "green"
        api_toggle_btn = ctk.CTkButton(
            api_control_frame,
            text=btn_text,
            command=toggle_api_server,
            width=100,
            height=32,
            fg_color=btn_color
        )
        api_toggle_btn.pack(side="left", padx=5)

        # 监听地址 + 端口 (同一行)
        ctk.CTkLabel(settings_win, text="监听地址:", font=("Microsoft YaHei UI", 12)).grid(
            row=11, column=0, padx=(40, 10), pady=8, sticky="w"
        )

        listen_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        listen_frame.grid(row=11, column=1, columnspan=2, padx=10, pady=8, sticky="w")

        listen_host_entry = ctk.CTkEntry(listen_frame, width=150,
                                          placeholder_text="127.0.0.1")
        listen_host_entry.insert(0, self.config.get("api.host", "127.0.0.1"))
        listen_host_entry.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(listen_frame, text=":", font=("Microsoft YaHei UI", 14)).pack(side="left")

        listen_port_entry = ctk.CTkEntry(listen_frame, width=80, placeholder_text="18000")
        listen_port_entry.insert(0, str(self.config.get("api.port", 8000)))
        listen_port_entry.pack(side="left", padx=(0, 8))

        def confirm_listen_addr():
            import ipaddress
            host = listen_host_entry.get().strip()
            port_str = listen_port_entry.get().strip()

            # 校验 host：只允许 0.0.0.0 / 127.0.0.1 / 有效 IP
            if not host:
                ToastNotification.show(settings_win, "⚠ 监听地址不能为空", duration=1500)
                return
            if host not in ("0.0.0.0", "127.0.0.1", "localhost", "::1", "::"):
                try:
                    ipaddress.ip_address(host)
                except ValueError:
                    ToastNotification.show(settings_win, "⚠ 无效的监听地址", duration=2000)
                    return

            # 0.0.0.0 安全警告
            if host == "0.0.0.0":
                result = messagebox.askyesno(
                    "安全警告",
                    "监听 0.0.0.0 将允许局域网内所有设备访问 API 服务。\n\n是否继续？",
                    parent=settings_win
                )
                if not result:
                    return

            # 校验端口
            port_valid, port_info = _validate_port(port_str)
            if not port_valid:
                ToastNotification.show(settings_win, f"⚠ 端口无效: {port_info}", duration=2000)
                return

            port = int(port_str)
            self.config.set("api.host", host)
            self.config.set("api.port", port)
            self.config.save_config()
            ToastNotification.show(settings_win, f"✓ 监听地址已设置为 {host}:{port}", duration=1500)
            self.log(f"API 监听地址已设置为: {host}:{port}")

        listen_host_entry.bind("<Return>", lambda e: confirm_listen_addr())
        listen_port_entry.bind("<Return>", lambda e: confirm_listen_addr())

        ctk.CTkButton(
            listen_frame, text="确认", command=confirm_listen_addr, width=60, height=28
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            listen_frame,
            text="(重启API后生效)",
            font=("Microsoft YaHei UI", 10),
            text_color="gray"
        ).pack(side="left", padx=5)

        # ========== 启动模式设置 ==========
        ctk.CTkLabel(settings_win, text="启动模式", font=("Microsoft YaHei UI", 14)).grid(
            row=12, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        startup_mode_map = {
            "ui": "纯界面模式",
            "ui+api": "界面 + API 服务",
            "api": "纯 API 服务（无界面）"
        }
        startup_mode_reverse = {v: k for k, v in startup_mode_map.items()}

        # 推断当前模式：兼容旧版本（如果 startup_mode 未设置，检查 api.enabled）
        current_startup = self.config.get("app.startup_mode", "ui")
        if current_startup == "ui" and self.config.get("api.enabled", False):
            current_startup = "ui+api"
        startup_display = startup_mode_map.get(current_startup, "纯界面模式")
        startup_mode_var = ctk.StringVar(settings_win, value=startup_display)

        def on_startup_mode_change(choice):
            mode = startup_mode_reverse.get(choice, "ui")

            # 纯 API 模式警告
            if mode == "api":
                result = messagebox.askyesno(
                    "警告",
                    "纯 API 模式下程序启动后没有图形界面，仅提供 API 服务。\n\n"
                    "如需恢复界面模式，需要手动编辑 config.json\n"
                    "或使用命令行启动：python main.py（不带参数）\n\n"
                    "确认切换到纯 API 模式？",
                    parent=settings_win
                )
                if not result:
                    startup_mode_var.set(startup_display)
                    return

            self.config.set("app.startup_mode", mode)
            # 同步 api.enabled 保持一致
            self.config.set("api.enabled", mode in ("ui+api", "api"))
            self.config.save_config()

            ToastNotification.show(
                settings_win, f"✓ 启动模式: {choice}（重启后生效）", duration=2000
            )
            self.log(f"启动模式已设置为: {choice}")

        ctk.CTkOptionMenu(
            settings_win,
            variable=startup_mode_var,
            values=list(startup_mode_map.values()),
            command=on_startup_mode_change,
            width=250,
            font=("Microsoft YaHei UI", 12)
        ).grid(row=12, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        # ========== 开机自动启动设置 ==========
        ctk.CTkLabel(settings_win, text="开机自启", font=("Microsoft YaHei UI", 14)).grid(
            row=13, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        # 读取注册表中的实际状态
        from utils.AutoStart import is_auto_start_enabled, set_auto_start
        auto_start_var = ctk.BooleanVar(settings_win, value=is_auto_start_enabled())

        def save_auto_start():
            enabled = auto_start_var.get()
            success = set_auto_start(enabled)
            if success:
                self.config.set("ui.auto_start", enabled)
                self.config.save_config()
                # 同步托盘菜单
                if hasattr(self, 'tray_manager'):
                    self.tray_manager.set_auto_start_status(enabled)
                status = "启用" if enabled else "禁用"
                ToastNotification.show(settings_win, f"✓ 开机自动启动已{status}", duration=1500)
                self.log(f"开机自动启动已{status}")
            else:
                # 设置失败，恢复复选框状态
                auto_start_var.set(not enabled)
                ToastNotification.show(settings_win, "✗ 设置失败，请检查权限", duration=2000)

        auto_start_checkbox = ctk.CTkCheckBox(
            settings_win,
            text="开机时自动启动（最小化到托盘）",
            variable=auto_start_var,
            command=save_auto_start
        )
        auto_start_checkbox.grid(row=13, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        # ========== 关闭行为设置 ==========
        ctk.CTkLabel(settings_win, text="关闭行为", font=("Microsoft YaHei UI", 14)).grid(
            row=14, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        close_behavior_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        close_behavior_frame.grid(row=14, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        current_choice = self.config.get("ui.minimize_to_tray", None)
        if current_choice is True:
            choice_text = "最小化到托盘"
        elif current_choice is False:
            choice_text = "直接退出"
        else:
            choice_text = "每次询问"

        close_choice_label = ctk.CTkLabel(
            close_behavior_frame,
            text=f"当前: {choice_text}",
            font=("Microsoft YaHei UI", 12)
        )
        close_choice_label.pack(side="left", padx=(0, 10))

        def reset_close_behavior():
            self.config.set("ui.minimize_to_tray", None)
            self.config.save_config()
            close_choice_label.configure(text="当前: 每次询问")
            ToastNotification.show(settings_win, "✓ 已重置，下次关闭时将重新询问", duration=1500)
            self.log("关闭行为已重置为每次询问")

        ctk.CTkButton(
            close_behavior_frame,
            text="重置",
            command=reset_close_behavior,
            width=60,
            height=28
        ).pack(side="left", padx=5)

        # ========== 关闭按钮 ==========
        ctk.CTkButton(
            settings_win,
            text=self.lang.get("close"),
            command=settings_win.destroy,
            width=120,
            height=35
        ).grid(row=15, column=0, columnspan=3, pady=(25, 20))

    def _save_language(self, language, parent_win):
        """保存语言设置

        Args:
            language: 语言名称
            parent_win: 父窗口（用于显示 Toast 提示）
        """
        self.config.set("ui.language", language)
        self.config.save_config()

        # 更新语言管理器
        self.lang.set_language(language)

        # 更新界面语言
        self.update_ui_language()

        # 显示 Toast（使用新语言）
        toast_text = self.lang.get("toast_language_saved")
        ToastNotification.show(parent_win, f"{toast_text} {language}", duration=1500)
        self.log(f"界面语言已设置为: {language}")

    def log(self, message: str):
        """添加日志（线程安全）

        Args:
            message: 日志消息文本
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        def _insert():
            self.log_text.insert("end", line)
            self.log_text.see("end")

        # 如果不在主线程，调度到主线程执行
        try:
            if threading.current_thread() is not threading.main_thread():
                self.after(0, _insert)
            else:
                _insert()
        except RuntimeError:
            # 窗口已销毁
            pass

    def clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", "end")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
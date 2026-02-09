"""
主界面模块
使用 CustomTkinter 构建现代化 UI
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import io

from core.Config import Config
from core.OCREngine import OCREngine
from utils.FileUtils import FileUtils
from utils.ClipboardUtils import ClipboardUtils
from utils.QRCodeUtils import QRCodeUtils
from utils.ScreenCapture import ScreenCapture
from utils.PDFUtils import PDFUtils
from ui.ToastNotification import ToastNotification
from ui.LanguageManager import LanguageManager


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self, base_dir=None):
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

        # OCR 引擎
        self.ocr_engine = None
        self.model_loaded = False

        # 动态 Token 设置
        self.current_tokens = self.config.get("model.max_new_tokens", 2048)

        # UI 初始化
        self.setup_window()
        self.create_widgets()

        # 绑定快捷键
        self.bind_shortcuts()

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

    def create_sidebar(self):
        """创建侧边栏"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(7, weight=1)

        # Logo / 标题
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="GLM-OCR",
            font=("Microsoft YaHei UI", 24, "bold")
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
            font=("Microsoft YaHei UI", 12),
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
        self.tab_single = self.tabview.add("单图OCR")
        self.create_single_tab()

        # 批量 OCR 标签页
        self.tab_batch = self.tabview.add("批量OCR")
        self.create_batch_tab()

        # PDF OCR 标签页
        self.tab_pdf = self.tabview.add("PDF OCR")
        self.create_pdf_tab()

        # 二维码生成标签页
        self.tab_qrgen = self.tabview.add("二维码生成")
        self.create_qrgen_tab()

        # 日志标签页
        self.tab_log = self.tabview.add("日志")
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
            font=("Microsoft YaHei UI", 13)
        )
        self.btn_quick_ocr.grid(row=0, column=1, padx=5)

        # 复制结果按钮
        self.btn_copy_result = ctk.CTkButton(
            result_header_frame,
            text=self.lang.get("copy_result"),
            command=self.copy_result,
            width=120,
            height=35,
            font=("Microsoft YaHei UI", 13),
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
            from PIL import ImageTk

            qr = qrcode.QRCode(box_size=10, border=4)
            qr.add_data(text)
            qr.make(fit=True)
            self._qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            # 缩放到预览尺寸
            preview = self._qr_image.copy()
            preview.thumbnail((380, 380))

            tk_image = ImageTk.PhotoImage(preview)
            self.qr_preview_label.configure(image=tk_image, text="")
            self.qr_preview_label._tk_image = tk_image  # 防止被 GC 回收

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

    # ==================== 功能方法 ====================

    def toggle_model(self):
        """加载/卸载模型"""
        if not self.model_loaded:
            self.load_model()
        else:
            self.unload_model()

    def load_model(self):
        """加载模型"""

        def load_thread():
            self.log("开始加载模型...")
            self.btn_load_model.configure(state="disabled", text="加载中...")
            quantization = self.config.get("model.quantization", "none")
            if self.config.get("model.use_local_only"):
                self.ocr_engine = OCREngine(
                    model_path=self.config.get("model.local_path"),
                    device=self.config.get("model.device"),
                    use_local_only=self.config.get("model.use_local_only"),
                    quantization=quantization
                )
            else:
                self.ocr_engine = OCREngine(
                    model_path=self.config.get("model.name"),
                    device=self.config.get("model.device"),
                    quantization=quantization
                )

            success = self.ocr_engine.load_model(
                progress_callback=lambda msg, prog: self.log(f"[模型加载] {msg}")
            )

            if success:
                self.model_loaded = True
                self.model_status_label.configure(text="模型已加载", text_color="green")
                self.btn_load_model.configure(
                    text="卸载模型",
                    fg_color="red",
                    state="normal"
                )
                self.log("✓ 模型加载成功")
            else:
                self.model_status_label.configure(text="加载失败", text_color="red")
                self.btn_load_model.configure(text="加载模型", state="normal")
                self.log("✗ 模型加载失败")

        threading.Thread(target=load_thread, daemon=True).start()

    def unload_model(self):
        """卸载模型"""
        if self.ocr_engine:
            self.ocr_engine.unload_model()
        self.model_loaded = False
        self.model_status_label.configure(text="模型未加载", text_color="red")
        self.btn_load_model.configure(text="加载模型", fg_color="green")
        self.log("模型已卸载")

    def screenshot_ocr(self):
        """截图"""
        screenshots_dir = self.base_dir / "screenshots"
        capture = ScreenCapture(
            parent=self,
            save_dir=str(screenshots_dir),
            callback=self._on_screenshot_done,
        )
        capture.start()

    def _show_screenshot_success_dialog(self, save_path):
        """显示截图成功对话框（带"下次不再提醒"选项）"""
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
        """截图完成回调"""
        if image is None:
            self.log("截图已取消")
            return

        self.log(f"截图已保存: {save_path}")
        self.log("截图已复制到剪贴板")
        self.show_image_preview(image)

        # 检查是否设置了不再提醒
        if not self.config.get("ui.screenshot_reminder_disabled", False):
            self._show_screenshot_success_dialog(save_path)

    def clipboard_ocr(self):
        """剪贴板OCR"""
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
        """批量OCR"""
        self.tabview.set("批量OCR")

    def folder_ocr(self):
        """文件夹OCR"""
        self.tabview.set("批量OCR")
        self.add_batch_folder()

    def pdf_ocr(self):
        """PDF 文档 OCR"""
        if not self.model_loaded:
            messagebox.showwarning("警告", "请先加载模型")
            return

        file_path = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf")]
        )

        if not file_path:
            return

        self.tabview.set("PDF OCR")
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
        """PDF OCR 后台线程"""
        try:
            # 转换 PDF 为图片
            self.log("正在将 PDF 转换为图片...")
            images = PDFUtils.pdf_to_images(pdf_path)
            total = len(images)
            self.log(f"PDF 共 {total} 页，开始逐页识别...")
            self.pdf_progress_label.configure(text=f"进度: 0/{total}")

            pdf_name = Path(pdf_path).name
            result_parts = [f"# {pdf_name} OCR 结果\n"]

            for i, page_image in enumerate(images, 1):
                self.pdf_progress_label.configure(text=f"正在识别第 {i}/{total} 页...")
                self.log(f"正在识别第 {i}/{total} 页...")

                text = self.ocr_engine.recognize_image(
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

                # 实时更新结果显示
                self._pdf_result_content = "\n".join(result_parts)
                self.pdf_result_text.delete("1.0", "end")
                self.pdf_result_text.insert("1.0", self._pdf_result_content)
                self.pdf_result_text.see("end")

                # 更新进度条
                self.pdf_progress_bar.set(i / total)
                self.pdf_progress_label.configure(text=f"进度: {i}/{total}")

            self.log(f"✓ PDF OCR 完成，共识别 {total} 页")
            messagebox.showinfo("完成", f"PDF OCR 完成！\n共识别 {total} 页")

        except ImportError as e:
            self.log(f"✗ 依赖缺失: {e}")
            messagebox.showerror("依赖缺失", str(e))
        except Exception as e:
            self.log(f"✗ PDF OCR 失败: {e}")
            messagebox.showerror("错误", f"PDF OCR 失败:\n{e}")

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
            except Exception as e:
                self.log(f"✗ 保存失败: {e}")
                messagebox.showerror("错误", f"保存失败: {e}")

    def quick_ocr(self):
        """快速OCR"""
        if ClipboardUtils.has_image():
            self.clipboard_ocr()
        else:
            self.select_image()

    def show_image_preview(self, image):
        """在预览区显示图片"""
        from PIL import Image, ImageTk

        if isinstance(image, (str, Path)):
            pil_image = Image.open(str(image))
        else:
            pil_image = image

        # 缩放到预览区大小，保持比例
        preview = pil_image.copy()
        preview.thumbnail((600, 200))

        tk_image = ImageTk.PhotoImage(preview)
        self.image_label.configure(image=tk_image, text="")
        self.image_label._tk_image = tk_image  # 防止 GC 回收

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

    def recognize_image(self, image):
        """识别图片"""
        is_qrcode_mode = self.prompt_type.get() == "二维码识别"

        if not is_qrcode_mode and not self.model_loaded:
            messagebox.showwarning("警告", "请先加载模型")
            return

        def recognize_thread():
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
                if self.model_loaded:
                    self.log("正在 OCR 识别文字...")
                    ocr_result = self.ocr_engine.recognize_image(
                        image,
                        prompt="Text Recognition:",
                        max_new_tokens=self.current_tokens
                    )
                    if ocr_result and ocr_result.strip():
                        output_parts.append(f"[文字识别结果]\n{ocr_result}")
                        self.log("✓ 文字识别完成")

                if output_parts:
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("1.0", "\n\n".join(output_parts))
                    self.log("✓ 识别完成")
                else:
                    self.log("✗ 未检测到二维码或文字")
                    messagebox.showinfo("提示", "未检测到二维码")
            else:
                # 常规 OCR 模式
                prompt_map = {
                    "文本识别": "Text Recognition:",
                    "文档解析": "Document Parsing:",
                    "表格识别": "Table Recognition:",
                    "公式识别": "Formula Recognition:"
                }

                prompt = prompt_map.get(self.prompt_type.get(), "Text Recognition:")

                result = self.ocr_engine.recognize_image(
                    image,
                    prompt=prompt,
                    max_new_tokens=self.current_tokens
                )

                if result:
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("1.0", result)
                    self.log("✓ 识别完成")
                else:
                    self.log("✗ 识别失败")
                    messagebox.showerror("错误", "识别失败")

        threading.Thread(target=recognize_thread, daemon=True).start()

    def copy_result(self):
        """复制结果"""
        text = self.result_text.get("1.0", "end-1c")
        if text.strip():
            ClipboardUtils.set_text_to_clipboard(text)
            self.log("✓ 结果已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "没有可复制的内容")

    def add_batch_files(self):
        """添加批量文件"""
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
        """添加文件夹"""
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
        """清空批量列表"""
        self.batch_files = []
        self.update_batch_list()
        self.log("已清空文件列表")

    def update_batch_list(self):
        """更新批量文件列表显示"""
        self.file_listbox.delete("1.0", "end")
        for i, file in enumerate(self.batch_files, 1):
            self.file_listbox.insert("end", f"{i}. {file}\n")

    def start_batch_ocr(self):
        """开始批量识别"""
        if not self.model_loaded:
            messagebox.showwarning("警告", "请先加载模型")
            return

        if not self.batch_files:
            messagebox.showwarning("警告", "请先添加要处理的文件")
            return

        def batch_thread():
            total = len(self.batch_files)
            self.log(f"开始批量识别 {total} 个文件...")

            def progress_callback(current, total, result):
                progress = current / total
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"进度: {current}/{total}")
                self.log(f"[{current}/{total}] 识别完成")

            prompt_map = {
                "文本识别": "Text Recognition:",
                "文档解析": "Document Parsing:",
                "表格识别": "Table Recognition:",
                "公式识别": "Formula Recognition:"
            }
            prompt = prompt_map.get(self.prompt_type.get(), "Text Recognition:")

            results = self.ocr_engine.recognize_batch(
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
        """提示词类型变化"""
        self.log(f"切换识别类型: {value}")

    def on_token_change(self, value):
        """Token 滑块值变化回调"""
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

    def on_token_entry_change(self, event=None):
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
        """打开设置窗口"""
        settings_win = ctk.CTkToplevel(self)
        settings_win.title(self.lang.get("settings_title"))
        settings_win.geometry("550x450")
        settings_win.resizable(False, False)
        settings_win.grab_set()

        # 居中显示
        settings_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 550) // 2
        y = self.winfo_y() + (self.winfo_height() - 450) // 2
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

        # ========== 输出目录设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("output_directory"), font=("Microsoft YaHei UI", 14)).grid(
            row=3, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        output_dir_var = ctk.StringVar(settings_win, value=self.config.get("batch.output_dir", "./output"))
        output_dir_entry = ctk.CTkEntry(settings_win, textvariable=output_dir_var, width=250)
        output_dir_entry.grid(row=3, column=1, padx=10, pady=12)

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
            row=3, column=2, padx=10, pady=12
        )

        # ========== 最大 Token 限制设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("max_token_limit"), font=("Microsoft YaHei UI", 14)).grid(
            row=4, column=0, padx=(40, 10), pady=12, sticky="w"
        )

        max_tokens_var = ctk.IntVar(
            settings_win,
            value=self.config.get("model.max_new_tokens_limit", 8192)
        )

        def save_max_tokens(*args):
            try:
                new_value = max_tokens_var.get()
                if new_value < 512:
                    new_value = 512
                    max_tokens_var.set(512)
                    ToastNotification.show(settings_win, "⚠ 最小值为 512", duration=1500)
                elif new_value > 32768:
                    new_value = 32768
                    max_tokens_var.set(32768)
                    ToastNotification.show(settings_win, "⚠ 最大值为 32768", duration=1500)

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
            except:
                pass

        max_tokens_var.trace_add("write", save_max_tokens)

        max_tokens_entry = ctk.CTkEntry(
            settings_win,
            textvariable=max_tokens_var,
            width=120
        )
        max_tokens_entry.grid(row=4, column=1, padx=10, pady=12, sticky="w")

        ctk.CTkLabel(
            settings_win,
            text="(512-32768)",
            font=("Microsoft YaHei UI", 11),
            text_color="gray"
        ).grid(row=4, column=2, padx=10, pady=12, sticky="w")

        # ========== 截图提示设置 ==========
        ctk.CTkLabel(settings_win, text=self.lang.get("screenshot_prompt"), font=("Microsoft YaHei UI", 14)).grid(
            row=5, column=0, padx=(40, 10), pady=12, sticky="w"
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
        screenshot_reminder_checkbox.grid(row=5, column=1, columnspan=2, padx=10, pady=12, sticky="w")

        # ========== 关闭按钮 ==========
        ctk.CTkButton(
            settings_win,
            text=self.lang.get("close"),
            command=settings_win.destroy,
            width=100,
            height=35
        ).grid(row=6, column=0, columnspan=3, pady=(25, 20))

    def _save_language(self, language, parent_win):
        """保存语言设置"""
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
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", "end")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
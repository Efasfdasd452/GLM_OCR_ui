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

        # OCR 引擎
        self.ocr_engine = None
        self.model_loaded = False

        # UI 初始化
        self.setup_window()
        self.create_widgets()

        # 绑定快捷键
        self.bind_shortcuts()

    def setup_window(self):
        """设置窗口"""
        self.title("GLM-OCR GUI")

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
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Logo / 标题
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="GLM-OCR",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 功能按钮
        self.btn_screenshot = ctk.CTkButton(
            self.sidebar,
            text="📸 截图 OCR",
            command=self.screenshot_ocr,
            height=40
        )
        self.btn_screenshot.grid(row=1, column=0, padx=20, pady=10)

        self.btn_clipboard = ctk.CTkButton(
            self.sidebar,
            text="📋 剪贴板 OCR",
            command=self.clipboard_ocr,
            height=40
        )
        self.btn_clipboard.grid(row=2, column=0, padx=20, pady=10)

        self.btn_batch = ctk.CTkButton(
            self.sidebar,
            text="📁 批量 OCR",
            command=self.batch_ocr,
            height=40
        )
        self.btn_batch.grid(row=3, column=0, padx=20, pady=10)

        self.btn_folder = ctk.CTkButton(
            self.sidebar,
            text="📂 文件夹 OCR",
            command=self.folder_ocr,
            height=40
        )
        self.btn_folder.grid(row=4, column=0, padx=20, pady=10)

        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text="⚙️ 设置",
            command=self.open_settings,
            height=40
        )
        self.btn_settings.grid(row=5, column=0, padx=20, pady=10)

        # 模型状态
        self.model_status_label = ctk.CTkLabel(
            self.sidebar,
            text="模型未加载",
            text_color="red"
        )
        self.model_status_label.grid(row=7, column=0, padx=20, pady=(10, 20))

        # 加载/卸载模型按钮
        self.btn_load_model = ctk.CTkButton(
            self.sidebar,
            text="加载模型",
            command=self.toggle_model,
            fg_color="green",
            height=40
        )
        self.btn_load_model.grid(row=8, column=0, padx=20, pady=(10, 20))

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
        self.prompt_label = ctk.CTkLabel(self.control_frame, text="识别类型:")
        self.prompt_label.grid(row=0, column=0, padx=(10, 5), pady=10)

        self.prompt_type = ctk.CTkOptionMenu(
            self.control_frame,
            values=["文本识别", "文档解析", "表格识别", "公式识别", "二维码识别"],
            command=self.on_prompt_change
        )
        self.prompt_type.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # 快速操作按钮
        self.btn_quick_ocr = ctk.CTkButton(
            self.control_frame,
            text="快速识别 (Ctrl+Q)",
            command=self.quick_ocr,
            width=150
        )
        self.btn_quick_ocr.grid(row=0, column=2, padx=5, pady=10)

        self.btn_copy_result = ctk.CTkButton(
            self.control_frame,
            text="复制结果",
            command=self.copy_result,
            width=100
        )
        self.btn_copy_result.grid(row=0, column=3, padx=5, pady=10)

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
            text="点击选择图片或粘贴图片\n支持拖拽图片到此处",
            height=200,
            fg_color="gray85"
        )
        self.image_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # 文件选择按钮
        self.btn_select_image = ctk.CTkButton(
            self.image_frame,
            text="选择图片",
            command=self.select_image
        )
        self.btn_select_image.grid(row=1, column=0, padx=10, pady=(0, 10))

        # 结果显示区
        self.result_label = ctk.CTkLabel(self.tab_single, text="识别结果:")
        self.result_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")

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
            if self.config.get("model.use_local_only"):
                self.ocr_engine = OCREngine(
                    model_path=self.config.get("model.local_path"),
                    device=self.config.get("model.device"),
                    use_local_only=self.config.get("model.use_local_only")
                )
            else:
                self.ocr_engine = OCREngine(
                    model_path=self.config.get("model.name"),
                    device=self.config.get("model.device")
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
        """截图OCR"""
        self.log("截图功能待实现...")
        messagebox.showinfo("提示", "截图功能需要安装额外的截图库")

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
                        max_new_tokens=self.config.get("model.max_new_tokens")
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
                    max_new_tokens=self.config.get("model.max_new_tokens")
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
                max_new_tokens=self.config.get("model.max_new_tokens")
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

    def open_settings(self):
        """打开设置窗口"""
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("设置")
        settings_win.geometry("500x200")
        settings_win.resizable(False, False)
        settings_win.grab_set()

        # 居中显示
        settings_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 200) // 2
        settings_win.geometry(f"+{x}+{y}")

        # 输出目录设置
        ctk.CTkLabel(settings_win, text="输出目录:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=(20, 10), pady=(30, 10), sticky="w"
        )

        output_dir_var = ctk.StringVar(value=self.config.get("batch.output_dir", "./output"))
        output_dir_entry = ctk.CTkEntry(settings_win, textvariable=output_dir_var, width=280)
        output_dir_entry.grid(row=0, column=1, padx=5, pady=(30, 10))

        def browse_output_dir():
            folder = filedialog.askdirectory(title="选择输出目录", parent=settings_win)
            if folder:
                output_dir_var.set(folder)

        ctk.CTkButton(settings_win, text="浏览", command=browse_output_dir, width=80).grid(
            row=0, column=2, padx=(5, 20), pady=(30, 10)
        )

        def save_settings():
            new_dir = output_dir_var.get().strip()
            if not new_dir:
                new_dir = "./output"
            self.config.set("batch.output_dir", new_dir)
            self.config.save_config()
            self.log(f"输出目录已设置为: {new_dir}")
            messagebox.showinfo("提示", f"设置已保存!\n输出目录: {new_dir}", parent=settings_win)

        ctk.CTkButton(settings_win, text="保存设置", command=save_settings, width=120, fg_color="green").grid(
            row=1, column=0, columnspan=3, pady=(20, 10)
        )

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
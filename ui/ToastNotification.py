"""
Toast 通知组件
悬浮气泡提示
"""
import customtkinter as ctk


class ToastNotification:
    """Toast 通知类"""

    @staticmethod
    def show(parent, message, duration=2000, position="bottom"):
        """
        显示 Toast 通知

        Args:
            parent: 父窗口
            message: 提示消息
            duration: 显示时长（毫秒）
            position: 位置 ("top", "bottom", "center")
        """
        # 创建 Toast 窗口
        toast = ctk.CTkToplevel(parent)
        toast.withdraw()  # 先隐藏
        toast.overrideredirect(True)  # 无边框
        toast.attributes("-topmost", True)  # 置顶

        # 设置透明度（Windows）
        try:
            toast.attributes("-alpha", 0.95)
        except:
            pass

        # 创建标签
        label = ctk.CTkLabel(
            toast,
            text=message,
            fg_color=("#2CC985", "#2FA572"),  # 绿色背景
            text_color="white",
            corner_radius=8,
            padx=20,
            pady=12,
            font=ctk.CTkFont(size=13)
        )
        label.pack(padx=2, pady=2)

        # 更新窗口以获取尺寸
        toast.update_idletasks()
        width = toast.winfo_reqwidth()
        height = toast.winfo_reqheight()

        # 计算位置
        parent.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        x = parent_x + (parent_width - width) // 2

        if position == "top":
            y = parent_y + 80
        elif position == "center":
            y = parent_y + (parent_height - height) // 2
        else:  # bottom
            y = parent_y + parent_height - height - 100

        toast.geometry(f"+{x}+{y}")
        toast.deiconify()  # 显示

        # 淡入效果
        def fade_in(alpha=0.0):
            if alpha < 0.95:
                alpha += 0.1
                try:
                    toast.attributes("-alpha", alpha)
                except:
                    pass
                toast.after(20, lambda: fade_in(alpha))

        # 淡出效果
        def fade_out(alpha=0.95):
            if alpha > 0:
                alpha -= 0.1
                try:
                    toast.attributes("-alpha", alpha)
                except:
                    pass
                toast.after(20, lambda: fade_out(alpha))
            else:
                toast.destroy()

        # 启动动画
        fade_in()
        toast.after(duration, fade_out)

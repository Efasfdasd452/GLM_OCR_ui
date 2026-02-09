"""
GLM-OCR GUI 主程序入口
"""
import sys
from pathlib import Path
import os

os.environ["TORCH_DISABLE_TORCH_NP"] = "1"
# 减少 CUDA 显存碎片化
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


def main():
    """主函数"""
    try:
        # 直接导入并创建主窗口
        from ui.MainWindow import MainWindow

        app = MainWindow(base_dir=BASE_DIR)
        app.mainloop()

    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按任意键退出...")


if __name__ == "__main__":
    main()

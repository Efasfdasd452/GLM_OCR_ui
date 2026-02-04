"""
GLM-OCR GUI 主程序入口
"""
import sys
from pathlib import Path
import os
os.environ["TORCH_DISABLE_TORCH_NP"] = "1"


# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.MainWindow import MainWindow


def main():
    """主函数"""
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
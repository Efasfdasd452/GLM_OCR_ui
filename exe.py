"""
PyInstaller 打包配置

注意：将深度学习模型打包成 EXE 会非常大（3-4GB+）
建议使用便携版（Python + 模型文件）分发
"""

# build_exe.py

import PyInstaller.__main__


def build_exe():
    """使用 PyInstaller 打包"""

    # 注意：这会创建一个非常大的 EXE 文件
    PyInstaller.__main__.run([
        'main.py',  # 主程序
        '--name=GLM-OCR',  # 程序名称
        #'--onefile',  # 打包成单个文件（不推荐，太大）
        '--onedir',                       # 推荐：打包成文件夹
        '--windowed',  # 无控制台窗口
        '--icon=icon.ico',  # 图标（如果有）
        '--add-data=models;models',  # 包含模型文件夹
        '--add-data=core;core',  # 包含核心模块
        '--add-data=utils;utils',  # 包含工具模块
        '--add-data=ui;ui',  # 包含界面模块
        '--hidden-import=torch',  # 隐藏导入
        '--hidden-import=transformers',
        '--hidden-import=customtkinter',

    # transformers 相关（关键）
    "--hidden-import=transformers.models.auto.processing_auto",
    "--hidden-import=transformers.models.auto.modeling_auto",
    "--hidden-import=transformers.image_processing_utils",
    "--hidden-import=transformers.image_processing_base",
    "--hidden-import=transformers.image_utils",
        '--hidden-import=PIL',
        '--collect-all=torch',  # 收集所有 torch 文件
        "--exclude-module=torch._numpy",
        "--exclude-module=torch._numpy._ufuncs",
        "--exclude-module=torch._numpy._ndarray",
        '--collect-all=transformers',
        '--noconfirm',  # 覆盖输出
    ])


if __name__ == "__main__":
    print("=" * 60)
    print("PyInstaller 打包工具")
    print("=" * 60)
    print("\n⚠️  警告:")
    print("- 打包后的文件会非常大（3-4GB+）")
    print("- 打包过程需要 10-30 分钟")
    print("- 建议使用便携版（Python + 模型）分发")
    print()

    response = input("确认继续打包？(y/n): ").strip().lower()

    if response == 'y':
        print("\n开始打包...")
        print("这可能需要较长时间，请耐心等待...\n")
        build_exe()
        print("\n✅ 打包完成！")
        print("输出目录: ./dist/GLM-OCR/")
    else:
        print("已取消")

# ============================================
# 推荐的打包方式：便携版
# ============================================

print("""
推荐使用便携版分发方式：

1. 运行导出脚本:
   python export_model.py
   选择 2 - 创建便携版程序包

2. 压缩生成的文件夹:
   GLM-OCR-Portable.zip

3. 分发给用户:
   - 解压即用
   - 无需打包成 EXE
   - 文件更小（压缩后约 1GB）
   - 更新方便

优势对比:

便携版 (推荐):
✅ 文件小（压缩后 ~1GB）
✅ 启动快
✅ 易于更新
✅ 跨平台

EXE 版本:
❌ 文件巨大（3-4GB）
❌ 启动慢
❌ 只支持 Windows
❌ 难以更新
""")
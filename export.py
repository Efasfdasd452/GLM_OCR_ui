"""
模型导出工具
将 HuggingFace 缓存中的模型复制到指定目录
"""
import shutil
from pathlib import Path


def export_model(output_dir="./models/GLM-OCR"):
    """
    导出模型到指定目录

    Args:
        output_dir: 输出目录
    """
    print("=" * 60)
    print("GLM-OCR 模型导出工具")
    print("=" * 60)

    # 源目录（HuggingFace 缓存）
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    source_dir = cache_dir / "models--zai-org--GLM-OCR" / "snapshots"

    if not source_dir.exists():
        print("\n✗ 模型未找到！")
        print(f"缓存目录: {cache_dir}")
        print("\n请确保已经下载过模型:")
        print("python main.py  # 首次运行会自动下载")
        return False

    # 找到最新的快照
    snapshots = list(source_dir.iterdir())
    if not snapshots:
        print("\n✗ 没有找到模型快照")
        return False

    # 使用最新的快照（通常是 main 或最新的 commit）
    snapshot = snapshots[0]
    print(f"\n源目录: {snapshot}")

    # 目标目录
    output_path = Path(output_dir)
    print(f"目标目录: {output_path.absolute()}")

    # 检查目标是否已存在
    if output_path.exists():
        print(f"\n⚠️  目标目录已存在")
        response = input("是否覆盖？(y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            return False
        print("删除旧目录...")
        shutil.rmtree(output_path)

    # 复制文件
    print("\n开始复制模型文件...")
    try:
        shutil.copytree(snapshot, output_path)

        # 验证关键文件
        required_files = [
            "model.safetensors",
            "config.json",
            "tokenizer.json",
            "preprocessor_config.json"
        ]

        print("\n验证文件:")
        all_ok = True
        for filename in required_files:
            file_path = output_path / filename
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {filename:30} ({size_mb:.2f} MB)")
            else:
                print(f"  ✗ {filename:30} (缺失)")
                all_ok = False

        if all_ok:
            print("\n" + "=" * 60)
            print("✅ 模型导出成功！")
            print("=" * 60)
            print(f"\n模型位置: {output_path.absolute()}")

            # 计算总大小
            total_size = sum(f.stat().st_size for f in output_path.rglob("*") if f.is_file())
            print(f"总大小: {total_size / (1024 ** 3):.2f} GB")

            print("\n现在可以:")
            print("1. 将整个项目文件夹打包")
            print("2. 分发给其他人使用")
            print("3. 程序会自动检测并使用本地模型")

            return True
        else:
            print("\n⚠️  部分文件缺失，请检查")
            return False

    except Exception as e:
        print(f"\n✗ 复制失败: {e}")
        return False


def create_portable_package():
    """创建便携版程序包"""
    print("\n" + "=" * 60)
    print("创建便携版程序包")
    print("=" * 60)

    package_dir = Path("./GLM-OCR-Portable")

    print(f"\n输出目录: {package_dir.absolute()}")

    if package_dir.exists():
        print("⚠️  目录已存在，将被覆盖")
        response = input("继续？(y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            return
        shutil.rmtree(package_dir)

    # 创建目录结构
    package_dir.mkdir(parents=True)
    (package_dir / "models").mkdir()
    (package_dir / "output").mkdir()

    # 1. 导出模型
    print("\n步骤 1: 导出模型...")
    if not export_model(package_dir / "models" / "GLM-OCR"):
        print("✗ 模型导出失败")
        return

    # 2. 复制程序文件
    print("\n步骤 2: 复制程序文件...")
    files_to_copy = [
        ("main.py", "主程序"),
        ("requirements.txt", "依赖列表"),
        ("core/", "核心模块"),
        ("utils/", "工具模块"),
        ("ui/", "界面模块"),
    ]

    for src, desc in files_to_copy:
        src_path = Path(src)
        if not src_path.exists():
            print(f"  ⚠️  {src} 不存在，跳过")
            continue

        dst_path = package_dir / src

        if src_path.is_dir():
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            print(f"  ✓ {desc}: {src}")
        else:
            shutil.copy2(src_path, dst_path)
            print(f"  ✓ {desc}: {src}")

    # 3. 创建使用说明
    print("\n步骤 3: 创建使用说明...")
    readme = """# GLM-OCR 便携版使用说明

## 快速开始

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行程序：
   ```
   python main.py
   ```

3. 程序会自动检测并使用 models/GLM-OCR 中的模型

## 目录结构

```
GLM-OCR-Portable/
├── main.py              # 主程序
├── requirements.txt     # 依赖列表
├── models/              # 模型文件夹
│   └── GLM-OCR/        # 本地模型（已包含）
├── core/               # 核心模块
├── utils/              # 工具模块
├── ui/                 # 界面模块
└── output/             # 输出目录
```

## 系统要求

- Python 3.8+
- 8GB+ RAM
- 5GB+ 硬盘空间
- （可选）NVIDIA GPU

## 注意事项

- 首次运行需要安装依赖
- 模型已包含在程序包中，无需下载
- 完全离线可用

## 常见问题

Q: 如何使用 GPU 加速？
A: 确保安装了 CUDA 和 PyTorch GPU 版本

Q: 占用多少空间？
A: 约 3-4GB（包含模型）

Q: 可以删除模型文件夹吗？
A: 不可以，程序需要加载模型才能运行
"""

    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme)
    print("  ✓ README.txt")

    # 4. 创建启动脚本
    print("\n步骤 4: 创建启动脚本...")

    # Windows 批处理
    bat_script = """@echo off
echo Starting GLM-OCR...
python main.py
pause
"""
    with open(package_dir / "start.bat", "w", encoding="utf-8") as f:
        f.write(bat_script)
    print("  ✓ start.bat (Windows)")

    # Linux/Mac shell 脚本
    sh_script = """#!/bin/bash
echo "Starting GLM-OCR..."
python3 main.py
"""
    with open(package_dir / "start.sh", "w", encoding="utf-8") as f:
        f.write(sh_script)
    print("  ✓ start.sh (Linux/Mac)")

    print("\n" + "=" * 60)
    print("✅ 便携版程序包创建完成！")
    print("=" * 60)
    print(f"\n位置: {package_dir.absolute()}")

    # 计算总大小
    total_size = sum(f.stat().st_size for f in package_dir.rglob("*") if f.is_file())
    print(f"大小: {total_size / (1024 ** 3):.2f} GB")

    print("\n现在可以:")
    print("1. 压缩整个文件夹: GLM-OCR-Portable.zip")
    print("2. 分发给其他人")
    print("3. 解压后直接运行 start.bat (Windows) 或 start.sh (Linux/Mac)")


if __name__ == "__main__":
    print("\nGLM-OCR 模型导出工具\n")
    print("选择操作:")
    print("1. 仅导出模型到 ./models/GLM-OCR")
    print("2. 创建完整的便携版程序包")
    print("3. 退出")

    choice = input("\n请选择 (1-3): ").strip()

    if choice == "1":
        export_model()
    elif choice == "2":
        create_portable_package()
    elif choice == "3":
        print("再见！")
    else:
        print("无效选择")
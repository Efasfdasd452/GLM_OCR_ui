"""
GLM-OCR 测试脚本（修正版）
使用 trust_remote_code=True 加载模型
"""
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def test_model_loading():
    """测试模型加载"""
    print("=" * 60)
    print("测试 1: 模型加载")
    print("=" * 60)

    try:
        MODEL_PATH = "zai-org/GLM-OCR"

        print(f"正在加载处理器...")
        # 关键：添加 trust_remote_code=True
        processor = AutoProcessor.from_pretrained(
            MODEL_PATH
        )
        print(f"✓ 处理器加载成功")

        print(f"正在加载模型...")
        model = AutoModelForImageTextToText.from_pretrained(
            pretrained_model_name_or_path=MODEL_PATH,
            torch_dtype="auto",
            device_map="auto",
        )
        print(f"✓ 模型加载成功")
        print(f"✓ 设备: {model.device}")
        print(f"✓ 数据类型: {model.dtype}")

        return processor, model

    except Exception as e:
        print(f"✗ 加载失败: {e}")
        print(f"\n请确保:")
        print(f"1. 已安装最新版 transformers:")
        print(f"   pip install git+https://github.com/huggingface/transformers.git")
        print(f"2. 模型文件已下载到缓存目录")
        import traceback
        traceback.print_exc()
        return None, None


def create_test_image():
    """创建测试图片"""
    print("创建测试图片...")

    # 创建一个白色背景的图片
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体
    try:
        # Windows
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 30)
    except:
        try:
            # Linux
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except:
            # 使用默认字体
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

    # 写入文字
    draw.text((50, 80), "Hello World!", fill='black', font=font_large)
    draw.text((50, 180), "GLM-OCR Test", fill='blue', font=font_large)
    draw.text((50, 280), "这是一个测试图片", fill='red', font=font_small)

    test_image_path = "test_image.png"
    img.save(test_image_path)
    print(f"✓ 测试图片已创建: {test_image_path}")

    return test_image_path


def test_image_recognition(processor, model, test_image_path=None):
    """测试图片识别"""
    print("\n" + "=" * 60)
    print("测试 2: 图片识别")
    print("=" * 60)

    if processor is None or model is None:
        print("✗ 模型未加载，跳过测试")
        return None

    try:
        # 如果没有提供测试图片，创建一个
        if test_image_path is None or not Path(test_image_path).exists():
            test_image_path = create_test_image()

        print(f"\n正在识别图片: {test_image_path}")

        # 按官方文档方式构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "url": test_image_path
                    },
                    {
                        "type": "text",
                        "text": "Text Recognition:"
                    }
                ],
            }
        ]

        # 处理输入
        print("正在处理输入...")
        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        ).to(model.device)

        inputs.pop("token_type_ids", None)

        # 生成结果
        print("正在生成识别结果（这可能需要几秒钟）...")
        generated_ids = model.generate(**inputs, max_new_tokens=1024)

        # 解码输出
        output_text = processor.decode(
            generated_ids[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=False
        )

        print(f"\n✓ 识别完成！")
        print(f"=" * 60)
        print(f"识别结果:")
        print(f"-" * 60)
        print(output_text)
        print(f"=" * 60)

        return output_text

    except Exception as e:
        print(f"✗ 识别失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主测试函数"""
    print("\n")
    print("=" * 60)
    print("GLM-OCR 模型测试（修正版）")
    print("=" * 60)
    print()

    # 检查版本
    import transformers
    print(f"Transformers 版本: {transformers.__version__}")
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA 版本: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    print()

    # 测试 1: 加载模型
    processor, model = test_model_loading()

    if processor is None or model is None:
        print("\n❌ 测试失败：无法加载模型")
        print("\n请确保:")
        print("1. pip install git+https://github.com/huggingface/transformers.git")
        print("2. 模型文件已完整下载")
        return

    # 测试 2: 识别图片
    result = test_image_recognition(processor, model)

    if result is None:
        print("\n❌ 测试失败：无法识别图片")
        return

    print("\n" + "=" * 60)
    print("✅ 测试通过！")
    print("=" * 60)
    print("\n模型工作正常，现在可以运行主程序:")
    print("python main.py")


if __name__ == "__main__":
    main()

     ===========================================                                                                                                                 
       GLM-OCR 配置说明 (config.json)                                                                                                                         
  ===========================================

  【模型设置 model】

    name          HuggingFace 模型名称
                  默认: zai-org/GLM-OCR
                  仅在 use_local_only 为 false 时生效

    local_path    本地模型文件夹路径（优先级高于 name）
                  默认: ./models/GLM-OCR
                  支持相对路径或绝对路径
                  示例: D:/my_models/GLM-OCR

    device        运行设备
                  auto  - 自动选择（有显卡用显卡，没有用CPU）
                  cuda  - 强制使用显卡
                  cpu   - 强制使用CPU

    torch_dtype   模型精度
                  float16 - 半精度（推荐，省显存）
                  auto    - 自动选择
                  float32 - 全精度（更准但占用翻倍）

    max_new_tokens  最大生成字数
                    默认: 2048
                    识别长文档时可适当增大

    use_local_only  是否仅使用本地模型
                    true  - 离线模式，不连接网络（推荐）
                    false - 允许从 HuggingFace 在线下载

  【识别设置 ocr】

    language      识别语言
                  默认: 简体中文

    prompt_type   默认识别类型
                  text_recognition - 文本识别
                  document_parsing - 文档解析
                  table_recognition - 表格识别
                  formula_recognition - 公式识别

    output_format 输出格式
                  txt      - 纯文本
                  json     - JSON（含时间等元数据）
                  markdown - Markdown 格式

  【批量处理 batch】

    output_dir       结果保存目录
                     默认: ./output
                     示例: D:/OCR结果

    recursive        是否扫描子文件夹
                     true / false

    filename_format  输出文件名格式
                     {name} = 原文件名, {date} = 日期时间
                     默认: [OCR]_{name}_{date}

    date_format      日期格式
                     默认: %Y%m%d_%H%M%S
                     效果: 20260204_153012

  【界面设置 ui】

    theme         主题: light（浅色）/ dark（深色）
    font_size     字体大小，默认 12
    window_size   窗口尺寸，默认 1200x800
    
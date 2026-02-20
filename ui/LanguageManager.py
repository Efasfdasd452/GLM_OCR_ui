"""
多语言管理器
"""


class LanguageManager:
    """语言管理类"""

    # 所有支持的语言
    LANGUAGES = {
        "简体中文": "zh_CN",
        "繁體中文（香港）": "zh_HK",
        "繁體中文（台灣）": "zh_TW",
        "English": "en",
        "Français": "fr",
        "Deutsch": "de",
        "日本語": "ja",
        "Italiano": "it",
        "Русский": "ru"
    }

    # 多语言文本字典
    TRANSLATIONS = {
        # ========== 主窗口 ==========
        "window_title": {
            "zh_CN": "GLM-OCR GUI",
            "zh_HK": "GLM-OCR 圖形界面",
            "zh_TW": "GLM-OCR 圖形介面",
            "en": "GLM-OCR GUI",
            "fr": "GLM-OCR Interface",
            "de": "GLM-OCR Oberfläche",
            "ja": "GLM-OCR GUI",
            "it": "GLM-OCR Interfaccia",
            "ru": "GLM-OCR Интерфейс"
        },

        # ========== 侧边栏 ==========
        "screenshot_ocr": {
            "zh_CN": "📸 截图 OCR",
            "zh_HK": "📸 截圖 OCR",
            "zh_TW": "📸 截圖 OCR",
            "en": "📸 Screenshot OCR",
            "fr": "📸 Capture OCR",
            "de": "📸 Screenshot OCR",
            "ja": "📸 スクリーンショット OCR",
            "it": "📸 Screenshot OCR",
            "ru": "📸 Скриншот OCR"
        },
        "clipboard_ocr": {
            "zh_CN": "📋 剪贴板 OCR",
            "zh_HK": "📋 剪貼板 OCR",
            "zh_TW": "📋 剪貼簿 OCR",
            "en": "📋 Clipboard OCR",
            "fr": "📋 Presse-papiers OCR",
            "de": "📋 Zwischenablage OCR",
            "ja": "📋 クリップボード OCR",
            "it": "📋 Appunti OCR",
            "ru": "📋 Буфер обмена OCR"
        },
        "batch_ocr": {
            "zh_CN": "📁 批量 OCR",
            "zh_HK": "📁 批量 OCR",
            "zh_TW": "📁 批次 OCR",
            "en": "📁 Batch OCR",
            "fr": "📁 OCR par lots",
            "de": "📁 Stapel-OCR",
            "ja": "📁 一括 OCR",
            "it": "📁 OCR batch",
            "ru": "📁 Пакетный OCR"
        },
        "folder_ocr": {
            "zh_CN": "📂 文件夹 OCR",
            "zh_HK": "📂 資料夾 OCR",
            "zh_TW": "📂 資料夾 OCR",
            "en": "📂 Folder OCR",
            "fr": "📂 Dossier OCR",
            "de": "📂 Ordner OCR",
            "ja": "📂 フォルダ OCR",
            "it": "📂 Cartella OCR",
            "ru": "📂 Папка OCR"
        },
        "document_ocr": {
            "zh_CN": "📄 文档 OCR",
            "zh_HK": "📄 文檔 OCR",
            "zh_TW": "📄 文件 OCR",
            "en": "📄 Document OCR",
            "fr": "📄 Document OCR",
            "de": "📄 Dokument OCR",
            "ja": "📄 ドキュメント OCR",
            "it": "📄 Documento OCR",
            "ru": "📄 Документ OCR"
        },
        "settings": {
            "zh_CN": "⚙️ 设置",
            "zh_HK": "⚙️ 設定",
            "zh_TW": "⚙️ 設定",
            "en": "⚙️ Settings",
            "fr": "⚙️ Paramètres",
            "de": "⚙️ Einstellungen",
            "ja": "⚙️ 設定",
            "it": "⚙️ Impostazioni",
            "ru": "⚙️ Настройки"
        },
        "model_not_loaded": {
            "zh_CN": "模型未加载",
            "zh_HK": "模型未載入",
            "zh_TW": "模型未載入",
            "en": "Model Not Loaded",
            "fr": "Modèle non chargé",
            "de": "Modell nicht geladen",
            "ja": "モデル未ロード",
            "it": "Modello non caricato",
            "ru": "Модель не загружена"
        },
        "model_loaded": {
            "zh_CN": "模型已加载",
            "zh_HK": "模型已載入",
            "zh_TW": "模型已載入",
            "en": "Model Loaded",
            "fr": "Modèle chargé",
            "de": "Modell geladen",
            "ja": "モデルロード済み",
            "it": "Modello caricato",
            "ru": "Модель загружена"
        },
        "load_model": {
            "zh_CN": "加载模型",
            "zh_HK": "載入模型",
            "zh_TW": "載入模型",
            "en": "Load Model",
            "fr": "Charger le modèle",
            "de": "Modell laden",
            "ja": "モデルをロード",
            "it": "Carica modello",
            "ru": "Загрузить модель"
        },
        "unload_model": {
            "zh_CN": "卸载模型",
            "zh_HK": "卸載模型",
            "zh_TW": "卸載模型",
            "en": "Unload Model",
            "fr": "Décharger le modèle",
            "de": "Modell entladen",
            "ja": "モデルをアンロード",
            "it": "Scarica modello",
            "ru": "Выгрузить модель"
        },

        # ========== 控制栏 ==========
        "recognition_type": {
            "zh_CN": "识别类型:",
            "zh_HK": "識別類型:",
            "zh_TW": "識別類型:",
            "en": "Recognition Type:",
            "fr": "Type de reconnaissance:",
            "de": "Erkennungstyp:",
            "ja": "認識タイプ:",
            "it": "Tipo di riconoscimento:",
            "ru": "Тип распознавания:"
        },
        "text_recognition": {
            "zh_CN": "文本识别",
            "zh_HK": "文本識別",
            "zh_TW": "文字識別",
            "en": "Text Recognition",
            "fr": "Reconnaissance de texte",
            "de": "Texterkennung",
            "ja": "テキスト認識",
            "it": "Riconoscimento testo",
            "ru": "Распознавание текста"
        },
        "document_parsing": {
            "zh_CN": "文档解析",
            "zh_HK": "文檔解析",
            "zh_TW": "文件解析",
            "en": "Document Parsing",
            "fr": "Analyse de document",
            "de": "Dokumentenanalyse",
            "ja": "ドキュメント解析",
            "it": "Analisi documento",
            "ru": "Анализ документа"
        },
        "table_recognition": {
            "zh_CN": "表格识别",
            "zh_HK": "表格識別",
            "zh_TW": "表格識別",
            "en": "Table Recognition",
            "fr": "Reconnaissance de tableau",
            "de": "Tabellenerkennung",
            "ja": "表認識",
            "it": "Riconoscimento tabella",
            "ru": "Распознавание таблиц"
        },
        "formula_recognition": {
            "zh_CN": "公式识别",
            "zh_HK": "公式識別",
            "zh_TW": "公式識別",
            "en": "Formula Recognition",
            "fr": "Reconnaissance de formule",
            "de": "Formelerkennung",
            "ja": "数式認識",
            "it": "Riconoscimento formula",
            "ru": "Распознавание формул"
        },
        "qrcode_recognition": {
            "zh_CN": "二维码识别",
            "zh_HK": "二維碼識別",
            "zh_TW": "QR碼識別",
            "en": "QR Code Recognition",
            "fr": "Reconnaissance QR code",
            "de": "QR-Code-Erkennung",
            "ja": "QRコード認識",
            "it": "Riconoscimento QR code",
            "ru": "Распознавание QR-кода"
        },
        "token_count": {
            "zh_CN": "Token数:",
            "zh_HK": "Token數:",
            "zh_TW": "Token數:",
            "en": "Token Count:",
            "fr": "Nombre de tokens:",
            "de": "Token-Anzahl:",
            "ja": "トークン数:",
            "it": "Conteggio token:",
            "ru": "Количество токенов:"
        },

        # ========== 按钮 ==========
        "quick_recognition": {
            "zh_CN": "⚡ 快速识别 (Ctrl+Q)",
            "zh_HK": "⚡ 快速識別 (Ctrl+Q)",
            "zh_TW": "⚡ 快速識別 (Ctrl+Q)",
            "en": "⚡ Quick Recognition (Ctrl+Q)",
            "fr": "⚡ Reconnaissance rapide (Ctrl+Q)",
            "de": "⚡ Schnellerkennung (Ctrl+Q)",
            "ja": "⚡ クイック認識 (Ctrl+Q)",
            "it": "⚡ Riconoscimento rapido (Ctrl+Q)",
            "ru": "⚡ Быстрое распознавание (Ctrl+Q)"
        },
        "copy_result": {
            "zh_CN": "📋 复制结果",
            "zh_HK": "📋 複製結果",
            "zh_TW": "📋 複製結果",
            "en": "📋 Copy Result",
            "fr": "📋 Copier le résultat",
            "de": "📋 Ergebnis kopieren",
            "ja": "📋 結果をコピー",
            "it": "📋 Copia risultato",
            "ru": "📋 Копировать результат"
        },
        "fix_formula": {
            "zh_CN": "🔧 修复公式",
            "zh_HK": "🔧 修復公式",
            "zh_TW": "🔧 修復公式",
            "en": "🔧 Fix Formula",
            "fr": "🔧 Corriger la formule",
            "de": "🔧 Formel korrigieren",
            "ja": "🔧 数式を修正",
            "it": "🔧 Correggi formula",
            "ru": "🔧 Исправить формулу"
        },
        "select_image": {
            "zh_CN": "选择图片",
            "zh_HK": "選擇圖片",
            "zh_TW": "選擇圖片",
            "en": "Select Image",
            "fr": "Sélectionner une image",
            "de": "Bild auswählen",
            "ja": "画像を選択",
            "it": "Seleziona immagine",
            "ru": "Выбрать изображение"
        },

        # ========== 标签页 ==========
        "tab_single_ocr": {
            "zh_CN": "单图OCR",
            "zh_HK": "單圖OCR",
            "zh_TW": "單圖OCR",
            "en": "Single OCR",
            "fr": "OCR unique",
            "de": "Einzel-OCR",
            "ja": "単一OCR",
            "it": "OCR singolo",
            "ru": "Одиночный OCR"
        },
        "tab_batch_ocr": {
            "zh_CN": "批量OCR",
            "zh_HK": "批量OCR",
            "zh_TW": "批次OCR",
            "en": "Batch OCR",
            "fr": "OCR par lots",
            "de": "Stapel-OCR",
            "ja": "一括OCR",
            "it": "OCR batch",
            "ru": "Пакетный OCR"
        },
        "tab_pdf_ocr": {
            "zh_CN": "PDF OCR",
            "zh_HK": "PDF OCR",
            "zh_TW": "PDF OCR",
            "en": "PDF OCR",
            "fr": "OCR PDF",
            "de": "PDF-OCR",
            "ja": "PDF OCR",
            "it": "OCR PDF",
            "ru": "PDF OCR"
        },
        "tab_qrcode_gen": {
            "zh_CN": "二维码生成",
            "zh_HK": "二維碼生成",
            "zh_TW": "QR碼生成",
            "en": "QR Code Generator",
            "fr": "Générateur QR code",
            "de": "QR-Code-Generator",
            "ja": "QRコード生成",
            "it": "Generatore QR code",
            "ru": "Генератор QR-кода"
        },
        "tab_log": {
            "zh_CN": "日志",
            "zh_HK": "日誌",
            "zh_TW": "日誌",
            "en": "Log",
            "fr": "Journal",
            "de": "Protokoll",
            "ja": "ログ",
            "it": "Registro",
            "ru": "Журнал"
        },

        # ========== 标签 ==========
        "recognition_result": {
            "zh_CN": "识别结果:",
            "zh_HK": "識別結果:",
            "zh_TW": "識別結果:",
            "en": "Recognition Result:",
            "fr": "Résultat de reconnaissance:",
            "de": "Erkennungsergebnis:",
            "ja": "認識結果:",
            "it": "Risultato riconoscimento:",
            "ru": "Результат распознавания:"
        },
        "image_preview_hint": {
            "zh_CN": "点击选择图片或粘贴图片\n支持拖拽图片到此处",
            "zh_HK": "點擊選擇圖片或貼上圖片\n支援拖曳圖片到此處",
            "zh_TW": "點擊選擇圖片或貼上圖片\n支援拖曳圖片到此處",
            "en": "Click to select or paste image\nDrag and drop supported",
            "fr": "Cliquez pour sélectionner ou coller une image\nGlisser-déposer pris en charge",
            "de": "Klicken Sie, um ein Bild auszuwählen oder einzufügen\nDrag & Drop unterstützt",
            "ja": "画像を選択または貼り付けるにはクリック\nドラッグ＆ドロップ対応",
            "it": "Clicca per selezionare o incollare un'immagine\nTrascina e rilascia supportato",
            "ru": "Нажмите, чтобы выбрать или вставить изображение\nПоддерживается перетаскивание"
        },

        # ========== 设置窗口 ==========
        "settings_title": {
            "zh_CN": "⚙️ 设置",
            "zh_HK": "⚙️ 設定",
            "zh_TW": "⚙️ 設定",
            "en": "⚙️ Settings",
            "fr": "⚙️ Paramètres",
            "de": "⚙️ Einstellungen",
            "ja": "⚙️ 設定",
            "it": "⚙️ Impostazioni",
            "ru": "⚙️ Настройки"
        },
        "auto_save_hint": {
            "zh_CN": "修改后自动保存",
            "zh_HK": "修改後自動儲存",
            "zh_TW": "修改後自動儲存",
            "en": "Auto-save after modification",
            "fr": "Sauvegarde automatique après modification",
            "de": "Automatisches Speichern nach Änderung",
            "ja": "変更後自動保存",
            "it": "Salvataggio automatico dopo la modifica",
            "ru": "Автосохранение после изменения"
        },
        "interface_language": {
            "zh_CN": "界面语言:",
            "zh_HK": "介面語言:",
            "zh_TW": "介面語言:",
            "en": "Interface Language:",
            "fr": "Langue de l'interface:",
            "de": "Oberflächensprache:",
            "ja": "インターフェース言語:",
            "it": "Lingua interfaccia:",
            "ru": "Язык интерфейса:"
        },
        "batch_output_path": {
            "zh_CN": "输出路径:",
            "zh_HK": "輸出路徑:",
            "zh_TW": "輸出路徑:",
            "en": "Output path:",
            "fr": "Chemin de sortie:",
            "de": "Ausgabepfad:",
            "ja": "出力先:",
            "it": "Percorso output:",
            "ru": "Путь вывода:"
        },
        "batch_save_mode": {
            "zh_CN": "输出方式:",
            "zh_HK": "輸出方式:",
            "zh_TW": "輸出方式:",
            "en": "Output format:",
            "fr": "Format de sortie:",
            "de": "Ausgabeformat:",
            "ja": "出力形式:",
            "it": "Formato output:",
            "ru": "Формат вывода:"
        },
        "batch_save_single_md": {
            "zh_CN": "每个结果 → Markdown 文件 (.md)",
            "zh_HK": "每個結果 → Markdown 檔案 (.md)",
            "zh_TW": "每個結果 → Markdown 檔案 (.md)",
            "en": "Each result → Markdown (.md)",
            "fr": "Chaque résultat → Markdown (.md)",
            "de": "Jedes Ergebnis → Markdown (.md)",
            "ja": "各結果 → Markdown (.md)",
            "it": "Ogni risultato → Markdown (.md)",
            "ru": "Каждый результат → Markdown (.md)"
        },
        "batch_save_single_txt": {
            "zh_CN": "每个结果 → 文本文件 (.txt)",
            "zh_HK": "每個結果 → 文字檔 (.txt)",
            "zh_TW": "每個結果 → 文字檔 (.txt)",
            "en": "Each result → Text (.txt)",
            "fr": "Chaque résultat → Texte (.txt)",
            "de": "Jedes Ergebnis → Text (.txt)",
            "ja": "各結果 → テキスト (.txt)",
            "it": "Ogni risultato → Testo (.txt)",
            "ru": "Каждый результат → Текст (.txt)"
        },
        "batch_save_zip_md": {
            "zh_CN": "全部 → 一个 ZIP，内为 Markdown (.md)",
            "zh_HK": "全部 → 一個 ZIP，內為 Markdown (.md)",
            "zh_TW": "全部 → 一個 ZIP，內為 Markdown (.md)",
            "en": "All → one ZIP with Markdown (.md)",
            "fr": "Tout → un ZIP en Markdown (.md)",
            "de": "Alle → eine ZIP mit Markdown (.md)",
            "ja": "全て → 1つのZIP（中身は.md）",
            "it": "Tutti → un ZIP con Markdown (.md)",
            "ru": "Всё → один ZIP с Markdown (.md)"
        },
        "batch_save_zip_txt": {
            "zh_CN": "全部 → 一个 ZIP，内为文本 (.txt)",
            "zh_HK": "全部 → 一個 ZIP，內為文字 (.txt)",
            "zh_TW": "全部 → 一個 ZIP，內為文字 (.txt)",
            "en": "All → one ZIP with Text (.txt)",
            "fr": "Tout → un ZIP en Texte (.txt)",
            "de": "Alle → eine ZIP mit Text (.txt)",
            "ja": "全て → 1つのZIP（中身は.txt）",
            "it": "Tutti → un ZIP con Testo (.txt)",
            "ru": "Всё → один ZIP с текстом (.txt)"
        },
        "batch_save_single_pdf": {
            "zh_CN": "全部 → 一个 PDF（每页一个结果）",
            "zh_HK": "全部 → 一個 PDF（每頁一個結果）",
            "zh_TW": "全部 → 一個 PDF（每頁一個結果）",
            "en": "All → one PDF (one result per page)",
            "fr": "Tout → un PDF (un résultat par page)",
            "de": "Alle → ein PDF (ein Ergebnis pro Seite)",
            "ja": "全て → 1つのPDF（1結果1ページ）",
            "it": "Tutti → un PDF (un risultato per pagina)",
            "ru": "Всё → один PDF (один результат на страницу)"
        },
        "output_directory": {
            "zh_CN": "输出目录:",
            "zh_HK": "輸出目錄:",
            "zh_TW": "輸出目錄:",
            "en": "Output Directory:",
            "fr": "Répertoire de sortie:",
            "de": "Ausgabeverzeichnis:",
            "ja": "出力ディレクトリ:",
            "it": "Directory di output:",
            "ru": "Выходной каталог:"
        },
        "performance_mode_label": {
            "zh_CN": "推理模式:",
            "zh_HK": "推理模式:",
            "zh_TW": "推理模式:",
            "en": "Inference Mode:",
            "fr": "Mode d'inférence:",
            "de": "Inferenzmodus:",
            "ja": "推論モード:",
            "it": "Modalità inferenza:",
            "ru": "Режим вывода:"
        },
        "performance_mode_accurate_fast": {
            "zh_CN": "高显存·快速·高精度",
            "zh_HK": "高顯存·快速·高精度",
            "zh_TW": "高顯存·快速·高精度",
            "en": "High VRAM · Fast · Accurate",
            "fr": "VRAM élevée · Rapide · Précise",
            "de": "Hoher VRAM · Schnell · Genau",
            "ja": "高VRAM·高速·高精度",
            "it": "Alto VRAM · Veloce · Accurato",
            "ru": "Больше VRAM · Быстро · Точно"
        },
        "performance_mode_accurate_save": {
            "zh_CN": "低显存·省资源·高精度",
            "zh_HK": "低顯存·省資源·高精度",
            "zh_TW": "低顯存·省資源·高精度",
            "en": "Low VRAM · Save Resources · Accurate",
            "fr": "VRAM faible · Économiser · Précise",
            "de": "Wenig VRAM · Ressourcenschonend · Genau",
            "ja": "低VRAM·省リソース·高精度",
            "it": "Basso VRAM · Risparmio · Accurato",
            "ru": "Меньше VRAM · Экономия · Точно"
        },
        "performance_mode_fast_save": {
            "zh_CN": "低显存·快速·一般精度",
            "zh_HK": "低顯存·快速·一般精度",
            "zh_TW": "低顯存·快速·一般精度",
            "en": "Low VRAM · Fast · Lower Accuracy",
            "fr": "VRAM faible · Rapide · Précision moindre",
            "de": "Wenig VRAM · Schnell · Geringere Genauigkeit",
            "ja": "低VRAM·高速·やや精度低下",
            "it": "Basso VRAM · Veloce · Precisione minore",
            "ru": "Меньше VRAM · Быстро · Ниже точность"
        },
        "performance_mode_reload_hint": {
            "zh_CN": "切换后需重新加载模型生效",
            "zh_HK": "切換後需重新載入模型生效",
            "zh_TW": "切換後需重新載入模型生效",
            "en": "Reload model to apply",
            "fr": "Recharger le modèle pour appliquer",
            "de": "Modell neu laden zum Übernehmen",
            "ja": "適用にはモデルの再読み込みが必要",
            "it": "Ricarica il modello per applicare",
            "ru": "Перезагрузите модель для применения"
        },
        "performance_mode_token_hint": {
            "zh_CN": "Token 按模式限制：高显存 4096～8192，省显存·高精度 2048～4096，快速省显存 1024～2048",
            "zh_HK": "Token 依模式限制：高顯存 4096～8192，省顯存·高精度 2048～4096，快速省顯存 1024～2048",
            "zh_TW": "Token 依模式限制：高顯存 4096～8192，省顯存·高精度 2048～4096，快速省顯存 1024～2048",
            "en": "Token by mode: High VRAM 4096–8192, Save+Accurate 2048–4096, Fast Save 1024–2048",
            "fr": "Token par mode : High VRAM 4096–8192, Écon+Précise 2048–4096, Rapide 1024–2048",
            "de": "Token nach Modus: High VRAM 4096–8192, Sparsam+Genau 2048–4096, Schnell 1024–2048",
            "ja": "Tokenはモードで制限：高VRAM 4096～8192、省・高精度 2048～4096、高速省 1024～2048",
            "it": "Token per modo: High VRAM 4096–8192, Risparmio+Accurato 2048–4096, Veloce 1024–2048",
            "ru": "Token по режиму: High VRAM 4096–8192, Эконом+Точно 2048–4096, Быстро 1024–2048"
        },
        "max_token_limit": {
            "zh_CN": "最大 Token 限制:",
            "zh_HK": "最大 Token 限制:",
            "zh_TW": "最大 Token 限制:",
            "en": "Max Token Limit:",
            "fr": "Limite de tokens max:",
            "de": "Max. Token-Limit:",
            "ja": "最大トークン制限:",
            "it": "Limite token massimo:",
            "ru": "Макс. лимит токенов:"
        },
        "screenshot_prompt": {
            "zh_CN": "截图提示:",
            "zh_HK": "截圖提示:",
            "zh_TW": "截圖提示:",
            "en": "Screenshot Prompt:",
            "fr": "Invite de capture:",
            "de": "Screenshot-Eingabeaufforderung:",
            "ja": "スクリーンショットプロンプト:",
            "it": "Prompt screenshot:",
            "ru": "Подсказка скриншота:"
        },
        "show_screenshot_success": {
            "zh_CN": "显示截图成功提示",
            "zh_HK": "顯示截圖成功提示",
            "zh_TW": "顯示截圖成功提示",
            "en": "Show screenshot success prompt",
            "fr": "Afficher l'invite de réussite de capture",
            "de": "Screenshot-Erfolg anzeigen",
            "ja": "スクリーンショット成功を表示",
            "it": "Mostra prompt successo screenshot",
            "ru": "Показать успех скриншота"
        },
        "browse": {
            "zh_CN": "浏览",
            "zh_HK": "瀏覽",
            "zh_TW": "瀏覽",
            "en": "Browse",
            "fr": "Parcourir",
            "de": "Durchsuchen",
            "ja": "参照",
            "it": "Sfoglia",
            "ru": "Обзор"
        },
        "close": {
            "zh_CN": "关闭",
            "zh_HK": "關閉",
            "zh_TW": "關閉",
            "en": "Close",
            "fr": "Fermer",
            "de": "Schließen",
            "ja": "閉じる",
            "it": "Chiudi",
            "ru": "Закрыть"
        },

        # ========== 截图界面提示 ==========
        "screenshot_hint": {
            "zh_CN": "拖拽鼠标选择截图区域  |  按 ESC 取消  |  提示: Ctrl+Shift+S 可快速截图哦~",
            "zh_HK": "拖曳滑鼠選擇截圖區域  |  按 ESC 取消  |  提示: Ctrl+Shift+S 可快速截圖哦~",
            "zh_TW": "拖曳滑鼠選擇截圖區域  |  按 ESC 取消  |  提示: Ctrl+Shift+S 可快速截圖哦~",
            "en": "Drag to select area  |  Press ESC to cancel  |  Tip: Ctrl+Shift+S for quick screenshot",
            "fr": "Faites glisser pour sélectionner  |  ESC pour annuler  |  Astuce: Ctrl+Shift+S pour capture rapide",
            "de": "Ziehen Sie, um auszuwählen  |  ESC zum Abbrechen  |  Tipp: Ctrl+Shift+S für schnellen Screenshot",
            "ja": "ドラッグして範囲を選択  |  ESC でキャンセル  |  ヒント: Ctrl+Shift+S で素早くスクリーンショット",
            "it": "Trascina per selezionare  |  ESC per annullare  |  Suggerimento: Ctrl+Shift+S per screenshot veloce",
            "ru": "Перетащите для выбора  |  ESC для отмены  |  Совет: Ctrl+Shift+S для быстрого скриншота"
        },

        # ========== 截图成功对话框 ==========
        "screenshot_success_title": {
            "zh_CN": "✓ 截图成功",
            "zh_HK": "✓ 截圖成功",
            "zh_TW": "✓ 截圖成功",
            "en": "✓ Screenshot Success",
            "fr": "✓ Capture réussie",
            "de": "✓ Screenshot erfolgreich",
            "ja": "✓ スクリーンショット成功",
            "it": "✓ Screenshot riuscito",
            "ru": "✓ Скриншот успешен"
        },
        "screenshot_success_message": {
            "zh_CN": "截图已保存到:\n{0}\n\n同时已复制到剪贴板。\n\n提示: 下次可以直接按 Ctrl+Shift+S 快速截图哦~",
            "zh_HK": "截圖已儲存到:\n{0}\n\n同時已複製到剪貼板。\n\n提示: 下次可以直接按 Ctrl+Shift+S 快速截圖哦~",
            "zh_TW": "截圖已儲存到:\n{0}\n\n同時已複製到剪貼簿。\n\n提示: 下次可以直接按 Ctrl+Shift+S 快速截圖哦~",
            "en": "Screenshot saved to:\n{0}\n\nAlso copied to clipboard.\n\nTip: Press Ctrl+Shift+S for quick screenshot next time~",
            "fr": "Capture enregistrée dans:\n{0}\n\nÉgalement copié dans le presse-papiers.\n\nAstuce: Appuyez sur Ctrl+Shift+S pour une capture rapide~",
            "de": "Screenshot gespeichert unter:\n{0}\n\nAuch in Zwischenablage kopiert.\n\nTipp: Drücken Sie Ctrl+Shift+S für schnellen Screenshot~",
            "ja": "スクリーンショットの保存先:\n{0}\n\nクリップボードにもコピーされました。\n\nヒント: 次回はCtrl+Shift+Sで素早くスクリーンショット~",
            "it": "Screenshot salvato in:\n{0}\n\nAnche copiato negli appunti.\n\nSuggerimento: Premi Ctrl+Shift+S per screenshot veloce~",
            "ru": "Скриншот сохранен в:\n{0}\n\nТакже скопировано в буфер обмена.\n\nСовет: Нажмите Ctrl+Shift+S для быстрого скриншота~"
        },
        "dont_show_again": {
            "zh_CN": "下次不再提醒",
            "zh_HK": "下次不再提示",
            "zh_TW": "下次不再提醒",
            "en": "Don't show again",
            "fr": "Ne plus afficher",
            "de": "Nicht wieder anzeigen",
            "ja": "次回から表示しない",
            "it": "Non mostrare più",
            "ru": "Не показывать снова"
        },
        "confirm": {
            "zh_CN": "确定",
            "zh_HK": "確定",
            "zh_TW": "確定",
            "en": "Confirm",
            "fr": "Confirmer",
            "de": "Bestätigen",
            "ja": "確認",
            "it": "Conferma",
            "ru": "Подтвердить"
        },
        "cancel": {
            "zh_CN": "取消",
            "zh_HK": "取消",
            "zh_TW": "取消",
            "en": "Cancel",
            "fr": "Annuler",
            "de": "Abbrechen",
            "ja": "キャンセル",
            "it": "Annulla",
            "ru": "Отмена"
        },

        # ========== Toast 提示 ==========
        "toast_language_saved": {
            "zh_CN": "✓ 语言已设置为",
            "zh_HK": "✓ 語言已設定為",
            "zh_TW": "✓ 語言已設定為",
            "en": "✓ Language set to",
            "fr": "✓ Langue définie sur",
            "de": "✓ Sprache eingestellt auf",
            "ja": "✓ 言語を設定しました",
            "it": "✓ Lingua impostata su",
            "ru": "✓ Язык установлен на"
        },
        "toast_output_dir_saved": {
            "zh_CN": "✓ 输出目录已保存",
            "zh_HK": "✓ 輸出目錄已儲存",
            "zh_TW": "✓ 輸出目錄已儲存",
            "en": "✓ Output directory saved",
            "fr": "✓ Répertoire de sortie enregistré",
            "de": "✓ Ausgabeverzeichnis gespeichert",
            "ja": "✓ 出力ディレクトリを保存しました",
            "it": "✓ Directory di output salvata",
            "ru": "✓ Выходной каталог сохранен"
        },
        "toast_token_saved": {
            "zh_CN": "✓ Token 已设置为",
            "zh_HK": "✓ Token 已設定為",
            "zh_TW": "✓ Token 已設定為",
            "en": "✓ Token set to",
            "fr": "✓ Token défini sur",
            "de": "✓ Token eingestellt auf",
            "ja": "✓ トークンを設定しました",
            "it": "✓ Token impostato su",
            "ru": "✓ Токен установлен на"
        },
        "toast_screenshot_enabled": {
            "zh_CN": "✓ 截图提示已启用",
            "zh_HK": "✓ 截圖提示已啟用",
            "zh_TW": "✓ 截圖提示已啟用",
            "en": "✓ Screenshot prompt enabled",
            "fr": "✓ Invite de capture activée",
            "de": "✓ Screenshot-Eingabeaufforderung aktiviert",
            "ja": "✓ スクリーンショットプロンプトを有効にしました",
            "it": "✓ Prompt screenshot abilitato",
            "ru": "✓ Подсказка скриншота включена"
        },
        "toast_screenshot_disabled": {
            "zh_CN": "✓ 截图提示已禁用",
            "zh_HK": "✓ 截圖提示已停用",
            "zh_TW": "✓ 截圖提示已停用",
            "en": "✓ Screenshot prompt disabled",
            "fr": "✓ Invite de capture désactivée",
            "de": "✓ Screenshot-Eingabeaufforderung deaktiviert",
            "ja": "✓ スクリーンショットプロンプトを無効にしました",
            "it": "✓ Prompt screenshot disabilitato",
            "ru": "✓ Подсказка скриншота отключена"
        },

        # ========== 字体设置 ==========
        "font_family": {
            "zh_CN": "字体:",
            "zh_HK": "字體:",
            "zh_TW": "字體:",
            "en": "Font:",
            "fr": "Police:",
            "de": "Schriftart:",
            "ja": "フォント:",
            "it": "Carattere:",
            "ru": "Шрифт:"
        },
        "font_size_label": {
            "zh_CN": "字体大小:",
            "zh_HK": "字體大小:",
            "zh_TW": "字體大小:",
            "en": "Font Size:",
            "fr": "Taille de police:",
            "de": "Schriftgröße:",
            "ja": "フォントサイズ:",
            "it": "Dimensione carattere:",
            "ru": "Размер шрифта:"
        },
        "toast_font_saved": {
            "zh_CN": "✓ 字体已设置为",
            "zh_HK": "✓ 字體已設定為",
            "zh_TW": "✓ 字體已設定為",
            "en": "✓ Font set to",
            "fr": "✓ Police définie sur",
            "de": "✓ Schriftart eingestellt auf",
            "ja": "✓ フォントを設定しました",
            "it": "✓ Carattere impostato su",
            "ru": "✓ Шрифт установлен на"
        },

        # ========== 公式修复功能 ==========
        "fix_formula_title": {
            "zh_CN": "🔧 公式修复模式",
            "zh_HK": "🔧 公式修復模式",
            "zh_TW": "🔧 公式修復模式",
            "en": "🔧 Formula Fix Mode",
            "fr": "🔧 Mode de correction de formule",
            "de": "🔧 Formelkorrekturmodus",
            "ja": "🔧 数式修正モード",
            "it": "🔧 Modalità correzione formula",
            "ru": "🔧 Режим исправления формулы"
        },
        "fix_formula_prompt": {
            "zh_CN": "请选择公式识别结果的处理方式：",
            "zh_HK": "請選擇公式識別結果的處理方式：",
            "zh_TW": "請選擇公式識別結果的處理方式：",
            "en": "Please select how to handle formula recognition results:",
            "fr": "Veuillez sélectionner comment traiter les résultats de reconnaissance de formule:",
            "de": "Bitte wählen Sie, wie Formelergebnisse behandelt werden sollen:",
            "ja": "数式認識結果の処理方法を選択してください：",
            "it": "Seleziona come gestire i risultati del riconoscimento formula:",
            "ru": "Выберите, как обрабатывать результаты распознавания формулы:"
        },
        "replace_original": {
            "zh_CN": "替换原结果",
            "zh_HK": "替換原結果",
            "zh_TW": "取代原結果",
            "en": "Replace Original",
            "fr": "Remplacer l'original",
            "de": "Original ersetzen",
            "ja": "元の結果を置換",
            "it": "Sostituisci originale",
            "ru": "Заменить оригинал"
        },
        "append_to_original": {
            "zh_CN": "追加到原结果后",
            "zh_HK": "追加到原結果後",
            "zh_TW": "追加到原結果後",
            "en": "Append to Original",
            "fr": "Ajouter à l'original",
            "de": "An Original anhängen",
            "ja": "元の結果に追加",
            "it": "Aggiungi all'originale",
            "ru": "Добавить к оригиналу"
        },
        "fix_formula_hint": {
            "zh_CN": "替换：仅保留公式识别结果\n追加：保留原文本+添加公式修复",
            "zh_HK": "替換：僅保留公式識別結果\n追加：保留原文本+添加公式修復",
            "zh_TW": "取代：僅保留公式識別結果\n追加：保留原文字+新增公式修復",
            "en": "Replace: Keep only formula result\nAppend: Keep original text + add formula fix",
            "fr": "Remplacer: Garder seulement le résultat de formule\nAjouter: Garder le texte original + ajouter la correction",
            "de": "Ersetzen: Nur Formelergebnis behalten\nAnhängen: Original + Formelkorrektur",
            "ja": "置換: 数式結果のみ保持\n追加: 元のテキスト + 数式修正を追加",
            "it": "Sostituisci: Mantieni solo risultato formula\nAggiungi: Mantieni testo originale + aggiungi correzione",
            "ru": "Заменить: Сохранить только результат формулы\nДобавить: Сохранить оригинал + добавить исправление"
        },
        "fix_formula_dont_show": {
            "zh_CN": "下次直接使用 {0} 模式，不再询问",
            "zh_HK": "下次直接使用 {0} 模式，不再詢問",
            "zh_TW": "下次直接使用 {0} 模式，不再詢問",
            "en": "Use {0} mode directly next time, don't ask again",
            "fr": "Utiliser directement le mode {0} la prochaine fois, ne plus demander",
            "de": "Nächstes Mal direkt {0}-Modus verwenden, nicht mehr fragen",
            "ja": "次回から {0} モードを直接使用し、再度尋ねない",
            "it": "Usa direttamente la modalità {0} la prossima volta, non chiedere più",
            "ru": "В следующий раз использовать режим {0} напрямую, больше не спрашивать"
        },
        "formula_result_header": {
            "zh_CN": "【公式识别结果】",
            "zh_HK": "【公式識別結果】",
            "zh_TW": "【公式識別結果】",
            "en": "[Formula Recognition Result]",
            "fr": "[Résultat de reconnaissance de formule]",
            "de": "[Formelerkennungsergebnis]",
            "ja": "【数式認識結果】",
            "it": "[Risultato riconoscimento formula]",
            "ru": "[Результат распознавания формулы]"
        },
        "fix_formula_success": {
            "zh_CN": "公式识别完成！",
            "zh_HK": "公式識別完成！",
            "zh_TW": "公式識別完成！",
            "en": "Formula recognition complete!",
            "fr": "Reconnaissance de formule terminée!",
            "de": "Formelerkennung abgeschlossen!",
            "ja": "数式認識完了！",
            "it": "Riconoscimento formula completato!",
            "ru": "Распознавание формулы завершено!"
        },
        "fix_formula_tips": {
            "zh_CN": "提示：如果结果仍不理想，可以尝试：\n1. 调整 Token 数量到更大值\n2. 使用更清晰的图片\n3. 重新截图确保公式清晰可见",
            "zh_HK": "提示：如果結果仍不理想，可以嘗試：\n1. 調整 Token 數量到更大值\n2. 使用更清晰的圖片\n3. 重新截圖確保公式清晰可見",
            "zh_TW": "提示：如果結果仍不理想，可以嘗試：\n1. 調整 Token 數量到更大值\n2. 使用更清晰的圖片\n3. 重新截圖確保公式清晰可見",
            "en": "Tip: If result is still not ideal, try:\n1. Increase Token count\n2. Use clearer image\n3. Retake screenshot ensuring formula is clear",
            "fr": "Astuce: Si le résultat n'est toujours pas idéal, essayez:\n1. Augmenter le nombre de tokens\n2. Utiliser une image plus claire\n3. Reprendre la capture en assurant que la formule est claire",
            "de": "Tipp: Wenn das Ergebnis noch nicht ideal ist, versuchen Sie:\n1. Token-Anzahl erhöhen\n2. Klareres Bild verwenden\n3. Screenshot erneut aufnehmen und sicherstellen, dass die Formel klar ist",
            "ja": "ヒント: 結果が理想的でない場合は、次のことを試してください：\n1. トークン数を増やす\n2. より鮮明な画像を使用\n3. 数式が鮮明に見えるようにスクリーンショットを撮り直す",
            "it": "Suggerimento: Se il risultato non è ancora ideale, prova:\n1. Aumenta il conteggio Token\n2. Usa un'immagine più chiara\n3. Rifai lo screenshot assicurandoti che la formula sia chiara",
            "ru": "Совет: Если результат все еще не идеальный, попробуйте:\n1. Увеличить количество токенов\n2. Использовать более четкое изображение\n3. Переснять скриншот, убедившись, что формула четкая"
        },
    }

    def __init__(self, language="简体中文"):
        """初始化语言管理器

        Args:
            language: 语言名称，如 "简体中文"、"English"
        """
        self.current_language = language
        self.current_code = self.LANGUAGES.get(language, "zh_CN")

    def set_language(self, language):
        """设置当前语言

        Args:
            language: 语言名称，如 "简体中文"、"English"
        """
        self.current_language = language
        self.current_code = self.LANGUAGES.get(language, "zh_CN")

    def get(self, key, *args):
        """获取翻译文本

        Args:
            key: 翻译键名
            *args: 用于 str.format() 的参数

        Returns:
            翻译后的文本，未找到则返回 key 本身
        """
        if key not in self.TRANSLATIONS:
            return key

        text = self.TRANSLATIONS[key].get(self.current_code, key)

        # 如果有参数，进行格式化
        if args:
            try:
                text = text.format(*args)
            except (IndexError, KeyError):
                pass

        return text

    def get_code(self):
        """获取当前语言代码

        Returns:
            语言代码，如 "zh_CN"、"en"
        """
        return self.current_code

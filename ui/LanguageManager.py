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
    }

    def __init__(self, language="简体中文"):
        """初始化语言管理器"""
        self.current_language = language
        self.current_code = self.LANGUAGES.get(language, "zh_CN")

    def set_language(self, language):
        """设置当前语言"""
        self.current_language = language
        self.current_code = self.LANGUAGES.get(language, "zh_CN")

    def get(self, key, *args):
        """获取翻译文本"""
        if key not in self.TRANSLATIONS:
            return key

        text = self.TRANSLATIONS[key].get(self.current_code, key)

        # 如果有参数，进行格式化
        if args:
            try:
                text = text.format(*args)
            except:
                pass

        return text

    def get_code(self):
        """获取当前语言代码"""
        return self.current_code

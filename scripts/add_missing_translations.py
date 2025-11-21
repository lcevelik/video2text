#!/usr/bin/env python3
"""
Add translations for the 23 missing strings.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Translations for the 23 missing strings
MISSING_TRANSLATIONS = {
    'cs': {  # Czech
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Zpracování Zvuku",
        "  ▼ 📝 Transcription": "  ▼ 📝 Přepis",
        "00:00:00": "00:00:00",
        "Change Folder": "Změnit Složku",
        "Deep Scan": "Hluboké Skenování",
        "Enhance Audio": "Vylepšit Zvuk",
        "Open Folder": "Otevřít Složku",
        "Quick Actions": "Rychlé Akce",
        "Ready for new transcription": "Připraven k novému přepisu",
        "Recording will use the system": "Nahrávání použije systém",
        "Settings": "Nastavení",
        "Settings Sections": "Sekce Nastavení",
        "Start Recording": "Začít Nahrávání",
        "Stop Recording": "Zastavit Nahrávání",
        "Unknown": "Neznámý",
        "⚙️ Recordings Settings": "⚙️ Nastavení Nahrávek",
        "🎙️ Audio Processing": "🎙️ Zpracování Zvuku",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 Po zastavení je nahrávka uložena, ale NENÍ automaticky přepsána\n💡 Klikněte ",
        "📝 Transcription": "📝 Přepis",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ Bylo detekováno zvukové vstupní zařízení!\n\nNyní můžete začít nahrávat.",
        "🎤 Microphone": "🎤 Mikrofon",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Perfektní pro videohovory, schůzky nebo jakýkoliv scénář, kde potřebujete\nzachytit váš hlas i systémový zvuk.",
        "🔊 Speaker/System": "🔊 Reproduktor/Systém",
    },
    'de': {  # German
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Audioverarbeitung",
        "  ▼ 📝 Transcription": "  ▼ 📝 Transkription",
        "00:00:00": "00:00:00",
        "Change Folder": "Ordner Ändern",
        "Deep Scan": "Tiefenscan",
        "Enhance Audio": "Audio Verbessern",
        "Open Folder": "Ordner Öffnen",
        "Quick Actions": "Schnellaktionen",
        "Ready for new transcription": "Bereit für neue Transkription",
        "Recording will use the system": "Aufnahme verwendet das System",
        "Settings": "Einstellungen",
        "Settings Sections": "Einstellungsbereiche",
        "Start Recording": "Aufnahme Starten",
        "Stop Recording": "Aufnahme Stoppen",
        "Unknown": "Unbekannt",
        "⚙️ Recordings Settings": "⚙️ Aufnahmeeinstellungen",
        "🎙️ Audio Processing": "🎙️ Audioverarbeitung",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 Nach dem Stoppen wird die Aufnahme gespeichert, aber NICHT automatisch transkribiert\n💡 Klicken Sie auf ",
        "📝 Transcription": "📝 Transkription",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ Audio-Eingabegerät erkannt!\n\nSie können jetzt mit der Aufnahme beginnen.",
        "🎤 Microphone": "🎤 Mikrofon",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Perfekt für Videoanrufe, Meetings oder jedes Szenario, in dem Sie sowohl\nIhre Stimme als auch System-Audio aufnehmen müssen.",
        "🔊 Speaker/System": "🔊 Lautsprecher/System",
    },
    'es': {  # Spanish
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Procesamiento de Audio",
        "  ▼ 📝 Transcription": "  ▼ 📝 Transcripción",
        "00:00:00": "00:00:00",
        "Change Folder": "Cambiar Carpeta",
        "Deep Scan": "Escaneo Profundo",
        "Enhance Audio": "Mejorar Audio",
        "Open Folder": "Abrir Carpeta",
        "Quick Actions": "Acciones Rápidas",
        "Ready for new transcription": "Listo para nueva transcripción",
        "Recording will use the system": "La grabación usará el sistema",
        "Settings": "Configuración",
        "Settings Sections": "Secciones de Configuración",
        "Start Recording": "Iniciar Grabación",
        "Stop Recording": "Detener Grabación",
        "Unknown": "Desconocido",
        "⚙️ Recordings Settings": "⚙️ Configuración de Grabaciones",
        "🎙️ Audio Processing": "🎙️ Procesamiento de Audio",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 Después de detener, la grabación se guarda pero NO se transcribe automáticamente\n💡 Haga clic en ",
        "📝 Transcription": "📝 Transcripción",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ ¡Dispositivo de entrada de audio detectado!\n\nAhora puede comenzar a grabar.",
        "🎤 Microphone": "🎤 Micrófono",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Perfecto para videollamadas, reuniones o cualquier escenario donde necesite\ncapturar tanto su voz como el audio del sistema.",
        "🔊 Speaker/System": "🔊 Altavoz/Sistema",
    },
    'fr': {  # French
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Traitement Audio",
        "  ▼ 📝 Transcription": "  ▼ 📝 Transcription",
        "00:00:00": "00:00:00",
        "Change Folder": "Changer de Dossier",
        "Deep Scan": "Analyse Approfondie",
        "Enhance Audio": "Améliorer l'Audio",
        "Open Folder": "Ouvrir le Dossier",
        "Quick Actions": "Actions Rapides",
        "Ready for new transcription": "Prêt pour nouvelle transcription",
        "Recording will use the system": "L'enregistrement utilisera le système",
        "Settings": "Paramètres",
        "Settings Sections": "Sections des Paramètres",
        "Start Recording": "Démarrer l'Enregistrement",
        "Stop Recording": "Arrêter l'Enregistrement",
        "Unknown": "Inconnu",
        "⚙️ Recordings Settings": "⚙️ Paramètres d'Enregistrement",
        "🎙️ Audio Processing": "🎙️ Traitement Audio",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 Après l'arrêt, l'enregistrement est sauvegardé mais NON transcrit automatiquement\n💡 Cliquez sur ",
        "📝 Transcription": "📝 Transcription",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ Périphérique d'entrée audio détecté!\n\nVous pouvez maintenant commencer l'enregistrement.",
        "🎤 Microphone": "🎤 Microphone",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Parfait pour les appels vidéo, réunions ou tout scénario où vous avez besoin\nde capturer votre voix et l'audio système.",
        "🔊 Speaker/System": "🔊 Haut-parleur/Système",
    },
    'it': {  # Italian
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Elaborazione Audio",
        "  ▼ 📝 Transcription": "  ▼ 📝 Trascrizione",
        "00:00:00": "00:00:00",
        "Change Folder": "Cambia Cartella",
        "Deep Scan": "Scansione Profonda",
        "Enhance Audio": "Migliora Audio",
        "Open Folder": "Apri Cartella",
        "Quick Actions": "Azioni Rapide",
        "Ready for new transcription": "Pronto per nuova trascrizione",
        "Recording will use the system": "La registrazione utilizzerà il sistema",
        "Settings": "Impostazioni",
        "Settings Sections": "Sezioni Impostazioni",
        "Start Recording": "Avvia Registrazione",
        "Stop Recording": "Ferma Registrazione",
        "Unknown": "Sconosciuto",
        "⚙️ Recordings Settings": "⚙️ Impostazioni Registrazioni",
        "🎙️ Audio Processing": "🎙️ Elaborazione Audio",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 Dopo l'arresto, la registrazione viene salvata ma NON trascritta automaticamente\n💡 Clicca ",
        "📝 Transcription": "📝 Trascrizione",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ Dispositivo di input audio rilevato!\n\nPuoi iniziare la registrazione.",
        "🎤 Microphone": "🎤 Microfono",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Perfetto per videochiamate, riunioni o qualsiasi scenario in cui è necessario\ncatturare sia la voce che l'audio di sistema.",
        "🔊 Speaker/System": "🔊 Altoparlante/Sistema",
    },
    'ja': {  # Japanese
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ 音声処理",
        "  ▼ 📝 Transcription": "  ▼ 📝 文字起こし",
        "00:00:00": "00:00:00",
        "Change Folder": "フォルダを変更",
        "Deep Scan": "ディープスキャン",
        "Enhance Audio": "音声を強化",
        "Open Folder": "フォルダを開く",
        "Quick Actions": "クイックアクション",
        "Ready for new transcription": "新しい文字起こしの準備完了",
        "Recording will use the system": "録音はシステムを使用します",
        "Settings": "設定",
        "Settings Sections": "設定セクション",
        "Start Recording": "録音開始",
        "Stop Recording": "録音停止",
        "Unknown": "不明",
        "⚙️ Recordings Settings": "⚙️ 録音設定",
        "🎙️ Audio Processing": "🎙️ 音声処理",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 停止後、録音は保存されますが自動的に文字起こしされません\n💡 クリック ",
        "📝 Transcription": "📝 文字起こし",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ オーディオ入力デバイスが検出されました！\n\n録音を開始できます。",
        "🎤 Microphone": "🎤 マイク",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 ビデオ通話、会議、または音声とシステムオーディオの両方を\nキャプチャする必要があるあらゆるシナリオに最適です。",
        "🔊 Speaker/System": "🔊 スピーカー/システム",
    },
    'ko': {  # Korean
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ 오디오 처리",
        "  ▼ 📝 Transcription": "  ▼ 📝 전사",
        "00:00:00": "00:00:00",
        "Change Folder": "폴더 변경",
        "Deep Scan": "정밀 스캔",
        "Enhance Audio": "오디오 향상",
        "Open Folder": "폴더 열기",
        "Quick Actions": "빠른 작업",
        "Ready for new transcription": "새 전사 준비 완료",
        "Recording will use the system": "녹음은 시스템을 사용합니다",
        "Settings": "설정",
        "Settings Sections": "설정 섹션",
        "Start Recording": "녹음 시작",
        "Stop Recording": "녹음 중지",
        "Unknown": "알 수 없음",
        "⚙️ Recordings Settings": "⚙️ 녹음 설정",
        "🎙️ Audio Processing": "🎙️ 오디오 처리",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 중지 후 녹음은 저장되지만 자동으로 전사되지 않습니다\n💡 클릭 ",
        "📝 Transcription": "📝 전사",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ 오디오 입력 장치가 감지되었습니다!\n\n이제 녹음을 시작할 수 있습니다.",
        "🎤 Microphone": "🎤 마이크",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 화상 통화, 회의 또는 음성과 시스템 오디오를 모두\n캡처해야 하는 모든 시나리오에 완벽합니다.",
        "🔊 Speaker/System": "🔊 스피커/시스템",
    },
    'pl': {  # Polish
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Przetwarzanie Dźwięku",
        "  ▼ 📝 Transcription": "  ▼ 📝 Transkrypcja",
        "00:00:00": "00:00:00",
        "Change Folder": "Zmień Folder",
        "Deep Scan": "Głębokie Skanowanie",
        "Enhance Audio": "Ulepsz Dźwięk",
        "Open Folder": "Otwórz Folder",
        "Quick Actions": "Szybkie Akcje",
        "Ready for new transcription": "Gotowy do nowej transkrypcji",
        "Recording will use the system": "Nagrywanie użyje systemu",
        "Settings": "Ustawienia",
        "Settings Sections": "Sekcje Ustawień",
        "Start Recording": "Rozpocznij Nagrywanie",
        "Stop Recording": "Zatrzymaj Nagrywanie",
        "Unknown": "Nieznany",
        "⚙️ Recordings Settings": "⚙️ Ustawienia Nagrań",
        "🎙️ Audio Processing": "🎙️ Przetwarzanie Dźwięku",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 Po zatrzymaniu nagranie jest zapisywane, ale NIE jest automatycznie transkrybowane\n💡 Kliknij ",
        "📝 Transcription": "📝 Transkrypcja",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ Wykryto urządzenie wejścia audio!\n\nMożesz teraz rozpocząć nagrywanie.",
        "🎤 Microphone": "🎤 Mikrofon",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Idealne do połączeń wideo, spotkań lub każdego scenariusza, w którym\npotrzebujesz przechwycić zarówno swój głos, jak i dźwięk systemu.",
        "🔊 Speaker/System": "🔊 Głośnik/System",
    },
    'pt_BR': {  # Portuguese (Brazil)
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Processamento de Áudio",
        "  ▼ 📝 Transcription": "  ▼ 📝 Transcrição",
        "00:00:00": "00:00:00",
        "Change Folder": "Mudar Pasta",
        "Deep Scan": "Varredura Profunda",
        "Enhance Audio": "Melhorar Áudio",
        "Open Folder": "Abrir Pasta",
        "Quick Actions": "Ações Rápidas",
        "Ready for new transcription": "Pronto para nova transcrição",
        "Recording will use the system": "A gravação usará o sistema",
        "Settings": "Configurações",
        "Settings Sections": "Seções de Configurações",
        "Start Recording": "Iniciar Gravação",
        "Stop Recording": "Parar Gravação",
        "Unknown": "Desconhecido",
        "⚙️ Recordings Settings": "⚙️ Configurações de Gravação",
        "🎙️ Audio Processing": "🎙️ Processamento de Áudio",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 Após parar, a gravação é salva mas NÃO transcrita automaticamente\n💡 Clique em ",
        "📝 Transcription": "📝 Transcrição",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ Dispositivo de entrada de áudio detectado!\n\nVocê pode começar a gravar agora.",
        "🎤 Microphone": "🎤 Microfone",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Perfeito para chamadas de vídeo, reuniões ou qualquer cenário onde você\nprecisa capturar sua voz e o áudio do sistema.",
        "🔊 Speaker/System": "🔊 Alto-falante/Sistema",
    },
    'ru': {  # Russian
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ Обработка Аудио",
        "  ▼ 📝 Transcription": "  ▼ 📝 Транскрипция",
        "00:00:00": "00:00:00",
        "Change Folder": "Изменить Папку",
        "Deep Scan": "Глубокое Сканирование",
        "Enhance Audio": "Улучшить Аудио",
        "Open Folder": "Открыть Папку",
        "Quick Actions": "Быстрые Действия",
        "Ready for new transcription": "Готов к новой транскрипции",
        "Recording will use the system": "Запись будет использовать систему",
        "Settings": "Настройки",
        "Settings Sections": "Разделы Настроек",
        "Start Recording": "Начать Запись",
        "Stop Recording": "Остановить Запись",
        "Unknown": "Неизвестно",
        "⚙️ Recordings Settings": "⚙️ Настройки Записи",
        "🎙️ Audio Processing": "🎙️ Обработка Аудио",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 После остановки запись сохраняется, но НЕ транскрибируется автоматически\n💡 Нажмите ",
        "📝 Transcription": "📝 Транскрипция",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ Обнаружено устройство ввода звука!\n\nТеперь вы можете начать запись.",
        "🎤 Microphone": "🎤 Микрофон",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 Идеально для видеозвонков, встреч или любого сценария, где вам нужно\nзахватить как ваш голос, так и системный звук.",
        "🔊 Speaker/System": "🔊 Динамик/Система",
    },
    'zh_CN': {  # Chinese (Simplified)
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ 音频处理",
        "  ▼ 📝 Transcription": "  ▼ 📝 转录",
        "00:00:00": "00:00:00",
        "Change Folder": "更改文件夹",
        "Deep Scan": "深度扫描",
        "Enhance Audio": "增强音频",
        "Open Folder": "打开文件夹",
        "Quick Actions": "快速操作",
        "Ready for new transcription": "准备新转录",
        "Recording will use the system": "录制将使用系统",
        "Settings": "设置",
        "Settings Sections": "设置部分",
        "Start Recording": "开始录制",
        "Stop Recording": "停止录制",
        "Unknown": "未知",
        "⚙️ Recordings Settings": "⚙️ 录制设置",
        "🎙️ Audio Processing": "🎙️ 音频处理",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 停止后，录音已保存但不会自动转录\n💡 单击 ",
        "📝 Transcription": "📝 转录",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ 检测到音频输入设备！\n\n现在可以开始录制。",
        "🎤 Microphone": "🎤 麦克风",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 非常适合视频通话、会议或任何需要同时\n捕获您的语音和系统音频的场景。",
        "🔊 Speaker/System": "🔊 扬声器/系统",
    },
    'ar': {  # Arabic
        "  ▼ 🎙️ Audio Processing": "  ▼ 🎙️ معالجة الصوت",
        "  ▼ 📝 Transcription": "  ▼ 📝 النسخ",
        "00:00:00": "00:00:00",
        "Change Folder": "تغيير المجلد",
        "Deep Scan": "فحص عميق",
        "Enhance Audio": "تحسين الصوت",
        "Open Folder": "فتح المجلد",
        "Quick Actions": "إجراءات سريعة",
        "Ready for new transcription": "جاهز لنسخ جديد",
        "Recording will use the system": "سيستخدم التسجيل النظام",
        "Settings": "الإعدادات",
        "Settings Sections": "أقسام الإعدادات",
        "Start Recording": "بدء التسجيل",
        "Stop Recording": "إيقاف التسجيل",
        "Unknown": "غير معروف",
        "⚙️ Recordings Settings": "⚙️ إعدادات التسجيل",
        "🎙️ Audio Processing": "🎙️ معالجة الصوت",
        "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ": "💡 بعد الإيقاف، يتم حفظ التسجيل ولكن لا يتم نسخه تلقائيًا\n💡 انقر ",
        "📝 Transcription": "📝 النسخ",
        "✅ Audio input device detected!\n\nYou can now start recording.": "✅ تم اكتشاف جهاز إدخال صوتي!\n\nيمكنك الآن بدء التسجيل.",
        "🎤 Microphone": "🎤 ميكروفون",
        "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.": "💡 مثالي لمكالمات الفيديو أو الاجتماعات أو أي سيناريو تحتاج فيه\nإلى التقاط صوتك وصوت النظام معًا.",
        "🔊 Speaker/System": "🔊 مكبر الصوت/النظام",
    },
}

def apply_missing_translations(ts_file: Path, lang_code: str):
    """Apply missing translations to a .ts file."""
    if lang_code not in MISSING_TRANSLATIONS:
        return 0

    translations = MISSING_TRANSLATIONS[lang_code]

    tree = ET.parse(ts_file)
    root = tree.getroot()

    translated_count = 0

    for context in root.findall('context'):
        for message in context.findall('message'):
            source_elem = message.find('source')
            translation_elem = message.find('translation')

            if source_elem is not None and translation_elem is not None:
                source_text = source_elem.text
                trans_type = translation_elem.get('type', '')

                # Only update unfinished translations
                if trans_type == 'unfinished' and source_text in translations:
                    translation_elem.text = translations[source_text]
                    del translation_elem.attrib['type']  # Remove unfinished tag
                    translated_count += 1

    # Save with proper formatting
    indent_xml(root)
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)

    # Fix XML declaration format
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("<?xml version='1.0' encoding='utf-8'?>",
                             '<?xml version="1.0" encoding="utf-8"?>')
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return translated_count

def indent_xml(elem, level=0):
    """Add pretty-printing indentation to XML."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent

def main():
    """Apply missing translations to all .ts files."""
    i18n_dir = Path('/home/user/video2text/i18n')

    lang_names = {
        'ar': 'Arabic',
        'cs': 'Czech',
        'de': 'German',
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'pl': 'Polish',
        'pt_BR': 'Portuguese (Brazil)',
        'ru': 'Russian',
        'zh_CN': 'Chinese (Simplified)'
    }

    print("=" * 80)
    print("APPLYING 23 MISSING TRANSLATIONS")
    print("=" * 80)

    total_translated = 0

    for ts_file in sorted(i18n_dir.glob('fonixflow_*.ts')):
        lang_code = ts_file.stem.replace('fonixflow_', '')
        lang_name = lang_names.get(lang_code, lang_code)

        translated = apply_missing_translations(ts_file, lang_code)
        total_translated += translated

        status = "✅" if translated == 23 else f"⚠️  {translated}/23"
        print(f"{lang_name:20s} {status}")

    print("\n" + "=" * 80)
    print("FINAL COMPLETION STATUS")
    print("=" * 80)

    for ts_file in sorted(i18n_dir.glob('fonixflow_*.ts')):
        lang_code = ts_file.stem.replace('fonixflow_', '')
        lang_name = lang_names.get(lang_code, lang_code)

        tree = ET.parse(ts_file)
        root = tree.getroot()

        total = 0
        finished = 0

        for context in root.findall('context'):
            for message in context.findall('message'):
                translation = message.find('translation')
                if translation is not None:
                    trans_type = translation.get('type', '')
                    if trans_type != 'vanished':
                        total += 1
                        if trans_type != 'unfinished' and translation.text:
                            finished += 1

        pct = (finished / total * 100) if total > 0 else 0
        status = "✅ COMPLETE" if pct == 100 else f"⚠️ {pct:.1f}%"
        print(f"{lang_name:20s} {finished:3d}/{total:3d} {status}")

    print("\n✅ Total translations applied: {}".format(total_translated))

if __name__ == "__main__":
    main()

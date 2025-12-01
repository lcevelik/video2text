#!/bin/bash
# Complete the final 3 translations for all languages

python3 << 'ENDPYTHON'
import xml.etree.ElementTree as ET
from pathlib import Path

# Final 3 translations - using actual \n in the string
FINAL_TRANS = {
    'cs': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 Po zastavení je nahrávka uložena, ale NENÍ automaticky přepsána\n💡 Klikněte ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ Bylo detekováno zvukové vstupní zařízení!\n\nNyní můžete začít nahrávat.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 Perfektní pro videohovory, schůzky nebo jakýkoliv scénář, kde potřebujete\nzachytit váš hlas i systémový zvuk.',
    },
    'de': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 Nach dem Stoppen wird die Aufnahme gespeichert, aber NICHT automatisch transkribiert\n💡 Klicken Sie auf ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ Audio-Eingabegerät erkannt!\n\nSie können jetzt mit der Aufnahme beginnen.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 Perfekt für Videoanrufe, Meetings oder jedes Szenario, in dem Sie sowohl\nIhre Stimme als auch System-Audio aufnehmen müssen.',
    },
    'es': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 Después de detener, la grabación se guarda pero NO se transcribe automáticamente\n💡 Haga clic en ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ ¡Dispositivo de entrada de audio detectado!\n\nAhora puede comenzar a grabar.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 Perfecto para videollamadas, reuniones o cualquier escenario donde necesite\ncapturar tanto su voz como el audio del sistema.',
    },
    'fr': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            "💡 Après l'arrêt, l'enregistrement est sauvegardé mais NON transcrit automatiquement\n💡 Cliquez sur ",
        '✅ Audio input device detected!\n\nYou can now start recording.':
            "✅ Périphérique d'entrée audio détecté!\n\nVous pouvez maintenant commencer l'enregistrement.",
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            "💡 Parfait pour les appels vidéo, réunions ou tout scénario où vous avez besoin\nde capturer votre voix et l'audio système.",
    },
    'it': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            "💡 Dopo l'arresto, la registrazione viene salvata ma NON trascritta automaticamente\n💡 Clicca ",
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ Dispositivo di input audio rilevato!\n\nPuoi iniziare la registrazione.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            "💡 Perfetto per videochiamate, riunioni o qualsiasi scenario in cui è necessario\ncatturare sia la voce che l'audio di sistema.",
    },
    'ja': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 停止後、録音は保存されますが自動的に文字起こしされません\n💡 クリック ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ オーディオ入力デバイスが検出されました！\n\n録音を開始できます。',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 ビデオ通話、会議、または音声とシステムオーディオの両方を\nキャプチャする必要があるあらゆるシナリオに最適です。',
    },
    'ko': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 중지 후 녹음은 저장되지만 자동으로 전사되지 않습니다\n💡 클릭 ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ 오디오 입력 장치가 감지되었습니다!\n\n이제 녹음을 시작할 수 있습니다.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 화상 통화, 회의 또는 음성과 시스템 오디오를 모두\n캡처해야 하는 모든 시나리오에 완벽합니다.',
    },
    'pl': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 Po zatrzymaniu nagranie jest zapisywane, ale NIE jest automatycznie transkrybowane\n💡 Kliknij ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ Wykryto urządzenie wejścia audio!\n\nMożesz teraz rozpocząć nagrywanie.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 Idealne do połączeń wideo, spotkań lub każdego scenariusza, w którym\npotrzebujesz przechwycić zarówno swój głos, jak i dźwięk systemu.',
    },
    'pt_BR': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 Após parar, a gravação é salva mas NÃO transcrita automaticamente\n💡 Clique em ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ Dispositivo de entrada de áudio detectado!\n\nVocê pode começar a gravar agora.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 Perfeito para chamadas de vídeo, reuniões ou qualquer cenário onde você\nprecisa capturar sua voz e o áudio do sistema.',
    },
    'ru': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 После остановки запись сохраняется, но НЕ транскрибируется автоматически\n💡 Нажмите ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ Обнаружено устройство ввода звука!\n\nТеперь вы можете начать запись.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 Идеально для видеозвонков, встреч или любого сценария, где вам нужно\nзахватить как ваш голос, так и системный звук.',
    },
    'zh_CN': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 停止后，录音已保存但不会自动转录\n💡 单击 ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ 检测到音频输入设备！\n\n现在可以开始录制。',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 非常适合视频通话、会议或任何需要同时\n捕获您的语音和系统音频的场景。',
    },
    'ar': {
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ':
            '💡 بعد الإيقاف، يتم حفظ التسجيل ولكن لا يتم نسخه تلقائيًا\n💡 انقر ',
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ تم اكتشاف جهاز إدخال صوتي!\n\nيمكنك الآن بدء التسجيل.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 مثالي لمكالمات الفيديو أو الاجتماعات أو أي سيناريو تحتاج فيه\nإلى التقاط صوتك وصوت النظام معًا.',
    },
}

def indent_xml(elem, level=0):
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

# Apply to all languages
i18n_dir = Path('/home/user/video2text/i18n')
count = 0

for ts_file in sorted(i18n_dir.glob('fonixflow_*.ts')):
    lang_code = ts_file.stem.replace('fonixflow_', '')

    if lang_code not in FINAL_TRANS:
        continue

    tree = ET.parse(ts_file)
    root = tree.getroot()

    for context in root.findall('context'):
        for message in context.findall('message'):
            source = message.find('source')
            translation = message.find('translation')

            if source is not None and translation is not None:
                if source.text in FINAL_TRANS[lang_code]:
                    trans_type = translation.get('type', '')
                    if trans_type == 'unfinished':
                        translation.text = FINAL_TRANS[lang_code][source.text]
                        if 'type' in translation.attrib:
                            del translation.attrib['type']
                        count += 1

    indent_xml(root)
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)

    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("<?xml version='1.0' encoding='utf-8'?>",
                             '<?xml version="1.0" encoding="utf-8"?>')
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"✅ Applied {count} final translations")

# Verify completion
lang_names = {
    'ar': 'Arabic', 'cs': 'Czech', 'de': 'German', 'es': 'Spanish',
    'fr': 'French', 'it': 'Italian', 'ja': 'Japanese', 'ko': 'Korean',
    'pl': 'Polish', 'pt_BR': 'Portuguese (BR)', 'ru': 'Russian', 'zh_CN': 'Chinese'
}

print("\n" + "=" * 80)
print("FINAL VERIFICATION")
print("=" * 80)

all_complete = True
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

    if pct == 100:
        status = "✅ COMPLETE"
    else:
        status = f"⚠️  {finished}/{total}"
        all_complete = False

    print(f"{lang_name:20s} {status}")

print("=" * 80)
if all_complete:
    print("🎉 ALL 12 LANGUAGES 100% COMPLETE!")
else:
    print("⚠️  Some translations incomplete")
ENDPYTHON

#!/usr/bin/env python3
"""
Complete all remaining translations to reach 100% for all languages.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Complete translations for ALL remaining strings
COMPLETE_TRANSLATIONS = {
    'cs': {  # Czech - 2 remaining
        '✅ Audio input device detected!\n\nYou can now start recording.':
            '✅ Bylo detekováno zvukové vstupní zařízení!\n\nNyní můžete začít nahrávat.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.':
            '💡 Perfektní pro videohovory, schůzky nebo jakýkoliv scénář, kde potřebujete\nzachytit váš hlas i systémový zvuk.',
    },
    'de': {  # German - 40 remaining (need to add all from translation_data.py)
        'Extracting audio...': 'Audio wird extrahiert...',
        'Finalizing transcription...': 'Transkription wird abgeschlossen...',
        'Finishing up...': 'Abschließen...',
        'Transcribing...': 'Transkribiere...',
        'Transcription complete!': 'Transkription abgeschlossen!',
        'Could Not Open Folder': 'Ordner Konnte Nicht Geöffnet Werden',
        'Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)': 'Mediendateien (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;Alle Dateien (*.*)',
        'Select Recordings Folder': 'Aufnahmeordner Auswählen',
        'Select Video or Audio File': 'Video- oder Audiodatei Auswählen',
        'Settings Updated': 'Einstellungen Aktualisiert',
        '  ▼ 🎙️ Audio Processing': '  ▼ 🎙️ Audioverarbeitung',
        '  ▼ 📝 Transcription': '  ▼ 📝 Transkription',
        '00:00:00': '00:00:00',
        'Change Folder': 'Ordner Ändern',
        'Deep Scan': 'Tiefenscan',
        'Drag and drop video/audio file': 'Video-/Audiodatei per Drag & Drop',
        'Enhance Audio': 'Audio Verbessern',
        'No recording available. Please record first.': 'Keine Aufnahme verfügbar. Bitte zuerst aufnehmen.',
        'Open Folder': 'Ordner Öffnen',
        'Please select a file first.': 'Bitte wählen Sie zuerst eine Datei aus.',
        'Please transcribe a file first.': 'Bitte transkribieren Sie zuerst eine Datei.',
        'Quick Actions': 'Schnellaktionen',
        'Ready for new transcription': 'Bereit für neue Transkription',
        'Recording will use the system': 'Aufnahme verwendet das System',
        'Settings': 'Einstellungen',
        'Settings Sections': 'Einstellungsbereiche',
        'Start Recording': 'Aufnahme Starten',
        'Stop Recording': 'Aufnahme Stoppen',
        'Unknown': 'Unbekannt',
        '⚙️ Recordings Settings': '⚙️ Aufnahmeeinstellungen',
        '🎙️ Audio Processing': '🎙️ Audioverarbeitung',
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 Nach dem Stoppen wird die Aufnahme gespeichert, aber NICHT automatisch transkribiert\n💡 Klicken Sie auf ',
        '📝 Transcription': '📝 Transkription',
        'At least one language must be selected before confirming.': 'Mindestens eine Sprache muss vor dem Bestätigen ausgewählt werden.',
        'Cancel to decide later.': 'Abbrechen, um später zu entscheiden.',
        'Close': 'Schließen',
        'Confirm Languages': 'Sprachen Bestätigen',
        'Confirm Selection': 'Auswahl Bestätigen',
        'Device Found': 'Gerät Gefunden',
        'Duration: 0:00': 'Dauer: 0:00',
        'English (uses optimized .en model)': 'Englisch (verwendet optimiertes .en-Modell)',
        'Is your file multi-language?': 'Ist Ihre Datei mehrsprachig?',
        'Language Mode': 'Sprachmodus',
        'Multi-Language': 'Mehrsprachig',
        'No Language Type Selected': 'Kein Sprachtyp Ausgewählt',
        'No Languages Selected': 'Keine Sprachen Ausgewählt',
        'No Microphone Found': 'Kein Mikrofon Gefunden',
        'No audio input device detected!': 'Kein Audio-Eingabegerät erkannt!',
        'Other language (uses multilingual model)': 'Andere Sprache (verwendet mehrsprachiges Modell)',
        'Please select either English or Other language.': 'Bitte wählen Sie Englisch oder Andere Sprache.',
        'Ready to record': 'Bereit zur Aufnahme',
        'Select at least one language to proceed.': 'Wählen Sie mindestens eine Sprache aus, um fortzufahren.',
        'Select language type:': 'Sprachtyp auswählen:',
        'Select languages present (check all that apply):': 'Vorhandene Sprachen auswählen (alle zutreffenden markieren):',
        'Select one language type before confirming.': 'Wählen Sie einen Sprachtyp vor dem Bestätigen aus.',
        'Single-Language': 'Einsprachig',
        'What will be recorded:': 'Was wird aufgenommen:',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ Audio-Eingabegerät erkannt!\n\nSie können jetzt mit der Aufnahme beginnen.',
        '🎤 Microphone': '🎤 Mikrofon',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Perfekt für Videoanrufe, Meetings oder jedes Szenario, in dem Sie sowohl\nIhre Stimme als auch System-Audio aufnehmen müssen.',
        '🔊 Speaker/System': '🔊 Lautsprecher/System',
    },
    'fr': {  # French - 40 remaining
        'Extracting audio...': 'Extraction de l\'audio...',
        'Finalizing transcription...': 'Finalisation de la transcription...',
        'Finishing up...': 'Finalisation...',
        'Transcribing...': 'Transcription...',
        'Transcription complete!': 'Transcription terminée!',
        'Could Not Open Folder': 'Impossible d\'Ouvrir le Dossier',
        'Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)': 'Fichiers Multimédias (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;Tous les Fichiers (*.*)',
        'Select Recordings Folder': 'Sélectionner le Dossier d\'Enregistrements',
        'Select Video or Audio File': 'Sélectionner Fichier Vidéo ou Audio',
        'Settings Updated': 'Paramètres Mis à Jour',
        '  ▼ 🎙️ Audio Processing': '  ▼ 🎙️ Traitement Audio',
        '  ▼ 📝 Transcription': '  ▼ 📝 Transcription',
        '00:00:00': '00:00:00',
        'Change Folder': 'Changer de Dossier',
        'Deep Scan': 'Analyse Approfondie',
        'Drag and drop video/audio file': 'Glisser-déposer fichier vidéo/audio',
        'Enhance Audio': 'Améliorer l\'Audio',
        'No recording available. Please record first.': 'Aucun enregistrement disponible. Veuillez d\'abord enregistrer.',
        'Open Folder': 'Ouvrir le Dossier',
        'Please select a file first.': 'Veuillez d\'abord sélectionner un fichier.',
        'Please transcribe a file first.': 'Veuillez d\'abord transcrire un fichier.',
        'Quick Actions': 'Actions Rapides',
        'Ready for new transcription': 'Prêt pour nouvelle transcription',
        'Recording will use the system': 'L\'enregistrement utilisera le système',
        'Settings': 'Paramètres',
        'Settings Sections': 'Sections des Paramètres',
        'Start Recording': 'Démarrer l\'Enregistrement',
        'Stop Recording': 'Arrêter l\'Enregistrement',
        'Unknown': 'Inconnu',
        '⚙️ Recordings Settings': '⚙️ Paramètres d\'Enregistrement',
        '🎙️ Audio Processing': '🎙️ Traitement Audio',
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 Après l\'arrêt, l\'enregistrement est sauvegardé mais NON transcrit automatiquement\n💡 Cliquez sur ',
        '📝 Transcription': '📝 Transcription',
        'At least one language must be selected before confirming.': 'Au moins une langue doit être sélectionnée avant de confirmer.',
        'Cancel to decide later.': 'Annuler pour décider plus tard.',
        'Close': 'Fermer',
        'Confirm Languages': 'Confirmer les Langues',
        'Confirm Selection': 'Confirmer la Sélection',
        'Device Found': 'Périphérique Trouvé',
        'Duration: 0:00': 'Durée: 0:00',
        'English (uses optimized .en model)': 'Anglais (utilise modèle .en optimisé)',
        'Is your file multi-language?': 'Votre fichier est-il multilingue?',
        'Language Mode': 'Mode Linguistique',
        'Multi-Language': 'Multilingue',
        'No Language Type Selected': 'Aucun Type de Langue Sélectionné',
        'No Languages Selected': 'Aucune Langue Sélectionnée',
        'No Microphone Found': 'Aucun Microphone Trouvé',
        'No audio input device detected!': 'Aucun périphérique d\'entrée audio détecté!',
        'Other language (uses multilingual model)': 'Autre langue (utilise modèle multilingue)',
        'Please select either English or Other language.': 'Veuillez sélectionner Anglais ou Autre langue.',
        'Ready to record': 'Prêt à enregistrer',
        'Select at least one language to proceed.': 'Sélectionnez au moins une langue pour continuer.',
        'Select language type:': 'Sélectionnez le type de langue:',
        'Select languages present (check all that apply):': 'Sélectionnez les langues présentes (cochez toutes celles qui s\'appliquent):',
        'Select one language type before confirming.': 'Sélectionnez un type de langue avant de confirmer.',
        'Single-Language': 'Monolingue',
        'What will be recorded:': 'Ce qui sera enregistré:',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ Périphérique d\'entrée audio détecté!\n\nVous pouvez maintenant commencer l\'enregistrement.',
        '🎤 Microphone': '🎤 Microphone',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Parfait pour les appels vidéo, réunions ou tout scénario où vous avez besoin\nde capturer votre voix et l\'audio système.',
        '🔊 Speaker/System': '🔊 Haut-parleur/Système',
    },
    'ar': {  # Arabic - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 بعد الإيقاف، يتم حفظ التسجيل ولكن لا يتم نسخه تلقائيًا\n💡 انقر ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ تم اكتشاف جهاز إدخال صوتي!\n\nيمكنك الآن بدء التسجيل.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 مثالي لمكالمات الفيديو أو الاجتماعات أو أي سيناريو تحتاج فيه\nإلى التقاط صوتك وصوت النظام معًا.',
    },
    'es': {  # Spanish - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 Después de detener, la grabación se guarda pero NO se transcribe automáticamente\n💡 Haga clic en ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ ¡Dispositivo de entrada de audio detectado!\n\nAhora puede comenzar a grabar.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Perfecto para videollamadas, reuniones o cualquier escenario donde necesite\ncapturar tanto su voz como el audio del sistema.',
    },
    'it': {  # Italian - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 Dopo l\'arresto, la registrazione viene salvata ma NON trascritta automaticamente\n💡 Clicca ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ Dispositivo di input audio rilevato!\n\nPuoi iniziare la registrazione.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Perfetto per videochiamate, riunioni o qualsiasi scenario in cui è necessario\ncatturare sia la voce che l\'audio di sistema.',
    },
    'ja': {  # Japanese - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 停止後、録音は保存されますが自動的に文字起こしされません\n💡 クリック ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ オーディオ入力デバイスが検出されました！\n\n録音を開始できます。',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 ビデオ通話、会議、または音声とシステムオーディオの両方を\nキャプチャする必要があるあらゆるシナリオに最適です。',
    },
    'ko': {  # Korean - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 중지 후 녹음은 저장되지만 자동으로 전사되지 않습니다\n💡 클릭 ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ 오디오 입력 장치가 감지되었습니다!\n\n이제 녹음을 시작할 수 있습니다.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 화상 통화, 회의 또는 음성과 시스템 오디오를 모두\n캡처해야 하는 모든 시나리오에 완벽합니다.',
    },
    'pl': {  # Polish - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 Po zatrzymaniu nagranie jest zapisywane, ale NIE jest automatycznie transkrybowane\n💡 Kliknij ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ Wykryto urządzenie wejścia audio!\n\nMożesz teraz rozpocząć nagrywanie.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Idealne do połączeń wideo, spotkań lub każdego scenariusza, w którym\npotrzebujesz przechwycić zarówno swój głos, jak i dźwięk systemu.',
    },
    'pt_BR': {  # Portuguese (Brazil) - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 Após parar, a gravação é salva mas NÃO transcrita automaticamente\n💡 Clique em ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ Dispositivo de entrada de áudio detectado!\n\nVocê pode começar a gravar agora.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Perfeito para chamadas de vídeo, reuniões ou qualquer cenário onde você\nprecisa capturar sua voz e o áudio do sistema.',
    },
    'ru': {  # Russian - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 После остановки запись сохраняется, но НЕ транскрибируется автоматически\n💡 Нажмите ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ Обнаружено устройство ввода звука!\n\nТеперь вы можете начать запись.',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Идеально для видеозвонков, встреч или любого сценария, где вам нужно\nзахватить как ваш голос, так и системный звук.',
    },
    'zh_CN': {  # Chinese - 3 remaining
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click ': '💡 停止后，录音已保存但不会自动转录\n💡 单击 ',
        '✅ Audio input device detected!\n\nYou can now start recording.': '✅ 检测到音频输入设备！\n\n现在可以开始录制。',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 非常适合视频通话、会议或任何需要同时\n捕获您的语音和系统音频的场景。',
    },
}

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

def complete_language(ts_file: Path, lang_code: str):
    """Complete all remaining translations for a language."""
    if lang_code not in COMPLETE_TRANSLATIONS:
        return 0

    translations = COMPLETE_TRANSLATIONS[lang_code]

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
                    if 'type' in translation_elem.attrib:
                        del translation_elem.attrib['type']
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

def main():
    """Complete all translations to 100%."""
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
    print("COMPLETING ALL TRANSLATIONS TO 100%")
    print("=" * 80)

    total_translated = 0

    for ts_file in sorted(i18n_dir.glob('fonixflow_*.ts')):
        lang_code = ts_file.stem.replace('fonixflow_', '')
        lang_name = lang_names.get(lang_code, lang_code)

        count = complete_language(ts_file, lang_code)
        total_translated += count

        print(f"{lang_name:20s} +{count:2d} translations")

    print("\n" + "=" * 80)
    print("VERIFICATION")
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
            status = "✅ 100% COMPLETE"
        else:
            status = f"⚠️  {finished}/{total} ({pct:.1f}%)"
            all_complete = False

        print(f"{lang_name:20s} {status}")

    print("=" * 80)
    if all_complete:
        print("🎉 SUCCESS! ALL 12 LANGUAGES AT 100%!")
    else:
        print("⚠️  Some translations still incomplete")

    print(f"\n✅ Total translations applied: {total_translated}")

if __name__ == "__main__":
    main()

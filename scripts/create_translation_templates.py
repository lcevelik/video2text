#!/usr/bin/env python3
"""
Create Qt .ts translation template files manually from known string inventory.

Generates properly formatted XML .ts files that can be edited with Qt Linguist
or any text editor, then compiled to .qm files.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path


# All translatable strings from the application
# Format: (context, source_text)
TRANSLATABLE_STRINGS = [
    # Window titles and main UI
    ("FonixFlowQt", "FonixFlow - Whisper Transcription"),
    ("FonixFlowQt", "Ready"),
    ("FonixFlowQt", "Ready to transcribe"),
    ("FonixFlowQt", "Ready to record"),

    # Tab names
    ("FonixFlowQt", "Record"),
    ("FonixFlowQt", "Upload"),
    ("FonixFlowQt", "Transcript"),

    # Menu items
    ("FonixFlowQt", "⚙️ Settings"),
    ("FonixFlowQt", "🎨 Theme"),
    ("FonixFlowQt", "🔄 Auto (System)"),
    ("FonixFlowQt", "🔄 Auto"),
    ("FonixFlowQt", "☀️ Light"),
    ("FonixFlowQt", "🌙 Dark"),
    ("FonixFlowQt", "Enable Deep Scan (Slower)"),
    ("FonixFlowQt", "📁 Change Recording Directory"),
    ("FonixFlowQt", "🗂️ Open Recording Directory"),
    ("FonixFlowQt", "🔄 New Transcription"),

    # Settings sidebar
    ("FonixFlowQt", "▼ ⚙️ Settings"),
    ("FonixFlowQt", "▶ ⚙️ Settings"),
    ("FonixFlowQt", "▼ 🎨 Theme"),
    ("FonixFlowQt", "▶ 🎨 Theme"),
    ("FonixFlowQt", "Recordings save to:"),
    ("FonixFlowQt", "📂 Change Folder"),
    ("FonixFlowQt", "🗂️ Open Folder"),

    # Sidebar actions
    ("FonixFlowQt", "New Transcription"),
    ("FonixFlowQt", "Change Recordings Folder"),
    ("FonixFlowQt", "Open Recordings Folder"),

    # Buttons
    ("FonixFlowQt", "Start Recording"),
    ("FonixFlowQt", "Transcribe Recording"),
    ("FonixFlowQt", "💾 Save Transcription"),
    ("FonixFlowQt", "✖ Cancel Transcription"),
    ("FonixFlowQt", "Close"),

    # Info labels
    ("FonixFlowQt", "Recording will use the system's default microphone and audio output."),
    ("FonixFlowQt", "💡 Files automatically transcribe when dropped or selected"),
    ("FonixFlowQt", "💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click 'Transcribe Recording' to manually start transcription"),
    ("FonixFlowQt", "Transcription text will appear here..."),
    ("FonixFlowQt", "Duration: 0:00"),

    # VU Meters
    ("FonixFlowQt", "Microphone"),
    ("FonixFlowQt", "Speaker"),

    # Recording status
    ("FonixFlowQt", "🔴 Recording from Microphone + Speaker..."),
    ("FonixFlowQt", "Recording in progress..."),
    ("FonixFlowQt", "Processing recording..."),

    # Transcription progress
    ("FonixFlowQt", "Starting…"),

    # File dialogs
    ("FonixFlowQt", "Select Video or Audio File"),
    ("FonixFlowQt", "Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)"),
    ("FonixFlowQt", "Select Recordings Folder"),
    ("FonixFlowQt", "Save Transcription"),
    ("FonixFlowQt", "Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)"),

    # Message boxes
    ("FonixFlowQt", "No Microphone Found"),
    ("FonixFlowQt", "No audio input device detected!"),
    ("FonixFlowQt", "Device Found"),
    ("FonixFlowQt", "No Recording"),
    ("FonixFlowQt", "No recording available. Please record first."),
    ("FonixFlowQt", "No File"),
    ("FonixFlowQt", "Please select a file first."),
    ("FonixFlowQt", "No Transcription"),
    ("FonixFlowQt", "Please transcribe a file first."),
    ("FonixFlowQt", "Saved Successfully"),
    ("FonixFlowQt", "Settings Updated"),
    ("FonixFlowQt", "Save Error"),
    ("FonixFlowQt", "Could Not Open Folder"),
    ("FonixFlowQt", "Transcription Error"),

    # Recording Dialog
    ("RecordingDialog", "Audio Recording"),
    ("RecordingDialog", "Audio Recording"),
    ("RecordingDialog", "What will be recorded:"),
    ("RecordingDialog", "Microphone: Your voice and ambient sounds"),
    ("RecordingDialog", "Speaker: System audio, music, video calls"),
    ("RecordingDialog", "📝 Both sources mixed into one recording"),
    ("RecordingDialog", "🔴 Start Recording"),
    ("RecordingDialog", "⏹️ Stop Recording"),
    ("RecordingDialog", "💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured."),
    ("RecordingDialog", "⏹️ Stopping recording..."),

    # Language Selection Dialog
    ("MultiLanguageChoiceDialog", "Language Mode"),
    ("MultiLanguageChoiceDialog", "Is your file multi-language?"),
    ("MultiLanguageChoiceDialog", "Select language type:"),
    ("MultiLanguageChoiceDialog", "English (uses optimized .en model)"),
    ("MultiLanguageChoiceDialog", "Other language (uses multilingual model)"),
    ("MultiLanguageChoiceDialog", "Select one language type before confirming."),
    ("MultiLanguageChoiceDialog", "Select languages present (check all that apply):"),
    ("MultiLanguageChoiceDialog", "At least one language must be selected before confirming."),
    ("MultiLanguageChoiceDialog", "Multi-Language"),
    ("MultiLanguageChoiceDialog", "Confirm Languages"),
    ("MultiLanguageChoiceDialog", "Single-Language"),
    ("MultiLanguageChoiceDialog", "Confirm Selection"),
    ("MultiLanguageChoiceDialog", "Cancel to decide later."),
    ("MultiLanguageChoiceDialog", "No Languages Selected"),
    ("MultiLanguageChoiceDialog", "Select at least one language to proceed."),
    ("MultiLanguageChoiceDialog", "No Language Type Selected"),
    ("MultiLanguageChoiceDialog", "Please select either English or Other language."),

    # Language names
    ("MultiLanguageChoiceDialog", "English"),
    ("MultiLanguageChoiceDialog", "Czech"),
    ("MultiLanguageChoiceDialog", "German"),
    ("MultiLanguageChoiceDialog", "French"),
    ("MultiLanguageChoiceDialog", "Spanish"),
    ("MultiLanguageChoiceDialog", "Italian"),
    ("MultiLanguageChoiceDialog", "Polish"),
    ("MultiLanguageChoiceDialog", "Russian"),
    ("MultiLanguageChoiceDialog", "Chinese"),
    ("MultiLanguageChoiceDialog", "Japanese"),
    ("MultiLanguageChoiceDialog", "Korean"),
    ("MultiLanguageChoiceDialog", "Arabic"),

    # Widgets
    ("DropZone", "Drag and drop video/audio file"),

    # Workers
    ("TranscriptionWorker", "Extracting audio..."),
    ("TranscriptionWorker", "Transcribing..."),
    ("TranscriptionWorker", "Finishing up..."),
    ("TranscriptionWorker", "Finalizing transcription..."),
    ("TranscriptionWorker", "Transcription complete!"),
]


def create_ts_file(lang_code, output_path):
    """
    Create a .ts translation file for the specified language.

    Args:
        lang_code: Language code (e.g., 'es', 'fr', 'zh_CN')
        output_path: Path where the .ts file should be saved
    """
    # Create root TS element
    root = ET.Element('TS')
    root.set('version', '2.1')
    root.set('language', lang_code)

    # Group strings by context
    contexts = {}
    for context, source_text in TRANSLATABLE_STRINGS:
        if context not in contexts:
            contexts[context] = []
        contexts[context].append(source_text)

    # Create context elements
    for context_name, messages in sorted(contexts.items()):
        context = ET.SubElement(root, 'context')

        name_elem = ET.SubElement(context, 'name')
        name_elem.text = context_name

        # Add each message
        for source_text in messages:
            message = ET.SubElement(context, 'message')

            source = ET.SubElement(message, 'source')
            source.text = source_text

            # Add empty translation element for translators to fill
            translation = ET.SubElement(message, 'translation')
            translation.set('type', 'unfinished')
            translation.text = ''

    # Pretty print XML
    xml_str = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    pretty_xml = '\n'.join(lines)

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print(f"✓ Created: {output_path.name} ({len(TRANSLATABLE_STRINGS)} strings)")


def main():
    """Generate .ts template files for multiple languages."""
    print("="*60)
    print("Creating Qt Translation Template Files (.ts)")
    print("="*60)
    print()

    # Create i18n directory at project root (parent of scripts dir)
    i18n_dir = Path(__file__).parent.parent / "i18n"
    i18n_dir.mkdir(exist_ok=True)

    # Priority languages
    languages = [
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('zh_CN', 'Chinese (Simplified)'),
        ('ja', 'Japanese'),
        ('pt_BR', 'Portuguese (Brazil)'),
        ('ru', 'Russian'),
        ('ko', 'Korean'),
        ('it', 'Italian'),
        ('pl', 'Polish'),
        ('ar', 'Arabic'),
        ('cs', 'Czech'),
    ]

    print(f"Generating templates for {len(languages)} languages...\n")

    for lang_code, lang_name in languages:
        ts_file = i18n_dir / f"fonixflow_{lang_code}.ts"
        print(f"{lang_name} ({lang_code})...")
        create_ts_file(lang_code, ts_file)

    print("\n" + "="*60)
    print("✓ All translation templates created successfully!")
    print("="*60)
    print(f"\nGenerated {len(languages)} .ts files in: {i18n_dir}")
    print(f"Total translatable strings: {len(TRANSLATABLE_STRINGS)}")
    print("\nNext steps:")
    print("1. Edit .ts files to add translations (use Qt Linguist or text editor)")
    print("2. Compile to .qm files: pyside6-lrelease i18n/fonixflow_<lang>.ts")
    print("3. App will auto-load based on system language")


if __name__ == "__main__":
    main()

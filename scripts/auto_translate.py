#!/usr/bin/env python3
"""
Auto-translate all unfinished strings in translation files.

This script provides translations for all languages based on the source English strings.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Translation dictionary: {language_code: {english_text: translated_text}}
TRANSLATIONS = {
    'cs': {  # Czech
        '🔍 Enable Deep Scan (Slower)': '🔍 Povolit Hluboké Skenování (Pomalejší)',
        '🗂️ Open Recording Directory': '🗂️ Otevřít Adresář Nahrávek',
        '▼ 🎨 Theme': '▼ 🎨 Motiv',
        '▶ 🎨 Theme': '▶ 🎨 Motiv',
        '📂 Change Folder': '📂 Změnit Složku',
        '🗂️ Open Folder': '🗂️ Otevřít Složku',
        'Change Recordings Folder': 'Změnit Složku Nahrávek',
        'Open Recordings Folder': 'Otevřít Složku Nahrávek',
        'Duration: 0:00': 'Trvání: 0:00',
        'English': 'Angličtina',
        'Czech': 'Čeština',
        'German': 'Němčina',
        'French': 'Francouzština',
        'Spanish': 'Španělština',
        'Italian': 'Italština',
        'Polish': 'Polština',
        'Russian': 'Ruština',
        'Chinese': 'Čínština',
        'Japanese': 'Japonština',
        'Korean': 'Korejština',
        'Arabic': 'Arabština',
        'Extracting audio...': 'Extrakce zvuku...',
        'Transcribing...': 'Přepisování...',
        'Finishing up...': 'Dokončování...',
        'Finalizing transcription...': 'Finalizace přepisu...',
        'Transcription complete!': 'Přepis dokončen!',
    },
    'es': {  # Spanish
        '🗂️ Open Recording Directory': '🗂️ Abrir Directorio de Grabaciones',
        '🔍 Enable Deep Scan (Slower)': '🔍 Activar Escaneo Profundo (Más Lento)',
        '▼ ⚙️ Settings': '▼ ⚙️ Configuración',
        '▶ ⚙️ Settings': '▶ ⚙️ Configuración',
        '▼ 🎨 Theme': '▼ 🎨 Tema',
        '▶ 🎨 Theme': '▶ 🎨 Tema',
        '📂 Change Folder': '📂 Cambiar Carpeta',
        '🗂️ Open Folder': '🗂️ Abrir Carpeta',
        'Change Recordings Folder': 'Cambiar Carpeta de Grabaciones',
        'Open Recordings Folder': 'Abrir Carpeta de Grabaciones',
        'Duration: 0:00': 'Duración: 0:00',
        'No Transcription': 'Sin Transcripción',
        'Select at least one language to proceed.': 'Seleccione al menos un idioma para continuar.',
        'English': 'Inglés',
        'Czech': 'Checo',
        'German': 'Alemán',
        'French': 'Francés',
        'Spanish': 'Español',
        'Italian': 'Italiano',
        'Polish': 'Polaco',
        'Russian': 'Ruso',
        'Chinese': 'Chino',
        'Japanese': 'Japonés',
        'Korean': 'Coreano',
        'Arabic': 'Árabe',
        'Extracting audio...': 'Extrayendo audio...',
        'Transcribing...': 'Transcribiendo...',
        'Finishing up...': 'Finalizando...',
        'Finalizing transcription...': 'Finalizando transcripción...',
        'Transcription complete!': '¡Transcripción completa!',
    },
    'fr': {  # French
        'FonixFlow - Whisper Transcription': 'FonixFlow - Transcription Whisper',
        'Ready': 'Prêt',
        'Ready to transcribe': 'Prêt à transcrire',
        'Ready to record': 'Prêt à enregistrer',
        'Record': 'Enregistrer',
        'Upload': 'Télécharger',
        'Transcript': 'Transcription',
        '⚙️ Settings': '⚙️ Paramètres',
        '🎨 Theme': '🎨 Thème',
        '🔄 Auto (System)': '🔄 Auto (Système)',
        '☀️ Light': '☀️ Clair',
        '🌙 Dark': '🌙 Sombre',
        '🔍 Enable Deep Scan (Slower)': '🔍 Activer Scan Profond (Plus Lent)',
        '📁 Change Recording Directory': '📁 Changer le Répertoire d\'Enregistrement',
        '🗂️ Open Recording Directory': '🗂️ Ouvrir le Répertoire d\'Enregistrement',
        '🔄 New Transcription': '🔄 Nouvelle Transcription',
        '▼ ⚙️ Settings': '▼ ⚙️ Paramètres',
        '▶ ⚙️ Settings': '▶ ⚙️ Paramètres',
        '▼ 🎨 Theme': '▼ 🎨 Thème',
        '▶ 🎨 Theme': '▶ 🎨 Thème',
        'Recordings save to:': 'Les enregistrements sont sauvegardés dans :',
        '📂 Change Folder': '📂 Changer le Dossier',
        '🗂️ Open Folder': '🗂️ Ouvrir le Dossier',
        'New Transcription': 'Nouvelle Transcription',
        'Change Recordings Folder': 'Changer le Dossier d\'Enregistrements',
        'Open Recordings Folder': 'Ouvrir le Dossier d\'Enregistrements',
        '🎤 Start Recording': '🎤 Démarrer l\'Enregistrement',
        'Transcribe Recording': 'Transcrire l\'Enregistrement',
        '💾 Save Transcription': '💾 Enregistrer la Transcription',
        '✖ Cancel Transcription': '✖ Annuler la Transcription',
        'Close': 'Fermer',
        'Recording will use the system\'s default microphone and audio output.': 'L\'enregistrement utilisera le microphone et la sortie audio par défaut du système.',
        '💡 Files automatically transcribe when dropped or selected': '💡 Les fichiers se transcrivent automatiquement lorsqu\'ils sont déposés ou sélectionnés',
        '💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click \'Transcribe Recording\' to manually start transcription': '💡 Après l\'arrêt, l\'enregistrement est sauvegardé mais PAS automatiquement transcrit\n💡 Cliquez sur \'Transcrire l\'Enregistrement\' pour démarrer manuellement la transcription',
        'Transcription text will appear here...': 'Le texte de transcription apparaîtra ici...',
        'Duration: 0:00': 'Durée : 0:00',
        'Microphone': 'Microphone',
        'Speaker': 'Haut-parleur',
        '🔴 Recording from Microphone + Speaker...': '🔴 Enregistrement du Microphone + Haut-parleur...',
        'Recording in progress...': 'Enregistrement en cours...',
        'Processing recording...': 'Traitement de l\'enregistrement...',
        'Starting…': 'Démarrage…',
        'Select Video or Audio File': 'Sélectionner un Fichier Vidéo ou Audio',
        'Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)': 'Fichiers Média (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;Tous les Fichiers (*.*)',
        'Select Recordings Folder': 'Sélectionner le Dossier d\'Enregistrements',
        'Save Transcription': 'Enregistrer la Transcription',
        'Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)': 'Fichiers Texte (*.txt);;Sous-titres SRT (*.srt);;Sous-titres VTT (*.vtt)',
        'No Microphone Found': 'Aucun Microphone Trouvé',
        'No audio input device detected!': 'Aucun périphérique d\'entrée audio détecté !',
        'Device Found': 'Périphérique Trouvé',
        'No Recording': 'Aucun Enregistrement',
        'No recording available. Please record first.': 'Aucun enregistrement disponible. Veuillez d\'abord enregistrer.',
        'No File': 'Aucun Fichier',
        'Please select a file first.': 'Veuillez d\'abord sélectionner un fichier.',
        'No Transcription': 'Aucune Transcription',
        'Please transcribe a file first.': 'Veuillez d\'abord transcrire un fichier.',
        'Saved Successfully': 'Enregistré avec Succès',
        'Settings Updated': 'Paramètres Mis à Jour',
        'Save Error': 'Erreur d\'Enregistrement',
        'Could Not Open Folder': 'Impossible d\'Ouvrir le Dossier',
        'Transcription Error': 'Erreur de Transcription',
        'Language Mode': 'Mode Linguistique',
        'Is your file multi-language?': 'Votre fichier est-il multilingue ?',
        'Select language type:': 'Sélectionner le type de langue :',
        'English (uses optimized .en model)': 'Anglais (utilise le modèle .en optimisé)',
        'Other language (uses multilingual model)': 'Autre langue (utilise le modèle multilingue)',
        'Select one language type before confirming.': 'Sélectionnez un type de langue avant de confirmer.',
        'Select languages present (check all that apply):': 'Sélectionnez les langues présentes (cochez toutes celles qui s\'appliquent) :',
        'At least one language must be selected before confirming.': 'Au moins une langue doit être sélectionnée avant de confirmer.',
        'Multi-Language': 'Multi-Langue',
        'Confirm Languages': 'Confirmer les Langues',
        'Single-Language': 'Langue Unique',
        'Confirm Selection': 'Confirmer la Sélection',
        'Cancel to decide later.': 'Annuler pour décider plus tard.',
        'No Languages Selected': 'Aucune Langue Sélectionnée',
        'Select at least one language to proceed.': 'Sélectionnez au moins une langue pour continuer.',
        'No Language Type Selected': 'Aucun Type de Langue Sélectionné',
        'Please select either English or Other language.': 'Veuillez sélectionner Anglais ou Autre langue.',
        'English': 'Anglais',
        'Czech': 'Tchèque',
        'German': 'Allemand',
        'French': 'Français',
        'Spanish': 'Espagnol',
        'Italian': 'Italien',
        'Polish': 'Polonais',
        'Russian': 'Russe',
        'Chinese': 'Chinois',
        'Japanese': 'Japonais',
        'Korean': 'Coréen',
        'Arabic': 'Arabe',
        'Audio Recording': 'Enregistrement Audio',
        '🎤 Audio Recording': '🎤 Enregistrement Audio',
        'What will be recorded:': 'Ce qui sera enregistré :',
        '🎤 Microphone: Your voice and ambient sounds': '🎤 Microphone : Votre voix et les sons ambiants',
        '🔊 Speaker: System audio, music, video calls': '🔊 Haut-parleur : Audio système, musique, appels vidéo',
        '📝 Both sources mixed into one recording': '📝 Les deux sources mélangées dans un enregistrement',
        '🔴 Start Recording': '🔴 Démarrer l\'Enregistrement',
        '⏹️ Stop Recording': '⏹️ Arrêter l\'Enregistrement',
        '💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.': '💡 Parfait pour les appels vidéo, les réunions, ou tout scénario où vous avez besoin\nde capturer votre voix et l\'audio système.',
        '⏹️ Stopping recording...': '⏹️ Arrêt de l\'enregistrement...',
        'Extracting audio...': 'Extraction de l\'audio...',
        'Transcribing...': 'Transcription en cours...',
        'Finishing up...': 'Finalisation...',
        'Finalizing transcription...': 'Finalisation de la transcription...',
        'Transcription complete!': 'Transcription terminée !',
    },
}


def translate_file(ts_file: Path, lang_code: str) -> int:
    """Translate unfinished strings in a .ts file."""
    if lang_code not in TRANSLATIONS:
        print(f"No translations available for {lang_code}")
        return 0

    translations = TRANSLATIONS[lang_code]
    tree = ET.parse(ts_file)
    root = tree.getroot()

    count = 0
    for context in root.findall('context'):
        for message in context.findall('message'):
            source = message.find('source')
            translation = message.find('translation')

            if source is not None and translation is not None:
                source_text = source.text or ""
                trans_type = translation.get('type', '')

                # Only translate unfinished strings
                if trans_type == 'unfinished' and source_text in translations:
                    translation.text = translations[source_text]
                    del translation.attrib['type']  # Remove unfinished attribute
                    count += 1

    # Write back to file
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)
    return count


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    i18n_dir = script_dir.parent / 'i18n'

    if not i18n_dir.exists():
        print(f"Error: i18n directory not found at {i18n_dir}")
        return 1

    print("Auto-translating unfinished strings...\n")

    total_translated = 0
    for lang_code in TRANSLATIONS.keys():
        ts_file = i18n_dir / f'fonixflow_{lang_code}.ts'
        if ts_file.exists():
            count = translate_file(ts_file, lang_code)
            print(f"{lang_code}: Translated {count} strings")
            total_translated += count
        else:
            print(f"{lang_code}: File not found - {ts_file}")

    print(f"\nTotal strings translated: {total_translated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

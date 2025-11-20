# PyInstaller build script for FonixFlow (Video2Text)
# Usage: Run this from the project root directory
# Example: powershell -Command "pyinstaller fonixflow.spec"

# Main entry point
main_script = 'fonixflow_qt.py'

# App name
app_name = 'FonixFlow'

# Icon file (optional, update path if you have a .ico)
icon_file = None  # e.g., 'assets/fonixflow.ico'

# Hidden imports (add any missing modules PyInstaller can't detect)
hidden_imports = [
    'PySide6',
    'numpy',
    'sounddevice',
    'transcription',
    'gui',
]

# Data files to include (add logo, themes, etc.)
datas = [
    # ('path/to/logo.png', 'assets'),
]

# Build command
build_cmd = f"pyinstaller --name {app_name} --onefile --windowed {main_script} "
if icon_file:
    build_cmd += f"--icon {icon_file} "
for imp in hidden_imports:
    build_cmd += f"--hidden-import {imp} "
for data in datas:
    build_cmd += f"--add-data '{data[0]};{data[1]}' "

print('Run this command to build your app:')
print(build_cmd)

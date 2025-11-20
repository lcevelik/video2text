# FonixFlow (Video2Text) - Building a Single Executable

## Prerequisites
- Windows 10 or later
- Python 3.11.x (for building, not required for end users)
- All dependencies listed in requirements.txt

## Build Steps
1. Open PowerShell in the project root directory.
2. (Optional) Create a virtual environment and install dependencies:
   ```powershell
   python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```
3. Install PyInstaller (already included in requirements.txt):
   ```powershell
   pip install pyinstaller
   ```
4. Build the executable:
   ```powershell
   pyinstaller fonixflow.spec
   ```
   - This will create a single .exe file in the `dist` folder.
   - The app will be fully portable and self-contained.

## Customization
- To add an icon, update `icon_file` in `fonixflow.spec` and place your .ico file in the project.
- To include extra data files (logos, themes), add them to the `datas` list in `fonixflow.spec`.

## Running the App
- After building, distribute the `dist\FonixFlow.exe` file.
- No installation or Python required for end users.

## Troubleshooting
- If you see missing DLL or module errors, add them to `hidden_imports` or `datas` in `fonixflow.spec`.
- Test on a clean Windows machine to confirm portability.

---
For advanced packaging (smaller size, faster startup), consider Nuitka. Let me know if you want Nuitka setup instructions!

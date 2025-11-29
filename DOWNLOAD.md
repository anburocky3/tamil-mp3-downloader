# Download & Build (Windows)

Simple guidance so users can get a ready EXE or build one locally.

Download a ready-made EXE

- Check the Releases page on GitHub for pre-built Windows EXE files:

  https://github.com/anburocky3/tamil-mp3-downloader/releases

Build a local EXE (one-file) using the included helper

1. Open a Windows Command Prompt in the project root.
2. (Optional) Create a virtual environment and activate it:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

3. Install runtime requirements and PyInstaller (the helper script does this too):

```cmd
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

4. Build using the helper script:

```cmd
build_exe.bat
```

What the build produces

- The EXE will be produced in `dist\` and will include the `VERSION` value in its filename, for example:

```
dist\tamil-mp3-downloader-v2.0.0.exe
```

- Run the EXE from a command prompt to see the interactive menu:

```cmd
cd dist
tamil-mp3-downloader-v2.0.0.exe
```

Notes & troubleshooting

- The EXE is a single-file bundle and can be large.
- Some antivirus scanners may flag freshly-built EXEs as suspicious. If that happens, test on another machine or submit the EXE to your AV vendor.
- If the EXE reports missing modules at runtime, re-run the build and check the `build\<name>\warn-*.txt` file produced by PyInstaller for hints; you may need to add hidden imports to `tamil_mp3_downloader.spec`.

Advanced (manual PyInstaller command)

If you prefer to run PyInstaller directly:

```cmd
pyinstaller tamil_mp3_downloader.spec
```

This uses the included spec which bundles the `data/` and `screenshots/` folders and reads `VERSION` for naming.

Questions?

Open an issue on GitHub or read `CONTRIBUTING.md` to suggest improvements to the build or release process.

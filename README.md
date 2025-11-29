# Tamil MP3 Downloader
A small, friendly tool to browse and download Tamil MP3 collections from index pages.

This project gives you two ways to run the downloader:
- `main.py` — the latest version with a nicer menu, download progress, sizes shown in MB, and smarter folder handling.
- `main-classic.py` — the older (classic) script. Use this if you prefer the original behavior.

Both scripts work similarly: pick a category, choose an album or enter an "Index of" URL, and the script downloads MP3 files into an `output/` folder.

---

Quick highlights (what's new / useful)
- Menu-driven UI: choose categories, artists or composers from the built-in lists.
- Index numbers and ranges: pick single items like `3`, several like `1,3,5`, or a range like `2-4` — or just `all` to download everything in the list.
- Clear progress: each file shows an index number and a download icon (⬇️) while downloading.
- Size in MB: where available the script shows file sizes in MB instead of raw chunk counts.
- Nested folders: if MP3s live inside subfolders, the downloader will enter those folders and fetch the files.
- Organized output: files are saved under `output/<Category>/<AlbumName>/` so downloads stay tidy.
- By-Genre: planned and shown as "Coming Soon" in the menu (not implemented yet).

---

Getting started (simple)

1) Prerequisites
- Python 3.8+ installed on your system.
- A working internet connection to fetch files.

2) Install dependencies
Open a terminal (Windows cmd / PowerShell or macOS/Linux terminal) in this repository folder and run:

```bash
pip install -r requirements.txt
```

3) Run the downloader
- Latest UI (recommended):

```bash
python main.py
```

- Classic script (original experience):

```bash
python main-classic.py
```

When the menu appears:
- Type the number for the category you want (for example: `2` for Music Director Hits).
- For JSON-backed lists (Star/Music Director/Singer hits) you'll see numbered albums — choose by number, range, `all`, or `back`.
- When asked for a save folder, press Enter to accept the default (album name), or type another name.
- The script will show per-file progress and a final summary (total, successful, failed).

Where files are saved
- The downloader saves files to:

```
output/<CategoryName>/<AlbumName>/
```

Example:
```
output/Music Director Hits/A.R.Rahman Hits-1 (Soulful Melodies)/song.mp3
```

Data used by the menu
- The app reads pre-built lists in the `data/` folder, for example:
  - `data/music-directors-hits.json`
  - `data/singer-hits.json`
  - `data/star-hits.json`
  - and other `data/*.json` files that contain album lists.

If you want to add your own list, add a JSON file in the same format (array of {id, href, name}).

Notes and behavior details (friendly)
- Size display: the script uses the server's `Content-Length` header to show MB; if the server doesn't provide it the size may show as `Unknown` or `0.00 MB` during the progress bar.
- Nested folders: the downloader will follow directory links and collect MP3s inside nested folders (limited depth to avoid very deep crawls).
- "Download All": this will download every album you selected — for very large selections this can take a long time and use lots of disk space.
- If a download fails it will be skipped and shown in the final summary.

A short, important note
> Use this script responsibly. This tool is intended for educational and personal use. Do not use it to infringe copyrights — only download material you are allowed to.

Screenshots
- The `screenshots/` folder contains sample images showing the UI and how results look.

License and links
- License: MIT — see the `LICENSE` file.
- More projects and pro tools by the author:
  - Mp3 Downloader Pro (latest): https://github.com/anburocky3/mp3-downloader
  - Fork / download this project: https://github.com/anburocky3/tamil-mp3-downloader/fork

Author
- Anbuselvan Rocky — https://github.com/anburocky3

---

If you'd like, I can:
- Add a short video or GIF showing the menu-driven flow.
- Print a short preview (first 5 files) before downloading a big selection.
- Add a small config file to tweak recursion depth or default output location.

Tell me which (if any) you want next and I'll implement it.

---

## Building a Windows EXE (Windows users)

If you'd like to distribute a single executable so Windows users don't need Python or dependencies installed, you can build a single-file EXE using PyInstaller. A helper batch script (`build_exe.bat`) is included in the repository to make this easy.

Quick steps (recommended, Windows cmd.exe):

1. Open a command prompt in the project root (where this README and `main.py` live).
2. (Optional) Create and activate a virtual environment to keep the build environment clean:

   python -m venv .venv
   .venv\Scripts\activate

3. Install build-time dependencies:

   pip install --upgrade pip
   pip install pyinstaller

4. Build using the included helper script (double-click or run from cmd):

   build_exe.bat

   The script runs PyInstaller with the options to create a single-file console EXE named `tamil-mp3-downloader.exe`. The resulting EXE will be created in `dist\tamil-mp3-downloader.exe`.

Manual PyInstaller command (if you prefer):

pyinstaller --clean --noconfirm --onefile --console --name "tamil-mp3-downloader" \
  --add-data "data;data" \
  --add-data "data\\old;data\\old" \
  --add-data "screenshots;screenshots" \
  main.py

Notes and tips:

- The `--add-data` options bundle the `data/` JSON files and `screenshots/` into the EXE so the menu lists still work at runtime.
- On Windows, PyInstaller uses a semicolon (`;`) as the source;dest separator for `--add-data`.
- The generated EXE can be large (tens of MB) because it embeds Python and dependencies.
- Some antivirus products may flag newly-built EXEs as suspicious (false positives). If that happens, test on a second machine or submit the EXE to the vendor for whitelisting.
- If you want a GUI-less console, keep `--console` so the interactive menu works; if you later build a GUI wrapper, remove `--console`.

Basic testing after build:

1. Run the EXE from a command prompt: `dist\\tamil-mp3-downloader.exe`.
2. Try a quick download with a small album or a single Index Of URL to confirm networking and file writes work.
3. Check the `output/` folder next to the EXE (or the current working directory that launched the EXE) for saved files.

Troubleshooting:

- If the EXE fails to run due to missing modules, re-run PyInstaller and inspect the build log. You can also create and edit a `.spec` file to add hiddenimports or tweak bundling.
- If icons or extra files are needed, update `build_exe.bat` to include `--icon "path\\to\\icon.ico"` and other `--add-data` entries.

If you want, I can also:
- Add a ready-made `.spec` file (for fine-grained control) and an example icon.
- Add a small smoke test script that runs the built EXE with a non-interactive mode for CI validation.

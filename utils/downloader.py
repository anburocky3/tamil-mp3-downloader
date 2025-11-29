from pathlib import Path
import requests
from urllib.parse import unquote
from clint.textui import progress
from colorama import Fore, Style

AUDIO_EXTS = ('.wav', '.mp3', '.mp4', '.m4a', '.aac', '.flac')

BLUE_COLOR = Fore.BLUE
RESET = Style.RESET_ALL

def _is_audio(href: str) -> bool:
    return bool(href) and href.lower().endswith(AUDIO_EXTS)


def download_links(links, base_url, out_dir: Path, chunk_size: int = 256):
    """Download audio links from a list of hrefs.

    links: iterable of href strings (maybe absolute or relative)
    base_url: used to build absolute URL for relative hrefs
    out_dir: Path object for destination directory
    chunk_size: chunk size for streaming

    Returns: (total_audio, success_count, failed_count)
    """
    # Normalize links to a list so we can count and enumerate audio files
    link_list = list(links)
    audio_links = [h for h in link_list if _is_audio(h)]
    total_audio = len(audio_links)
    success = 0
    failed = 0

    # enumerate audio links so we can show the index number (1-based)
    for idx, href in enumerate(audio_links, start=1):
        if href.startswith('http://') or href.startswith('https://'):
            file_url = href
        else:
            file_url = base_url.rstrip('/') + '/' + href.lstrip('/')

        filename = unquote(href).split('/')[-1]
        out_path = out_dir / filename

        try:
            req = requests.get(file_url, stream=True, timeout=30)
            req.raise_for_status()
        except Exception:
            failed += 1
            continue

        try:
            with open(str(out_path), 'wb') as fh:
                length_header = req.headers.get('content-length')
                try:
                    length = int(length_header) if length_header else 0
                except Exception:
                    length = 0

                # expected_size for the progress bar should be number of chunks
                # but for user-friendly display show the size in MB
                if length:
                    # compute number of chunks (at least 1) for progress bar
                    expected_chunks = max(1, int(length // chunk_size))
                    size_mb = length / (1024 * 1024)
                    size_display = f"{size_mb:.2f} MB"
                else:
                    expected_chunks = None
                    size_display = 'Unknown size'

                # label includes download icon, index, total and size in MB
                label = f"⬇️  [{idx}/{total_audio}] {filename} ({size_display})"
                for chunk in progress.bar(req.iter_content(chunk_size), expected_size=expected_chunks, label=label):
                    if chunk:
                        fh.write(chunk)
            success += 1
        except Exception:
            failed += 1
            try:
                if out_path.exists():
                    out_path.unlink()
            except Exception:
                pass
            continue

    return total_audio, success, failed

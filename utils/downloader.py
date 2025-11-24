from pathlib import Path
import requests
from urllib.parse import unquote
from clint.textui import progress

AUDIO_EXTS = ('.wav', '.mp3', '.mp4', '.m4a', '.aac', '.flac')


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
    total_audio = 0
    success = 0
    failed = 0

    for href in links:
        if not _is_audio(href):
            continue
        total_audio += 1

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

                expected = int(length / chunk_size) if length else None
                for chunk in progress.bar(req.iter_content(chunk_size), expected_size=expected, label=filename + '  '):
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


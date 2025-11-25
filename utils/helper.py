from bs4 import BeautifulSoup
import re
from typing import List, Tuple
import os
from typing import Optional


def ensure_emoji_spacing(s: str) -> str:
    """Ensure there's a space after common emojis so text doesn't look glued to them."""
    if not s:
        return s
    emojis = ['👋', '😀', '✅', '❌', '💁\u200d♂️', '💁']
    out = s
    for e in emojis:
        out = re.sub(re.escape(e) + r"(?!\s)", e + ' ', out)
    return out


def is_navigation_or_sort_link(href: str) -> bool:
    if not href:
        return True
    h = href.strip()
    low = h.lower()
    if low.startswith('javascript:') or low.startswith('mailto:') or low.startswith('#'):
        return True
    if low.startswith('?c=') or ('?c=' in low and ';o=' in low):
        return True
    if low.startswith('?'):
        return True
    if h.endswith('/'):
        return True
    if h in ('../', './'):
        return True
    return False


def collect_filtered_hrefs(soup: BeautifulSoup) -> List[str]:
    hrefs: List[str] = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if is_navigation_or_sort_link(href):
            continue
        hrefs.append(href)
    return hrefs


def count_audio_hrefs(hrefs: List[str]) -> int:
    audio_exts = ('.wav', '.mp3', '.mp4', '.m4a', '.aac', '.flac')
    return sum(1 for h in hrefs if h.lower().endswith(audio_exts))


def parse_star_selection(sel: str, star_data: List[dict]) -> Tuple[List[dict], List[int]]:
    """Parse selection string (e.g. 'all', '1', '1,3,5', '2-4') and return (selected_items, missing_ids)."""
    sel = (sel or '').strip().lower()
    if not sel:
        return [], []
    if sel in ('all', 'a'):
        return list(star_data), []

    parts = [p.strip() for p in sel.split(',') if p.strip()]
    ids = []
    for part in parts:
        if '-' in part:
            try:
                start_s, end_s = part.split('-', 1)
                start = int(start_s)
                end = int(end_s)
                if start > end:
                    start, end = end, start
                ids.extend(range(start, end + 1))
            except Exception:
                continue
        else:
            try:
                ids.append(int(part))
            except Exception:
                continue

    seen = set()
    uniq_ids = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            uniq_ids.append(i)

    selected_items = []
    missing = []
    for sid in uniq_ids:
        found = None
        for item in star_data:
            try:
                if int(item.get('id')) == sid:
                    found = item
                    break
            except Exception:
                continue
        if found:
            selected_items.append(found)
        else:
            missing.append(sid)

    return selected_items, missing


def clear_screen() -> None:
    """Clear terminal screen in a cross-platform way (cls on Windows, clear on POSIX)."""
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    except Exception:
        # fallback
        print('\n' * 3)


def print_banner(banner: str, color_prefix: Optional[str] = '', reset: Optional[str] = '') -> None:
    """Print the provided banner string, wrapped in optional color prefixes and reset.

    The helper doesn't assume where the banner text comes from so the caller (main.py)
    can pass `BANNER` and color constants.
    """
    try:
        if color_prefix is None:
            color_prefix = ''
        if reset is None:
            reset = ''
        print(f"{color_prefix}{banner}{reset}")
    except Exception:
        # Last-resort: just print raw banner
        try:
            print(banner)
        except Exception:
            pass


def clear_below_banner(banner: str, color_prefix: Optional[str] = '', reset: Optional[str] = '') -> None:
    """Clear the terminal and re-print the banner so the banner stays visible below a cleared screen."""
    clear_screen()
    print_banner(banner, color_prefix, reset)

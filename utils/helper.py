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


def format_terminal_link(text: str, url: str) -> str:
    """Return a terminal clickable link (OSC 8) if the terminal supports it.

    Many modern terminals (iTerm2, Windows Terminal, GNOME Terminal, kitty) support
    the OSC 8 sequence that wraps text as a clickable link. Older terminals (classic
    cmd.exe) won't render it and will display the raw escape codes; the caller may
    choose to fall back to printing the plain URL as well.

    This function always returns the OSC 8 sequence; callers can decide to also
    print the raw URL as fallback or open the URL in a browser when selected.
    """
    if not text or not url:
        return text or url
    # OSC 8 format: ESC ] 8 ;; URL ST  text  ESC ] 8 ;; ST
    # ST can be either BEL (\a) or ESC backslash; use ESC backslash for portability
    ESC = "\033"
    OSC = f"{ESC}]8;;{url}{ESC}\\"
    OSC_END = f"{ESC}]8;;{ESC}\\"
    return f"{OSC}{text}{OSC_END}"


def supports_terminal_links() -> bool:
    """Heuristically determine whether the current terminal likely supports OSC 8 links.

    This cannot be perfect. We look for known environment signals used by modern
    terminals that support hyperlinks: Windows Terminal (WT_SESSION), iTerm2 (TERM_PROGRAM),
    many xterm-like terminals via TERM, and the presence of COLORTERM. If unsure, return False.
    """
    try:
        # Windows Terminal exposes WT_SESSION
        if os.name == 'nt' and 'WT_SESSION' in os.environ:
            return True
        # iTerm2 exposes TERM_PROGRAM=Apple_Terminal or iTerm.app
        term_program = os.environ.get('TERM_PROGRAM', '')
        if term_program:
            if 'iTerm' in term_program or 'Apple_Terminal' in term_program:
                return True
        # Common Unix TERM values that typically support OSC/ANSI sequences
        term = os.environ.get('TERM', '')
        if term and any(x in term.lower() for x in ('xterm', 'screen', 'tmux', 'rxvt', 'vt100', 'linux', 'konsole')):
            return True
        # Many terminal emulators set COLORTERM
        if os.environ.get('COLORTERM'):
            return True
    except Exception:
        return False
    return False

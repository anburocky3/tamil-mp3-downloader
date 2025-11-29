from pathlib import Path
from bs4 import BeautifulSoup
import requests
from urllib.parse import unquote
import sys
import json
import os

# colorama init (cross-platform ANSI support)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except Exception:
    class _Dummy:
        def __getattr__(self, _):
            return ''
    Fore = _Dummy()
    Style = _Dummy()

# Import helpers from split modules
from utils.helper import (
    collect_filtered_hrefs,
    count_audio_hrefs,
    parse_star_selection,
    ensure_emoji_spacing,
    clear_screen,
    print_banner,
    clear_below_banner,
    format_terminal_link,
    supports_terminal_links,
)
from utils.downloader import download_links

# Re-export parse_star_selection for backward compatibility
__all__ = ["parse_star_selection"]

# Banner, author and version
BANNER = r'''
 /$$$$$$$$                      /$$ /$$       /$$      /$$ /$$$$$$$   /$$$$$$ 
|__  $$__/                     |__/| $$      | $$$    /$$$| $$__  $$ /$$__  $$
   | $$  /$$$$$$  /$$$$$$/$$$$  /$$| $$      | $$$$  /$$$$| $$  \ $$|__/  \ $$
   | $$ |____  $$| $$_  $$_  $$| $$| $$      | $$ $$/$$ $$| $$$$$$$/   /$$$$$/
   | $$  /$$$$$$$| $$ \ $$ \ $$| $$| $$      | $$  $$$| $$| $$____/   |___  $$
   | $$ /$$__  $$| $$ | $$ | $$| $$| $$      | $$\  $ | $$| $$       /$$  \ $$
   | $$|  $$$$$$$| $$ | $$ | $$| $$| $$      | $$ \/  | $$| $$      |  $$$$$$/
   |__/ \_______/|__/ |__/ |__/|__/|__/      |__/     |__/|__/       \______/ 
 
       Tamil MP3 Downloader - Author: Anbuselvan Rocky
'''

# Color choices
BANNER_COLOR = Fore.CYAN + Style.BRIGHT
MENU_COLOR = Fore.YELLOW + Style.BRIGHT
PROMPT_COLOR = Fore.GREEN + Style.BRIGHT
SUCCESS_COLOR = Fore.GREEN
ERROR_COLOR = Fore.RED
INFO_COLOR = Fore.MAGENTA
COMING_SOON_COLOR = Fore.MAGENTA + Style.DIM
RESET = Style.RESET_ALL

CATEGORIES = {
    '1': 'Star Hits',
    '2': 'Music Director Hits',
    '3': 'Singer Hits',
    '4': 'Old Songs',
    '5': 'Ring tones / Instrumentals',
    '6': 'By Genre',
}


def goodbye_and_exit():
    try:
        print('\n' + INFO_COLOR + 'GoodBye Nanba/Nanbis!' + RESET)
    except Exception:
        print('\nGoodBye Nanba/Nanbis!')
    sys.exit(0)


def get_resource_path(rel_path: str) -> str:
    """Return an absolute path to a resource, working both when running from source
    and when bundled by PyInstaller (where resources are extracted to sys._MEIPASS).

    rel_path should be the path relative to the project root, for example: 'data/star-hits.json'
    """
    try:
        # If running as a PyInstaller bundle, files are in sys._MEIPASS
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base = sys._MEIPASS
        else:
            # Use the directory containing main.py as the project root
            base = os.path.dirname(os.path.abspath(__file__))
        # Normalize separators and join into a single relative path string
        rel_normalized = rel_path.replace('/', os.sep).lstrip(os.sep)
        return os.path.join(base, rel_normalized)
    except Exception:
        return rel_path


def read_version() -> str:
    """Read version string from VERSION file located at the project root (bundled via PyInstaller)."""
    try:
        vpath = get_resource_path('VERSION')
        with open(vpath, 'r', encoding='utf-8') as vf:
            ver = vf.read().strip()
            if ver:
                return ver
    except Exception:
        pass
    return '0.0.0'


def print_banner_and_menu():
    # full clear then print banner
    clear_screen()
    # Replace the author name with a clickable terminal link when supported
    author_name = 'Anbuselvan Rocky'
    github_url = 'https://github.com/anburocky3'
    # Insert the version inline next to the author name inside the banner.
    # Read runtime version first (fallback to 0.0.0 on error)
    try:
        version = read_version()
    except Exception:
        version = '0.0.0'

    try:
        if supports_terminal_links():
            formatted_author = format_terminal_link(author_name, github_url)
            banner_to_print = BANNER.replace(author_name, f"{formatted_author} - v{version}")
        else:
            banner_to_print = BANNER.replace(author_name, f"{author_name} | v{version}")
    except Exception:
        # On any error, fall back to the original banner without inline version
        banner_to_print = BANNER

    print_banner(banner_to_print, BANNER_COLOR, RESET)
    print(MENU_COLOR + 'What would you like to download? (type the number; type "exit" to quit)' + RESET)
    # only display actual numbered categories
    for k, v in CATEGORIES.items():
        # Present 'By Genre' (6) as coming soon so users know it's not implemented
        if k == '6':
            print(f" {Fore.CYAN}{k}{RESET}. {COMING_SOON_COLOR}{v} (Coming Soon){RESET}")
        else:
            print(f" {Fore.CYAN}{k}{RESET}. {v}")
    print(f"")


def prompt_choice(prompt: str, default: str = '') -> str:
    return input(PROMPT_COLOR + prompt + RESET).strip() or default


def show_and_download(index_url: str, category_name: str, save_subpath_default: str):
    clear_below_banner(BANNER, BANNER_COLOR, RESET)
    try:
        page = requests.get(index_url, timeout=30)
        page.raise_for_status()
    except Exception as e:
        print(ERROR_COLOR + f"Failed to fetch URL {index_url}: {e}" + RESET)
        return

    soup = BeautifulSoup(page.content, 'html.parser')
    hrefs = collect_filtered_hrefs(soup)
    audio_count = count_audio_hrefs(hrefs)

    print("")
    print(INFO_COLOR + ensure_emoji_spacing(f"👋  I found {audio_count} audio links for {save_subpath_default}.\n") + RESET)

    # build output directory
    out_dir = Path(f'output/{category_name}/{save_subpath_default}')
    print(INFO_COLOR + f"Saving to: {out_dir}" + RESET)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Download audio links (downloader.download_links provides a default chunk_size)
    total_audio, successful, failed = download_links(hrefs, index_url, out_dir)

    print(INFO_COLOR + ensure_emoji_spacing('\n\n' + '-----------------------------------------------------------') + RESET)
    print(INFO_COLOR + ensure_emoji_spacing(f'💁\u200d♂️  Total Downloadable files: {total_audio}') + RESET)
    print(SUCCESS_COLOR + ensure_emoji_spacing(f'✅  Successful: {successful}') + RESET)
    print(ERROR_COLOR + ensure_emoji_spacing(f"❌  Couldn't download: {failed}") + RESET)
    print(INFO_COLOR + ensure_emoji_spacing('-----------------------------------------------------------') + RESET)


def handle_data_category(data_file: str, category_name: str):
    """Load a JSON list of {id, href/path, name} and drive the same flow as Star Hits.

    data_file: path to JSON file under data/
    category_name: top-level category used for output path
    """
    try:
        data_path = get_resource_path(data_file)
        with open(data_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
    except Exception as e:
        print(ERROR_COLOR + f"Failed to load {data_file}: {e}" + RESET)
        return

    # Display list (clear below the banner so banner remains visible)
    clear_below_banner(BANNER, BANNER_COLOR, RESET)
    print(MENU_COLOR + f"Available {category_name}:" + RESET)
    for item in data_list:
        print(f" {Fore.CYAN}{item.get('id')}{RESET}. {item.get('name')}")
    print(f" {Fore.CYAN}all{RESET}. Download ALL entries")
    print(f"")

    sel = prompt_choice("Select number(s)/ranges (e.g. 1,3,5 or 2-4) or 'all' (back/exit): ")
    if not sel:
        print(ERROR_COLOR + "No selection made, returning to menu." + RESET)
        return
    if sel.lower() in ('back', 'b'):
        return
    if sel.lower() in ('exit', '0', 'quit'):
        goodbye_and_exit()

    # Special case: when viewing the Ringtones list, pressing '6' should open the
    # prepopulated list from data/new-movies-ringtone.json
    try:
        if data_file.endswith('ringtones.json') and sel.strip() == '6':
            # Delegate to the new-movies JSON file (drill-down)
            new_file = 'data/new-movies-ringtone.json'
            # Use a friendly category name when showing the nested list
            handle_data_category(new_file, 'New Movies Ring Tone')
            return
    except Exception:
        # ignore and continue with normal flow on unexpected errors
        pass

    selected_items, missing = parse_star_selection(sel, data_list)
    for mid in missing:
        print(ERROR_COLOR + f"No item with id {mid}, skipping." + RESET)
    if not selected_items:
        print(ERROR_COLOR + f"No valid selections found, returning to menu." + RESET)
        return

    for item in selected_items:
        item_name = item.get('name')
        # prefer 'href' then 'path'
        index_url = item.get('href') or item.get('path')
        if not index_url:
            print(ERROR_COLOR + f"No URL for '{item_name}', skipping." + RESET)
            continue

        user_path = prompt_choice(f"Enter The Path To Save Files inside '{category_name}/{item_name}': (DEFAULT: {item_name}) (skip/back/exit): ", item_name)
        if user_path.lower() in ('skip', 's'):
            print(INFO_COLOR + f"Skipped {item_name}" + RESET)
            continue
        if user_path.lower() in ('back', 'b'):
            break
        if user_path.lower() in ('exit', '0', 'quit'):
            goodbye_and_exit()

        dir_path = Path(f'output/{category_name}/{user_path}')
        print(INFO_COLOR + '----------------------------------------------')
        print(INFO_COLOR + f' 🎼   Files will be saved to: {dir_path}')
        print(INFO_COLOR + '----------------------------------------------' + RESET)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Reuse show_and_download which fetches index, filters links and downloads
        show_and_download(index_url, category_name, user_path)


def handle_old_songs():
    """Show a small submenu for 'Old Songs' and delegate to handle_data_category.

    Options:
      1 - Old Collections -> data/old/collections.json
      2 - Old Hits (Singers) -> data/old/singers.json
    """
    clear_below_banner(BANNER, BANNER_COLOR, RESET)
    print(MENU_COLOR + "Old Songs - select a subcategory:" + RESET)
    print(f" {Fore.CYAN}1{RESET}. Old Collections")
    print(f" {Fore.CYAN}2{RESET}. Old Hits (Singers)")
    print(f" {Fore.CYAN}b{RESET}. Back to main menu")
    print(f"")

    sel = prompt_choice("Enter choice (1-2, b/back): ")
    if not sel:
        print(ERROR_COLOR + "No selection made, returning to menu." + RESET)
        return
    sel_low = sel.lower()
    if sel_low in ('b', 'back'):
        return
    if sel_low in ('exit', '0', 'quit'):
        goodbye_and_exit()

    if sel_low == '1':
        handle_data_category('data/old/collections.json', 'Old Collections')
    elif sel_low == '2':
        handle_data_category('data/old/singers.json', 'Old Hits (Singers)')
    else:
        print(ERROR_COLOR + f"Invalid choice '{sel}', returning to menu." + RESET)


def handle_ringtones_instrumentals():
    """Submenu for Ringtones and Instrumental Collections.

    Options:
      1 - Ringtones -> data/ringtones.json
      2 - Instrumentals -> data/instrumentals.json
    """
    clear_below_banner(BANNER, BANNER_COLOR, RESET)
    print(MENU_COLOR + "Ring Tones / Instrumentals - select a subcategory:" + RESET)
    print(f" {Fore.CYAN}1{RESET}. Ringtones")
    print(f" {Fore.CYAN}2{RESET}. Instrumentals")
    print(f" {Fore.CYAN}b{RESET}. Back to main menu")
    print(f"")

    sel = prompt_choice("Enter choice (1-2, b/back): ")
    if not sel:
        print(ERROR_COLOR + "No selection made, returning to menu." + RESET)
        return
    sel_low = sel.lower()
    if sel_low in ('b', 'back'):
        return
    if sel_low in ('exit', '0', 'quit'):
        goodbye_and_exit()

    if sel_low == '1':
        handle_data_category('data/ringtones.json', 'Ring Tones')
    elif sel_low == '2':
        handle_data_category('data/instrumentals.json', 'Instrumental Collections')
    else:
        print(ERROR_COLOR + f"Invalid choice '{sel}', returning to menu." + RESET)


def main():
    while True:
        # Show banner and menu, get a valid choice
        print_banner_and_menu()
        choice = prompt_choice('Enter choice (1-7) [default 1]: ', '1').lower()
        if choice in ('0', 'exit', 'quit'):
            goodbye_and_exit()
        if choice not in CATEGORIES:
            print(ERROR_COLOR + f"Invalid choice '{choice}', please try again." + RESET)
            continue

        category_name = CATEGORIES[choice]
        print(INFO_COLOR + f"Selected: {category_name}\n" + RESET)

        # Special flows for Star Hits (1), Music Director Hits (2) and Singer Hits (3)
        if choice in ('1', '2', '3'):
            mapping = {
                '1': 'data/star-hits.json',
                '2': 'data/music-directors-hits.json',
                '3': 'data/singer-hits.json',
            }
            data_file = mapping.get(choice)
            handle_data_category(data_file, category_name)
            continue

        # Handle Old Songs subcategories
        if choice == '4':
            handle_old_songs()
            continue

        # Handle Ring tones / Instrumentals subcategories
        if choice == '5':
            handle_ringtones_instrumentals()
            continue

        # Handle By Genre as 'coming soon'
        if choice == '6':
            clear_below_banner(BANNER, BANNER_COLOR, RESET)
            print(COMING_SOON_COLOR + '🚧  By Genre is coming soon. This feature is not implemented yet.' + RESET)
            _ = prompt_choice('\nPress Enter to return to the main menu...')
            continue

        # Generic flow for other categories
        index_url = prompt_choice("Enter 'Index Of' URL (back/exit): ")
        if not index_url:
            print(ERROR_COLOR + "No URL provided, returning to menu." + RESET)
            continue
        if index_url.lower() in ('back', 'b'):
            continue
        if index_url.lower() in ('exit', '0', 'quit'):
            goodbye_and_exit()

        try:
            project_name = unquote(index_url.rsplit('/', 2)[1])
        except Exception:
            project_name = unquote(index_url.rstrip('/').rsplit('/', 1)[-1])

        user_path = prompt_choice(f"Enter The Path To Save Files inside '{category_name}': (DEFAULT: {project_name}) (back/exit): ", project_name)
        if user_path.lower() in ('back', 'b'):
            continue
        if user_path.lower() in ('exit', '0', 'quit'):
            goodbye_and_exit()

        dir_path = Path(f'output/{category_name}/{user_path}')
        print(INFO_COLOR + str(dir_path) + RESET)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Fetch index and download
        show_and_download(index_url, category_name, user_path)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        goodbye_and_exit()

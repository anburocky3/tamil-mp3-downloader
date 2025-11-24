from pathlib import Path
from bs4 import BeautifulSoup
import requests
from urllib.parse import unquote
import sys
import json

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
 Tamil MP3 Downloader - Author: Anbuselvan Rocky - v2.0.0
'''

# Color choices
BANNER_COLOR = Fore.CYAN + Style.BRIGHT
MENU_COLOR = Fore.YELLOW + Style.BRIGHT
PROMPT_COLOR = Fore.GREEN + Style.BRIGHT
SUCCESS_COLOR = Fore.GREEN
ERROR_COLOR = Fore.RED
INFO_COLOR = Fore.MAGENTA
RESET = Style.RESET_ALL

CATEGORIES = {
    '1': 'A-Z Movie Songs',
    '2': 'Star Hits',
    '3': 'Music Director Hits',
    '4': 'Singer Hits',
    '5': 'Karaoke',
    '6': 'Ring tones',
    '7': 'By Genre',
}


def goodbye_and_exit():
    try:
        print('\n' + INFO_COLOR + 'GoodBye Nanba/Nanbis!' + RESET)
    except Exception:
        print('\nGoodBye Nanba/Nanbis!')
    sys.exit(0)


def print_banner_and_menu():
    print(BANNER_COLOR + BANNER + RESET)
    print(MENU_COLOR + 'What would you like to download? (type the number; type "exit" to quit)' + RESET)
    # only display actual numbered categories
    for k, v in CATEGORIES.items():
        print(f" {Fore.CYAN}{k}{RESET}. {v}")


def prompt_choice(prompt: str, default: str = '') -> str:
    return input(PROMPT_COLOR + prompt + RESET).strip() or default


def show_and_download(index_url: str, category_name: str, save_subpath_default: str):
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

        # Special flow for Star Hits (choice == '2')
        if choice == '2':
            # Load data/star-hits.json
            try:
                with open('data/star-hits.json', 'r', encoding='utf-8') as f:
                    star_data = json.load(f)
            except Exception as e:
                print(ERROR_COLOR + f"Failed to load star-hits.json: {e}" + RESET)
                continue

            # Display list
            print(MENU_COLOR + "Available Star Hits:" + RESET)
            for item in star_data:
                print(f" {Fore.CYAN}{item.get('id')}{RESET}. {item.get('name')}")
            print(f" {Fore.CYAN}all{RESET}. Download ALL entries")

            sel = prompt_choice("Select number(s)/ranges (e.g. 1,3,5 or 2-4) or 'all' (back/exit): ")
            if not sel:
                print(ERROR_COLOR + "No selection made, returning to menu." + RESET)
                continue
            if sel.lower() in ('back', 'b'):
                continue
            if sel.lower() in ('exit', '0', 'quit'):
                goodbye_and_exit()

            selected_items, missing = parse_star_selection(sel, star_data)
            for mid in missing:
                print(ERROR_COLOR + f"No item with id {mid}, skipping." + RESET)
            if not selected_items:
                print(ERROR_COLOR + f"No valid selections found, returning to menu." + RESET)
                continue

            for item in selected_items:
                item_name = item.get('name')
                index_url = item.get('href')

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
                print(INFO_COLOR + f' 🎼  Files will be saved to: {dir_path}')
                print(INFO_COLOR + '----------------------------------------------' + RESET)
                dir_path.mkdir(parents=True, exist_ok=True)

                # Reuse show_and_download which fetches index, filters links and downloads
                show_and_download(index_url, category_name, user_path)

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

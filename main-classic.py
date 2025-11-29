from pathlib import Path
from bs4 import BeautifulSoup
import requests
from urllib.parse import unquote
from clint.textui import progress

links = []
chunk_size = 256

print("Enter 'Index Of' URL: ")
url = input()
projectName = unquote(url.rsplit('/', 2)[1])

path = input(f"Enter The Path To Save Files: (DEFAULT: {projectName}) ") or projectName


dirPath = Path(f'output/{path}')

print(dirPath)

# Create directory if not exist
dirPath.mkdir(parents=True, exist_ok=True)

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

for link in (soup.find_all('a')):
    links.append(link['href'])

print("")
print(f"👋 Hello, I found {len(links)} files, some might have image, but i will ignore it for now. 😀 \n\n")

totalDownloadedFiles= len(links)
successfulDownloads = 0
unSuccessfulDownloads = 0
for  link in links:
    # only check the below formats and ignore the rest.
    if link.endswith((".wav", ".mp3", ".MP3")):
        req = requests.get(url + '/' + link, stream=True)
        try:
            with open(dirPath.__str__() + '/' + unquote(link), "wb") as file:
                length = int(req.headers.get('content-length'))
                for chunk in progress.bar(req.iter_content(chunk_size), expected_size=(length / chunk_size),
                                          label= unquote(link) + "  "):
                    if chunk:
                        file.write(chunk)
                         # if successful, increase the successful download
                print(f"✅ Download Successful: \t {unquote(link)}\n")
                successfulDownloads += 1
        except OSError as e:
            continue
    else:
        print('❌ Ignored, because it might not be music. - ', unquote(link), '\n')
        unSuccessfulDownloads += 1
print(f'\n\n'
      f'-----------------------------------------------------------')
print(f'💁‍♂️ Total Downloadable files: {totalDownloadedFiles}')
print(f'✅ Successful: {successfulDownloads}')
print(f"❌ Couldn't download: {unSuccessfulDownloads}")
print(f'-----------------------------------------------------------')
# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('Hello Awesome, Coded by Anbuselvan Rocky!')


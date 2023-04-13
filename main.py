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

for link in links:
    # print("P: " + dirPath.__str__() + '/'+ link)

    req = requests.get(url + '/' + link, stream=True)
    try:
        with open(dirPath.__str__() + '/' + unquote(link), "wb") as file:
            length = int(req.headers.get('content-length'))
            for chunk in progress.bar(req.iter_content(chunk_size), expected_size=(length / chunk_size),
                                      label=link + "  "):
                if chunk:
                    file.write(chunk)
            print(f"Download Successful: \t {unquote(link)}")

    except OSError as e:
        continue


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')


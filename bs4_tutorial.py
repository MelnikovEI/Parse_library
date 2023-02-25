import os.path
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup

import requests


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    Path(Path.cwd() / folder).mkdir(parents=True, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()
    path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


def main():
    url = f"https://tululu.org/b4/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text.split(sep='::')
    print(title_text[0].strip())
    print(title_text[1].strip())

    # print(soup.find('img', class_='attachment-post-image')['src'])

    # Примеры использования
    url = 'http://tululu.org/txt.php?id=1'

    filepath = download_txt(url, 'Алиби')
    print(filepath)  # Выведется books/Алиби.txt

    filepath = download_txt(url, 'Али/би', folder='books/')
    print(filepath)  # Выведется books/Алиби.txt

    filepath = download_txt(url, 'Али\\би', folder='txt/')
    print(filepath)  # Выведется txt/Алиби.txt


if __name__ == '__main__':
    main()

import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


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


def download_image(url, folder='images/'):
    Path(Path.cwd() / folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()

    filename = urlsplit(url).path.split('/')[-1]
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


def main():
    for book_id in range(1, 11):
        url = f"https://tululu.org/b{book_id}/"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('h1')
        title_text = title_tag.text.split(sep='::')
        book_title = title_text[0].strip()
        filename = f'{book_id}. {book_title}'
        txt_url = f"https://tululu.org/txt.php?id={book_id}"
        download_txt(txt_url, filename)

        img_url = soup.find('div', class_='bookimage').find('img')['src']
        full_img_url = urljoin("https://tululu.org/", img_url)
        download_image(full_img_url)


if __name__ == '__main__':
    main()

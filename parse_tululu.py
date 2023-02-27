import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Ссылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    Path(Path.cwd() / folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


def download_image(url, folder='images/'):
    Path(Path.cwd() / folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = unquote(urlsplit(url).path.split('/')[-1])
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


def parse_book_page(soup):
    title_tag = soup.find('h1')
    title_text = title_tag.text.split(sep='::')
    genres = soup.find('span', class_='d_book').find_all('a')
    comments = soup.find('td', class_='ow_px_td').find_all('span', class_='black')

    book_info = {
        'title': title_text[0].strip(),
        'author': title_text[1].strip(),
        'genres': [genre.text for genre in genres],
        'comments': [comment.text for comment in comments],
    }
    return book_info


def main():
    parser = argparse.ArgumentParser(description='Downloads books and cover images from tululu.org')
    parser.add_argument('start_id', nargs='?', type=int, default=1,
                        help='starting book_id to download, must be integer >= 1')
    parser.add_argument('end_id', nargs='?', type=int, default=10,
                        help='last book_id to download, must be integer >= start_id')
    args = parser.parse_args()

    for book_id in tqdm(range(args.start_id, args.end_id+1)):
        url = f"https://tululu.org/b{book_id}/"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            print('\n', f'page for book number {book_id} doesn\'t exist', file=sys.stderr)
            continue
        soup = BeautifulSoup(response.text, 'lxml')

        book_title = parse_book_page(soup)['title']
        filename = f'{book_id}.{book_title}'
        book_text_url = f"https://tululu.org/txt.php?id={book_id}"

        img_url = soup.find('div', class_='bookimage').find('img')['src']
        full_img_url = urljoin("https://tululu.org/", img_url)

        try:
            download_txt(book_text_url, filename)
        except requests.HTTPError:
            print('\n', f'url for text of book number {book_id} wasn\'t found ', file=sys.stderr)
            continue
        try:
            download_image(full_img_url)
        except requests.HTTPError:
            print('\n', f'url for cover image of book number {book_id} wasn\'t found ', file=sys.stderr)


if __name__ == '__main__':
    main()

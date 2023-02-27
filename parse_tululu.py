import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm
from retry import retry


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


@retry(requests.ConnectionError, delay=1, backoff=2, tries=5)
def download_txt(book_id, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        book_id  (int): id книги для скачивания.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    Path(Path.cwd() / folder).mkdir(parents=True, exist_ok=True)
    book_text_url = "https://tululu.org/txt.php"
    params = {'id': book_id}
    response = requests.get(book_text_url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


@retry(requests.ConnectionError, delay=1, backoff=2, tries=5)
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


@retry(requests.ConnectionError, delay=1, backoff=2, tries=5)
def get_response(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def parse_book_page(soup):
    title_tag = soup.find('h1')
    title, author = title_tag.text.split(sep='::')
    genres = soup.find('span', class_='d_book').find_all('a')
    comments = soup.find('td', class_='ow_px_td').find_all('span', class_='black')
    return {
        'title': title.strip(),
        'author': author.strip(),
        'genres': [genre.text for genre in genres],
        'comments': [comment.text for comment in comments],
        'img_url': soup.find('div', class_='bookimage').find('img')['src'],
    }


def main():
    parser = argparse.ArgumentParser(description='Downloads books and cover images from tululu.org')
    parser.add_argument('start_id', nargs='?', type=int, default=1,
                        help='starting book_id to download, must be integer >= 1')
    parser.add_argument('end_id', nargs='?', type=int, default=10,
                        help='last book_id to download, must be integer >= start_id')
    args = parser.parse_args()

    for book_id in tqdm(range(args.start_id, args.end_id+1)):
        url = f"https://tululu.org/b{book_id}/"
        try:
            response = get_response(url)
            check_for_redirect(response)
        except requests.HTTPError:
            print('\n', f'page for book number {book_id} doesn\'t exist', file=sys.stderr)
            continue
        except (requests.ConnectionError, requests.Timeout) as err:
            print('\n', err, file=sys.stderr)
            continue

        soup = BeautifulSoup(response.text, 'lxml')

        book_title = parse_book_page(soup)['title']
        filename = f'{book_id}.{book_title}'

        img_url = parse_book_page(soup)['img_url']
        full_img_url = urljoin("https://tululu.org/", img_url)

        try:
            try:
                download_txt(book_id, filename)
            except requests.HTTPError:
                print('\n', f'url for text of book number {book_id} wasn\'t found ', file=sys.stderr)
                continue
            try:
                download_image(full_img_url)
            except requests.HTTPError:
                print('\n', f'url for cover image of book number {book_id} wasn\'t found ', file=sys.stderr)
        except (requests.ConnectionError, requests.Timeout) as err:
            print('\n', err, file=sys.stderr)


if __name__ == '__main__':
    main()

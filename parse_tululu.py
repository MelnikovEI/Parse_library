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


def download_txt(book_id, filename, folder='books'):
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
    response = get_response(book_text_url, params=params)
    path = os.path.join(folder, f'{sanitize_filename(filename)}.txt')
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


def download_image(url, folder='images'):
    Path(Path.cwd() / folder).mkdir(parents=True, exist_ok=True)
    response = get_response(url)
    filename = unquote(urlsplit(url).path.split('/')[-1])
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


@retry(requests.ConnectionError, delay=1, backoff=2, tries=5)
def get_response(url, params={}):
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def parse_book_page(soup):
    title_tag = soup.select_one('h1')
    title, author = title_tag.text.split(sep='::')
    genres = soup.select('span.d_book a')
    comments = soup.select('.texts .black')
    return {
        'title': title.strip(),
        'author': author.strip(),
        'img_src': soup.select_one('.bookimage img')['src'],
        'comments': [comment.text for comment in comments],
        'genres': [genre.text for genre in genres],
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
        except requests.HTTPError:
            print('\n', f'page for book number {book_id} doesn\'t exist', file=sys.stderr)
            continue
        except (requests.ConnectionError, requests.Timeout) as err:
            print('\n', err, file=sys.stderr)
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        book_details = parse_book_page(soup)
        book_title = book_details['title']
        filename = f'{book_id}.{book_title}'
        img_url = book_details['img_src']
        full_img_url = urljoin(url, img_url)

        try:
            download_txt(book_id, filename)
        except requests.HTTPError:
            print('\n', f'url for text of book number {book_id} wasn\'t found ', file=sys.stderr)
            continue
        except (requests.ConnectionError, requests.Timeout) as err:
            print('\n', err, file=sys.stderr)

        try:
            download_image(full_img_url)
        except requests.HTTPError:
            print('\n', f'url for cover image of book number {book_id} wasn\'t found ', file=sys.stderr)
        except (requests.ConnectionError, requests.Timeout) as err:
            print('\n', err, file=sys.stderr)


if __name__ == '__main__':
    main()

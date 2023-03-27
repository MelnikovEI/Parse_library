import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from parse_tululu import get_response, parse_book_page, download_txt, download_image
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser(description='Downloads books and cover images from tululu.org/l55')
    parser.add_argument('--start_page', nargs='?', type=int, default=1,
                        help='starting book_id to download, must be integer >= 1')
    parser.add_argument('--end_page', nargs='?', type=int, default=702,
                        help='download book_id to --end_page, excluded, must be integer >= start_id')
    parser.add_argument('--dest_folder', nargs='?', default='media', help='folder to download books to')
    parser.add_argument('--skip_imgs', action='store_true', help='skip downloading images')
    parser.add_argument('--skip_txt', action='store_true', help='skip downloading book texts')
    parser.add_argument('--json_path', nargs='?', default='media', help='folder to download "books details json" to')

    args = parser.parse_args()
    Path(Path.cwd() / args.dest_folder).mkdir(parents=True, exist_ok=True)
    books_details = []
    for page_number in tqdm(range(args.start_page, args.end_page)):
        print()
        url = f"https://tululu.org/l55/{page_number}/"
        try:
            response = get_response(url)
        except requests.HTTPError:
            print(f'page for book number  doesn\'t exist', file=sys.stderr)
            continue
        except (requests.ConnectionError, requests.Timeout) as err:
            print(err, file=sys.stderr)
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        book_links = soup.select('#content .d_book')

        for book_link in book_links:
            full_book_link = urljoin(url, book_link.select_one('a').get('href'))
            book_id = urlparse(full_book_link).path.strip('/').strip('b')

            try:
                response = get_response(full_book_link)
            except requests.HTTPError:
                print(f'page for book number {book_id} doesn\'t exist', file=sys.stderr)
                continue
            except (requests.ConnectionError, requests.Timeout) as err:
                print(err, file=sys.stderr)
                continue

            soup = BeautifulSoup(response.text, 'lxml')
            book_details = parse_book_page(soup)

            if not args.skip_txt:
                book_title = book_details['title']
                filename = f'{book_id}.{book_title}'
                try:
                    book_path = download_txt(book_id, filename, folder=os.path.join(args.dest_folder, 'books'))
                except requests.HTTPError:
                    print(f'url for text of book number {book_id} wasn\'t found ', file=sys.stderr)
                    continue
                except (requests.ConnectionError, requests.Timeout) as err:
                    print(err, file=sys.stderr)
                    continue
                book_details['book_path'] = book_path

            if not args.skip_imgs:
                img_url = book_details['img_src']
                full_img_url = urljoin(url, img_url)
                try:
                    img_path = download_image(full_img_url, folder=os.path.join(args.dest_folder, 'images'))
                except requests.HTTPError:
                    print(f'url for cover image of book number {book_id} wasn\'t found ', file=sys.stderr)
                except (requests.ConnectionError, requests.Timeout) as err:
                    print(err, file=sys.stderr)
                book_details['img_path'] = img_path
                books_details.append(book_details)
                print(f'{book_path}     downloaded')

    json_folder = args.json_path
    Path(Path.cwd() / json_folder).mkdir(parents=True, exist_ok=True)
    books_details_file = os.path.join(json_folder, "books.json")
    books_details_json = json.dumps(books_details, ensure_ascii=False)
    with open(books_details_file, "w") as books_file:
        books_file.write(books_details_json)


if __name__ == '__main__':
    main()

import argparse
import json
import sys
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
    args = parser.parse_args()

    for i in tqdm(range(args.start_page, args.end_page)):
        print()
        url = f"https://tululu.org/l55/{i}/"
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
            book_title = book_details['title']
            filename = f'{book_id}.{book_title}'
            img_url = book_details['img_src']
            full_img_url = urljoin(url, img_url)
            
            try:
                book_path = download_txt(book_id, filename)
            except requests.HTTPError:
                print(f'url for text of book number {book_id} wasn\'t found ', file=sys.stderr)
                continue
            except (requests.ConnectionError, requests.Timeout) as err:
                print(err, file=sys.stderr)
                continue
            book_details.update({'book_path': book_path})
            book_details_json = json.dumps(book_details, ensure_ascii=False)
            with open("books.json", "w") as books_file:
                books_file.write(book_details_json)
            print(f'{book_path}     downloaded')

            try:
                download_image(full_img_url)
            except requests.HTTPError:
                print(f'url for cover image of book number {book_id} wasn\'t found ', file=sys.stderr)
            except (requests.ConnectionError, requests.Timeout) as err:
                print(err, file=sys.stderr)


if __name__ == '__main__':
    main()

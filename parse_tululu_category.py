import json
import sys
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from parse_tululu import get_response, parse_book_page, download_txt, download_image

for i in range(1, 3):
    url = f"https://tululu.org/l55/{i}/"
    try:
        response = get_response(url)
    except requests.HTTPError:
        print('\n', f'page for book number  doesn\'t exist', file=sys.stderr)
    except (requests.ConnectionError, requests.Timeout) as err:
        print('\n', err, file=sys.stderr)
    soup = BeautifulSoup(response.text, 'lxml')
    book_links = soup.find_all('table', class_='d_book')

    for book_link in book_links:
        full_book_link = urljoin(url, book_link.find('a').get('href'))
        book_id = urlparse(full_book_link).path.strip('/').strip('b')

        try:
            response = get_response(full_book_link)
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
            book_path = download_txt(book_id, filename)
        except requests.HTTPError:
            print('\n', f'url for text of book number {book_id} wasn\'t found ', file=sys.stderr)
            continue
        except (requests.ConnectionError, requests.Timeout) as err:
            print('\n', err, file=sys.stderr)
            continue
        book_details.update({'book_path': book_path})
        print(book_details)
        book_details_json = json.dumps(book_details, ensure_ascii=False)
        with open("books.json", "a") as books_file:
            books_file.write(book_details_json)

        try:
            download_image(full_img_url)
        except requests.HTTPError:
            print('\n', f'url for cover image of book number {book_id} wasn\'t found ', file=sys.stderr)
        except (requests.ConnectionError, requests.Timeout) as err:
            print('\n', err, file=sys.stderr)

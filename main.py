import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
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

    filename = unquote(urlsplit(url).path.split('/')[-1])
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file_to_save:
        file_to_save.write(response.content)
    return path


def parse_book_page(soup):
    book_info = {}

    title_tag = soup.find('h1')
    title_text = title_tag.text.split(sep='::')
    genres = soup.find('span', class_='d_book').find_all('a')
    comments = soup.find('td', class_='ow_px_td').find_all('span', class_='black')

    book_info.update(
        title=title_text[0].strip(),
        author=title_text[1].strip(),
        genres=[genre.text for genre in genres],
        comments=[comment.text for comment in comments],
    )
    return book_info


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
        #download_txt(txt_url, filename)

        img_url = soup.find('div', class_='bookimage').find('img')['src']
        full_img_url = urljoin("https://tululu.org/", img_url)
        #download_image(full_img_url)

        comments = soup.find('td', class_='ow_px_td').find_all('span', class_='black')
        #for comment in comments:
        #    print(comment.text)

        genres = soup.find('span', class_='d_book').find_all('a')
        #for genre in genres:
        #    print(genre.text)

        print(parse_book_page(soup))

if __name__ == '__main__':
    main()

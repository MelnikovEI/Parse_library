from pathlib import Path

import requests


def main():
    Path(Path.cwd() / 'books').mkdir(parents=True, exist_ok=True)

    for book_id in range(1, 10):
        url = f"https://tululu.org/txt.php?id={book_id}"
        response = requests.get(url)
        response.raise_for_status()
        with open(Path.cwd() / 'books' / f'book_{book_id}.txt', 'wb') as file_to_save:
            file_to_save.write(response.content)


if __name__ == '__main__':
    main()

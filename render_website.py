import json
import math
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

BOOKS_PER_PAGE = 20


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open(os.path.join('media', "books.json"), "r") as books_file:
        books_json = books_file.read()
    books = json.loads(books_json)
    Path(Path.cwd() / 'pages').mkdir(parents=True, exist_ok=True)
    num_pages = math.ceil(len(books)/BOOKS_PER_PAGE)
    for page_num, books_part in enumerate(chunked(books, BOOKS_PER_PAGE), 1):
        rendered_page = template.render(
            books=books_part,
            current_page=page_num,
            num_pages=num_pages,
        )
        with open(os.path.join('pages', f'index{page_num}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print("Site rebuilt")


rebuild()

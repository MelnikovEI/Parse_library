import argparse
import json
import math
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

BOOK_CARDS_PER_PAGE = 20


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    parser = argparse.ArgumentParser(description='Creates html files with book cards from "books.json"')
    parser.add_argument('--json_path', nargs='?', default='media/books.json', help='folder, containing file "books.json"')
    args = parser.parse_args()

    with open(args.json_path, "r") as books_file:
        book_descriptions = json.load(books_file)

    Path(Path.cwd() / 'pages').mkdir(parents=True, exist_ok=True)
    num_pages = math.ceil(len(book_descriptions) / BOOK_CARDS_PER_PAGE)
    for page_num, book_descriptions_for_page in enumerate(chunked(book_descriptions, BOOK_CARDS_PER_PAGE), 1):
        rendered_page = template.render(
            book_descriptions_for_page=book_descriptions_for_page,
            current_page=page_num,
            num_pages=num_pages,
        )
        with open(os.path.join('pages', f'index{page_num}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


rebuild()
server = Server()
server.watch('template.html', rebuild)
server.serve(root='.')

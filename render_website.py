import json
import os
from pathlib import Path

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open(os.path.join('books', "books.json"), "r") as books_file:
        books_json = books_file.read()
    books = json.loads(books_json)
    Path(Path.cwd() / 'pages').mkdir(parents=True, exist_ok=True)
    for part_num, books_part in enumerate(chunked(books, 20), 1):
        rendered_page = template.render(
            books=books_part,
        )
        with open(os.path.join('pages', f'index{part_num}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print("Site rebuilt")


rebuild()
#server = Server()
#server.watch('template.html', rebuild)
#server.serve(root='.')

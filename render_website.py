import json
import os
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def rebuild():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open(os.path.join('books', "books.json"), "r") as books_file:
        books_json = books_file.read()
    books = json.loads(books_json)
    # print(books)
    rendered_page = template.render(
        books=books,
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuilt")


rebuild()
#server = Server()
#server.watch('template.html', rebuild)
#server.serve(root='.')

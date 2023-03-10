# Парсер книг с сайта tululu.org
Скрипт `parse_tululu.py` скачивает книги и обложки с сайта [БОЛЬШАЯ БЕСПЛАТНАЯ БИБЛИОТЕКА](https://tululu.org/)

Скрипт `parse_tululu_category.py` скачивает книги и обложки жанра "Научная фантастика" с сайта [БОЛЬШАЯ БЕСПЛАТНАЯ БИБЛИОТЕКА](https://tululu.org/l55/)

## Как установить
Для запуска у вас уже должен быть установлен Python 3.
- Скачайте код
- Установите зависимости командой
```sh
pip install -r requirements.txt
```

## Как использовать parse_tululu.py
Запустите скрипт командой
```sh
python parse_tululu.py
```
По умолчанию скрипт скачивает книги с 1 по 10.
Вы можете указать диапазон книг для скачивания (начало конец):
```sh
python3 parse_tululu.py 15 20
```
Скачанные книги и обложки будут сохранены в папках "books" и "images".
Если папки отсутствуют, скрипт их создаст.
Файлы в этих папках могут быть перезаписаны!

## Как использовать parse_tululu_category.py
Запустите скрипт командой
```sh
python parse_tululu_category.py
```

По умолчанию скрипт скачивает книги со всех страниц с 1 по 701.
Вы можете указать диапазон книг для скачивания [начало конец), например:
```sh
python3 parse_tululu_category.py --start_page 650
```
```sh
python3 parse_tululu_category.py --start_page 700 --end_page 701
```
По умолчанию скачанные книги и обложки будут сохранены в папке "books". Если папка отсутствует, скрипт её создаст.
Файлы в этих папках могут быть перезаписаны!
Вы можете указать папки, например:
```sh
python3 parse_tululu_category.py --dest_folder 'Моя папка' --json_path 'Папка для json' 
```
Вы можете выключить загрузку книг или обложек, например:
```sh
python3 parse_tululu_category.py --skip_txt 
```
```sh
python3 parse_tululu_category.py --skip_imgs 
```

Пример списка книг:
```
- 1.Административные рынки СССР и России.txt
- 3.Азбука экономики.txt
- 4.Азиатский способ производства и Азиатский социализм.txt
- 5.Бал хищников.txt
- ...
```
_Книга №2 не была скачана, поскольку она отсутствует на сайте._

### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

### Authors
[Evgeny Melnikov](https://github.com/MelnikovEI)

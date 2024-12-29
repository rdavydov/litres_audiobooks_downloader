import requests
import browsercookie
from pathvalidate import sanitize_filename
import argparse
import logging
from pathlib import Path
from fake_useragent import UserAgent
from tqdm import tqdm
import litres_auth
try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib
import json
from requests.utils import dict_from_cookiejar, cookiejar_from_dict

logger = logging.getLogger(__name__)
LITRES_DOMAIN_NAME = 'litres.ru'
api_url = f'https://api.{LITRES_DOMAIN_NAME}/foundation/api/arts/'


def get_headers(browser):
    ua = UserAgent()
    agent = ua.chrome
    if browser == "firefox":
        agent = ua.firefox
    elif browser == "edge":
        agent = ua.edge
    elif browser == "safari":
        agent = ua.safari
    return {
        'User-Agent': agent,
    }


def get_cookies(browser):
    cookies = ""
    if browser == "chrome":
        cookies = browsercookie.chrome()
    elif browser == "chromium":
        cookies = browsercookie.chromium()
    elif browser == "vivaldi":
        cookies = browsercookie.vivaldi()
    elif browser == "edge":
        cookies = browsercookie.edge()
    elif browser == "firefox":
        cookies = browsercookie.firefox()
    elif browser == "safari":
        cookies = browsercookie.safari()
    return cookies


def download_mp3(url, path, filename, cookies, headers):
    print(f"Загрузка файла: {url}")
    full_filename = Path(path) / sanitize_filename(filename)

    res = requests.get(url, stream=True,
                       cookies=cookies, headers=headers)
    if res.status_code == 200:
        total_size = int(res.headers.get("content-length", 0))
        block_size = 1024
        with tqdm(total=total_size, unit="B", unit_scale=True, desc=filename) as progress_bar:
            with open(full_filename, "wb") as file:
                for data in res.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

            if total_size != 0 and progress_bar.n != total_size:
                logger.error(f"Не удалось загрузить файл: {url}")
    else:
        logger.error(
            f"код: {res.status_code} При загрузке с адреса: {url}")


def get_book_info(json_data):
    book_info = {"title": "", "author": "", "reader": "",
                 "series": "", "series_count": 0, "series_num": 0}
    book_info["title"] = json_data["title"]

    for person_info in json_data["persons"]:
        if person_info["role"] == "author" and book_info["author"] == "":
            book_info["author"] = person_info["full_name"]
            author_split = book_info["author"].split()
            # Переворачиваем фамилию и имя
            if len(author_split) == 2:
                book_info["author"] = f'{author_split[1]} {author_split[0]}'

        if person_info["role"] == "reader" and book_info["reader"] == "":
            book_info["reader"] = person_info["full_name"]

    for series_info in json_data["series"]:
        if "name" in series_info and series_info["name"] != None:
            book_info["series"] = series_info["name"]
        if "arts_count" in series_info and series_info["arts_count"] != None:
            book_info["series_count"] = series_info["arts_count"]
        if "art_order" in series_info and series_info["art_order"] != None:
            book_info["series_num"] = series_info["art_order"]
        break

    return book_info


def get_book_folder(output, book_info):
    book_folder = Path(output)
    if book_info["author"] != "":
        book_folder = Path(book_folder) / \
            sanitize_filename(book_info["author"])

    if book_info["series"] != "":
        book_folder = Path(book_folder) / \
            sanitize_filename(book_info["series"])

    if book_info["series_num"] > 0:
        book_folder = Path(
            book_folder) / sanitize_filename(f'{book_info["series_num"]:02d} {book_info["title"]}')
    else:
        book_folder = Path(book_folder) / sanitize_filename(book_info["title"])
    Path(book_folder).mkdir(exist_ok=True, parents=True)
    return book_folder


def download_book(url, output, browser, cookies):
    headers = get_headers(browser)
    book_id = url.split("-")[-1].split("/")[0]

    url_string = api_url+book_id
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if res.status_code != 200:
        logger.error(
            f"Ошибка запроса GET: {url_string}. Статус: {res.status_code}")
        exit(1)

    book_info = get_book_info(res.json()["payload"]["data"])
    logger.debug(f"Получена информация о книге: {book_info['title']}")
    book_folder = get_book_folder(output, book_info)
    print(f"Загрузка файлов в каталог: {book_folder}")

    # Список файлов для загрузки
    url_string = url_string + "/files/grouped"
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if res.status_code != 200:
        logger.error(
            f"Ошибка запроса GET: {url_string}. Статус: {res.status_code}")
        exit(1)

    groups_info = res.json()["payload"]["data"]
    for group_info in groups_info:
        if "standard_quality_mp3" in group_info["file_type"]:
            files_info = group_info["files"]
            for file_info in files_info:
                file_id = file_info["id"]
                filename = file_info["filename"]
                file_url = f"https://www.{LITRES_DOMAIN_NAME}/download_book_subscr/{book_id}/{file_id}/{filename}"
                download_mp3(file_url, book_folder,
                             filename, cookies, headers)
            break


def cookies_is_valid(cookies):
    result = False
    res = requests.get(f"https://{LITRES_DOMAIN_NAME}", cookies=cookies)
    if res.ok:
        content_list = res.text.split('/me/profile/')
        if len(content_list) > 1:
            result = True

    return result


def convert_editthiscookie_to_requests(cookie_list):
    """Конвертирует формат EditThisCookie в формат, совместимый с requests"""
    cookies_dict = {}
    for cookie in cookie_list:
        # Включаем только необходимые поля, которые нужны для requests
        cookies_dict[cookie['name']] = cookie['value']
    return cookies_dict


def is_etc_format(cookie_data):
    """Проверяет, соответствует ли формат данных формату EditThisCookie"""
    return isinstance(cookie_data, list) and all(isinstance(c, dict) and 'name' in c and 'value' in c for c in cookie_data)


def load_cookies_from_file(cookies_file, import_from_etc=False):
    """Загружает и конвертирует cookies из JSON файла"""
    try:
        with open(cookies_file, 'r') as f:
            cookie_data = json.loads(f.read())
            
        # Если указан флаг import_from_etc, проверяем формат
        if import_from_etc and is_etc_format(cookie_data):
            # Конвертируем только если данные действительно в формате EditThisCookie
            return convert_editthiscookie_to_requests(cookie_data)
        elif isinstance(cookie_data, dict):
            # Если данные уже в формате requests, используем как есть
            return cookie_data
        else:
            raise ValueError("Неверный формат cookies")
            
    except Exception as e:
        logger.error(f"Ошибка загрузки cookies из {cookies_file}: {str(e)}")
        return None


def process_url_list(url_list_file, output, browser, cookies):
    """Обрабатывает несколько URL из файла"""
    successful = 0
    failed = 0
    
    try:
        with open(url_list_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        total = len(urls)
        logger.info(f"Найдено {total} URL для обработки")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Обработка URL {i}/{total}: {url}")
            try:
                download_book(url, output, browser, cookies)
                successful += 1
            except Exception as e:
                logger.error(f"Не удалось загрузить книгу с {url}: {str(e)}")
                failed += 1
                
        logger.info(f"\nИтоги загрузки:")
        logger.info(f"Всего обработано URL: {total}")
        logger.info(f"Успешно загружено: {successful}")
        if failed > 0:
            logger.info(f"Не удалось загрузить: {failed}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки файла со списком URL: {str(e)}")
        return 0, 0


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(
        description=f"Загрузчик аудиокниг с сайта {LITRES_DOMAIN_NAME} ДОСТУПНЫХ ПОЛЬЗОВАТЕЛЮ ПО ПОДПИСКЕ")
    parser.add_argument(
        "-b", "--browser", help=f"Браузер в котором вы авторизованы на сайте {LITRES_DOMAIN_NAME}. \
            Будут использоваться cookies из этого браузера. Также при загрузке книг будет эмулироваться\
            User agent этого браузера. По умолчанию: chrome", default="chrome",
        choices=["chrome", "edge", "firefox", "safari"])
    parser.add_argument("-u", "--user", help="Имя пользователя", default="")
    parser.add_argument("-p", "--password", help="Пароль", default="")
    parser.add_argument(
        "--create-cookies", help="Создавать cookies используя полученные имя пользователя и пароль",
        choices=["always", "never", "invalid"], default="invalid")
    parser.add_argument("--cookies-file", help="Если параметр задан, то cookies будут загружаться из него.\
                        При создании cookies по пользователю-паролю данные сохранятся в этот файл", default="")
    parser.add_argument(
        "-o", "--output", help="Путь к папке загрузки", default=".")
    parser.add_argument("--url", help="Адрес (url) страницы с книгой", default="")
    # Новые аргументы
    parser.add_argument("--import-from-etc", help="Импортировать cookies из формата EditThisCookie и сконвертировать их", 
                       action="store_true")
    parser.add_argument("-a", help="Файл со списком URL книг для загрузки (по одной ссылке на строку)",
                       metavar="LIST", default="")

    args = parser.parse_args()
    logger.info(args)

    cookies = None

    # Получение cookies
    if 'always' in args.create_cookies:
        if len(args.user) > 0 and len(args.password) > 0:
            logger.info('Попытка создания cookies по логину/паролю')
            cookies = litres_auth.create_cookies(
                args.user, args.password, args.browser)
            if not cookies_is_valid(cookies):
                logger.error('Созданные cookies недействительны')
                exit(0)
        else:
            logger.error('Не указаны логин/пароль')
            exit(0)
    else:  # never или invalid
        if len(args.cookies_file) > 0:
            if Path(args.cookies_file).is_file():
                logger.info(f'Попытка получения cookies из файла {args.cookies_file}')
                
                if args.import_from_etc:
                    # Использование импорта формата EditThisCookie
                    cookies_dict = load_cookies_from_file(args.cookies_file, import_from_etc=True)
                    if cookies_dict:
                        cookies = cookiejar_from_dict(cookies_dict)
                else:
                    # Использование оригинального формата
                    cookies_dict = json.loads(Path(args.cookies_file).read_text())
                    cookies = cookiejar_from_dict(cookies_dict)

                if not cookies_is_valid(cookies):
                    logger.warning(f'Cookies в файле {args.cookies_file} недействительны')
                    cookies = None
            else:
                logger.warning(f'Файл {args.cookies_file} не существует')

        if cookies == None:
            logger.info(f'Попытка получения cookies из браузера {args.browser}')
            cookies = get_cookies(args.browser)

        if not cookies_is_valid(cookies):
            if 'never' in args.create_cookies:
                logger.error(f'Cookies браузера {args.browser} недействительны')
                exit(0)
            else:  # создать если недействительны
                logger.warning(f'Cookies браузера {args.browser} недействительны')
                if len(args.user) > 0 and len(args.password) > 0:
                    logger.warning('Попытка создания cookies по логину/паролю')
                    cookies = litres_auth.create_cookies(
                        args.user, args.password, args.browser)
                    if not cookies_is_valid(cookies):
                        logger.error('Созданные cookies недействительны')
                        exit(0)
                else:
                    logger.error('Не указаны логин/пароль')
                    exit(0)

    # Сохранение cookies если указан файл
    if len(args.cookies_file) > 0:
        Path(args.cookies_file).write_text(
            json.dumps(dict_from_cookiejar(cookies)))

    # Обработка загрузок
    if len(args.a) > 0 and Path(args.a).is_file():
        # Обработка списка URL
        process_url_list(args.a, args.output, args.browser, cookies)
    elif len(args.url) > 0:
        # Обработка одного URL
        download_book(args.url, args.output, args.browser, cookies=cookies)
    else:
        logger.error("Не указан URL или файл со списком URL")
        exit(1)

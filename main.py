import requests
import shutil
import browsercookie
from pathvalidate import sanitize_filename
import argparse
import logging
from pathlib import Path
from fake_useragent import UserAgent
from tqdm import tqdm

logger = logging.getLogger(__name__)
api_url = "https://api.litres.ru/foundation/api/arts/"


def get_headers(browser):
    ua = UserAgent()
    agent = ua.random
    if browser == "chrome":
        agent = ua.chrome
    elif browser == "firefox":
        agent = ua.firefox
    return {
        'User-Agent': agent,
    }


def get_cookies(browser):
    cookies = browsercookie.chrome()
    if browser == "chromium":
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
    logger.debug("try to download file: " + url)
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
            f"code: {res.status_code} При загрузке с адреса: {url}")


def download_book(url, output, browser):
    headers = get_headers(browser)
    cookies = get_cookies(browser)
    book_id = url.split("-")[-1].split("/")[0]

    url_string = api_url+book_id
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if res.status_code != 200:
        logger.error(
            f"Ошибка запроса GET: {url_string}. Статус: {res.status_code}")
        exit(1)

    book_info = res.json()["payload"]["data"]
    logger.debug(f"Получена информация о книге: {book_info['title']}")
    book_folder = Path(output) / sanitize_filename(book_info["title"])
    Path(book_folder).mkdir(exist_ok=True, parents=True)

    # Список файлов для загрузки
    url_string = url_string + "/files/grouped"
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if res.status_code != 200:
        logger.error(
            f"Ошибка запроса GET: {url_string}. Статус: {res.status_code}")
        exit(1)

    groups_info = res.json()["payload"]["data"]
    for group_info in groups_info:
        if group_info["file_type"] == "standard_quality_mp3":
            files_info = group_info["files"]
            for file_info in files_info:
                file_id = file_info["id"]
                filename = file_info["filename"]
                file_url = f"https://www.litres.ru/download_book_subscr/{book_id}/{file_id}/{filename}"
                download_mp3(file_url, book_folder,
                             filename, cookies, headers)
            break


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    parser = argparse.ArgumentParser(
        description="Загрузчик аудиокниг доступных по подписке с сайта litres.ru. \n Прежде чем использовать скрипт, небходимо в браузере залогиниться на сайте. \n Загрузчик использует cookies из браузера.")
    parser.add_argument(
        "-b", "--browser", help="Браузер в котором вы авторизованы на сайте litres.ru. Будут использоваться cookies из этого браузера. По умолчанию: chrome", default="chrome",
        choices=["chrome", "chromium", "vivaldi", "edge", "firefox", "safari"])
    parser.add_argument(
        "-o", "--output", help="Путь к папке загрузки", default=".")
    parser.add_argument("url", help="Адрес (url) страницы с книгой")

    args = parser.parse_args()
    logger.info(args)
    download_book(args.url, args.output, args.browser)

import requests
import shutil
import browsercookie
from pathvalidate import sanitize_filename
import argparse
import logging
from pathlib import Path
from fake_useragent import UserAgent

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


def download_mp3(url, path, filename, cookies, headers):

    url_string = url
    logger.debug("try to download file: " + url_string)
    full_filename = Path(path) / sanitize_filename(f"{filename}.mp3")

    res = requests.get(url_string, stream=True,
                       cookies=cookies, headers=headers)
    if res.status_code == 200:
        with open(full_filename, "wb") as f:
            shutil.copyfileobj(res.raw, f)
        logger.warning(
            f"file has been downloaded and saved as: {full_filename}")
    else:
        logger.error(
            f"code: {res.status_code} while downloading: {url_string}")
        exit(1)


# url = "https://www.litres.ru/download_book_subscr/69566866/100682116/02_04.mp3"
# path = "/home/artem/Загрузки"
# filename = "02_04"

# download_mp3(url, path, filename)

def download_book(url, output, browser):
    headers = get_headers(browser)
    cookies = browsercookie.chrome()
    book_id = url.split("-")[-1].split("/")[0]
    
    url_string = api_url+book_id
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if res.status_code == 200:
        book_info = res.json()["payload"]["data"]
        logger.debug(f"Получена информация о книге: ${book_info["title"]}")
        
    else:
        logger.debug(f"Ошибка запроса GET: ${url_string}. Статус: ${res.status_code}")
        exit(1)


# if __name__ == "__main__":
#     logging.basicConfig(
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#         level=logging.DEBUG,
#     )
#     parser = argparse.ArgumentParser(
#         description="Загрузчик аудиокниг доступных по подписке с сайта litres.ru. \n Прежде чем использовать скрипт, небходимо в браузере залогиниться на сайте. \n Загрузчик использует cookies из браузера.")
#     parser.add_argument(
#         "-b", "--browser", help="Браузер в котором вы авторизованы на сайте litres.ru. Будут использоваться cookies из этого браузера", default="chrome",
#         choices=["chrome", "firefox"])
#     parser.add_argument(
#         "-o", "--output", help="Путь к папке загрузки", default=".")
#     parser.add_argument("url", help="Адрес (url) страницы с книгой")

#     args = parser.parse_args()
#     logger.info(args)
#     download_book(args.url, args.output, args.browser)

download_book("https://www.litres.ru/audiobook/sergey-lukyanenko/poiski-utrachennogo-zavtra-71056879/", ".", "chrome")
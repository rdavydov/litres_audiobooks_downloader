import argparse
import logging
from loader import download_book, get_cookies

logger = logging.getLogger(__name__)


def download_books(input, output, browser):
    cookies = get_cookies(args.browser)
    with open(input, 'r') as f:
        for url in f:
            url_trim = url.strip()
            if "litres.ru" in url_trim:
                print(f"Адрес к загрузке: {url_trim}")
                download_book(url_trim, output, browser, cookies)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    parser = argparse.ArgumentParser(
        description="Загрузчик аудиокниг доступных по подписке с сайта litres.ru. \n Прежде чем использовать скрипт, небходимо в браузере залогиниться на сайте. \n Загрузчик использует cookies из браузера.")
    parser.add_argument(
        "-b", "--browser", help="Браузер в котором вы авторизованы на сайте litres.ru. Будут использоваться cookies из этого браузера. По умолчанию: chrome",
        default="chrome",
        choices=["chrome", "chromium", "vivaldi", "edge", "firefox", "safari"])
    parser.add_argument(
        "-i", "--input", help="Путь к файлу со списком url книг к загрузке. Каждый адрес с новой строки", default="queue.txt")
    parser.add_argument(
        "-o", "--output", help="Путь к папке загрузки", default=".")

    args = parser.parse_args()
    logger.info(args)
    download_books(args.input, args.output, args.browser)

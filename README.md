# litres_audiobooks_downloader

Загружает файлы аудиокниг доступные по подписке с сайта [litres.ru](Литрес).
Данный скрипт не позволит скачать книги, которые вам недоступны. Просто если у вас оформлена подписка, но вам не нравится приложение литрес, можно скачать файлы и слушать в альтернативных плеерах.

## Требования

1. Установленный браузер, в котором разрешены куки и в которм вы вошли в личный кабинет [litres.ru](Литрес).
Потенциально поддерживаемые браузеры: **chrome, chromium, vivaldi, edge, firefox, safari**.
Тестировалось только на **chrome**

2. Установленный python3 >= 3.10. Чем новее, тем лучше.

## Установка
Скачиваем любым способом исходный код. Например:

```bash
git clone https://github.com/fabrikant/litres_audiobooks_downloader.git
```

Переходим в каталог с исходным кодом и выполняем команды:

**Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
deactivate
```

**Windows:**

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirement.txt
deactivate
```

## Использование

1. Войти в браузер и убедиться, что вы залогинены в личном кабинете [litres.ru](Литрес).
2. Активировать виртуальное окружение:

**Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```cmd
venv\Scripts\activate
```

3. Примеры использования:

Загрузка одной книги:

**Linux:**

```bash
python main.py -b chrome -o /tmp/audiobooks https://www.litres.ru/audiobook/sebastyan-fitcek/pacient-osoboy-kliniki-54990486/
```

**Windows:**

```cmd
python main.py -b chrome -o D:\audiobooks https://www.litres.ru/audiobook/sebastyan-fitcek/pacient-osoboy-kliniki-54990486/
```

Загрузка нескольких книг из списка:

```bash
python main.py -b chrome -o /tmp/audiobooks -a links.txt
```

**Windows:**

```cmd
python main.py -b chrome -o D:\audiobooks -a links.txt
```

Использование cookies, экспортированных из браузерного расширения EditThisCookie:

**Linux:**

```bash
python loader.py -o /путь/к/папке --cookies-file cookies.json --import-from-etc --url URL_КНИГИ
```

**Windows:**

```cmd
python loader.py -o D:\путь\к\папке --cookies-file cookies.json --import-from-etc --url URL_КНИГИ
```

4. Краткая справка по программе:

```bash
python loader.py -h
```

## Примечания

1. Ссылку нужно брать именно со страницы аудиокниги (там где доступно прослушивание). Идентификаторы текстового варианта и аудио варианта одной и той же книги отличаются.
В адресе должна быть подстрока "audiobook".

2. При использовании файла со списком книг (-a) каждая ссылка должна быть на отдельной строке.

3. Для использования cookies из браузера через расширение EditThisCookie:
   - Установите расширение EditThisCookie в браузер
   - Войдите на сайт litres.ru
   - Экспортируйте cookies через EditThisCookie в файл
   - Используйте этот файл с параметром --import-from-etc

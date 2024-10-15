# litres_audiobooks_downloader
Загружает файлы аудиокниг доступные по подписке с сайта [litres.ru](Литрес).
Данный скрипт не позволит скачать книги, которые вам недоступны. Просто если у вас оформлена подписка, но вам не нравится приложение литрес, можно скачать файлы и слушать в альтернативных плеерах.

# Требования
1. Установленный браузер, в котором разрешены куки и в которм вы вошли в личный кабинет [litres.ru](Литрес).
Потенциально поддерживаемые браузеры: **chrome, chromium, vivaldi, edge, firefox, safari**.
Тестировалось только на **chrome**

2. Установленный python3. Чем новее, тем лучше.

# Установка
Скачиваем любым способом исходный код. Например:  
```bash
git clone https://github.com/fabrikant/litres_audiobooks_downloader.git
```
Переходим в каталог с исходным кодом и выполняем команды  
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
# Использование
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
3. Пример загрузки книги:
**Linux:**
```bash
python main.py -b chrome -o /tmp/audiobooks https://www.litres.ru/audiobook/sebastyan-fitcek/pacient-osoboy-kliniki-54990486/
```
**Windows:**
```cmd
python main.py -b chrome -o D:\audiobooks https://www.litres.ru/audiobook/sebastyan-fitcek/pacient-osoboy-kliniki-54990486/
```
4. Краткая справка по программе
```bash
python main.py -h
```
# UnBlock

WebSocket прокси для Telegram Desktop. Ускоряет соединение через сокеты.

## Что внутри

Каждая платформа в отдельной папке:

- **Win/** — Windows (EXE)
- **Mac/** — macOS (APP)
- **Linux/** — Linux (бинарник)

В каждой папке:
- `gui.py` — исходники GUI
- `proxy/` — код прокси
- `build.spec` — конфиг для PyInstaller
- `requirements.txt` — зависимости Python
- `build.bat` / `build.sh` — скрипт сборки
- `README.md` — инструкция для платформы

## Быстрый старт

### Windows

```cmd
cd Win
build.bat
```

Или запустить без сборки:
```cmd
pip install -r requirements.txt
python gui.py
```

### macOS

```bash
cd Mac
chmod +x build.sh
./build.sh
```

Или запустить без сборки:
```bash
pip3 install -r requirements.txt
python3 gui.py
```

### Linux

```bash
cd Linux
chmod +x build.sh
./build.sh
```

Или запустить без сборки:
```bash
pip3 install -r requirements.txt
python3 gui.py
```


## Настройка Telegram

1. Telegram Desktop → Настройки → Продвинутые → Тип соединения
2. "Использовать прокси"
3. Тип: **SOCKS5**
4. Хост: `127.0.0.1`
5. Порт: `1080` (или ваш в настройках)
6. Сохранить

## Сборка из исходников

Требования:
- Python 3.8+
- pip

Шаги:

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Собрать
pyinstaller --clean build.spec

# 3. Готовый файл в dist/
```

## Структура проекта

```
tg-ws-proxy-1.2.0/
├── Win/           # Windows версия
├── Mac/           # macOS версия
├── Linux/         # Linux версия
├── proxy/         # Исходники прокси (общие)
└── README.md      # Этот файл
```

## Решение проблем

**Прокси не подключается:**
- Проверьте, что порт не занят другой программой
- Запустите от имени администратора/root
- Включите verbose режим в настройках

**GUI не запускается:**
- Убедитесь, что PyQt6 установлен: `pip install PyQt6`
- На Linux: установите `libxcb-xinerama0 libxcb-cursor0`

**Telegram не видит прокси:**
- Убедитесь, что прокси запущен (индикатор зелёный)
- Проверьте порт в настройках прокси и Telegram

## Авторы

MORALFUCK & Flowseal

[Оригинальный проект](https://github.com/Flowseal/tg-ws-proxy)

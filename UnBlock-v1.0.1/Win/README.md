# UnBlock для Windows

WebSocket прокси для Telegram Desktop.

## Быстрый старт

### Запуск без сборки

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить GUI
python gui.py
```

### Сборка EXE

Запустите `build.bat` или выполните вручную:

```bash
pip install -r requirements.txt
pyinstaller build.spec
```

Готовый файл: `dist/UnBlock.exe`

## Настройка Telegram

1. Откройте Telegram Desktop
2. Настройки → Продвинутые → Тип соединения
3. Выберите "Использовать прокси"
4. Тип: **SOCKS5**
5. Хост: `127.0.0.1`
6. Порт: `1080` (или ваш в настройках)
7. Нажмите "Сохранить"

## Конфигурация

Файл конфигурации: `%APPDATA%\UnBlock\config.json`

```json
{
  "port": 1080,
  "host": "127.0.0.1",
  "dc_ip": [
    "2:149.154.167.220",
    "4:149.154.167.220"
  ],
  "verbose": false,
  "autostart": false
}
```

## Требования

- Windows 10/11
- Python 3.8+ (для запуска из исходников)

## Сборка

- Python 3.8+
- PyQt6
- cryptography
- PyInstaller

Команды для чистой сборки:

```bash
pip install -r requirements.txt
pyinstaller --clean build.spec
```

## Решение проблем

**Не запускается EXE:**
- Установите Visual C++ Redistributable
- Проверьте антивирус (может блокировать)

**Ошибка при сборке:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
pyinstaller --clean build.spec
```

**Прокси не работает:**
- Проверьте, что порт не занят
- Запустите от имени администратора
- Включите verbose режим в настройках

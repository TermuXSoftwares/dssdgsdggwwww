# UnBlock для macOS

WebSocket прокси для Telegram Desktop.

## Быстрый старт

### Запуск без сборки

```bash
# Установить зависимости
pip3 install -r requirements.txt

# Запустить GUI
python3 gui.py
```

### Сборка APP

```bash
chmod +x build.sh
./build.sh
```

Или вручную:

```bash
pip3 install -r requirements.txt
pyinstaller --clean build.spec
```

Готовый файл: `dist/UnBlock.app`

## Настройка Telegram

1. Откройте Telegram Desktop
2. Настройки → Продвинутые → Тип соединения
3. Выберите "Использовать прокси"
4. Тип: **SOCKS5**
5. Хост: `127.0.0.1`
6. Порт: `1080`
7. Нажмите "Сохранить"

## Конфигурация

Файл конфигурации: `~/Library/Application Support/UnBlock/config.json`

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

- macOS 10.15+
- Python 3.8+ (для запуска из исходников)

## Сборка

- Python 3.8+
- PyQt6
- cryptography
- PyInstaller

```bash
pip3 install -r requirements.txt
pyinstaller --clean build.spec
```

## Решение проблем

**Не запускается APP:**
- Откройте через Правой кнопкой → Открыть (первый запуск)
- Или: `xattr -cr dist/UnBlock.app`

**Ошибка подписи:**
```bash
codesign --force --deep --sign - dist/UnBlock.app
```

**Прокси не работает:**
- Проверьте порт в настройках
- Включите verbose режим

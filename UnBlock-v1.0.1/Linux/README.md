# UnBlock для Linux

WebSocket прокси для Telegram Desktop.

## Быстрый старт

### Запуск без сборки

```bash
# Установить зависимости
pip3 install -r requirements.txt

# Запустить GUI
python3 gui.py
```

### Сборка

```bash
chmod +x build.sh
./build.sh
```

Или вручную:

```bash
# Debian/Ubuntu
sudo apt-get install libxcb-xinerama0 libxcb-cursor0 libegl1 libopengl0

pip3 install -r requirements.txt
pyinstaller --clean build.spec
```

Готовый файл: `dist/UnBlock`

## Настройка Telegram

1. Откройте Telegram Desktop
2. Настройки → Продвинутые → Тип соединения
3. Выберите "Использовать прокси"
4. Тип: **SOCKS5**
5. Хост: `127.0.0.1`
6. Порт: `1080`
7. Нажмите "Сохранить"

## Конфигурация

Файл конфигурации: `~/.config/UnBlock/config.json`

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

- Python 3.8+
- PyQt6
- X11 или Wayland

### Зависимости

**Debian/Ubuntu:**
```bash
sudo apt-get install libxcb-xinerama0 libxcb-cursor0 libegl1 libopengl0
```

**Fedora:**
```bash
sudo dnf install libxcb libxcb-util xcb-util-cursor
```

**Arch:**
```bash
sudo pacman -S libxcb xcb-util-cursor
```

## Сборка

```bash
pip3 install -r requirements.txt
pyinstaller --clean build.spec
```

## Решение проблем

**Ошибка: "cannot connect to X server"**
- Запускайте из терминала в графической сессии

**Qt ошибка: "could not load the Qt platform plugin xcb"**
```bash
sudo apt-get install libxcb-xinerama0 libxcb-cursor0
```

**Прокси не работает:**
- Проверьте порт: `netstat -tlnp | grep 1080`
- Включите verbose режим в настройках

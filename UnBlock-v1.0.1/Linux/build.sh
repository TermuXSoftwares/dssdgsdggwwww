#!/bin/bash

echo "============================================"
echo "UnBlock - Сборка для Linux"
echo "============================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 не найден"
    exit 1
fi

# Установка системных зависимостей (Debian/Ubuntu)
if command -v apt-get &> /dev/null; then
    echo "[INFO] Установка системных библиотек..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq libxcb-xinerama0 libxcb-cursor0 libegl1 libopengl0
fi

# Установка зависимостей
echo "[1/3] Установка зависимостей..."
pip3 install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "[ERROR] Не удалось установить зависимости"
    exit 1
fi

# Очистка старых сборок
echo "[2/3] Очистка старых файлов..."
rm -rf build dist

# Сборка EXE
echo "[3/3] Сборка UnBlock..."
pyinstaller --clean build.spec
if [ $? -ne 0 ]; then
    echo "[ERROR] Ошибка сборки"
    exit 1
fi

echo ""
echo "============================================"
echo "Готово! UnBlock находится в папке dist"
echo "============================================"

#!/bin/bash

echo "============================================"
echo "UnBlock - Сборка для macOS"
echo "============================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 не найден"
    exit 1
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

# Сборка APP
echo "[3/3] Сборка UnBlock.app..."
pyinstaller --clean build.spec
if [ $? -ne 0 ]; then
    echo "[ERROR] Ошибка сборки"
    exit 1
fi

echo ""
echo "============================================"
echo "Готово! UnBlock.app находится в папке dist"
echo "============================================"

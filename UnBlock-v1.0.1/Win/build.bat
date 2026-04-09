@echo off
chcp 65001 >nul
echo ============================================
echo UnBlock - Сборка для Windows
echo ============================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден. Установите Python 3.8+
    pause
    exit /b 1
)

:: Установка зависимостей
echo [1/3] Установка зависимостей...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Не удалось установить зависимости
    pause
    exit /b 1
)

:: Очистка старых сборок
echo [2/3] Очистка старых файлов...
rmdir /s /q build dist 2>nul

:: Сборка EXE
echo [3/3] Сборка UnBlock.exe...
pyinstaller --clean build.spec
if errorlevel 1 (
    echo [ERROR] Ошибка сборки
    pause
    exit /b 1
)

echo.
echo ============================================
echo Готово! UnBlock.exe находится в папке dist
echo ============================================
pause

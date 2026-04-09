#!/bin/bash
# UnBlock APK Builder - запусти на Linux/macOS или GitHub Codespaces
# Usage: ./build_apk.sh

set -e

echo "=== UnBlock APK Builder ==="

# Установка зависимостей
echo "1. Установка зависимостей..."
apt-get update && apt-get install -y python3 python3-pip git curl unzip

# Установка buildozer
echo "2. Установка buildozer..."
pip3 install buildozer

# Установка Android SDK если нет
if [ -z "$ANDROID_HOME" ]; then
    echo "3. Настройка Android SDK..."
    mkdir -p ~/android-sdk/cmdline-tools
    cd ~/android-sdk/cmdline-tools
    
    # Скачивание cmdline-tools
    if [ ! -f commandlinetools-linux.zip ]; then
        curl -o commandlinetools-linux.zip https://dl.google.com/android/repository/commandlinetools-linux-11076738_latest.zip
    fi
    unzip -o commandlinetools-linux.zip
    mv cmdline-tools latest
    
    export ANDROID_HOME=~/android-sdk
    export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
    
    # Принятие лицензий
    yes | sdkmanager --licenses 2>/dev/null || true
    sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
fi

cd "$(dirname "$0")"

# Запуск сборки
echo "4. Сборка APK..."
buildozer android debug

echo "=== APK готов ==="
ls -la bin/*.apk 2>/dev/null || echo "APK в bin/"
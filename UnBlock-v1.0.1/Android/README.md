# UnBlock для Android (APK)

## Требования для сборки на Linux/macOS

```bash
# 1. Установить зависимости
sudo apt-get update
sudo apt-get install -y python3 python3-pip git openjdk-17-jdk

# 2. Установить buildozer
pip3 install buildozer==1.5.0 kivy==2.3.0 cryptography

# 3. Собрать APK
cd Android
buildozer android debug
```

APK будет в `bin/`

## Быстрая сборка через GitHub (бесплатно)

1. Зайдите на https://github.com и создайте аккаунт
2. Загрузите этот проект в свой репозиторий
3. Перейдите в Actions → Build APK → Run workflow
4. Скачайте готовый APK из Artifacts

## Готовая APK (скоро)

Следите за релизами на https://github.com/ваш-репозиторий/releases

## Использование APK

1. Установите APK на Android устройство
2. Откройте UnBlock
3. Нажмите "Запустить"
4. Настройте Telegram Desktop:
   - Тип: SOCKS5
   - Хост: 127.0.0.1
   - Порт: 1080
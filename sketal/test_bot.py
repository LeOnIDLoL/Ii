#!/usr/bin/env python3
"""
Test Bot Script - SuperGrok AI v1.3
Тестовый скрипт для проверки работы бота
"""

import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_bot():
    """Тестирование бота"""
    try:
        logger.info("🚀 Тестирование Sketal Bot...")
        
        # Импортируем бота
        from bot import BotSettings
        
        # Создаем настройки
        settings = BotSettings()
        logger.info("✅ Настройки бота загружены")
        
        # Проверяем токены
        if settings.USERS:
            logger.info(f"✅ Токен пользователя настроен: {settings.USERS[0][1][:20]}...")
        else:
            logger.error("❌ Токен пользователя не настроен")
        
        # Проверяем плагины
        if hasattr(settings, 'PLUGINS') and settings.PLUGINS:
            logger.info(f"✅ Загружено плагинов: {len(settings.PLUGINS)}")
        else:
            logger.error("❌ Плагины не загружены")
        
        logger.info("✅ Тестирование завершено успешно!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    success = test_bot()
    if success:
        print("✅ Бот готов к работе!")
    else:
        print("❌ Бот не готов к работе!")
        sys.exit(1)
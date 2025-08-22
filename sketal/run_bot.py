#!/usr/bin/env python3
"""
Run Bot Script - SuperGrok AI v1.3
Запускающий скрипт для полного Sketal бота
"""

import sys
import os
import logging
import asyncio

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция"""
    try:
        logger.info("🚀 Запуск полного Sketal Bot...")
        
        # Импортируем необходимые модули
        from bot import Bot
        from settings import BotSettings
        
        # Создаем настройки
        settings = BotSettings()
        logger.info("✅ Настройки загружены")
        
        # Создаем бота
        bot = Bot(settings)
        logger.info("✅ Бот создан")
        
        # Запускаем бота
        logger.info("🔄 Запуск Long Polling...")
        
        # Получаем клиент для Long Polling
        client = bot.api.target_client
        
        # Инициализируем Long Polling
        await bot.init_long_polling(client)
        
        logger.info("✅ Long Polling запущен")
        logger.info("📱 Бот готов к работе!")
        
        # Держим бота запущенным
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise
    finally:
        logger.info("🏁 Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1)
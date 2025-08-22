#!/usr/bin/env python3
"""
Sketal Bot Updated - SuperGrok AI v1.3
Обновленный бот с поддержкой VK API 5.199

Функции:
- VK API 5.199
- Автоответы в беседах
- Команды управления
- Защита от спама
- Детальная статистика
"""

import vk_api
import asyncio
import logging
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

# Импорт конфигурации и контроллера
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_vk_config, get_bot_config
from utils.vk_controller import VKController

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SketalBot:
    """Обновленный Sketal Bot с поддержкой VK API 5.199"""
    
    def __init__(self, settings=None):
        """Инициализация бота"""
        self.settings = settings
        self.logger = logger
        
        # Загружаем конфигурацию
        self.vk_config = get_vk_config()
        self.bot_config = get_bot_config()
        
        # Инициализация VK контроллера
        self.api = VKController(settings, logger=self.logger, loop=None)
        
        # Состояние бота
        self.running = False
        self.longpoll = None
        self.conversation_handlers = {}
        
        # Статистика
        self.message_count = 0
        self.command_count = 0
        self.start_time = time.time()
        
        # Инициализация обработчиков бесед
        self._init_conversation_handlers()
        
        self.logger.info("✅ Sketal Bot успешно инициализирован")
    
    def _init_conversation_handlers(self):
        """Инициализация обработчиков бесед"""
        try:
            # Базовые обработчики
            self.conversation_handlers = {
                'greeting': self._handle_greeting,
                'help': self._handle_help,
                'status': self._handle_status,
                'info': self._handle_info,
                'stats': self._handle_stats,
                'ping': self._handle_ping
            }
            
            self.logger.info(f"✅ Инициализировано {len(self.conversation_handlers)} обработчиков бесед")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации обработчиков бесед: {e}")
    
    async def start(self):
        """Запуск бота"""
        try:
            self.logger.info("🚀 Запуск Sketal Bot...")
            
            # Проверяем доступность VK API
            if not self.api.get_status()['initialized']:
                self.logger.error("❌ VK API не инициализирован")
                return False
            
            # Получаем информацию о группе
            group_info = await self._get_group_info()
            if group_info:
                self.logger.info(f"✅ Подключен к группе: {group_info['name']}")
            
            # Запускаем Long Polling
            await self._start_longpoll()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска бота: {e}")
            return False
    
    async def _get_group_info(self) -> Optional[Dict]:
        """Получение информации о группе"""
        try:
            # Получаем ID группы из токена
            api = self.api.get_api('group')
            if not api:
                return None
            
            # Пробуем получить информацию о группе
            groups = api.groups.getById()
            if groups:
                return groups[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения информации о группе: {e}")
            return None
    
    async def _start_longpoll(self):
        """Запуск Long Polling"""
        try:
            self.logger.info("🔌 Запуск Long Polling...")
            
            # Получаем сессию группы
            group_session = self.api.get_session('group')
            if not group_session:
                self.logger.error("❌ Групповая сессия недоступна")
                return
            
            # Получаем ID группы
            group_info = await self._get_group_info()
            if not group_info:
                self.logger.error("❌ Не удалось получить ID группы")
                return
            
            group_id = group_info['id']
            
            # Создаем Long Poll клиент
            self.longpoll = VkBotLongPoll(group_session, group_id)
            self.running = True
            
            self.logger.info(f"✅ Long Polling запущен для группы {group_id}")
            
            # Основной цикл обработки событий
            await self._event_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска Long Polling: {e}")
    
    async def _event_loop(self):
        """Основной цикл обработки событий"""
        try:
            for event in self.longpoll.listen():
                if not self.running:
                    break
                
                await self._handle_event(event)
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка в цикле событий: {e}")
        finally:
            self.logger.info("🏁 Цикл событий остановлен")
    
    async def _handle_event(self, event):
        """Обработка VK события"""
        try:
            if event.type == VkBotEventType.MESSAGE_NEW:
                await self._handle_new_message(event)
            elif event.type == VkBotEventType.MESSAGE_REPLY:
                await self._handle_message_reply(event)
            elif event.type == VkBotEventType.MESSAGE_EDIT:
                await self._handle_message_edit(event)
            elif event.type == VkBotEventType.MESSAGE_ALLOW:
                await self._handle_message_allow(event)
            elif event.type == VkBotEventType.MESSAGE_DENY:
                await self._handle_message_deny(event)
            else:
                self.logger.debug(f"📝 Необработанный тип события: {event.type}")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки события: {e}")
    
    async def _handle_new_message(self, event):
        """Обработка нового сообщения"""
        try:
            message = event.message
            user_id = message.from_id
            text = message.text
            peer_id = message.peer_id
            message_id = message.id
            
            self.message_count += 1
            
            self.logger.info(f"📨 Новое сообщение #{self.message_count} от {user_id} в {peer_id}: '{text[:50]}...'")
            
            # Проверяем на спам
            if await self._check_spam(user_id, peer_id):
                self.logger.warning(f"⚠️ Спам от пользователя {user_id}")
                return
            
            # Обработка команд
            if text.startswith('/'):
                await self._handle_command(text, user_id, peer_id, message_id)
            else:
                # Обычное сообщение
                await self._handle_regular_message(text, user_id, peer_id, message_id)
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки нового сообщения: {e}")
    
    async def _handle_command(self, command: str, user_id: int, peer_id: int, message_id: int):
        """Обработка команд"""
        try:
            self.command_count += 1
            
            # Разбираем команду
            parts = command[1:].split(' ', 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            self.logger.info(f"🔧 Команда #{self.command_count}: /{cmd} от {user_id}")
            
            # Обрабатываем команду
            if cmd in self.conversation_handlers:
                await self.conversation_handlers[cmd](user_id, peer_id, message_id, args)
            else:
                await self._send_error_message(peer_id, f"Команда /{cmd} не найдена. Используйте /help для справки.")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки команды: {e}")
            await self._send_error_message(peer_id, "Произошла ошибка при выполнении команды")
    
    async def _handle_regular_message(self, text: str, user_id: int, peer_id: int, message_id: int):
        """Обработка обычного сообщения"""
        try:
            # Автоматические ответы
            if self.bot_config['conversation_settings']['auto_reply']:
                await self._auto_reply(text, user_id, peer_id, message_id)
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки обычного сообщения: {e}")
    
    async def _auto_reply(self, text: str, user_id: int, peer_id: int, message_id: int):
        """Автоматический ответ на сообщение"""
        try:
            # Простые триггеры для ответов
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['привет', 'hello', 'hi']):
                await self.api.send_message(peer_id, "👋 Привет! Как дела?")
            
            elif any(word in text_lower for word in ['как дела', 'how are you']):
                await self.api.send_message(peer_id, "🤖 У меня все отлично! А у тебя?")
            
            elif any(word in text_lower for word in ['спасибо', 'thanks', 'thank you']):
                await self.api.send_message(peer_id, "😊 Пожалуйста! Рад помочь!")
            
            elif any(word in text_lower for word in ['пока', 'bye', 'goodbye']):
                await self.api.send_message(peer_id, "👋 До свидания! Буду ждать новых сообщений!")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка автоматического ответа: {e}")
    
    async def _check_spam(self, user_id: int, peer_id: int) -> bool:
        """Проверка на спам"""
        try:
            # Простая проверка на спам
            current_time = time.time()
            key = f"{user_id}_{peer_id}"
            
            if not hasattr(self, '_spam_check'):
                self._spam_check = {}
            
            if key in self._spam_check:
                last_time, count = self._spam_check[key]
                
                # Сброс счетчика если прошло больше минуты
                if current_time - last_time > 60:
                    self._spam_check[key] = (current_time, 1)
                    return False
                
                # Увеличиваем счетчик
                count += 1
                self._spam_check[key] = (current_time, count)
                
                # Блокируем если больше 5 сообщений в минуту
                if count > 5:
                    return True
            
            else:
                self._spam_check[key] = (current_time, 1)
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки спама: {e}")
            return False
    
    async def _send_error_message(self, peer_id: int, error_text: str):
        """Отправка сообщения об ошибке"""
        try:
            await self.api.send_message(peer_id, f"❌ {error_text}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки сообщения об ошибке: {e}")
    
    # Обработчики команд
    async def _handle_greeting(self, user_id: int, peer_id: int, message_id: int, args: str):
        """Обработка приветствия"""
        greeting = self.bot_config['conversation_settings']['greeting_message']
        await self.api.send_message(peer_id, greeting)
    
    async def _handle_help(self, user_id: int, peer_id: int, message_id: int, args: str):
        """Обработка справки"""
        help_text = self.bot_config['conversation_settings']['help_message']
        await self.api.send_message(peer_id, help_text)
    
    async def _handle_status(self, user_id: int, peer_id: int, message_id: int, args: str):
        """Обработка статуса"""
        try:
            bot_stats = self.api.get_stats()
            vk_status = self.api.get_status()
            
            status_text = f"""
📊 **Статус Sketal Bot:**
🤖 Версия: {self.bot_config['version']}
📱 VK API: {self.vk_config['api_version']}
⏱️ Время работы: {bot_stats['uptime_formatted']}
📨 Сообщений отправлено: {bot_stats['messages_sent']}
🔧 Команд обработано: {self.command_count}
✅ Успешность: {bot_stats['success_rate']}
🔌 Сессии: {', '.join(vk_status['apis_available'])}
            """
            
            await self.api.send_message(peer_id, status_text.strip())
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения статуса: {e}")
            await self._send_error_message(peer_id, "Не удалось получить статус")
    
    async def _handle_info(self, user_id: int, peer_id: int, message_id: int, args: str):
        """Обработка информации"""
        info_text = f"""
🤖 **Sketal Bot - SuperGrok AI v1.3**
📱 Полная поддержка VK API 5.199
🔌 Автоматические ответы в беседах
📦 Плагинная система
🛡️ Защита от спама
📊 Детальная статистика
        """
        
        await self.api.send_message(peer_id, info_text.strip())
    
    async def _handle_stats(self, user_id: int, peer_id: int, message_id: int, args: str):
        """Обработка статистики"""
        try:
            bot_stats = self.api.get_stats()
            
            stats_text = f"""
📈 **Статистика бота:**
⏱️ Время работы: {bot_stats['uptime_formatted']}
📨 Сообщений: {bot_stats['messages_sent']}
🔧 Команд: {self.command_count}
❌ Ошибок: {bot_stats['errors_count']}
✅ Успешность: {bot_stats['success_rate']}
            """
            
            await self.api.send_message(peer_id, stats_text.strip())
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения статистики: {e}")
            await self._send_error_message(peer_id, "Не удалось получить статистику")
    
    async def _handle_ping(self, user_id: int, peer_id: int, message_id: int, args: str):
        """Обработка ping команды"""
        start_time = time.time()
        await self.api.send_message(peer_id, "🏓 Pong!")
        end_time = time.time()
        
        ping_time = round((end_time - start_time) * 1000, 2)
        await self.api.send_message(peer_id, f"⏱️ Время ответа: {ping_time}ms")
    
    async def stop(self):
        """Остановка бота"""
        try:
            self.logger.info("🛑 Остановка Sketal Bot...")
            self.running = False
            
            if self.longpoll:
                self.longpoll.stop()
            
            self.logger.info("✅ Sketal Bot остановлен")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка остановки бота: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики бота"""
        uptime = time.time() - self.start_time
        return {
            'uptime_seconds': int(uptime),
            'uptime_formatted': f"{int(uptime // 3600)}ч {int((uptime % 3600) // 60)}м {int(uptime % 60)}с",
            'message_count': self.message_count,
            'command_count': self.command_count,
            'vk_stats': self.api.get_stats() if self.api else {},
            'bot_status': {
                'running': self.running,
                'longpoll_active': self.longpoll is not None,
                'conversation_handlers': len(self.conversation_handlers)
            }
        }


async def main():
    """Главная функция"""
    print("🚀 Sketal Bot with VK Support - SuperGrok AI v1.3")
    print("=" * 60)
    
    # Простые настройки для демонстрации
    class SimpleSettings:
        DEBUG = True
        PLUGINS = {}
    
    settings = SimpleSettings()
    
    # Создание и запуск бота
    bot = SketalBot(settings)
    
    try:
        # Запуск бота
        success = await bot.start()
        
        if success:
            print("✅ Бот успешно запущен!")
            print("📱 Ожидание сообщений...")
            
            # Держим бота запущенным
            while bot.running:
                await asyncio.sleep(1)
                
        else:
            print("❌ Не удалось запустить бота")
            
    except KeyboardInterrupt:
        print("\n⚠️ Получен сигнал остановки")
        await bot.stop()
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
        await bot.stop()
    finally:
        print("🏁 Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
#!/usr/bin/env python3
"""
VK Controller - SuperGrok AI v1.3
Обновленный VK контроллер с поддержкой API 5.199

Функции:
- Современный VK API 5.199
- Обработка ошибок и повторные попытки
- Поддержка групп, пользователей, бесед
- Автоматические ответы в беседах
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

# Импорт конфигурации
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_vk_config, get_bot_config

logger = logging.getLogger(__name__)

class VKController:
    """Обновленный VK контроллер с поддержкой API 5.199"""
    
    def __init__(self, settings=None, logger=None, loop=None):
        """Инициализация VK контроллера"""
        self.settings = settings
        self.logger = logger or logging.getLogger(__name__)
        self.loop = loop or asyncio.get_event_loop()
        
        # Загружаем конфигурацию
        self.vk_config = get_vk_config()
        self.bot_config = get_bot_config()
        
        # VK сессии
        self.vk_sessions = {}
        self.vk_apis = {}
        self.longpoll = None
        
        # Статистика
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        # Инициализация VK сессий
        self._init_vk_sessions()
        
        self.logger.info("🚀 VK Controller инициализирован с API 5.199")
    
    def _init_vk_sessions(self):
        """Инициализация VK сессий для всех токенов"""
        try:
            # Пользовательский токен
            if self.vk_config['vk_user_token']:
                user_session = vk_api.VkApi(token=self.vk_config['vk_user_token'])
                self.vk_sessions['user'] = user_session
                self.vk_apis['user'] = user_session.get_api()
                self.logger.info("✅ User VK session инициализирована")
            
            # Групповой токен
            if self.vk_config['vk_group_token']:
                group_session = vk_api.VkApi(token=self.vk_config['vk_group_token'])
                self.vk_sessions['group'] = group_session
                self.vk_apis['group'] = group_session.get_api()
                self.logger.info("✅ Group VK session инициализирована")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации VK сессий: {e}")
    
    def get_api(self, token_type: str = 'group'):
        """Получение VK API по типу токена"""
        return self.vk_apis.get(token_type)
    
    def get_session(self, token_type: str = 'group'):
        """Получение VK сессии по типу токена"""
        return self.vk_sessions.get(token_type)
    
    async def send_message(self, peer_id: int, message: str, token_type: str = 'group', **kwargs) -> bool:
        """Отправка сообщения через VK API"""
        try:
            api = self.get_api(token_type)
            if not api:
                self.logger.error(f"❌ VK API недоступен для типа: {token_type}")
                return False
            
            # Проверяем длину сообщения
            if len(message) > self.bot_config['message_settings']['max_length']:
                if self.bot_config['message_settings']['auto_split']:
                    messages = self._split_message(message)
                    for msg in messages:
                        await self._send_single_message(api, peer_id, msg, **kwargs)
                    return True
                else:
                    self.logger.error(f"❌ Сообщение слишком длинное: {len(message)} символов")
                    return False
            
            return await self._send_single_message(api, peer_id, message, **kwargs)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки сообщения: {e}")
            self.error_count += 1
            return False
    
    async def _send_single_message(self, api, peer_id: int, message: str, **kwargs) -> bool:
        """Отправка одного сообщения"""
        try:
            result = api.messages.send(
                peer_id=peer_id,
                message=message,
                random_id=get_random_id(),
                **kwargs
            )
            
            self.message_count += 1
            self.logger.info(f"✅ Сообщение #{self.message_count} отправлено в {peer_id}: '{message[:50]}...'")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки сообщения в {peer_id}: {e}")
            self.error_count += 1
            return False
    
    def _split_message(self, message: str, max_length: int = None) -> List[str]:
        """Разделение длинного сообщения на части"""
        if max_length is None:
            max_length = self.bot_config['message_settings']['max_length']
        
        messages = []
        while len(message) > max_length:
            # Ищем последний пробел в пределах лимита
            split_point = message.rfind(' ', 0, max_length)
            if split_point == -1:
                split_point = max_length
            
            messages.append(message[:split_point])
            message = message[split_point:].lstrip()
        
        if message:
            messages.append(message)
        
        return messages
    
    async def post_to_wall(self, owner_id: int, message: str, **kwargs) -> bool:
        """Публикация поста на стену"""
        try:
            api = self.get_api('group')
            if not api:
                self.logger.error("❌ Групповой VK API недоступен")
                return False
            
            result = api.wall.post(
                owner_id=owner_id,
                message=message,
                **kwargs
            )
            
            post_id = result.get('post_id', 'unknown')
            self.logger.info(f"✅ Пост опубликован на стене {owner_id} (ID: {post_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка публикации поста: {e}")
            self.error_count += 1
            return False
    
    async def get_conversations(self, count: int = 20) -> Optional[List]:
        """Получение списка бесед"""
        try:
            api = self.get_api('group')
            if not api:
                self.logger.error("❌ Групповой VK API недоступен")
                return None
            
            conversations = api.messages.getConversations(count=count)
            return conversations.get('items', [])
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения бесед: {e}")
            self.error_count += 1
            return None
    
    async def get_group_members(self, group_id: int, count: int = 1000) -> Optional[List]:
        """Получение участников группы"""
        try:
            api = self.get_api('group')
            if not api:
                self.logger.error("❌ Групповой VK API недоступен")
                return None
            
            members = api.groups.getMembers(group_id=group_id, count=count)
            return members.get('items', [])
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения участников группы: {e}")
            self.error_count += 1
            return None
    
    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        try:
            api = self.get_api('group')
            if not api:
                self.logger.error("❌ Групповой VK API недоступен")
                return None
            
            user_info = api.users.get(user_ids=user_id)[0]
            return user_info
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения информации о пользователе {user_id}: {e}")
            self.error_count += 1
            return None
    
    async def get_group_info(self, group_id: int) -> Optional[Dict]:
        """Получение информации о группе"""
        try:
            api = self.get_api('group')
            if not api:
                self.logger.error("❌ Групповой VK API недоступен")
                return None
            
            group_info = api.groups.getById(group_id=group_id)[0]
            return group_info
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения информации о группе {group_id}: {e}")
            self.error_count += 1
            return None
    
    async def reply_to_message(self, peer_id: int, reply_to: int, message: str, **kwargs) -> bool:
        """Ответ на конкретное сообщение"""
        try:
            api = self.get_api('group')
            if not api:
                self.logger.error("❌ Групповой VK API недоступен")
                return False
            
            result = api.messages.send(
                peer_id=peer_id,
                message=message,
                reply_to=reply_to,
                random_id=get_random_id(),
                **kwargs
            )
            
            self.message_count += 1
            self.logger.info(f"✅ Ответ #{self.message_count} отправлен в {peer_id} на сообщение {reply_to}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки ответа: {e}")
            self.error_count += 1
            return False
    
    async def send_sticker(self, peer_id: int, sticker_id: int, **kwargs) -> bool:
        """Отправка стикера"""
        try:
            api = self.get_api('group')
            if not api:
                self.logger.error("❌ Групповой VK API недоступен")
                return False
            
            result = api.messages.send(
                peer_id=peer_id,
                sticker_id=sticker_id,
                random_id=get_random_id(),
                **kwargs
            )
            
            self.message_count += 1
            self.logger.info(f"✅ Стикер #{self.message_count} отправлен в {peer_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки стикера: {e}")
            self.error_count += 1
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики контроллера"""
        uptime = time.time() - self.start_time
        return {
            'uptime_seconds': int(uptime),
            'uptime_formatted': f"{int(uptime // 3600)}ч {int((uptime % 3600) // 60)}м {int(uptime % 60)}с",
            'messages_sent': self.message_count,
            'errors_count': self.error_count,
            'success_rate': f"{(self.message_count / (self.message_count + self.error_count) * 100):.1f}%" if (self.message_count + self.error_count) > 0 else "0%",
            'api_version': self.vk_config['api_version'],
            'sessions_available': list(self.vk_sessions.keys())
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса контроллера"""
        return {
            'initialized': bool(self.vk_sessions),
            'sessions_count': len(self.vk_sessions),
            'apis_available': list(self.vk_apis.keys()),
            'longpoll_active': self.longpoll is not None,
            'config_loaded': bool(self.vk_config and self.bot_config)
        }
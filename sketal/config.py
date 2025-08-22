#!/usr/bin/env python3
"""
Sketal Bot Configuration - SuperGrok AI v1.3
Конфигурация бота с поддержкой VK API 5.199

Содержит:
- VK API токены (пользователь + группа)
- Настройки бота
- Конфигурацию плагинов
- Параметры безопасности
"""

import os
from typing import Dict, Any

class BotConfig:
    """Конфигурация Sketal Bot"""
    
    def __init__(self):
        """Инициализация конфигурации"""
        self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации"""
        # VK API Configuration
        self.VK_CONFIG = {
            # API версия
            'api_version': '5.199',
            
            # Токен пользователя (ваш личный токен)
            'vk_user_token': 'vk1.a.2Xtue-gz7QJxLXB6D5UGwKoPRzKSikXtnMSZ-jzWt6AvXLyTLelDmvAhf4tIpcC8xzJBtnhZBbjKPOeh7MQoU1Tb6XqlAQRG2QKuRUziuDmSZ_udQwusY3Elyn9YhbRjX_w6SRtJzIKGGjmdAcQx8J-IUKrluzlw6TJhMyDTU-jSZXWtPCh-yYyTO8KpE8T1',
            
            # Токен группы (Fallout coin)
            'vk_group_token': 'vk1.a.gw_xaDxcf_1hSZoVlt__iSEjsvwtHs-Bo_Q-8dAyWJ_d8WxwQSvuoNH0bIACX1BmJO_zWP1Mts7prFErFTrpD2KKKbxnku61YrAyeLlzoavzjWiR891KvGdjbn2kpA91eN6yfco0azsOvcZBrQdK_k06dIaXpW_ZZ5PgeF4yK-04grYCDQWnoGuo3Zf8PZ67EOdSKx-j6IvS463QRyk9xw',
            
            # Настройки API
            'api_settings': {
                'timeout': 15,
                'max_retries': 3,
                'retry_delay': 2,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        # Bot Configuration
        self.BOT_CONFIG = {
            'name': 'Sketal Bot - SuperGrok AI v1.3',
            'version': '2.0.0',
            'debug': True,
            'log_level': 'INFO',
            
            # Настройки сообщений
            'message_settings': {
                'max_length': 4096,
                'auto_split': True,
                'default_random_id': True,
                'auto_reply': True
            },
            
            # Настройки бесед
            'conversation_settings': {
                'auto_join': True,
                'auto_reply': True,
                'greeting_message': '🤖 Привет! Я Sketal Bot с поддержкой SuperGrok AI v1.3!',
                'help_message': '📱 Доступные команды:\n/help - Справка\n/status - Статус\n/info - Информация'
            },
            
            # Настройки групп
            'group_settings': {
                'auto_moderation': True,
                'spam_protection': True,
                'welcome_message': True,
                'auto_pin': False
            },
            
            # Настройки плагинов
            'plugin_settings': {
                'auto_load': True,
                'reload_on_change': True,
                'plugin_timeout': 30,
                'max_plugins': 50
            }
        }
        
        # Security Configuration
        self.SECURITY_CONFIG = {
            'admin_ids': [],  # ID администраторов
            'moderator_ids': [],  # ID модераторов
            'blocked_words': [],  # Заблокированные слова
            'rate_limit': {
                'messages_per_minute': 20,
                'commands_per_minute': 10
            }
        }
    
    def get_vk_config(self) -> Dict[str, Any]:
        """Получение конфигурации VK"""
        return self.VK_CONFIG.copy()
    
    def get_bot_config(self) -> Dict[str, Any]:
        """Получение конфигурации бота"""
        return self.BOT_CONFIG.copy()
    
    def get_security_config(self) -> Dict[str, Any]:
        """Получение конфигурации безопасности"""
        return self.SECURITY_CONFIG.copy()
    
    def get_token_by_type(self, token_type: str) -> str:
        """Получение токена по типу"""
        token_map = {
            'user': self.VK_CONFIG['vk_user_token'],
            'group': self.VK_CONFIG['vk_group_token']
        }
        return token_map.get(token_type)
    
    def check_tokens_availability(self) -> Dict[str, bool]:
        """Проверка доступности токенов"""
        return {
            'user_token': bool(self.VK_CONFIG['vk_user_token']),
            'group_token': bool(self.VK_CONFIG['vk_group_token'])
        }

# Глобальный экземпляр конфигурации
config = BotConfig()

# Функции для удобного доступа
def get_vk_config() -> Dict[str, Any]:
    """Получение конфигурации VK"""
    return config.get_vk_config()

def get_bot_config() -> Dict[str, Any]:
    """Получение конфигурации бота"""
    return config.get_bot_config()

def get_security_config() -> Dict[str, Any]:
    """Получение конфигурации безопасности"""
    return config.get_security_config()

def get_token_by_type(token_type: str) -> str:
    """Получение токена по типу"""
    return config.get_token_by_type(token_type)

def check_tokens_availability() -> Dict[str, bool]:
    """Проверка доступности токенов"""
    return config.check_tokens_availability()
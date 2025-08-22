#!/usr/bin/env python3
"""
Sketal Bot Settings - SuperGrok AI v1.3
Настройки для работы бота
"""

# Основные настройки
DEBUG = True
LOG_LEVEL = 'INFO'

# Настройки плагинов
PLUGINS = {
    'auto_load': True,
    'reload_on_change': True,
    'plugin_timeout': 30,
    'max_plugins': 50
}

# Настройки VK
VK_SETTINGS = {
    'api_version': '5.199',
    'long_poll_timeout': 25,
    'max_retries': 3
}

# Настройки безопасности
SECURITY = {
    'admin_ids': [],
    'moderator_ids': [],
    'blocked_words': [],
    'rate_limit': {
        'messages_per_minute': 20,
        'commands_per_minute': 10
    }
}

# Настройки логирования
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'sketal_bot.log'
}

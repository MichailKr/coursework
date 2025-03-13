"""
Happy Farm Game Package
Version: 1.0.0
"""

# Константы игры
GAME_TITLE = "Happy Farm"
GAME_VERSION = "1.0.0"

# Размеры окна по умолчанию
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600

# Настройки игрока
PLAYER_SPEED = 200
PLAYER_SIZE = (32, 32)

# Настройки карты
TILE_SIZE = 32
MAP_LAYERS = {
    'ground': 0,
    'buildings': 1,
    'objects': 2,
    'overlay': 3
}

# Настройки игры по умолчанию
DEFAULT_SETTINGS = {
    'sound_volume': 0.7,
    'music_volume': 0.5,
    'fullscreen': False,
    'fps_limit': 60
}

# Пути к ресурсам
RESOURCE_PATHS = {
    'maps': 'maps',
    'sprites': 'sprites',
    'sounds': 'sounds',
    'music': 'music',
    'fonts': 'fonts'
}

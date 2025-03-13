import pygame

# Инициализация pygame перед получением информации о дисплее
pygame.init()

# Константы для цветов
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Базовое разрешение для оконного режима
DEFAULT_WINDOW_SIZE = (800, 600)

# Получаем размер экрана
screen_info = pygame.display.Info()
FULLSCREEN_SIZE = (screen_info.current_w, screen_info.current_h)

# Настройки экрана
WINDOW_SIZE = {
    'windowed': DEFAULT_WINDOW_SIZE,
    'fullscreen': FULLSCREEN_SIZE
}

# Настройки по умолчанию
settings = {
    'window_mode': 'windowed',  # 'windowed', 'borderless', 'fullscreen'
    'music_volume': 0.7,
    'sound_volume': 0.7,
    'master_volume': 0.7
}
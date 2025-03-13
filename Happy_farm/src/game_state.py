from enum import Enum

class GameState(Enum):
    MENU = 0
    SETTINGS = 1
    GAME = 2
    PAUSE = 3  # Добавим еще и состояние паузы

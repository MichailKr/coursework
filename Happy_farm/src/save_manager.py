import pygame
import json
import os

default_save = { # ОБЯЗАТЕЛЬНО!!!!!!! СЮДА ЗАСУНУТЬ КОНСТАНТЫ ИЛИ ОСТАВИТЬ НАСТРОЙКИ ТОЛЬКО ТУТ
    'sound_volume': 0.7,
    'music_volume': 0.5,
    'fullscreen': False,
    'fps_limit': 60,
    'vsync': True,
    'language': 'en',
    'controls': {
        'up': pygame.K_w,
        'down': pygame.K_s,
        'left': pygame.K_a,
        'right': pygame.K_d,
        'interact': pygame.K_e,
        'inventory': pygame.K_i,
        'menu': pygame.K_ESCAPE
    }
}

class SaveManager:
    def __init__(self):
        self.path_to_save = os.path.join('saves', 'save.json')
        self.saved_data = {}

        if os.path.exists(self.path_to_save):
            with open(self.path_to_save, 'r') as save:
                self.saved_data = json.load(save)
        else:
            self.saved_data = default_save
            self.create()

    def create(self):
        with open(self.path_to_save, 'w') as save:
            json.dump(self.saved_data, save, indent = 4)

    def update(self, key, value):
        if os.path.exists(self.path_to_save):
            with open(self.path_to_save, 'r') as save:
                self.saved_data = json.load(save)

            self.saved_data[key] = value
            with open(self.path_to_save, 'w') as save:
                json.dump(self.saved_data, save, indent = 4)
    
    def get_one(self, key):
        if os.path.exists(self.path_to_save):
            return self.saved_data[key]
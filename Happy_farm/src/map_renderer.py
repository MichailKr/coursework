import pygame
from src.tilemap import TiledMap


class MapRenderer:
    def __init__(self):
        self.tilemap = None

    def load_map(self, map_path):
        """Загрузка карты"""
        try:
            self.tilemap = TiledMap(map_path)
            return True
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            return False

    def draw_map(self, screen, camera):
        """Отрисовка карты с учетом камеры"""
        if self.tilemap:
            screen.fill((0, 0, 0))  # Очистка экрана
            self.tilemap.draw(screen, camera)

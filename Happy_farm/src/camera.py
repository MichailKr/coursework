import pygame
from pygame.math import Vector2

class Camera:
    def __init__(self, width, height):
        """
        Инициализация камеры
        Args:
            width (int): Ширина видимой области (экрана)
            height (int): Высота видимой области (экрана)
        """
        self.width = width
        self.height = height
        self.offset = Vector2(0, 0)
        self.map_width = 0
        self.map_height = 0
        print("Камера инициализирована")

    def set_map_size(self, width, height):
        """Установка размеров карты для ограничения движения камеры"""
        self.map_width = width
        self.map_height = height
        print(f"Установлены размеры карты для камеры: {width}x{height}")

    def apply(self, entity):
        """
        Применяет смещение камеры к позиции объекта
        Args:
            entity: Объект с атрибутом rect
        Returns:
            pygame.Rect: Новый прямоугольник с учетом смещения камеры
        """
        return pygame.Rect(
            entity.rect.x - int(self.offset.x),
            entity.rect.y - int(self.offset.y),
            entity.rect.width,
            entity.rect.height
        )

    def apply_rect(self, rect):
        """Применяет смещение камеры к прямоугольнику"""
        return pygame.Rect(
            rect.x - int(self.offset.x),
            rect.y - int(self.offset.y),
            rect.width,
            rect.height
        )

    def apply_point(self, x, y):
        """Применяет смещение камеры к точке"""
        return (x - int(self.offset.x), y - int(self.offset.y))

    def update(self, target):
        """
        Обновляет позицию камеры, чтобы следовать за целью
        Args:
            target: Объект, за которым следует камера (обычно игрок)
        """
        # Вычисляем желаемое смещение камеры
        self.offset.x = target.rect.centerx - self.width // 2
        self.offset.y = target.rect.centery - self.height // 2

        # Ограничиваем смещение камеры границами карты
        self.offset.x = max(0, min(self.offset.x, self.map_width - self.width))
        self.offset.y = max(0, min(self.offset.y, self.map_height - self.height))

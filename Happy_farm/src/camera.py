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
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

        # Границы карты (установите их позже)
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
        return pygame.Rect(entity.rect.x - self.camera.x, entity.rect.y - self.camera.y,
                           entity.rect.width, entity.rect.height)

    def apply_rect(self, rect):
        """
        Применяет смещение камеры к произвольному прямоугольнику

        Args:
            rect (pygame.Rect): Прямоугольник

        Returns:
            pygame.Rect: Новый прямоугольник с учетом смещения камеры
        """
        return pygame.Rect(rect.x - self.camera.x, rect.y - self.camera.y,
                           rect.width, rect.height)

    def apply_point(self, x, y):
        """
        Применяет смещение камеры к точке

        Args:
            x (int): Координата X
            y (int): Координата Y

        Returns:
            tuple: Новые координаты с учетом смещения камеры
        """
        return x - self.camera.x, y - self.camera.y

    def update(self, target):
        """
        Обновляет позицию камеры, чтобы следовать за целью

        Args:
            target: Объект, за которым следует камера (обычно игрок)
        """
        # Центрируем камеру на игроке
        x = target.rect.centerx - self.width // 2
        y = target.rect.centery - self.height // 2

        # Ограничиваем положение камеры границами карты
        if self.map_width > 0 and self.map_height > 0:
            x = max(0, min(x, self.map_width - self.width))
            y = max(0, min(y, self.map_height - self.height))

        # Устанавливаем позицию камеры
        self.camera.x = x
        self.camera.y = y
        # print(f"Камера обновлена: {self.camera.x}, {self.camera.y}")

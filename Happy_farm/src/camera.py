# camera.py
import pygame


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = 0
        self.map_height = 0
        self.offset = pygame.math.Vector2(0, 0)  # Смещение камеры относительно верхнего левого угла карты

        self.zoom = 1.0  # <-- НОВЫЙ АТРИБУТ: Уровень масштабирования (1.0 = без масштабирования)
        # Если вы хотите, чтобы камера изначально была "ближе", установите zoom > 1.0.
        # Например, self.zoom = 1.5

        print("Камера инициализирована")

    def set_map_size(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        print(f"Установлены размеры карты для камеры: {self.map_width}x{self.map_height}")

    def update(self, target):
        """Обновляет позицию камеры, центрируя её на цели."""
        # Центр камеры должен быть равен центру цели
        center_x = target.rect.centerx * self.zoom
        center_y = target.rect.centery * self.zoom

        # Вычисляем смещение так, чтобы центр камеры был на центре цели
        # offset_x = (center_x - self.width / 2)
        # offset_y = (center_y - self.height / 2)
        # self.offset.x = offset_x
        # self.offset.y = offset_y

        # Расчет позиции камеры так, чтобы цель была по центру экрана
        # Сначала найдем желаемую верхнюю левую точку камеры
        self.camera.centerx = int(target.rect.centerx * self.zoom)
        self.camera.centery = int(target.rect.centery * self.zoom)

        # Ограничиваем камеру границами карты
        self.camera.left = max(0, self.camera.left)
        self.camera.top = max(0, self.camera.top)
        self.camera.right = min(self.map_width * self.zoom, self.camera.right)
        self.camera.bottom = min(self.map_height * self.zoom, self.camera.bottom)

        # Рассчитываем смещение на основе верхней левой точки камеры
        self.offset.x = self.camera.left
        self.offset.y = self.camera.top

    def apply(self, entity):
        """Применяет смещение камеры к позиции сущности."""
        # Для объектов, которые отрисовываются (спрайты), мы масштабируем их rect
        # и затем применяем смещение камеры.
        # Если сущность не имеет image или rect (как в случае с tiled_map),
        # то ее нужно обрабатывать по-другому.

        # Масштабируем позицию сущности
        scaled_x = int(entity.rect.x * self.zoom)
        scaled_y = int(entity.rect.y * self.zoom)

        # Возвращаем новую позицию относительно камеры
        return pygame.Rect(scaled_x - int(self.offset.x),
                           scaled_y - int(self.offset.y),
                           int(entity.rect.width * self.zoom),
                           int(entity.rect.height * self.zoom))

    def get_offset(self):
        """Возвращает текущее смещение камеры."""
        return self.offset

    def set_zoom(self, new_zoom):  # <-- НОВЫЙ МЕТОД ДЛЯ УСТАНОВКИ МАСШТАБА
        self.zoom = new_zoom
        # После изменения масштаба, возможно, потребуется пересчитать положение камеры
        # Вызов update(self.player) в GameManager позаботится об этом.
        print(f"Масштаб камеры установлен на: {self.zoom}")
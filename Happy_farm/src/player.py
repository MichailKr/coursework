import pygame
import pytmx
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, game_manager, x, y, speed=100):
        super().__init__()
        self.game = game_manager

        # Пути к спрайтам
        self.sprite_path = "sprites/player/sprites"

        # Загрузка и организация спрайтов
        self.animations = self.load_animations()

        # Начальное положение и скорость
        self.x = float(x)
        self.y = float(y)
        self.speed = speed

        # Анимационные переменные
        self.direction = "down"  # Начальное направление
        self.moving = False
        self.current_frame = 0
        self.animation_speed = 8  # Кадров в секунду
        self.animation_timer = 0

        # Установка начального изображения и прямоугольника
        self.image = self.animations[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Создаем отдельный прямоугольник для коллизий
        self.collision_rect = pygame.Rect(0, 0, 16, 16)  # Размер коллизии (16x16)
        self.update_collision_rect()  # Обновляем позицию коллизии

        print(f"Игрок создан на позиции ({x}, {y}) со скоростью {speed}")

    def load_animations(self):
        """Загрузка всех анимаций игрока"""
        animations = {
            "down": [],
            "left": [],
            "right": [],
            "up": [],
        }

        # Проверяем наличие папки со спрайтами
        if not os.path.exists(self.sprite_path):
            print(f"Ошибка: Путь {self.sprite_path} не существует.")
            # Создаем заглушку - зеленый квадрат
            dummy = pygame.Surface((16, 16))
            dummy.fill((0, 255, 0))
            for direction in animations:
                animations[direction] = [dummy]
            return animations

        try:
            # Сопоставляем индексы с направлениями
            directions_map = {
                "down": [0, 1, 2, 3],  # первая строка (индексы 0-3)
                "left": [8, 9, 10, 11],  # вторая строка (индексы 4-7)
                "right": [12, 13, 14, 15],  # третья строка (индексы 8-11)
                "up": [4, 5, 6, 7],  # четвертая строка (индексы 12-15)
            }

            # Загружаем все спрайты
            sprites = []
            for i in range(16):  # 16 спрайтов (4x4)
                img_path = os.path.join(self.sprite_path, f"sprite_{i}.png")
                if os.path.exists(img_path):
                    sprite = pygame.image.load(img_path).convert_alpha()
                    # Масштабируем спрайт, если нужно
                    sprite = pygame.transform.scale(sprite, (70, 92))
                    sprites.append(sprite)
                else:
                    print(f"Предупреждение: Файл {img_path} не найден.")
                    dummy = pygame.Surface((16, 16))
                    dummy.fill((255, 0, 255))  # Фиолетовый для обозначения отсутствия
                    sprites.append(dummy)

            # Распределяем спрайты по анимациям
            for direction, indices in directions_map.items():
                for idx in indices:
                    if idx < len(sprites):
                        animations[direction].append(sprites[idx])

        except Exception as e:
            print(f"Ошибка при загрузке спрайтов: {e}")
            # Создаем заглушку в случае ошибки
            dummy = pygame.Surface((32, 32))
            dummy.fill((0, 255, 0))
            for direction in animations:
                animations[direction] = [dummy]

        return animations

    def update(self, dt):
        """Обновление игрока"""
        keys = pygame.key.get_pressed()

        # Сохраняем предыдущее положение для проверки коллизий
        prev_x = self.x
        prev_y = self.y

        # Сбрасываем флаг движения
        was_moving = self.moving
        self.moving = False

        # Рассчитываем новое положение
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed * dt
            self.direction = "left"
            self.moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed * dt
            self.direction = "right"
            self.moving = True

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed * dt
            self.direction = "up"
            self.moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed * dt
            self.direction = "down"
            self.moving = True

        # Обновляем позиции отдельно, чтобы проверить коллизии
        # Обновляем X
        self.x += dx
        self.rect.x = int(self.x)
        self.update_collision_rect()  # Обновляем позицию прямоугольника коллизии
        if self.check_collision():
            self.x = prev_x
            self.rect.x = int(prev_x)

        # Обновляем Y
        self.y += dy
        self.rect.y = int(self.y)
        self.update_collision_rect()  # Обновляем позицию прямоугольника коллизии
        if self.check_collision():
            self.y = prev_y
            self.rect.y = int(prev_y)

        # Ограничение движения игрока границами карты
        if hasattr(self.game, "tmx_data") and self.game.map_loaded:
            map_width = self.game.tmx_data.width * self.game.tmx_data.tilewidth
            map_height = self.game.tmx_data.height * self.game.tmx_data.tileheight
            self.x = max(0, min(self.x, map_width - self.rect.width))
            self.y = max(0, min(self.y, map_height - self.rect.height))
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        # Обновление анимации
        self.update_animation(dt, was_moving)

    def update_collision_rect(self):
        """Обновляет позицию прямоугольника коллизии."""
        self.collision_rect.center = self.rect.center

    def update_animation(self, dt, was_moving):
        """Обновление анимации игрока"""
        # Если начали или прекратили движение, сбрасываем кадр и таймер
        if was_moving != self.moving:
            self.current_frame = 0
            self.animation_timer = 0

        if self.moving:
            # Обновляем таймер анимации
            self.animation_timer += dt
            # Если прошло достаточно времени, переходим к следующему кадру
            if self.animation_timer >= 1.0 / self.animation_speed:
                self.animation_timer = 0
                # Переключаемся на следующий кадр
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.direction])
        else:
            # Если не движемся, используем первый кадр
            self.current_frame = 0

        # Обновляем текущее изображение
        self.image = self.animations[self.direction][self.current_frame]

    def check_collision(self):
        """Проверка коллизий игрока с объектами на карте."""
        if not hasattr(self.game, "tmx_data") or not self.game.map_loaded:
            return False

        for layer in self.game.tmx_data.layers:
            if layer.name == "Коллизия лес" and isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0:
                        tile_rect = pygame.Rect(
                            x * self.game.tmx_data.tilewidth,
                            y * self.game.tmx_data.tileheight,
                            self.game.tmx_data.tilewidth,
                            self.game.tmx_data.tileheight,
                        )
                        if self.collision_rect.colliderect(tile_rect):
                            return True
            if layer.name == "Колилзия горок" and isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0:
                        tile_rect = pygame.Rect(
                            x * self.game.tmx_data.tilewidth,
                            y * self.game.tmx_data.tileheight,
                            self.game.tmx_data.tilewidth,
                            self.game.tmx_data.tileheight,
                        )
                        if self.collision_rect.colliderect(tile_rect):
                            return True
            if layer.name == "Коллизия река и Озеро" and isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0:
                        tile_rect = pygame.Rect(
                            x * self.game.tmx_data.tilewidth,
                            y * self.game.tmx_data.tileheight,
                            self.game.tmx_data.tilewidth,
                            self.game.tmx_data.tileheight,
                        )
                        if self.collision_rect.colliderect(tile_rect):
                            return True
            if layer.name == "Дом" and isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0:
                        tile_rect = pygame.Rect(
                            x * self.game.tmx_data.tilewidth,
                            y * self.game.tmx_data.tileheight,
                            self.game.tmx_data.tilewidth,
                            self.game.tmx_data.tileheight,
                        )
                        if self.collision_rect.colliderect(tile_rect):
                            return True
            if layer.name == "Коллизия Мосты" and isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0:
                        tile_rect = pygame.Rect(
                            x * self.game.tmx_data.tilewidth,
                            y * self.game.tmx_data.tileheight,
                            self.game.tmx_data.tilewidth,
                            self.game.tmx_data.tileheight,
                        )
                        if self.collision_rect.colliderect(tile_rect):
                            return True
        return False
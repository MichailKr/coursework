import pygame
import os

class Plant(pygame.sprite.Sprite):
    def __init__(self, game_manager, plant_type, tile_x, tile_y):
        super().__init__()
        self.game = game_manager # Ссылка на GameManager
        self.plant_type = plant_type # Тип растения ('cucumber', 'tomato', 'potato')
        self.tile_x = tile_x     # Координаты тайла, на котором растет растение
        self.tile_y = tile_y

        # Стадии роста и связанные с ними спрайты
        # В будущем это можно вынести в отдельный файл конфигурации
        self.growth_stages_sprites = self.load_growth_sprites(plant_type)
        self.current_stage = 0 # Начальная стадия роста (например, 0 - только что посажено)
        self.max_stage = len(self.growth_stages_sprites) - 1 # Максимальная стадия (урожай готов)

        self.image = self.growth_stages_sprites[self.current_stage]
        # Устанавливаем позицию спрайта растения по центру тайла
        # Нужно будет учесть смещение камеры при отрисовке
        tile_size = self.game.tmx_data.tilewidth # Предполагается доступ к tmx_data через game_manager
        tile_center_x = self.tile_x * tile_size + tile_size // 2
        tile_center_y = self.tile_y * tile_size + tile_size // 2
        self.rect = self.image.get_rect(center=(tile_center_x, tile_center_y))

        # Время, связанное с ростом
        self.growth_timer = 0 # Таймер для перехода к следующей стадии
        self.time_to_next_stage = 10 # Время в секундах до перехода к следующей стадии (для примера)

        self.is_watered = False # Флаг, полито ли растение (для будущей механики полива)
        self.ready_to_harvest = False # Флаг, готово ли к сбору урожая

        print(f"Создано растение: {self.plant_type} на тайле ({self.tile_x}, {self.tile_y})")


    def load_growth_sprites(self, plant_type):
        """Загружает спрайты стадий роста для данного типа растения."""
        sprites = []
        # Путь к спрайтам растений
        plant_sprites_dir = os.path.join("sprites", "plants", plant_type)
        # Предполагаем, что спрайты названы stage_0.png, stage_1.png, ..., stage_4.png
        num_stages = 5 # Количество стадий роста
        if not os.path.exists(plant_sprites_dir):
             print(f"Ошибка: Папка со спрайтами для растения '{plant_type}' не найдена: {plant_sprites_dir}")
             # В случае ошибки загрузки, добавим заглушку для каждой стадии
             dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
             dummy.fill((255, 0, 0, 150)) # Полупрозрачный красный
             return [dummy] * num_stages # Возвращаем список заглушек
        for stage_index in range(num_stages):
            sprite_path = os.path.join(plant_sprites_dir, f"stage_{stage_index}.png")
            if os.path.exists(sprite_path):
                try:
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    # Опционально: масштабирование спрайта под размер тайла
                    # Если тебе нужно масштабировать, раскомментируй и настрой этот блок:
                    if hasattr(self.game, 'tmx_data') and self.game.tmx_data:
                          tile_size = self.game.tmx_data.tilewidth
                          if sprite.get_size() != (tile_size, tile_size):
                              sprite = pygame.transform.scale(sprite, (tile_size, tile_size))
                    sprites.append(sprite)
                except pygame.error as e:
                    print(f"Ошибка загрузки спрайта {sprite_path}: {e}")
                    # Добавляем заглушку в случае ошибки загрузки конкретного файла
                    dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
                    dummy.fill((100, 100, 100, 100)) # Полупрозрачный серый
                    sprites.append(dummy)
            else:
                print(f"Предупреждение: Файл спрайта не найден: {sprite_path}. Добавляется заглушка.")
                # Добавляем заглушку, если файл спрайта отсутствует
                dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
                dummy.fill((100, 100, 100, 100)) # Полупрозрачный серый
                sprites.append(dummy)
        if not sprites:
            print(f"Предупреждение: Не загружено ни одного спрайта для растения типа '{plant_type}'. Возвращается одна заглушка.")
            # Если по какой-то причине список спрайтов пуст, возвращаем хотя бы одну заглушку
            dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
            dummy.fill((255, 0, 0, 100)) # Полупрозрачный красный
            return [dummy]
        # Устанавливаем максимальную стадию на основе количества загруженных спрайтов
        self.max_stage = len(sprites) - 1
        print(f"Для растения '{plant_type}' загружено {len(sprites)} стадий роста. Максимальная стадия: {self.max_stage}")
        return sprites

    def update(self, dt):
        """Обновление состояния растения (рост)."""
        # Логика роста будет здесь
        # Пока простая заглушка: растение растет со временем
        if not self.ready_to_harvest:
            self.growth_timer += dt
            if self.growth_timer >= self.time_to_next_stage:
                self.growth_timer = 0
                self.grow() # Переход к следующей стадии роста

    def grow(self):
        """Переход к следующей стадии роста."""
        if self.current_stage < self.max_stage:
            self.current_stage += 1
            self.image = self.growth_stages_sprites[self.current_stage]
            print(f"Растение {self.plant_type} на ({self.tile_x}, {self.tile_y}) перешло в стадию {self.current_stage}")

            if self.current_stage == self.max_stage:
                self.ready_to_harvest = True
                print(f"Растение {self.plant_type} на ({self.tile_x}, {self.tile_y}) готово к сбору урожая!")


    def water(self):
        """Поливает растение."""
        # Пока заглушка, в будущем может влиять на скорость роста
        self.is_watered = True
        print(f"Растение {self.plant_type} на ({self.tile_x}, {self.tile_y}) полито.")

    def harvest(self):
        """Собирает урожай с растения."""
        if self.ready_to_harvest:
            print(f"Урожай с растения {self.plant_type} на ({self.tile_x}, {self.tile_y}) собран.")
            # TODO: Добавить логику получения предметов урожая игроком
            # TODO: Удалить объект растения с карты
            return True # Урожай собран успешно
        else:
            print(f"Растение {self.plant_type} на ({self.tile_x}, {tile_y}) еще не готово к сбору урожая.")
            return False # Не готово к сбору

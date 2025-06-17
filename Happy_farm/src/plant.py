import pygame
import os
# Импортируем классы урожая, чтобы Plant мог их создавать
# Убедитесь, что пути к файлам правильные: src.item, если Item находится в src/item.py
from src.item import Tomato, Wheat


class Plant(pygame.sprite.Sprite):
    def __init__(self, game_manager, plant_type, tile_x, tile_y):
        super().__init__()
        self.game = game_manager  # Ссылка на GameManager
        self.plant_type = plant_type  # Тип растения ('cucumber', 'tomato', 'potato', 'wheat')
        self.tile_x = tile_x  # Координаты тайла, на котором растет растение
        self.tile_y = tile_y

        # Определяем класс предмета урожая в зависимости от типа растения
        if self.plant_type == "tomato":
            self.harvest_item_class = Tomato
            # Здесь можно определить количество стадий для каждого растения, если оно разное
            # Например, self.known_num_stages = 4
        elif self.plant_type == "wheat":
            self.harvest_item_class = Wheat
            # self.known_num_stages = 3
        else:
            self.harvest_item_class = None
            print(f"Неизвестный тип растения: {plant_type}. Класс урожая не определен.")

        self.growth_stages_sprites = self.load_growth_sprites(plant_type)
        self.current_stage = 0
        # Максимальная стадия теперь определяется количеством загруженных спрайтов
        self.max_stage = len(self.growth_stages_sprites) - 1

        self.image = self.growth_stages_sprites[self.current_stage]

        tile_size = self.game.tmx_data.tilewidth  # Предполагается доступ к tmx_data через game_manager
        tile_center_x = self.tile_x * tile_size + tile_size // 2
        tile_center_y = self.tile_y * tile_size + tile_size // 2
        self.rect = self.image.get_rect(center=(tile_center_x, tile_center_y))

        self.growth_timer = 0
        self.time_to_next_stage = 10  # Время в секундах до перехода к следующей стадии (для примера)
        self.is_watered = False
        self.ready_to_harvest = False

        print(f"Создано растение: {self.plant_type} на тайле ({self.tile_x}, {self.tile_y})")

    def load_growth_sprites(self, plant_type):
        """Загружает спрайты стадий роста для данного типа растения."""
        sprites = []
        plant_sprites_dir = os.path.join("sprites", "plants", plant_type)

        # Вы можете сделать num_stages динамическим или передавать его в Plant.__init__
        # Пока возьмем фиксированное число для примера или попробуем загрузить, пока есть файлы
        # Или, если вы хотите, чтобы Tomato всегда имел 4 стадии, а Wheat 3, то можно это задать тут.
        # Например:
        if plant_type == "tomato":
            num_expected_stages = 4  # Если у вас stage_0.png, stage_1.png, stage_2.png, stage_3.png
        elif plant_type == "wheat":
            num_expected_stages = 4  # Если у вас stage_0.png, stage_1.png, stage_2.png
        else:
            num_expected_stages = 5  # По умолчанию, если тип не tomato или wheat

        if not os.path.exists(plant_sprites_dir):
            print(f"Ошибка: Папка со спрайтами для растения '{plant_type}' не найдена: {plant_sprites_dir}")
            dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
            dummy.fill((255, 0, 0, 150))
            return [dummy] * num_expected_stages

        # Загружаем спрайты до num_expected_stages
        for stage_index in range(num_expected_stages):
            sprite_path = os.path.join(plant_sprites_dir, f"stage_{stage_index}.png")
            if os.path.exists(sprite_path):
                try:
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    if hasattr(self.game, 'tmx_data') and self.game.tmx_data:
                        tile_size = self.game.tmx_data.tilewidth
                        if sprite.get_size() != (tile_size, tile_size):
                            sprite = pygame.transform.scale(sprite, (tile_size, tile_size))
                    sprites.append(sprite)
                except pygame.error as e:
                    print(f"Ошибка загрузки спрайта {sprite_path}: {e}")
                    dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
                    dummy.fill((100, 100, 100, 100))
                    sprites.append(dummy)
            else:
                print(f"Предупреждение: Файл спрайта не найден: {sprite_path}. Добавляется заглушка.")
                dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
                dummy.fill((100, 100, 100, 100))
                sprites.append(dummy)

        if not sprites:
            print(
                f"Предупреждение: Не загружено ни одного спрайта для растения типа '{plant_type}'. Возвращается одна заглушка.")
            dummy = pygame.Surface((32, 32), pygame.SRCALPHA)
            dummy.fill((255, 0, 0, 100))
            return [dummy]

        # Устанавливаем max_stage на основе фактически загруженных спрайтов
        # Важно: это переопределяет initial self.max_stage, если оно было установлено ранее
        # self.max_stage = len(sprites) - 1 # Это будет установлено в __init__ после возврата
        print(f"Для растения '{plant_type}' загружено {len(sprites)} стадий роста.")
        return sprites

    def update(self, dt):
        """Обновление состояния растения (рост)."""
        if not self.ready_to_harvest:
            self.growth_timer += dt
            if self.growth_timer >= self.time_to_next_stage:
                self.growth_timer = 0
                self.grow()

    def grow(self):
        """Переход к следующей стадии роста."""
        if self.current_stage < self.max_stage:
            self.current_stage += 1
            # Убедитесь, что индекс находится в пределах списка спрайтов
            if self.current_stage < len(self.growth_stages_sprites):
                self.image = self.growth_stages_sprites[self.current_stage]
            else:  # Если вдруг вышли за пределы, используем последний доступный спрайт
                self.image = self.growth_stages_sprites[self.max_stage]

            print(f"Растение {self.plant_type} на ({self.tile_x}, {self.tile_y}) перешло в стадию {self.current_stage}")

            if self.current_stage == self.max_stage:
                self.ready_to_harvest = True
                print(f"Растение {self.plant_type} на ({self.tile_x}, {self.tile_y}) готово к сбору урожая!")

    def water(self):
        """Поливает растение."""
        self.is_watered = True
        print(f"Растение {self.plant_type} на ({self.tile_x}, {self.tile_y}) полито.")

    def harvest(self):
        """Собирает урожай с растения.
        Возвращает созданный объект урожая (например, Tomato, Wheat) или None.
        """
        if self.ready_to_harvest:
            print(f"Урожай с растения {self.plant_type} на ({self.tile_x}, {self.tile_y}) собран.")

            if self.harvest_item_class:
                # Определяем размер спрайта для предмета в инвентаре.
                # Можно использовать фиксированный размер, или относительный от размера тайла.
                # Предположим, что предметы в инвентаре должны быть меньше, чем тайлы на карте.
                # Если у вас есть InventoryManager с заданным размером слотов, можно брать оттуда.
                # Например, 32x32 пикселя для иконки предмета.

                # Если у вас есть доступ к game.TILE_SIZE:
                if hasattr(self.game, 'TILE_SIZE'):
                    item_sprite_size = (self.game.TILE_SIZE // 2, self.game.TILE_SIZE // 2)
                else:
                    item_sprite_size = (32, 32)  # Размер по умолчанию, если TILE_SIZE недоступен

                # Создаем экземпляр класса урожая, передавая ему размер для его спрайта
                return self.harvest_item_class(quantity=1, scale_to_size=item_sprite_size)
            else:
                print(f"Для растения {self.plant_type} не определен класс урожая, или он недоступен.")
                return None
        else:
            print(f"Растение {self.plant_type} на ({self.tile_x}, {self.tile_y}) еще не готово к сбору урожая.")
            return None
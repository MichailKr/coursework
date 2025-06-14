import pygame
import pytmx
import os
from src.item import Tool, Item, Seed # Убедитесь, что импорт Tool и Item корректен
from src.game_state import GameState # Импортируем GameState, если он используется в Player
from src.plant import Plant

class Player(pygame.sprite.Sprite):
    def __init__(self, game_manager, x, y, speed=100):
        super().__init__()
        self.coins = 1000
        self.hotbar_slots = [None] * 5
        self.inventory = [[] for _ in range(3)]
        self.game = game_manager # Ссылка на GameManager

        # Пути к спрайтам
        self.sprite_path = "sprites/player/sprites" # Путь к основным спрайтам движения

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
        # Уменьшаем скорость анимации движения (например, до 6 FPS). Настройте по вкусу.
        self.animation_speed = 6
        self.animation_timer = 0

        # Переменные для анимации использования инструмента (взмаха)
        self.is_using_tool = False
        self.tool_use_animation_timer = 0
        # Уменьшаем скорость анимации взмаха (например, до 8 FPS). Настройте по вкусу.
        self.tool_use_animation_speed = 8
        self.tool_use_current_frame = 0
        self.current_tool_animation_type = None # Тип текущей анимации инструмента (например, 'hoe_swing')

        # Установка начального изображения и прямоугольника
        if self.direction in self.animations and self.animations[self.direction]:
             self.image = self.animations[self.direction][0]
        else:
             print(f"Предупреждение: Начальная анимация для направления '{self.direction}' пуста или не существует. Используется заглушка.")
             dummy = pygame.Surface((16, 16))
             dummy.fill((0, 255, 0))
             self.image = dummy

        self.rect = self.image.get_rect(topleft=(x, y))

        # Создаем отдельный прямоугольник для коллизий
        self.collision_rect = pygame.Rect(0, 0, 10, 10) # Размер коллизии (настройте по необходимости)
        self.update_collision_rect()  # Обновляем позицию коллизии

        print(f"Игрок создан на позиции ({x}, {y}) со скоростью {speed}")


    def add_coins(self, amount):
        self.coins += amount
    

    def remove_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
        else:
            print("Недостаточно монет!")


    def draw_coins(self, screen):
        font = self.game.fonts['small']
        text = font.render(f"Coins: {self.coins}", True, (255, 255, 255))
        screen.blit(text, (5, 35,5,5))

    def add_item_to_inventory(self, item, slot_index=None):
        """Добавляет предмет в инвентарь или хотбар"""
        if slot_index is not None and 0 <= slot_index < len(self.hotbar_slots):
            # Добавляем в хотбар
            self.hotbar_slots[slot_index] = item
            return True
        elif self._find_empty_slot():
            # Добавляем в основной инвентарь
            row, col = self._find_empty_slot()
            self.inventory[row][col] = item
            return True
        else:
            print("Инвентарь полон!")
            return False

    def _find_empty_slot(self):
        """Ищет первый пустой слот в инвентаре"""
        for row in range(len(self.inventory)):
            for col in range(len(self.inventory[row])):
                if self.inventory[row][col] is None:
                    return row, col
        return None

    def load_animations(self):
        """Загрузка всех анимаций игрока"""
        animations = {
            "down": [],
            "left": [],
            "right": [],
            "up": [],
            "hoe_swing": [], # Анимация для взмаха мотыгой
            # Добавьте другие анимации инструментов здесь
        }

        # --- Загрузка основных анимаций движения ---
        self.sprite_path = "sprites/player/sprites"
        if not os.path.exists(self.sprite_path):
            print(f"Ошибка: Путь {self.sprite_path} для основных анимаций не существует.")
            dummy = pygame.Surface((16, 16))
            dummy.fill((0, 255, 0))
            for direction in ["down", "left", "right", "up"]:
                animations[direction] = [dummy]
        else:
            try:
                # Здесь должна быть ваша логика загрузки спрайтов движения
                # Пример для спрайт-листа 4x4 (16 спрайтов)
                directions_map = {
                    "down": [0, 1, 2, 3],
                    "left": [8, 9, 10, 11],
                    "right": [12, 13, 14, 15],
                    "up": [4, 5, 6, 7],
                }
                sprites = []
                for i in range(16): # Измените диапазон, если у вас другое количество спрайтов
                    img_path = os.path.join(self.sprite_path, f"sprite_{i}.png")
                    if os.path.exists(img_path):
                        sprite = pygame.image.load(img_path).convert_alpha()
                        # sprite = pygame.transform.scale(sprite, (70, 92)) # Пример масштабирования
                        sprites.append(sprite)
                    else:
                        print(f"Предупреждение: Файл {img_path} не найден для основной анимации.")
                        dummy = pygame.Surface((16, 16))
                        dummy.fill((255, 0, 255))
                        sprites.append(dummy)

                for direction, indices in directions_map.items():
                    for idx in indices:
                        if idx < len(sprites):
                            animations[direction].append(sprites[idx])
                        else:
                             print(f"Предупреждение: Индекс спрайта {idx} вне диапазона для направления {direction}.")
            except Exception as e:
                print(f"Ошибка при загрузке основных спрайтов: {e}")
                dummy = pygame.Surface((32, 32))
                dummy.fill((0, 255, 0))
                for direction in ["down", "left", "right", "up"]:
                    animations[direction] = [dummy]

        # --- Загрузка анимации взмаха мотыгой ---
        hoe_swing_sprites_dir = os.path.join("sprites", "player", "sprites_tools", "hoe_swing")
        hoe_swing_files = ["frame_0.png", "frame_1.png"] # Убедитесь, что имена файлов соответствуют

        if os.path.exists(hoe_swing_sprites_dir):
            try:
                loaded_frames = 0
                for filename in hoe_swing_files:
                    img_path = os.path.join(hoe_swing_sprites_dir, filename)
                    if os.path.exists(img_path):
                        sprite = pygame.image.load(img_path).convert_alpha()
                        # Масштабируйте, если нужно, до размера игрока
                        # sprite = pygame.transform.scale(sprite, (70, 92))
                        animations["hoe_swing"].append(sprite)
                        loaded_frames += 1
                    else:
                        print(f"Предупреждение: Файл {img_path} не найден для анимации взмаха мотыгой. Проверьте имя файла.")

                if loaded_frames == 0:
                    print(f"Предупреждение: Не загружено ни одного кадра для анимации взмаха мотыгой из {hoe_swing_sprites_dir}. Проверьте имена файлов ({', '.join(hoe_swing_files)}).")
                    if animations["down"]:
                         animations["hoe_swing"] = [animations["down"][0]]
                    else:
                         dummy = pygame.Surface((32, 32))
                         dummy.fill((255, 0, 255))
                         animations["hoe_swing"] = [dummy]
            except Exception as e:
                print(f"Ошибка при загрузке анимации взмаха мотыгой из {hoe_swing_sprites_dir}: {e}")
                if animations["down"]:
                     animations["hoe_swing"] = [animations["down"][0]]
                else:
                     dummy = pygame.Surface((32, 32))
                     dummy.fill((255, 0, 255))
                     animations["hoe_swing"] = [dummy]
        else:
            print(f"Предупреждение: Папка анимации взмаха мотыгой не найдена: {hoe_swing_sprites_dir}")
            if animations["down"]:
                 animations["hoe_swing"] = [animations["down"][0]]
            else:
                 dummy = pygame.Surface((32, 32))
                 dummy.fill((255, 0, 255))
                 animations["hoe_swing"] = [dummy]

        print(f"Загружено {len(animations['hoe_swing'])} кадров для анимации взмаха мотыгой.")
        return animations

    # --- Добавлен метод handle_input для обработки событий, специфичных для игрока ---
    def handle_input(self, event):
        """Обработка событий ввода, специфичных для игрока (использование предметов)."""
        # Обрабатываем ввод игрока только если игра в состоянии Game, не на паузе
        # и инвентарь НЕ открыт (так как клики мышью идут на инвентарь)
        if self.game.state == GameState.GAME and not self.game.paused and not self.game.inventory_manager.inventory_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    # Получаем выбранный предмет из хотбара через InventoryManager
                    selected_item_index = self.game.inventory_manager.selected_item_index
                    # Проверяем, что индекс корректен
                    if 0 <= selected_item_index < len(self.game.inventory_manager.hotbar_slots):
                        selected_item = self.game.inventory_manager.hotbar_slots[selected_item_index]
                        # --- Проверяем, является ли предмет инструментом (например, мотыгой) ---
                        if selected_item and isinstance(selected_item, Tool): # Используем isinstance(selected_item, Tool)
                             if selected_item.type == 'hoe' and not self.is_using_tool:
                                 self.use_tool() # Вызываем метод использования инструмента
                             # TODO: Добавить проверки для других типов инструментов (топор, лейка и т.д.)
                             # elif selected_item.type == 'axe' and not self.is_using_tool:
                             #     self.use_tool() # Запускаем анимацию топора
                             # elif selected_item.type == 'wateringcan' and not self.is_using_tool:
                             #     self.use_tool() # Запускаем анимацию лейки
                             # ...
                        # --- Проверяем, является ли предмет семенем ---
                        elif selected_item and isinstance(selected_item, Seed):
                            # Получаем координаты тайла перед игроком
                            target_tile_x, target_tile_y = self.get_tile_in_front()
                            # Проверяем, можно ли сажать на этом тайле, используя метод GameManager
                            if self.game and hasattr(self.game, 'is_tile_plantable') and (
                                    target_tile_x != -1 or target_tile_y != -1):
                                if self.game.is_tile_plantable(target_tile_x, target_tile_y):
                                    print(
                                        f"Попытка посадить семя {selected_item.name} на тайл ({target_tile_x}, {target_tile_y}).")
                                    # !!! ВОТ ТУТ НУЖНО ДОБАВИТЬ СОЗДАНИЕ ОБЪЕКТА PLANT И ДОБАВЛЕНИЕ В ГРУППЫ !!!
                                    if hasattr(selected_item, 'plant_type'):  # Убедимся, что у семени есть тип растения
                                        new_plant = Plant(self.game, selected_item.plant_type, target_tile_x,
                                                          target_tile_y)
                                        # Добавляем растение в группы спрайтов в GameManager
                                        if hasattr(self.game, 'all_sprites') and hasattr(self.game, 'plants'):
                                            self.game.all_sprites.add(new_plant)
                                            self.game.plants.add(new_plant)
                                            print(
                                                f"Объект растения {new_plant.plant_type} создан и добавлен в группы спрайтов.")
                                            # Удаляем одно семя из инвентаря после использования
                                            success = self.game.inventory_manager.remove_item_from_inventory(
                                                selected_item, quantity=1)
                                            if success:
                                                print(f"Одно {selected_item.name} удалено из инвентаря.")
                                            else:
                                                print(
                                                    f"Ошибка: Не удалось удалить {selected_item.name} из инвентаря после посадки.")
                                            # !!! Обновляем состояние тайла в GameManager !!!
                                            # Помечаем тайл как занятый растением, сохраняя ссылку на объект
                                            self.game.update_tile_state(target_tile_x, target_tile_y,
                                                                        has_plant=new_plant)
                                        else:
                                            print(
                                                "Ошибка: Группы спрайтов all_sprites или plants не найдены в GameManager.")
                                    else:
                                        print(
                                            f"Ошибка: У выбранного семени {selected_item.name} нет атрибута 'plant_type'.")
                                else:
                                    print("На этой земле нельзя сажать.")
                            else:
                                print("Неверные координаты тайла или метод is_tile_plantable не найден в GameManager.")
            # Обработка движения (клавиши get_pressed() обрабатываются в update)
            pass

    def update(self, dt):
        """Обновление игрока (движение и анимация)"""

        # --- Обработка движения (только если игрок не использует инструмент и инвентарь закрыт) ---
        # Логика движения обрабатывается здесь с помощью pygame.key.get_pressed()
        if not self.is_using_tool and not self.game.inventory_manager.inventory_open:

            keys = pygame.key.get_pressed()
            prev_x = self.x
            prev_y = self.y
            was_moving = self.moving # Сохраняем предыдущее состояние движения

            dx = 0
            dy = 0

            if keys[self.game.settings['controls']['left']]: # Используем настройки клавиш из GameManager
                dx = -self.speed * dt
            elif keys[self.game.settings['controls']['right']]:
                dx = self.speed * dt

            if keys[self.game.settings['controls']['up']]:
                dy = -self.speed * dt
            elif keys[self.game.settings['controls']['down']]:
                dy = self.speed * dt

            self.moving = (dx != 0 or dy != 0)

            # Определяем направление
            if self.moving:
                if keys[self.game.settings['controls']['up']]:
                    self.direction = "up"
                elif keys[self.game.settings['controls']['down']]:
                    self.direction = "down"
                elif keys[self.game.settings['controls']['left']]:
                    self.direction = "left"
                elif keys[self.game.settings['controls']['right']]:
                    self.direction = "right"


            # Обновляем позиции и проверяем коллизии
            self.x += dx
            self.rect.x = int(self.x)
            self.update_collision_rect()
            if self.game and hasattr(self.game, 'check_collision'):
                 if self.game.check_collision(self.collision_rect):
                     self.x = prev_x
                     self.rect.x = int(prev_x)
                     self.update_collision_rect()

            self.y += dy
            self.rect.y = int(self.y)
            self.update_collision_rect()
            if self.game and hasattr(self.game, 'check_collision'):
                 if self.game.check_collision(self.collision_rect):
                     self.y = prev_y
                     self.rect.y = int(prev_y)
                     self.update_collision_rect()

            # Ограничение движения игрока границами карты
            if hasattr(self.game, "tmx_data") and self.game.map_loaded:
                map_width = self.game.tmx_data.width * self.game.tmx_data.tilewidth
                map_height = self.game.tmx_data.height * self.game.tmx_data.tileheight
                self.x = max(0.0, min(self.x, float(map_width - self.rect.width)))
                self.y = max(0.0, min(self.y, float(map_height - self.rect.height)))
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
                self.update_collision_rect()

            # Обновление анимации движения
            self.update_animation(dt, was_moving)

        elif self.is_using_tool: # Если игрок использует инструмент, обновляем только анимацию инструмента
             self.update_tool_use_animation(dt)
        # else: # Если инвентарь открыт или игра на паузе, анимация движения не обновляется
            # was_moving = self.moving # Сохраняем предыдущее состояние движения
            # self.moving = False # Игрок не движется, если инвентарь открыт или пауза
            # self.update_animation(dt, was_moving) # Обновляем анимацию, чтобы перейти в idle

    def update_collision_rect(self):
        """Обновляет позицию прямоугольника коллизии."""
        self.collision_rect.center = (self.rect.center[0], self.rect.center[1]+7)

    def update_animation(self, dt, was_moving):
        """Обновление анимации игрока (движения)"""
        if self.is_using_tool: # Если используется инструмент, не обновляем анимацию движения
            return

        if self.direction not in self.animations or not self.animations[self.direction]:
            print(f"Предупреждение: Анимация для направления '{self.direction}' пуста или не существует. Используется Fallback.")
            if "down" in self.animations and self.animations["down"]:
                 self.image = self.animations["down"][0]
            else:
                 dummy = pygame.Surface((32, 32))
                 dummy.fill((0, 255, 0))
                 self.image = dummy
            return

        if was_moving != self.moving:
            self.current_frame = 0
            self.animation_timer = 0

        if self.moving:
            self.animation_timer += dt
            if self.animation_timer >= 1.0 / self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.direction])
        else:
            self.current_frame = 0 # Используем первый кадр (idle) при остановке

        self.image = self.animations[self.direction][self.current_frame]

    def update_tool_use_animation(self, dt):
        """Обновление анимации использования инструмента и вызов действия в нужный момент."""
        # Проверяем, что текущая анимация инструмента существует и не пуста
        if self.current_tool_animation_type and \
           self.current_tool_animation_type in self.animations and \
           self.animations[self.current_tool_animation_type]:

            self.tool_use_animation_timer += dt

            # Проигрываем анимацию взмаха
            if self.tool_use_animation_timer >= 1.0 / self.tool_use_animation_speed:
                self.tool_use_animation_timer = 0
                prev_frame = self.tool_use_current_frame # Сохраняем предыдущий кадр
                self.tool_use_current_frame += 1

                # Проверяем, закончилась ли анимация
                if self.tool_use_current_frame >= len(self.animations[self.current_tool_animation_type]):
                    self.is_using_tool = False # Сбрасываем флаг использования инструмента
                    self.tool_use_current_frame = 0 # Сбрасываем кадр анимации инструмента
                    self.current_tool_animation_type = None # Сбрасываем тип анимации инструмента

                    # После завершения анимации инструмента, возвращаемся к idle-анимации по текущему направлению
                    if self.direction in self.animations and self.animations[self.direction]:
                         self.image = self.animations[self.direction][0]
                    else:
                         dummy = pygame.Surface((32, 32))
                         dummy.fill((0, 255, 0))
                         self.image = dummy

                else:
                    # Проигрываем следующий кадр анимации инструмента
                    self.image = self.animations[self.current_tool_animation_type][self.tool_use_current_frame]

                # --- Вызов действия инструмента в определенный момент анимации ---
                # Вызываем till_tile только один раз при переходе на нужный кадр
                if self.current_tool_animation_type == 'hoe_swing':
                    # Например, вызов till_tile на втором кадре анимации взмаха (индекс 1)
                    if prev_frame == 0 and self.tool_use_current_frame == 1: # Вызываем при переходе от кадра 0 к 1
                         target_tile_x, target_tile_y = self.get_tile_in_front()
                         if self.game and hasattr(self.game, 'till_tile') and (target_tile_x != -1 or target_tile_y != -1):
                              self.game.till_tile(target_tile_x, target_tile_y)
                         # else:
                             # print("Не удалось определить координаты тайла перед игроком или GameManager не имеет till_tile.") # Отладочный принт

                # TODO: Добавить вызовы действий для других инструментов в соответствующие моменты анимации
                # elif self.current_tool_animation_type == 'axe_swing':
                #     if prev_frame == X and self.tool_use_current_frame == Y:
                #         self.game.cut_tree(...) # Вызов функции рубки дерева
                # elif self.current_tool_animation_type == 'watering_can':
                #     if prev_frame == X and self.tool_use_current_frame == Y:
                #         self.game.water_tile(...) # Вызов функции полива

        else:
            # Если нет текущей анимации инструмента или она пуста, сбрасываем флаг использования инструмента
            self.is_using_tool = False
            self.tool_use_current_frame = 0
            self.current_tool_animation_type = None
            # Возвращаемся к idle-анимации движения
            if self.direction in self.animations and self.animations[self.direction]:
                 self.image = self.animations[self.direction][0]
            else:
                 dummy = pygame.Surface((32, 32))
                 dummy.fill((0, 255, 0))
                 self.image = dummy

    def use_tool(self):
        """Запускает анимацию использования текущего выбранного инструмента."""
        # Получаем выбранный предмет из хотбара через InventoryManager
        if self.game is None or not hasattr(self.game, 'inventory_manager'):
             print("Ошибка в use_tool: Нет доступа к InventoryManager в GameManager.")
             return

        inventory_manager = self.game.inventory_manager
        selected_item_index = inventory_manager.selected_item_index

        if not (0 <= selected_item_index < len(inventory_manager.hotbar_slots)):
            # print("Неверный индекс выбранного слота хотбара.") # Отладочный принт
            return

        selected_item = inventory_manager.hotbar_slots[selected_item_index]

        if selected_item and isinstance(selected_item, Tool):
            if selected_item.type == 'hoe':
                self.is_using_tool = True
                self.tool_use_animation_timer = 0
                self.tool_use_current_frame = 0
                self.current_tool_animation_type = 'hoe_swing'
                # Логика вызова till_tile ПЕРЕНЕСЕНА в update_tool_use_animation!
            # TODO: Добавить запуск анимаций для других инструментов
            # elif selected_item.type == 'axe':
            #     self.is_using_tool = True
            #     self.tool_use_animation_timer = 0
            #     self.tool_use_current_frame = 0
            #     self.current_tool_animation_type = 'axe_swing'
            # ...
        # else:
            # print("В выбранном слоте нет инструмента или предмет не является инструментом.") # Отладочный принт

    def get_tile_in_front(self):
        """Определяет координаты клетки на карте, которая находится перед игроком."""
        if not self.game or not hasattr(self.game, 'tmx_data') or not self.game.map_loaded:
             print("Ошибка в get_tile_in_front: Нет доступа к tmx_data в GameManager или карта не загружена.")
             return -1, -1

        tile_size = self.game.tmx_data.tilewidth

        player_center_x = self.collision_rect.centerx
        player_center_y = self.collision_rect.centery

        offset_x, offset_y = 0, 0
        pixel_offset = tile_size // 2

        if self.direction == "right":
            offset_x = pixel_offset
        elif self.direction == "left":
            offset_x = -pixel_offset
        elif self.direction == "down":
            offset_y = pixel_offset
        elif self.direction == "up":
            offset_y = -pixel_offset

        target_center_x = player_center_x + offset_x
        target_center_y = player_center_y + offset_y

        target_tile_x = int(target_center_x // tile_size)
        target_tile_y = int(target_center_y // tile_size)

        map_width_tiles = self.game.tmx_data.width
        map_height_tiles = self.game.tmx_data.height

        target_tile_x = max(0, min(target_tile_x, map_width_tiles - 1))
        target_tile_y = max(0, min(target_tile_y, map_height_tiles - 1))

        return target_tile_x, target_tile_y
import pygame
import pytmx
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, game_manager, x, y, speed=100):
        super().__init__()
        self.game = game_manager

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
        self.animation_speed = 8  # Кадров в секунду
        self.animation_timer = 0

        # Переменные для анимации использования инструмента (взмаха)
        self.is_using_tool = False
        self.tool_use_animation_timer = 0
        self.tool_use_animation_speed = 12 # Скорость анимации взмаха
        self.tool_use_current_frame = 0
        self.current_tool_animation_type = None # Тип текущей анимации инструмента (например, 'hoe_swing')


        # Установка начального изображения и прямоугольника
        self.image = self.animations[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Создаем отдельный прямоугольник для коллизий
        self.collision_rect = pygame.Rect(0, 0, 16, 16)  # Размер коллизии (16x16) - возможно, нужно будет настроить
        self.update_collision_rect()  # Обновляем позицию коллизии

        print(f"Игрок создан на позиции ({x}, {y}) со скоростью {speed}")

    def load_animations(self):
        """Загрузка всех анимаций игрока"""
        animations = {
            "down": [],
            "left": [],
            "right": [],
            "up": [],
            "hoe_swing": [], # Новая анимация для взмаха мотыгой
            # Добавьте другие анимации инструментов здесь
        }

        # --- Загрузка основных анимаций движения ---
        # Проверяем наличие папки со спрайтами
        if not os.path.exists(self.sprite_path):
            print(f"Ошибка: Путь {self.sprite_path} для основных анимаций не существует.")
            # Создаем заглушку - зеленый квадрат
            dummy = pygame.Surface((16, 16))
            dummy.fill((0, 255, 0))
            for direction in ["down", "left", "right", "up"]: # Только для основных направлений
                animations[direction] = [dummy]
        else:
            try:
                # Сопоставляем индексы с направлениями (пример для спрайт-листа 4x4)
                directions_map = {
                    "down": [0, 1, 2, 3],
                    "left": [8, 9, 10, 11],
                    "right": [12, 13, 14, 15],
                    "up": [4, 5, 6, 7],
                }

                # Загружаем все спрайты из спрайт-листа
                sprites = []
                for i in range(16):  # Например, 16 спрайтов в спрайт-листе
                    img_path = os.path.join(self.sprite_path, f"sprite_{i}.png") # Убедитесь, что имена файлов соответствуют
                    if os.path.exists(img_path):
                        sprite = pygame.image.load(img_path).convert_alpha()
                        # Масштабируем спрайт, если нужно (сохраняя пропорции, если возможно)
                        # sprite = pygame.transform.scale(sprite, (70, 92)) # Пример масштабирования
                        sprites.append(sprite)
                    else:
                        print(f"Предупреждение: Файл {img_path} не найден для основной анимации.")
                        dummy = pygame.Surface((16, 16))
                        dummy.fill((255, 0, 255))  # Фиолетовый для обозначения отсутствия
                        sprites.append(dummy)

                # Распределяем спрайты по анимациям движения
                for direction, indices in directions_map.items():
                    for idx in indices:
                        if idx < len(sprites):
                            animations[direction].append(sprites[idx])
                        else:
                             print(f"Предупреждение: Индекс спрайта {idx} вне диапазона для направления {direction}.")

            except Exception as e:
                print(f"Ошибка при загрузке основных спрайтов: {e}")
                # Создаем заглушку в случае ошибки
                dummy = pygame.Surface((32, 32))
                dummy.fill((0, 255, 0))
                for direction in ["down", "left", "right", "up"]:
                    animations[direction] = [dummy]

        # --- Загрузка анимации взмаха мотыгой ---
        # Убедитесь, что путь к спрайтам анимации взмаха мотыгой правильный
        hoe_swing_sprites_dir = os.path.join("sprites", "player", "sprites_tools", "hoe_swing") # Путь к папке с анимацией взмаха мотыгой
        if os.path.exists(hoe_swing_sprites_dir):
            try:
                # Предполагаем, что файлы называются frame_0.png, frame_1.png и т.д.
                frame_index = 0
                while True:
                    img_path = os.path.join(hoe_swing_sprites_dir, f"frame_{frame_index}.png")
                    if os.path.exists(img_path):
                        sprite = pygame.image.load(img_path).convert_alpha()
                        # Масштабируйте, если нужно, до размера игрока
                        # sprite = pygame.transform.scale(sprite, (70, 92))
                        animations["hoe_swing"].append(sprite)
                        frame_index += 1
                    else:
                        break # Выходим из цикла, когда файл не найден
                if not animations["hoe_swing"]: # Если анимация не загружена (файлы не найдены)
                    print(f"Предупреждение: Не загружено ни одного кадра для анимации взмаха мотыгой из {hoe_swing_sprites_dir}. Проверьте имена файлов (frame_0.png, ...).")
                    # Fallback: использовать первый кадр из анимации "down" или заглушку
                    if animations["down"]:
                         animations["hoe_swing"] = [animations["down"][0]]
                    else:
                         dummy = pygame.Surface((32, 32))
                         dummy.fill((255, 0, 255))
                         animations["hoe_swing"] = [dummy]

            except Exception as e:
                print(f"Ошибка при загрузке анимации взмаха мотыгой из {hoe_swing_sprites_dir}: {e}")
                # Fallback
                if animations["down"]:
                     animations["hoe_swing"] = [animations["down"][0]]
                else:
                     dummy = pygame.Surface((32, 32))
                     dummy.fill((255, 0, 255))
                     animations["hoe_swing"] = [dummy]
        else:
            print(f"Предупреждение: Папка анимации взмаха мотыгой не найдена: {hoe_swing_sprites_dir}")
            # Fallback
            if animations["down"]:
                 animations["hoe_swing"] = [animations["down"][0]]
            else:
                 dummy = pygame.Surface((32, 32))
                 dummy.fill((255, 0, 255))
                 animations["hoe_swing"] = [dummy]


        return animations


    def update(self, dt):
        """Обновление игрока"""

        # --- Обработка использования инструмента (левая кнопка мыши) ---
        mouse_buttons = pygame.mouse.get_pressed()
        # Проверяем нажатие левой кнопки мыши и что игрок не использует инструмент
        if mouse_buttons[0] and not self.is_using_tool:
             self.use_tool()  # Вызываем метод использования инструмента


        # --- Обработка движения (только если игрок не использует инструмент) ---
        if not self.is_using_tool:
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

            # Проверка горизонтального движения
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -self.speed * dt
                self.direction = "left"
                self.moving = True
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = self.speed * dt
                self.direction = "right"
                self.moving = True

            # Проверка вертикального движения (теперь без условия "if not self.moving:")
            # Если игрок движется по горизонтали ИЛИ по вертикали, устанавливаем moving = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -self.speed * dt
                self.direction = "up" # Обновляем направление (будет последним установленным)
                self.moving = True
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = self.speed * dt
                self.direction = "down" # Обновляем направление
                self.moving = True

            # !!! При диагональном движении (dx != 0 и dy != 0)
            # self.direction будет установлено либо в горизонтальное, либо в вертикальное
            # в зависимости от того, какой блок if/elif сработал последним.
            # Если вам нужны отдельные анимации/направления для диагонального движения,
            # потребуется более сложная логика. Пока оставляем так.

            # Обновляем позиции отдельно, чтобы проверить коллизии

            # Обновляем X
            self.x += dx
            self.rect.x = int(self.x)
            self.update_collision_rect() # Обновляем позицию прямоугольника коллизии

            # Проверяем коллизию по X оси
            if self.game and hasattr(self.game, 'check_collision'): # Проверяем наличие метода в GameManager
                 if self.game.check_collision(self.collision_rect):
                     self.x = prev_x # Откатываем X позицию при коллизии
                     self.rect.x = int(prev_x)
                     self.update_collision_rect() # Обновляем прямоугольник коллизии после отката


            # Обновляем Y
            self.y += dy
            self.rect.y = int(self.y)
            self.update_collision_rect() # Обновляем позицию прямоугольника коллизии

            # Проверяем коллизию по Y оси
            if self.game and hasattr(self.game, 'check_collision'): # Проверяем наличие метода в GameManager
                 if self.game.check_collision(self.collision_rect):
                     self.y = prev_y # Откатываем Y позицию при коллизии
                     self.rect.y = int(prev_y)
                     self.update_collision_rect() # Обновляем прямоугольник коллизии после отката


            # Ограничение движения игрока границами карты
            if hasattr(self.game, "tmx_data") and self.game.map_loaded:
                map_width = self.game.tmx_data.width * self.game.tmx_data.tilewidth
                map_height = self.game.tmx_data.height * self.game.tmx_data.tileheight
                # Учитываем размер спрайта игрока при ограничении
                self.x = max(0.0, min(self.x, float(map_width - self.rect.width)))
                self.y = max(0.0, min(self.y, float(map_height - self.rect.height)))
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
                self.update_collision_rect() # Обновляем прямоугольник коллизии после ограничения границами карты


            # Обновление анимации движения
            self.update_animation(dt, was_moving)

        else: # Если игрок использует инструмент, обновляем только анимацию инструмента
             self.update_tool_use_animation(dt)


    def update_collision_rect(self):
        """Обновляет позицию прямоугольника коллизии.
           Размещаем прямоугольник коллизии в нижней части спрайта.
        """
        # Предполагаем, что коллизия находится в нижней части спрайта
        self.collision_rect.midbottom = self.rect.midbottom


    def update_animation(self, dt, was_moving):
        """Обновление анимации игрока (движения)"""
        # Эта логика выполняется только если self.is_using_tool == False

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
            # Если не движемся, используем первый кадр (idle) по текущему направлению
            self.current_frame = 0

        # Обновляем текущее изображение на кадр анимации движения
        # Убедимся, что анимация для текущего направления не пуста
        if self.direction in self.animations and self.animations[self.direction]:
             self.image = self.animations[self.direction][self.current_frame]
        else:
             # Fallback, если анимация направления не загружена
             print(f"Предупреждение: Анимация для направления '{self.direction}' пуста или не существует.")
             if "down" in self.animations and self.animations["down"]:
                  self.image = self.animations["down"][0] # Используем первый кадр "вниз" как заглушку
             else:
                  # Абсолютный Fallback - зеленая заглушка
                  dummy = pygame.Surface((32, 32))
                  dummy.fill((0, 255, 0))
                  self.image = dummy


    def update_tool_use_animation(self, dt):
        """Обновление анимации использования инструмента"""
        # Эта логика выполняется только если self.is_using_tool == True

        if self.current_tool_animation_type and self.current_tool_animation_type in self.animations and self.animations[self.current_tool_animation_type]:
            self.tool_use_animation_timer += dt
            # Проигрываем анимацию взмаха
            if self.tool_use_animation_timer >= 1.0 / self.tool_use_animation_speed:
                self.tool_use_animation_timer = 0
                self.tool_use_current_frame += 1

                # Проверяем, закончилась ли анимация
                if self.tool_use_current_frame >= len(self.animations[self.current_tool_animation_type]):
                    self.is_using_tool = False # Сбрасываем флаг использования инструмента
                    self.tool_use_current_frame = 0 # Сбрасываем кадр анимации инструмента
                    self.current_tool_animation_type = None # Сбрасываем тип анимации инструмента

                    # После завершения анимации инструмента, возвращаемся к idle-анимации по текущему направлению
                    if self.direction in self.animations and self.animations[self.direction]:
                         self.image = self.animations[self.direction][0] # Первый кадр idle
                    else:
                         # Fallback, если анимация направления не загружена
                         dummy = pygame.Surface((32, 32))
                         dummy.fill((0, 255, 0))
                         self.image = dummy
                else:
                    # Проигрываем следующий кадр анимации инструмента
                    self.image = self.animations[self.current_tool_animation_type][self.tool_use_current_frame]
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
        # Get the currently selected item from the hotbar
        selected_item_index = self.game.selected_item_index
        selected_item = self.game.hotbar_slots[selected_item_index]

        if selected_item: # Check if there is an item in the selected slot
            # Check the type of the selected item
            if hasattr(selected_item, 'type'):
                if selected_item.type == 'hoe':
                    # If the selected item is a hoe, activate the swing animation
                    self.is_using_tool = True
                    self.tool_use_animation_timer = 0
                    self.tool_use_current_frame = 0
                    self.current_tool_animation_type = 'hoe_swing' # Устанавливаем тип анимации инструмента

                    # Call the till_tile method in GameManager
                    target_tile_x, target_tile_y = self.get_tile_in_front()
                    if self.game and hasattr(self.game, 'till_tile'):
                         self.game.till_tile(target_tile_x, target_tile_y)

                # Add checks for other tool types here later (e.g., 'axe', 'wateringcan')
                # elif selected_item.type == 'axe':
                #     # Activate axe swing animation, call cut_tree
                #     pass
                # elif selected_item.type == 'wateringcan':
                #     # Activate watering animation, call water_tile
                #     pass
        else:
            # print("No item selected or item is not a tool.") # Optional: print a message if no tool is selected
            pass # No action if no item is selected


    def get_tile_in_front(self):
        """Определяет координаты клетки на карте, которая находится перед игроком."""
        # This assumes a grid-based map with fixed tile size

        if not self.game or not hasattr(self.game, 'tmx_data'):
             print("Ошибка в get_tile_in_front: Нет доступа к tmx_data в GameManager.")
             return -1, -1 # Возвращаем некорректные координаты в случае ошибки


        tile_size = self.game.tmx_data.tilewidth # Получаем размер тайла из GameManager

        # Рассчитываем центр прямоугольника коллизии игрока
        player_center_x = self.collision_rect.centerx
        player_center_y = self.collision_rect.centery


        # Определяем положение центра следующей клетки в зависимости от направления игрока
        offset_x, offset_y = 0, 0
        # Смещения в пикселях для определения центра следующей клетки
        pixel_offset = tile_size // 2 # Смещаемся на половину тайла в направлении движения

        if self.direction == "right":
            offset_x = pixel_offset
        elif self.direction == "left":
            offset_x = -pixel_offset
        elif self.direction == "down":
            offset_y = pixel_offset
        elif self.direction == "up":
            offset_y = -pixel_offset

        # Вычисляем примерный центр следующей клетки в мировых координатах
        target_center_x = player_center_x + offset_x
        target_center_y = player_center_y + offset_y

        # Переводим мировые координаты в координаты сетки тайлов
        target_tile_x = int(target_center_x // tile_size)
        target_tile_y = int(target_center_y // tile_size)

        # Ограничиваем координаты тайла границами карты
        map_width_tiles = self.game.tmx_data.width
        map_height_tiles = self.game.tmx_data.height

        target_tile_x = max(0, min(target_tile_x, map_width_tiles - 1))
        target_tile_y = max(0, min(target_tile_y, map_height_tiles - 1))


        return target_tile_x, target_tile_y


    def add_item_to_inventory(self, item, slot_index=None, inventory_coords=None):
        """
        Добавляет предмет в инвентарь игрока.
        Можно указать либо индекс слота хотбара (slot_index),
        либо координаты в основном инвентаре (inventory_coords = (row, col)).
        Если ничего не указано, попытается добавить в первый свободный слот хотбара.
        """
        if self.game is None or not hasattr(self.game, 'hotbar_slots') or not hasattr(self.game, 'inventory'):
             print("Ошибка в add_item_to_inventory: Нет доступа к инвентарю/хотбару в GameManager.")
             return

        if slot_index is not None:
            if 0 <= slot_index < len(self.game.hotbar_slots):
                self.game.hotbar_slots[slot_index] = item
                print(f"Предмет {item.name} добавлен в слот хотбара {slot_index}")
            else:
                print(f"Ошибка в add_item_to_inventory: Неверный индекс слота хотбара: {slot_index}")
        elif inventory_coords is not None:
            row, col = inventory_coords
            if 0 <= row < len(self.game.inventory) and 0 <= col < len(self.game.inventory[0]):
                self.game.inventory[row][col] = item
                print(f"Предмет {item.name} добавлен в инвентарь в ({row}, {col})")
            else:
                 print(f"Ошибка в add_item_to_inventory: Неверные координаты инвентаря: ({row}, {col})")
        else:
            # Попытка добавить в первый свободный слот хотбара
            for i in range(len(self.game.hotbar_slots)):
                if self.game.hotbar_slots[i] is None:
                    self.game.hotbar_slots[i] = item
                    print(f"Предмет {item.name} добавлен в первый свободный слот хотбара {i}")
                    return # Выходим после успешного добавления

            print(f"Ошибка в add_item_to_inventory: Нет свободного места в хотбаре для предмета {item.name}")


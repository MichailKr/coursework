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
        # Убедитесь, что анимация для начального направления существует и не пуста
        if self.direction in self.animations and self.animations[self.direction]:
             self.image = self.animations[self.direction][0]
        else:
             # Fallback, если начальная анимация не загружена
             print(f"Предупреждение: Начальная анимация для направления '{self.direction}' пуста или не существует. Используется заглушка.")
             dummy = pygame.Surface((32, 32))
             dummy.fill((0, 255, 0))
             self.image = dummy

        self.rect = self.image.get_rect(topleft=(x, y))

        # Создаем отдельный прямоугольник для коллизий
        # Размер коллизии (16x16) - возможно, нужно будет настроить
        self.collision_rect = pygame.Rect(0, 0, 16, 16)
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
        # Убедитесь, что этот путь правильный
        self.sprite_path = "sprites/player/sprites"

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
                # Этот код предполагает, что у вас есть спрайт-лист с 16 спрайтами
                # и они расположены в определенном порядке для каждого направления.
                # Если у вас отдельные файлы для каждого кадра движения, вам нужно
                # изменить эту часть логики загрузки.
                directions_map = {
                    "down": [0, 1, 2, 3],
                    "left": [8, 9, 10, 11],
                    "right": [12, 13, 14, 15],
                    "up": [4, 5, 6, 7],
                }
                # Загружаем все спрайты из спрайт-листа
                sprites = []
                # Предполагаем, что у вас есть 16 спрайтов в спрайт-листе для движения.
                # Если количество другое, измените диапазон.
                for i in range(16):
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
        # Явно указываем файлы для загрузки, предполагая, что анимация состоит из этих двух кадров
        hoe_swing_files = ["frame_0.png", "frame_1.png"]

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

                if loaded_frames == 0: # Если ни одного кадра не загружено
                    print(f"Предупреждение: Не загружено ни одного кадра для анимации взмаха мотыгой из {hoe_swing_sprites_dir}. Проверьте имена файлов ({', '.join(hoe_swing_files)}).")
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

        # Отладочный принт для проверки количества загруженных кадров hoe_swing
        print(f"Загружено {len(animations['hoe_swing'])} кадров для анимации взмаха мотыгой.")


        return animations

    def update(self, dt):
        """Обновление игрока"""
        # --- Обработка использования инструмента (левая кнопка мыши) ---
        mouse_buttons = pygame.mouse.get_pressed()
        # Проверяем нажатие левой кнопки мыши и что игрок не использует инструмент
        if mouse_buttons[0] and not self.is_using_tool:
             # Получаем выбранный предмет из хотбара
             # Убедитесь, что self.game существует и имеет атрибуты selected_item_index и hotbar_slots
             if self.game and hasattr(self.game, 'selected_item_index') and hasattr(self.game, 'hotbar_slots') and 0 <= self.game.selected_item_index < len(self.game.hotbar_slots):
                  selected_item_index = self.game.selected_item_index
                  selected_item = self.game.hotbar_slots[selected_item_index]
                  # Проверяем, есть ли предмет и является ли он мотыгой
                  if selected_item and hasattr(selected_item, 'type') and selected_item.type == 'hoe':
                      self.use_tool()  # Вызываем метод использования инструмента


        # --- Обработка движения (только если игрок не использует инструмент) ---
        if not self.is_using_tool:
            keys = pygame.key.get_pressed()

            prev_x = self.x
            prev_y = self.y
            was_moving = self.moving # Сохраняем предыдущее состояние движения

            # Считываем состояние клавиш движения
            input_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            input_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            input_up = keys[pygame.K_UP] or keys[pygame.K_w]
            input_down = keys[pygame.K_DOWN] or keys[pygame.K_s]

            # Рассчитываем смещение
            dx = 0
            dy = 0

            if input_left:
                dx = -self.speed * dt
            elif input_right:
                dx = self.speed * dt

            if input_up:
                dy = -self.speed * dt
            elif input_down:
                dy = self.speed * dt

            # Определяем, движется ли игрок
            self.moving = (dx != 0 or dy != 0)

            # Определяем направление (приоритет вертикали при диагональном движении)
            if self.moving:
                if input_up:
                    self.direction = "up"
                elif input_down:
                    self.direction = "down"
                elif input_left: # Если нет вертикального движения, но есть горизонтальное
                    self.direction = "left"
                elif input_right: # Если нет вертикального движения, но есть горизонтальное
                    self.direction = "right"
                # Если нажимаются обе горизонтальные и обе вертикальные (что маловероятно, но возможно),
                # направление будет последним из True, т.е. down. Это соответствует вашему исходному поведению.

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
            # was_moving передается, чтобы update_animation мог сбросить кадр при смене состояния движения
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

        # Проверяем, что анимация для текущего направления существует и не пуста
        if self.direction not in self.animations or not self.animations[self.direction]:
            print(f"Предупреждение: Анимация для направления '{self.direction}' пуста или не существует. Используется Fallback.")
            # Fallback, если анимация направления не загружена или пуста
            if "down" in self.animations and self.animations["down"]:
                 self.image = self.animations["down"][0] # Используем первый кадр "вниз" как заглушку
            else:
                 # Абсолютный Fallback - зеленая заглушка
                 dummy = pygame.Surface((32, 32))
                 dummy.fill((0, 255, 0))
                 self.image = dummy
            return # Выходим, если нет валидной анимации для текущего направления


        # Если начали или прекратили движение, сбрасываем кадр и таймер
        if was_moving != self.moving:
            self.current_frame = 0
            self.animation_timer = 0

        if self.moving:
            # Обновляем таймер анимации
            self.animation_timer += dt
            # Если прошло достаточно времени, переходим к следующему кадру
            # Используем len() для получения количества кадров в текущей анимации
            if self.animation_timer >= 1.0 / self.animation_speed:
                self.animation_timer = 0
                # Переключаемся на следующий кадр
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.direction])
        else:
            # Если не движемся, используем первый кадр (idle) по текущему направлению
            self.current_frame = 0

        # Обновляем текущее изображение на кадр анимации движения
        self.image = self.animations[self.direction][self.current_frame]


    def update_tool_use_animation(self, dt):
        """Обновление анимации использования инструмента"""
        # Эта логика выполняется только если self.is_using_tool == True

        # Проверяем, что текущая анимация инструмента существует и не пуста
        if self.current_tool_animation_type and \
           self.current_tool_animation_type in self.animations and \
           self.animations[self.current_tool_animation_type]:

            self.tool_use_animation_timer += dt

            # Проигрываем анимацию взмаха
            # Используем len() для получения количества кадров в текущей анимации инструмента
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
        # Убедитесь, что self.game существует и имеет атрибуты selected_item_index и hotbar_slots
        if self.game is None or not hasattr(self.game, 'selected_item_index') or not hasattr(self.game, 'hotbar_slots'):
             print("Ошибка в use_tool: Нет доступа к информации о хотбаре в GameManager.")
             return

        selected_item_index = self.game.selected_item_index
        # Проверяем, что индекс слота хотбара корректен
        if not (0 <= selected_item_index < len(self.game.hotbar_slots)):
            # print("Неверный индекс выбранного слота хотбара.") # Отладочный принт
            return # Выходим, если индекс некорректен

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
                    # Убедитесь, что self.game существует и имеет метод till_tile
                    if self.game and hasattr(self.game, 'till_tile'):
                         # Проверяем, что till_tile успешно получил координаты тайла
                         if target_tile_x != -1 or target_tile_y != -1:
                             self.game.till_tile(target_tile_x, target_tile_y)
                         # else:
                             # print("Не удалось определить координаты тайла перед игроком.") # Отладочный принт
                    # else:
                        # print("GameManager не имеет метода 'till_tile'.") # Отладочный принт

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

        if not self.game or not hasattr(self.game, 'tmx_data') or not self.game.map_loaded:
             print("Ошибка в get_tile_in_front: Нет доступа к tmx_data в GameManager или карта не загружена.")
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
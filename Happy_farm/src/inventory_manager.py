import pygame
from src.item import Item # Убедитесь, что путь к Item правильный

class InventoryManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager  # Ссылка на GameManager для доступа к другим частям игры
        self.inventory_open = False
        self.selected_item_index = 0 # Индекс выбранного слота в хотбаре
        self.hotbar_slots = [None] * 8 # Список для хотбара (8 слотов)
        self.inventory = [[None for _ in range(3)] for _ in range(6)] # Основной инвентарь (6x3 слота)

        # Перетаскивание предметов
        self.dragging_item = None
        self.drag_start_slot = None
        self.drag_offset = (0, 0)

        # Размеры и позиции для отрисовки (можно вынести в константы или получать из GameManager)
        self.hotbar_slot_size = 50
        self.hotbar_slot_padding = 10
        self.hotbar_panel_padding = 10
        self.inventory_slot_size = 60
        self.inventory_slot_padding = 10
        self.inventory_panel_padding = 10
        self.inventory_cols = 3
        self.inventory_rows = 6

    def add_item_to_inventory(self, item, slot_index=None, row=None, col=None):
        """
        Добавляет предмет в инвентарь или хотбар.
        Если slot_index указан, добавляет в хотбар.
        Если row и col указаны, добавляет в основной инвентарь.
        Если ничего не указано, пытается найти свободный слот.
        """
        if slot_index is not None:
            if 0 <= slot_index < len(self.hotbar_slots):
                if self.hotbar_slots[slot_index] is None:
                    self.hotbar_slots[slot_index] = item
                    print(f"Предмет {item.name} добавлен в хотбар слот {slot_index}")
                    return True
                else:
                    print(f"Хотбар слот {slot_index} занят.")
                    return False
            else:
                print(f"Неверный индекс хотбар слота: {slot_index}")
                return False
        elif row is not None and col is not None:
            if 0 <= row < self.inventory_rows and 0 <= col < self.inventory_cols:
                if self.inventory[row][col] is None:
                    self.inventory[row][col] = item
                    print(f"Предмет {item.name} добавлен в инвентарь слот ({row}, {col})")
                    return True
                else:
                    print(f"Инвентарь слот ({row}, {col}) занят.")
                    return False
            else:
                print(f"Неверные координаты инвентарь слота: ({row}, {col})")
                return False
        else:
            # Поиск свободного слота в инвентаре
            for r in range(self.inventory_rows):
                for c in range(self.inventory_cols):
                    if self.inventory[r][c] is None:
                        self.inventory[r][c] = item
                        print(f"Предмет {item.name} добавлен в инвентарь слот ({r}, {c})")
                        return True
            # Поиск свободного слота в хотбаре
            for i in range(len(self.hotbar_slots)):
                if self.hotbar_slots[i] is None:
                    self.hotbar_slots[i] = item
                    print(f"Предмет {item.name} добавлен в хотбар слот {i}")
                    return True

        print(f"Не удалось добавить предмет {item.name}: нет свободных слотов.")
        return False

    def handle_input(self, event):
        """Обработка событий ввода, связанных с инвентарем (открытие/закрытие, выбор слота, перетаскивание)"""
        if event.type == pygame.KEYDOWN:
            # Обработка открытия/закрытия инвентаря клавишей T
            if event.key == self.game_manager.settings['controls']['inventory']: # Например, pygame.K_i
                self.inventory_open = not self.inventory_open
                print(f"Инвентарь {'открыт' if self.inventory_open else 'закрыт'}")

            # Обработка выбора слота хотбара клавишами 1-8 (если инвентарь закрыт)
            if not self.inventory_open:
                for i in range(8):
                    if event.key == getattr(pygame, f'K_{i + 1}'):
                        self.selected_item_index = i
                        print(f"Выбран слот хотбара: {self.selected_item_index}")
                        break # Выходим после обработки нажатия 1-8

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_pos = event.pos
                if self.inventory_open:
                    # Проверяем клик по слотам инвентаря для начала перетаскивания
                    item, slot_info = self.get_item_from_click(mouse_pos)
                    if item:
                        self.dragging_item = item
                        self.drag_start_slot = slot_info
                        # Рассчитываем смещение для плавного перетаскивания
                        item_image_rect = self.get_item_image_rect(item, slot_info)
                        if item_image_rect:
                            self.drag_offset = (mouse_pos[0] - item_image_rect.x, mouse_pos[1] - item_image_rect.y)
                        else:
                            self.drag_offset = (0, 0)
                        # Временно убираем предмет из исходного слота
                        self._remove_item_from_slot(slot_info)


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Левая кнопка мыши
                if self.dragging_item:
                    mouse_pos = event.pos
                    # Определяем, куда бросили предмет
                    target_slot_info = self.get_slot_from_click(mouse_pos)

                    if target_slot_info:
                        # Попытка поместить предмет в новый слот
                        success = self.place_item_in_slot(self.dragging_item, target_slot_info, self.drag_start_slot)
                        if not success:
                            # Если не удалось поместить, вернуть в исходный слот
                            self.place_item_in_slot(self.dragging_item, self.drag_start_slot)
                    else:
                        # Предмет брошен вне инвентаря (логика выброса)
                        print(f"Предмет {self.dragging_item.name} выброшен.")
                        # Здесь можно добавить логику для создания объекта Item на земле
                        pass

                    self.dragging_item = None
                    self.drag_start_slot = None
                    self.drag_offset = (0, 0)

        # Обработка движения мыши только для обновления позиции перетаскиваемого предмета
        if event.type == pygame.MOUSEMOTION:
             if self.dragging_item:
                 pass
                 # Позиция будет обновляться при отрисовке

    def get_item_from_click(self, mouse_pos):
        """
        Определяет, был ли клик по предмету в инвентаре или хотбаре.
        Возвращает (предмет, информация_о_слоте) или (None, None).
        """
        screen = self.game_manager.screen_manager.get_screen()

        # Проверка хотбара
        panel_width = len(self.hotbar_slots) * (self.hotbar_slot_size + self.hotbar_slot_padding) + self.hotbar_panel_padding
        panel_height = self.hotbar_slot_size + 2 * self.hotbar_panel_padding
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = screen.get_height() - panel_height - 10

        for index, item in enumerate(self.hotbar_slots):
            slot_x = panel_x + self.hotbar_panel_padding + index * (self.hotbar_slot_size + self.hotbar_slot_padding)
            slot_y = panel_y + self.hotbar_panel_padding
            slot_rect = pygame.Rect(slot_x, slot_y, self.hotbar_slot_size, self.hotbar_slot_size)
            if slot_rect.collidepoint(mouse_pos) and item:
                return (item, ('hotbar', index))

        # Проверка основного инвентаря
        if self.inventory_open:
            inventory_width = self.inventory_cols * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_height = self.inventory_rows * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2

            for row in range(self.inventory_rows):
                for col in range(self.inventory_cols):
                    slot_x = inventory_x + self.inventory_panel_padding + col * (self.inventory_slot_size + self.inventory_slot_padding)
                    slot_y = inventory_y + self.inventory_panel_padding + row * (self.inventory_slot_size + self.inventory_slot_padding)
                    slot_rect = pygame.Rect(slot_x, slot_y, self.inventory_slot_size, self.inventory_slot_size)
                    if slot_rect.collidepoint(mouse_pos):
                        item = self.inventory[row][col]
                        if item:
                            return (item, ('inventory', row, col))

        return (None, None)

    def get_slot_from_click(self, mouse_pos):
        """
        Определяет, в какой слот инвентаря или хотбара был клик.
        Возвращает информация_о_слоте или None.
        """
        screen = self.game_manager.screen_manager.get_screen()

        # Проверка хотбара
        panel_width = len(self.hotbar_slots) * (self.hotbar_slot_size + self.hotbar_slot_padding) + self.hotbar_panel_padding
        panel_height = self.hotbar_slot_size + 2 * self.hotbar_panel_padding
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = screen.get_height() - panel_height - 10

        for index in range(len(self.hotbar_slots)):
            slot_x = panel_x + self.hotbar_panel_padding + index * (self.hotbar_slot_size + self.hotbar_slot_padding)
            slot_y = panel_y + self.hotbar_panel_padding
            slot_rect = pygame.Rect(slot_x, slot_y, self.hotbar_slot_size, self.hotbar_slot_size)
            if slot_rect.collidepoint(mouse_pos):
                return ('hotbar', index)

        # Проверка основного инвентаря
        if self.inventory_open:
            inventory_width = self.inventory_cols * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_height = self.inventory_rows * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2

            for row in range(self.inventory_rows):
                for col in range(self.inventory_cols):
                    slot_x = inventory_x + self.inventory_panel_padding + col * (self.inventory_slot_size + self.inventory_slot_padding)
                    slot_y = inventory_y + self.inventory_panel_padding + row * (self.inventory_slot_size + self.inventory_slot_padding)
                    slot_rect = pygame.Rect(slot_x, slot_y, self.inventory_slot_size, self.inventory_slot_size)
                    if slot_rect.collidepoint(mouse_pos):
                        return ('inventory', row, col)

        return None

    def get_item_image_rect(self, item, slot_info):
        """
        Возвращает pygame.Rect изображения предмета в заданном слоте для расчета смещения.
        Использует те же координаты и размеры, что и при отрисовке.
        """
        screen = self.game_manager.screen_manager.get_screen()
        if slot_info[0] == 'hotbar':
            index = slot_info[1]
            panel_width = len(self.hotbar_slots) * (self.hotbar_slot_size + self.hotbar_slot_padding) + self.hotbar_panel_padding
            panel_height = self.hotbar_slot_size + 2 * self.hotbar_panel_padding
            panel_x = (screen.get_width() - panel_width) // 2
            panel_y = screen.get_height() - panel_height - 10
            slot_x = panel_x + self.hotbar_panel_padding + index * (self.hotbar_slot_size + self.hotbar_slot_padding)
            slot_y = panel_y + self.hotbar_panel_padding
            # Размеры для отрисовки в слоте хотбара
            item_slot_size = 40 # Из вашей функции draw_inventory_and_hotbar

            if isinstance(item, Item) and hasattr(item, 'image') and item.image:
                img_width, img_height = item.image.get_size()
                scale_factor = min(item_slot_size / img_width, item_slot_size / img_height)
                scaled_width = int(img_width * scale_factor)
                scaled_height = int(img_height * scale_factor)
                img_x = slot_x + (self.hotbar_slot_size - scaled_width) // 2
                img_y = slot_y + (self.hotbar_slot_size - scaled_height) // 2
                return pygame.Rect(img_x, img_y, scaled_width, scaled_height)

        elif slot_info[0] == 'inventory':
            row, col = slot_info[1], slot_info[2]
            inventory_width = self.inventory_cols * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_height = self.inventory_rows * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2
            slot_x = inventory_x + self.inventory_panel_padding + col * (self.inventory_slot_size + self.inventory_slot_padding)
            slot_y = inventory_y + self.inventory_panel_padding + row * (self.inventory_slot_size + self.inventory_slot_padding)
            # Размеры для отрисовки в слоте инвентаря
            item_slot_size = 50 # Из вашей функции draw_inventory_and_hotbar

            if isinstance(item, Item) and hasattr(item, 'image') and item.image:
                img_width, img_height = item.image.get_size()
                scale_factor = min(item_slot_size / img_width, item_slot_size / img_height)
                scaled_width = int(img_width * scale_factor)
                scaled_height = int(img_height * scale_factor)
                img_x = slot_x + (self.inventory_slot_size - scaled_width) // 2
                img_y = slot_y + (self.inventory_slot_size - scaled_height) // 2
                return pygame.Rect(img_x, img_y, scaled_width, scaled_height)
        return None

    def place_item_in_slot(self, item, target_slot_info, source_slot_info=None):
        """
        Помещает предмет в целевой слот.
        Возвращает True при успехе, False при неудаче.
        Обрабатывает обмен и стакание (пока простая версия).
        """
        target_type = target_slot_info[0]

        # Получаем текущий предмет в целевом слоте
        current_item_in_target = None
        if target_type == 'hotbar':
            target_index = target_slot_info[1]
            if 0 <= target_index < len(self.hotbar_slots):
                 current_item_in_target = self.hotbar_slots[target_index]
            else:
                print(f"Неверный целевой хотбар слот: {target_slot_info}")
                return False
        elif target_type == 'inventory':
            target_row, target_col = target_slot_info[1], target_slot_info[2]
            if 0 <= target_row < self.inventory_rows and 0 <= target_col < self.inventory_cols:
                 current_item_in_target = self.inventory[target_row][target_col]
            else:
                 print(f"Неверный целевой инвентарь слот: {target_slot_info}")
                 return False
        else:
            print(f"Неизвестный целевой слот: {target_slot_info}")
            return False

        # Логика размещения
        if current_item_in_target is None:
            # Целевой слот пуст - просто помещаем предмет
            if target_type == 'hotbar':
                self.hotbar_slots[target_index] = item
            elif target_type == 'inventory':
                self.inventory[target_row][target_col] = item
            print(f"Предмет {item.name} помещен в целевой слот {target_slot_info}.")
            return True
        else:
            # Целевой слот занят - попытка обмена или стакания
            # Простая логика обмена: если предмет в целевом слоте не None, меняем местами
            print(f"Целевой слот {target_slot_info} занят предметом {current_item_in_target.name}. Попытка обмена.")
            if source_slot_info:
                # Удаляем предмет из исходного слота перед обменом
                 self._remove_item_from_slot(source_slot_info)
                 # Помещаем текущий предмет из целевого слота в исходный
                 self._place_item_in_slot_direct(current_item_in_target, source_slot_info)

            # Помещаем перетаскиваемый предмет в целевой слот
            if target_type == 'hotbar':
                self.hotbar_slots[target_index] = item
            elif target_type == 'inventory':
                self.inventory[target_row][target_col] = item
            print(f"Предметы успешно обменены между {source_slot_info} и {target_slot_info}.")
            return True # Обмен считается успешным

        # TODO: Добавить логику стакания предметов (если предметы стакуемые и одного типа)

    def _remove_item_from_slot(self, slot_info):
        """Вспомогательный метод для удаления предмета из слота."""
        slot_type = slot_info[0]
        if slot_type == 'hotbar':
            index = slot_info[1]
            if 0 <= index < len(self.hotbar_slots):
                self.hotbar_slots[index] = None
                # print(f"Предмет удален из хотбар слота {index}.")
        elif slot_type == 'inventory':
            row, col = slot_info[1], slot_info[2]
            if 0 <= row < self.inventory_rows and 0 <= col < self.inventory_cols:
                 self.inventory[row][col] = None
                 # print(f"Предмет удален из инвентарь слота ({row}, {col}).")

    def _place_item_in_slot_direct(self, item, slot_info):
        """Вспомогательный метод для прямого помещения предмета в слот (без проверок)."""
        slot_type = slot_info[0]
        if slot_type == 'hotbar':
            index = slot_info[1]
            if 0 <= index < len(self.hotbar_slots):
                self.hotbar_slots[index] = item
                # print(f"Предмет {item.name} напрямую помещен в хотбар слот {index}.")
        elif slot_type == 'inventory':
            row, col = slot_info[1], slot_info[2]
            if 0 <= row < self.inventory_rows and 0 <= col < self.inventory_cols:
                 self.inventory[row][col] = item
                 # print(f"Предмет {item.name} напрямую помещен в инвентарь слот ({row}, {col}).")


    def draw(self, screen):
        """Отрисовка инвентаря и хотбара"""
        # Отрисовка панели хотбара
        panel_width = len(self.hotbar_slots) * (self.hotbar_slot_size + self.hotbar_slot_padding) + self.hotbar_panel_padding
        panel_height = self.hotbar_slot_size + 2 * self.hotbar_panel_padding
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = screen.get_height() - panel_height - 10

        pygame.draw.rect(screen, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=10)

        for index, item in enumerate(self.hotbar_slots):
            slot_x = panel_x + self.hotbar_panel_padding + index * (self.hotbar_slot_size + self.hotbar_slot_padding)
            slot_y = panel_y + self.hotbar_panel_padding

            # Отрисовка рамки выбранного слота
            if index == self.selected_item_index:
                pygame.draw.rect(screen, (255, 215, 0), (slot_x - 5, slot_y - 5, self.hotbar_slot_size + 10, self.hotbar_slot_size + 10), 3, border_radius=10)

            # Отрисовка фона слота
            pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, self.hotbar_slot_size, self.hotbar_slot_size), border_radius=5)

            # Отрисовка предмета в слоте (если он не перетаскивается)
            # Проверяем, что предмет в слоте не является перетаскиваемым предметом
            if item and item is not self.dragging_item:
                self._draw_item_in_slot(screen, item, slot_x, slot_y, self.hotbar_slot_size, item_slot_size=40) # item_slot_size из вашей отрисовки

        # Отрисовка инвентаря (если открыт)
        if self.inventory_open:
            inventory_width = self.inventory_cols * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_height = self.inventory_rows * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2

            pygame.draw.rect(screen, (50, 50, 50), (inventory_x, inventory_y, inventory_width, inventory_height), border_radius=10)

            for row in range(self.inventory_rows):
                for col in range(self.inventory_cols):
                    slot_x = inventory_x + self.inventory_panel_padding + col * (self.inventory_slot_size + self.inventory_slot_padding)
                    slot_y = inventory_y + self.inventory_panel_padding + row * (self.inventory_slot_size + self.inventory_slot_padding)

                    # Отрисовка фона слота инвентаря
                    pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, self.inventory_slot_size, self.inventory_slot_size), border_radius=5)

                    item = self.inventory[row][col]
                    # Отрисовка предмета в слоте (если он не перетаскивается)
                    if item and item is not self.dragging_item:
                        self._draw_item_in_slot(screen, item, slot_x, slot_y, self.inventory_slot_size, item_slot_size=50) # item_slot_size из вашей отрисовки

        # Отрисовка перетаскиваемого предмета (всегда поверх всего)
        if self.dragging_item and self.dragging_item.image:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            draw_x = mouse_x - self.drag_offset[0]
            draw_y = mouse_y - self.drag_offset[1]

            # Масштабируем изображение предмета для перетаскивания (используем размер инвентарного слота)
            item_image = self.dragging_item.image
            img_width, img_height = item_image.get_size()
            drag_size = 50 # Размер для перетаскивания (можно сделать настраиваемым)
            scale_factor = min(drag_size / img_width, drag_size / img_height)
            scaled_width = int(img_width * scale_factor)
            scaled_height = int(img_height * scale_factor)
            scaled_image = pygame.transform.scale(item_image, (scaled_width, scaled_height))

            screen.blit(scaled_image, (draw_x, draw_y))


    def _draw_item_in_slot(self, screen, item, slot_x, slot_y, slot_size, item_slot_size):
        """Вспомогательный метод для отрисовки предмета внутри слота."""
        if isinstance(item, Item) and hasattr(item, 'image') and item.image:
             item_image = item.image
             img_width, img_height = item_image.get_size()
             scale_factor = min(item_slot_size / img_width, item_slot_size / img_height)
             scaled_width = int(img_width * scale_factor)
             scaled_height = int(img_height * scale_factor)
             scaled_image = pygame.transform.scale(item_image, (scaled_width, scaled_height))
             img_x = slot_x + (slot_size - scaled_width) // 2
             img_y = slot_y + (slot_size - scaled_height) // 2
             screen.blit(scaled_image, (img_x, img_y))
        else:
             # Заглушка для отсутствующего изображения/неправильного объекта
             dummy = pygame.Surface((item_slot_size, item_slot_size))
             dummy.fill((255, 0, 0)) # Красная заглушка
             screen.blit(dummy, (slot_x + (slot_size - item_slot_size) // 2, slot_y + (slot_size - item_slot_size) // 2))
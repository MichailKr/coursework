import pygame
from src.item import Item, Tool, Tomato, Wheat, Seed # Убедитесь, что путь к Item и Tool правильный

class InventoryManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager  # Ссылка на GameManager для доступа к другим частям игры

        self.inventory_open = False
        self.selected_item_index = 0 # Индекс выбранного слота в хотбаре
        self.hotbar_slots = [None] * 8 # Список для хотбара (8 слотов)
        self.inventory = [[None for _ in range(3)] for _ in range(6)] # Основной инвентарь (6x3 слота)

        # Перетаскивание предметов
        self.dragging_item = None
        self.drag_start_slot = None # Содержит ('hotbar', index) или ('inventory', row, col)
        self.drag_offset = (0, 0)

        # Размеры и позиции для отрисовки (можно вынести в константы или получать из GameManager)
        self.hotbar_slot_size = 50
        self.hotbar_slot_padding = 10
        self.hotbar_panel_padding = 10

        self.inventory_slot_size = 60
        self.inventory_slot_padding = 10
        self.inventory_cols = 3
        self.inventory_rows = 6
        self.inventory_panel_padding = 10 # Добавлена константа для отступа панели инвентаря

    def add_item_by_slot_or_find(self, item, slot_index=None, row=None, col=None):
        # Если предмет стакается, ищем такой же в инвентаре
        if item.stackable:
            # Проверяем хотбар
            for i, slot_item in enumerate(self.hotbar_slots):
                if slot_item and slot_item.name == item.name and slot_item.quantity < slot_item.max_stack:
                    # Увеличиваем количество, если нашли такой же предмет
                    # Здесь ОЧЕНЬ ВАЖНО: item.quantity - это сколько мы хотим добавить.
                    # slot_item.quantity - сколько уже есть.
                    # Нужно добавить min(item.quantity, space_available)
                    space_available = slot_item.max_stack - slot_item.quantity
                    amount_to_add = min(item.quantity, space_available)
                    slot_item.quantity += amount_to_add
                    item.quantity -= amount_to_add  # Уменьшаем количество у добавляемого предмета
                    if item.quantity == 0:  # Если все добавили, выходим
                        return True
            # Проверяем основной инвентарь
            for r in range(self.inventory_rows):
                for c in range(self.inventory_cols):
                    inv_item = self.inventory[r][c]
                    if inv_item and inv_item.name == item.name and inv_item.quantity < inv_item.max_stack:
                        space_available = inv_item.max_stack - inv_item.quantity
                        amount_to_add = min(item.quantity, space_available)
                        inv_item.quantity += amount_to_add
                        item.quantity -= amount_to_add
                        if item.quantity == 0:
                            return True

        # Если остались предметы (item.quantity > 0) или предмет не стакается,
        # ищем пустой слот.
        # Если указан конкретный слот
        if slot_index is not None:
            if 0 <= slot_index < len(self.hotbar_slots):
                if self.hotbar_slots[slot_index] is None:
                    self.hotbar_slots[slot_index] = item
                    return True
        elif row is not None and col is not None:
            if 0 <= row < self.inventory_rows and 0 <= col < self.inventory_cols:
                if self.inventory[row][col] is None:
                    self.inventory[row][col] = item
                    return True
        else:
            # Поиск первого свободного слота (сначала хотбар, потом инвентарь)
            # Внимание: если item.quantity > 1 и не все поместилось в стаки,
            # этот код сейчас будет пытаться поместить весь item.
            # Для корректной обработки, вам нужно будет создать новый экземпляр Item
            # с оставшимся количеством. Но чтобы не мудрить, пока оставим так.
            # Для урожая, приходящего из plant.harvest(), quantity = 1, так что это не проблема.
            for i in range(len(self.hotbar_slots)):
                if self.hotbar_slots[i] is None:
                    self.hotbar_slots[i] = item
                    return True
            for r in range(self.inventory_rows):
                for c in range(self.inventory_cols):
                    if self.inventory[r][c] is None:
                        self.inventory[r][c] = item
                        return True
        return False

    def add_item(self, item_instance: Item, quantity: int = 1):
        """
        Добавляет уже существующий экземпляр предмета в инвентарь.
        Используется, когда у нас уже есть объект Item (например, при сборе урожая).
        item_instance: экземпляр класса Item (или его подкласса), который нужно добавить.
                       Его image, name, stackable, max_stack уже определены.
        quantity: количество, которое нужно добавить.
        """
        if not isinstance(item_instance, Item):
            print(f"Ошибка: Попытка добавить не-Item объект в инвентарь: {item_instance}")
            return False
        # Подготовка аргументов для создания нового экземпляра/копии
        # Это нужно, потому что конструкторы Item, Tool, Seed, Tomato, Wheat
        # принимают разные наборы аргументов.
        # Общие аргументы, которые есть почти у всех
        common_args = {
            'quantity': quantity,
            'scale_to_size': item_instance.image.get_size() if item_instance.image else None,
            # 'image_path_or_surface' используется в Item и его прямых подклассах
            'image_path_or_surface': item_instance.image_path if hasattr(item_instance, 'image_path') else None
        }
        # Создаем копию объекта для работы с количеством (item_to_add)
        # Это важно, чтобы не менять оригинальный item_instance, который пришел извне
        if isinstance(item_instance, Tomato):
            # Tomato.__init__ принимает только quantity, description, scale_to_size, image_path_or_surface
            item_to_add = Tomato(
                quantity=quantity,
                description=item_instance.description,
                scale_to_size=common_args['scale_to_size'],
                image_path_or_surface=common_args['image_path_or_surface']  # Если Tomato может принимать Surface/path
            )
        elif isinstance(item_instance, Wheat):
            # Wheat.__init__ принимает только quantity, description, scale_to_size, image_path_or_surface
            item_to_add = Wheat(
                quantity=quantity,
                description=item_instance.description,
                scale_to_size=common_args['scale_to_size'],
                image_path_or_surface=common_args['image_path_or_surface']  # Если Wheat может принимать Surface/path
            )
        elif isinstance(item_instance, Seed):
            # Seed.__init__ принимает name, image_path_or_surface, plant_type, quantity, description, scale_to_size
            item_to_add = Seed(
                name=item_instance.name,
                image_path_or_surface=common_args['image_path_or_surface'],
                plant_type=item_instance.plant_type,
                quantity=quantity,
                description=item_instance.description,
                scale_to_size=common_args['scale_to_size']
            )
        elif isinstance(item_instance, Tool):
            # Tool.__init__ принимает name, image_path_or_surface, tool_type, durability, quantity, description, scale_to_size
            item_to_add = Tool(
                name=item_instance.name,
                image_path_or_surface=common_args['image_path_or_surface'],
                tool_type=item_instance.tool_type,
                durability=item_instance.durability,  # Копируем текущую прочность
                quantity=quantity,  # Инструменты обычно не стакуются, но оставляем для общности
                description=item_instance.description,
                scale_to_size=common_args['scale_to_size']
            )
        elif isinstance(item_instance, Item):  # Базовый Item
            # Item.__init__ принимает name, image_path_or_surface, item_type, stackable, max_stack, quantity, description, scale_to_size
            item_to_add = Item(
                name=item_instance.name,
                image_path_or_surface=common_args['image_path_or_surface'],
                item_type=item_instance.item_type,
                stackable=item_instance.stackable,
                max_stack=item_instance.max_stack,
                quantity=quantity,
                description=item_instance.description,
                scale_to_size=common_args['scale_to_size']
            )
        else:
            print(f"Ошибка: Неизвестный тип предмета {type(item_instance)} в add_item.")
            return False
        remaining_quantity = item_to_add.quantity
        # --- Шаг 1: Попытка стакать с существующими предметами ---
        if item_to_add.stackable:
            # Проверяем хотбар
            for i, slot_item in enumerate(self.hotbar_slots):
                if slot_item and slot_item.name == item_to_add.name and slot_item.quantity < slot_item.max_stack:
                    space_available = slot_item.max_stack - slot_item.quantity
                    amount_to_fill = min(remaining_quantity, space_available)
                    slot_item.quantity += amount_to_fill
                    remaining_quantity -= amount_to_fill
                    if remaining_quantity == 0:
                        print(f"Добавлено {quantity}x {item_to_add.name} в существующий стек хотбара.")
                        return True
            # Проверяем основной инвентарь
            for r in range(self.inventory_rows):
                for c in range(self.inventory_cols):
                    inv_item = self.inventory[r][c]
                    if inv_item and inv_item.name == item_to_add.name and inv_item.quantity < inv_item.max_stack:
                        space_available = inv_item.max_stack - inv_item.quantity
                        amount_to_fill = min(remaining_quantity, space_available)
                        inv_item.quantity += amount_to_fill
                        remaining_quantity -= amount_to_fill
                        if remaining_quantity == 0:
                            print(f"Добавлено {quantity}x {item_to_add.name} в существующий стек инвентаря.")
                            return True
        # --- Шаг 2: Создание новых стеков или размещение нестекуемых предметов ---
        while remaining_quantity > 0:
            found_empty_slot = False
            # Аргументы для создания new_slot_item
            # Количество для нового стека будет amount_for_new_stack
            new_item_creation_quantity = min(remaining_quantity, item_to_add.max_stack)
            # Сначала ищем пустой слот в хотбаре
            for i in range(len(self.hotbar_slots)):
                if self.hotbar_slots[i] is None:
                    if isinstance(item_to_add, Tomato):
                        new_slot_item = Tomato(
                            quantity=new_item_creation_quantity,
                            description=item_to_add.description,
                            scale_to_size=common_args['scale_to_size'],
                            image_path_or_surface=common_args['image_path_or_surface']
                        )
                    elif isinstance(item_to_add, Wheat):
                        new_slot_item = Wheat(
                            quantity=new_item_creation_quantity,
                            description=item_to_add.description,
                            scale_to_size=common_args['scale_to_size'],
                            image_path_or_surface=common_args['image_path_or_surface']
                        )
                    elif isinstance(item_to_add, Seed):
                        new_slot_item = Seed(
                            name=item_to_add.name,
                            image_path_or_surface=common_args['image_path_or_surface'],
                            plant_type=item_to_add.plant_type,
                            quantity=new_item_creation_quantity,
                            description=item_to_add.description,
                            scale_to_size=common_args['scale_to_size']
                        )
                    elif isinstance(item_to_add, Tool):
                        new_slot_item = Tool(
                            name=item_to_add.name,
                            image_path_or_surface=common_args['image_path_or_surface'],
                            tool_type=item_to_add.tool_type,
                            durability=item_to_add.durability,
                            quantity=new_item_creation_quantity,
                            description=item_to_add.description,
                            scale_to_size=common_args['scale_to_size']
                        )
                    elif isinstance(item_to_add, Item):
                        new_slot_item = Item(
                            name=item_to_add.name,
                            image_path_or_surface=common_args['image_path_or_surface'],
                            item_type=item_to_add.item_type,
                            stackable=item_to_add.stackable,
                            max_stack=item_to_add.max_stack,
                            quantity=new_item_creation_quantity,
                            description=item_to_add.description,
                            scale_to_size=common_args['scale_to_size']
                        )
                    else:  # Не должно быть достигнуто, но для безопасности
                        print(f"Ошибка: Неизвестный тип предмета {type(item_to_add)} при создании нового слота.")
                        break  # Выход из цикла while
                    self.hotbar_slots[i] = new_slot_item
                    remaining_quantity -= new_item_creation_quantity
                    found_empty_slot = True
                    print(f"Создан новый стек {new_slot_item.name} x{new_slot_item.quantity} в хотбаре.")
                    break
            if found_empty_slot and remaining_quantity == 0:
                return True
            # Если остались предметы, ищем пустой слот в основном инвентаре
            if remaining_quantity > 0:
                found_empty_slot_in_inventory = False
                for r in range(self.inventory_rows):
                    for c in range(self.inventory_cols):
                        if self.inventory[r][c] is None:
                            new_item_creation_quantity = min(remaining_quantity, item_to_add.max_stack)

                            if isinstance(item_to_add, Tomato):
                                new_slot_item = Tomato(
                                    quantity=new_item_creation_quantity,
                                    description=item_to_add.description,
                                    scale_to_size=common_args['scale_to_size'],
                                    image_path_or_surface=common_args['image_path_or_surface']
                                )
                            elif isinstance(item_to_add, Wheat):
                                new_slot_item = Wheat(
                                    quantity=new_item_creation_quantity,
                                    description=item_to_add.description,
                                    scale_to_size=common_args['scale_to_size'],
                                    image_path_or_surface=common_args['image_path_or_surface']
                                )
                            elif isinstance(item_to_add, Seed):
                                new_slot_item = Seed(
                                    name=item_to_add.name,
                                    image_path_or_surface=common_args['image_path_or_surface'],
                                    plant_type=item_to_add.plant_type,
                                    quantity=new_item_creation_quantity,
                                    description=item_to_add.description,
                                    scale_to_size=common_args['scale_to_size']
                                )
                            elif isinstance(item_to_add, Tool):
                                new_slot_item = Tool(
                                    name=item_to_add.name,
                                    image_path_or_surface=common_args['image_path_or_surface'],
                                    tool_type=item_to_add.tool_type,
                                    durability=item_to_add.durability,
                                    quantity=new_item_creation_quantity,
                                    description=item_to_add.description,
                                    scale_to_size=common_args['scale_to_size']
                                )
                            elif isinstance(item_to_add, Item):
                                new_slot_item = Item(
                                    name=item_to_add.name,
                                    image_path_or_surface=common_args['image_path_or_surface'],
                                    item_type=item_to_add.item_type,
                                    stackable=item_to_add.stackable,
                                    max_stack=item_to_add.max_stack,
                                    quantity=new_item_creation_quantity,
                                    description=item_to_add.description,
                                    scale_to_size=common_args['scale_to_size']
                                )
                            else:
                                print(
                                    f"Ошибка: Неизвестный тип предмета {type(item_to_add)} при создании нового слота.")
                                break
                            self.inventory[r][c] = new_slot_item
                            remaining_quantity -= new_item_creation_quantity
                            found_empty_slot_in_inventory = True
                            print(f"Создан новый стек {new_slot_item.name} x{new_slot_item.quantity} в инвентаре.")
                            break
                    if found_empty_slot_in_inventory:
                        break
                if not found_empty_slot_in_inventory:
                    print(
                        f"Инвентарь полон, не удалось добавить все {quantity}x {item_to_add.name}. Осталось: {remaining_quantity}")
                    return False
            if not found_empty_slot and not found_empty_slot_in_inventory and remaining_quantity > 0:
                print(
                    f"Инвентарь полон, не удалось добавить все {quantity}x {item_to_add.name}. Осталось: {remaining_quantity}")
                return False
        print(
            f"Предмет {item_to_add.name} добавлен в инвентарь (добавлено {quantity - remaining_quantity} из {quantity}).")
        return True

    def handle_input(self, event):
        """Обработка событий ввода, связанных с инвентарем (открытие/закрытие, выбор слота, перетаскивание)"""

        # --- Отладочные принты для проверки принимаемых событий ---
        # print(f"InventoryManager received event type: {event.type}")
        # if event.type == pygame.KEYDOWN:
        #     print(f"Key pressed: {event.key}")
        #     print(f"Expected inventory key: {self.game_manager.settings['controls']['inventory']}")
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #      print(f"Mouse button down at {event.pos}, button: {event.button}")
        # elif event.type == pygame.MOUSEBUTTONUP:
        #      print(f"Mouse button up at {event.pos}, button: {event.button}")
        # elif event.type == pygame.MOUSEMOTION:
        #      print(f"Mouse motion to {event.pos}")
        # --- Конец отладочных принтов ---

        if event.type == pygame.KEYDOWN:
            # Обработка открытия/закрытия инвентаря клавишей
            if event.key == self.game_manager.settings['controls']['inventory']:
                self.inventory_open = not self.inventory_open
                # print(f"Инвентарь {'открыт' if self.inventory_open else 'закрыт'}") # Отладочный принт

            # Обработка выбора слота хотбара клавишами 1-8 (если инвентарь закрыт)
            if not self.inventory_open:
                for i in range(8):
                    if event.key == getattr(pygame, f'K_{i + 1}'):
                        self.selected_item_index = i
                        # print(f"Выбран слот хотбара: {self.selected_item_index}") # Отладочный принт
                        break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_pos = event.pos
                # Проверяем клик только если инвентарь открыт (для перетаскивания)
                if self.inventory_open:
                    item, slot_info = self.get_item_from_click(mouse_pos)
                    if item:
                        self.dragging_item = item
                        self.drag_start_slot = slot_info
                        item_image_rect = self.get_item_image_rect(item, slot_info)
                        if item_image_rect:
                            self.drag_offset = (mouse_pos[0] - item_image_rect.x, mouse_pos[1] - item_image_rect.y)
                        else:
                            self.drag_offset = (0, 0)
                        # !!! КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: УДАЛИЛИ ЭТУ СТРОКУ !!!
                        # self._remove_item_from_slot(slot_info)
                        # Теперь предмет удаляется из исходного слота только если place_item_in_slot успешно его переместит.

                # TODO: Добавить здесь обработку кликов вне инвентаря (для использования предмета в мире),
                # если эта логика не в Player.handle_input

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Левая кнопка мыши
                if self.dragging_item:
                    mouse_pos = event.pos
                    target_slot_info = self.get_slot_from_click(mouse_pos)

                    if target_slot_info:
                        # Попытка поместить перетаскиваемый предмет в целевой слот
                        success = self.place_item_in_slot(self.dragging_item, target_slot_info, self.drag_start_slot)
                        if not success:
                            # Если не удалось поместить (например, целевой слот занят и не стакуется/обменялся),
                            # или если произошло частичное стакание (и place_item_in_slot вернул False),
                            # то возвращаем оставшийся предмет в исходный слот.
                            self._place_item_in_slot_direct(self.dragging_item, self.drag_start_slot)
                            print(f"Не удалось полностью переместить {self.dragging_item.name}. Остаток возвращен в исходный слот.")
                    else:
                        # Предмет брошен вне инвентаря (логика выброса)
                        print(f"Предмет {self.dragging_item.name} выброшен.")
                        # Здесь можно добавить логику для создания объекта Item на земле
                        # Например: self.game_manager.spawn_item_on_ground(self.dragging_item, self.game_manager.player.rect.center)

                    self.dragging_item = None
                    self.drag_start_slot = None
                    self.drag_offset = (0, 0)

                # TODO: Добавить здесь обработку отпускания кликов вне инвентаря

        elif event.type == pygame.MOUSEMOTION:
             if self.dragging_item:
                 # Позиция перетаскиваемого предмета обновляется при отрисовке.
                 # Здесь можно добавить логику для проверки наведения на слоты,
                 # если хотите визуально подсвечивать целевой слот.
                 pass


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
        if self.inventory_open: # Проверяем клик по инвентарю только если он открыт
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
        if self.inventory_open: # Проверяем клик по инвентарю только если он открыт
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

        # Убедитесь, что item является экземпляром Item и имеет изображение
        if not isinstance(item, Item) or not hasattr(item, 'image') or not item.image:
            return None # Возвращаем None, если предмет невалиден для отрисовки

        item_image = item.image
        img_width, img_height = item_image.get_size()

        if slot_info[0] == 'hotbar':
            index = slot_info[1]
            panel_width = len(self.hotbar_slots) * (self.hotbar_slot_size + self.hotbar_slot_padding) + self.hotbar_panel_padding
            panel_height = self.hotbar_slot_size + 2 * self.hotbar_panel_padding
            panel_x = (screen.get_width() - panel_width) // 2
            panel_y = screen.get_height() - panel_height - 10
            slot_x = panel_x + self.hotbar_panel_padding + index * (self.hotbar_slot_size + self.hotbar_slot_padding)
            slot_y = panel_y + self.hotbar_panel_padding

            item_slot_size = 40 # Размер для отрисовки в слоте хотбара

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

            item_slot_size = 50 # Размер для отрисовки в слоте инвентаря

            scale_factor = min(item_slot_size / img_width, item_slot_size / img_height)
            scaled_width = int(img_width * scale_factor)
            scaled_height = int(img_height * scale_factor)

            img_x = slot_x + (self.inventory_slot_size - scaled_width) // 2
            img_y = slot_y + (self.inventory_slot_size - scaled_height) // 2

            return pygame.Rect(img_x, img_y, scaled_width, scaled_height)

        return None # Неизвестный тип слота

    def place_item_in_slot(self, item_to_place: Item, target_slot_info, source_slot_info=None):
        """
        Помещает предмет в целевой слот.
        Обрабатывает обмен и стакание.
        Возвращает True при успехе, False при неудаче.
        """
        if not item_to_place:
            return False
        target_type = target_slot_info[0]
        target_index = target_slot_info[1] if target_type == 'hotbar' else None
        target_row, target_col = (target_slot_info[1], target_slot_info[2]) if target_type == 'inventory' else (
        None, None)
        current_item_in_target = None
        if target_type == 'hotbar':
            if 0 <= target_index < len(self.hotbar_slots):
                current_item_in_target = self.hotbar_slots[target_index]
        elif target_type == 'inventory':
            if 0 <= target_row < self.inventory_rows and 0 <= target_col < self.inventory_cols:
                current_item_in_target = self.inventory[target_row][target_col]
        else:
            return False
        # --- Логика стакания ---
        if item_to_place.stackable and current_item_in_target and \
                current_item_in_target.name == item_to_place.name and \
                current_item_in_target.quantity < current_item_in_target.max_stack:

            space_available = current_item_in_target.max_stack - current_item_in_target.quantity
            amount_to_move = item_to_place.quantity

            if amount_to_move <= space_available:
                # Весь предмет помещается в существующий стек
                current_item_in_target.quantity += amount_to_move
                if source_slot_info:
                    self._remove_item_from_slot(source_slot_info)  # Очищаем исходный слот
                return True
            else:
                # Часть предмета помещается, остальное остается
                current_item_in_target.quantity += space_available
                item_to_place.quantity -= space_available
                # !!! ОЧЕНЬ ВАЖНО !!! Если предмет был взят из source_slot_info
                # и его количество уменьшилось (item_to_place.quantity > 0),
                # то нужно вернуть оставшееся количество в source_slot_info.
                # Это должно быть сделано внешней логикой в handle_input после вызова place_item_in_slot,
                # если place_item_in_slot вернуло False (что означает, что не все поместилось).
                return False  # Возвращаем False, чтобы сообщить, что не все помещено
        # --- Логика обмена или размещения в пустой слот ---
        if current_item_in_target is None:
            # Целевой слот пуст - просто помещаем предмет
            if target_type == 'hotbar':
                self.hotbar_slots[target_index] = item_to_place
            elif target_type == 'inventory':
                self.inventory[target_row][target_col] = item_to_place

            if source_slot_info:
                self._remove_item_from_slot(source_slot_info)  # Очищаем исходный слот
            return True
        else:
            # Целевой слот занят и стакание невозможно - пробуем обменять
            if source_slot_info:
                # Обмениваем предметы: сначала текущий предмет из целевого слота помещаем в исходный
                self._place_item_in_slot_direct(current_item_in_target, source_slot_info)
                # Затем перетаскиваемый предмет помещаем в целевой слот
                if target_type == 'hotbar':
                    self.hotbar_slots[target_index] = item_to_place
                elif target_type == 'inventory':
                    self.inventory[target_row][target_col] = item_to_place
                return True
            else:
                # Целевой слот занят, и нет исходного слота (нельзя обменять)
                return False

    def _remove_item_from_slot(self, slot_info):
        """Вспомогательный метод для удаления предмета из слота."""
        slot_type = slot_info[0]
        if slot_type == 'hotbar':
            index = slot_info[1]
            if 0 <= index < len(self.hotbar_slots):
                self.hotbar_slots[index] = None
                # print(f"Предмет удален из хотбар слота {index}.") # Отладочный принт
            # else:
                # print(f"Ошибка удаления: Неверный индекс хотбар слота {index}") # Отладочный принт

        elif slot_type == 'inventory':
            row, col = slot_info[1], slot_info[2]
            if 0 <= row < self.inventory_rows and 0 <= col < self.inventory_cols:
                 self.inventory[row][col] = None
                 # print(f"Предмет удален из инвентарь слота ({row}, {col}).") # Отладочный принт
            # else:
                # print(f"Ошибка удаления: Неверные координаты инвентарь слота ({row}, {col})") # Отладочный принт

    def _place_item_in_slot_direct(self, item, slot_info):
        """Вспомогательный метод для прямого помещения предмета в слот (без проверок)."""
        if not item:
            # print("Попытка напрямую поместить None.") # Отладочный принт
            return

        slot_type = slot_info[0]
        if slot_type == 'hotbar':
            index = slot_info[1]
            if 0 <= index < len(self.hotbar_slots):
                self.hotbar_slots[index] = item
                # print(f"Предмет {item.name} напрямую помещен в хотбар слот {index}.") # Отладочный принт
            # else:
                # print(f"Ошибка прямого размещения: Неверный индекс хотбар слота {index}") # Отладочный принт

        elif slot_type == 'inventory':
            row, col = slot_info[1], slot_info[2]
            if 0 <= row < self.inventory_rows and 0 <= col < self.inventory_cols:
                 self.inventory[row][col] = item
                 # print(f"Предмет {item.name} напрямую помещен в инвентарь слот ({row}, {col}).") # Отладочный принт
            # else:
                # print(f"Ошибка прямого размещения: Неверные координаты инвентаря слота ({row}, {col})") # Отладочный принт



    def remove_item_from_inventory(self, item_to_remove, quantity=1):
        # Сначала проверяем хотбар
        for i, item in enumerate(self.hotbar_slots):
            if item and item.name == item_to_remove.name:
                if item.stackable:
                    if item.quantity > quantity:
                        item.quantity -= quantity
                        return True
                    elif item.quantity == quantity:
                        self.hotbar_slots[i] = None
                        return True
                else:
                    self.hotbar_slots[i] = None
                    return True

        # Затем основной инвентарь
        for r in range(self.inventory_rows):
            for c in range(self.inventory_cols):
                item = self.inventory[r][c]
                if item and item.name == item_to_remove.name:
                    if item.stackable:
                        if item.quantity > quantity:
                            item.quantity -= quantity
                            return True
                        elif item.quantity == quantity:
                            self.inventory[r][c] = None
                            return True
                    else:
                        self.inventory[r][c] = None
                        return True
        return False


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
                # Увеличиваем размер рамки и сдвигаем ее для центрирования вокруг слота
                border_size = 3 # Толщина рамки
                border_offset = 5 # Отступ рамки от слота
                pygame.draw.rect(screen, (255, 215, 0),
                                 (slot_x - border_offset, slot_y - border_offset,
                                  self.hotbar_slot_size + 2 * border_offset, self.hotbar_slot_size + 2 * border_offset),
                                 border_size, border_radius=10)


            # Отрисовка фона слота
            pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, self.hotbar_slot_size, self.hotbar_slot_size), border_radius=5)

            # Отрисовка предмета в слоте (если он не перетаскивается)
            if item and item is not self.dragging_item:
                self._draw_item_in_slot(screen, item, slot_x, slot_y, self.hotbar_slot_size, item_slot_size=40) # item_slot_size из вашей отрисовки

        # --- Отрисовка инвентаря (если открыт) ---
        if self.inventory_open: # Проверяем флаг inventory_open перед отрисовкой основного инвентаря

            inventory_width = self.inventory_cols * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_height = self.inventory_rows * (self.inventory_slot_size + self.inventory_slot_padding) + self.inventory_panel_padding
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2 # Позиция по Y для центрирования инвентаря

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
        # --- Конец отрисовки инвентаря ---


        # Отрисовка перетаскиваемого предмета (всегда поверх всего)
        if self.dragging_item and self.dragging_item.image:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Вычисляем позицию для отрисовки перетаскиваемого предмета с учетом смещения
            draw_x = mouse_x - self.drag_offset[0]
            draw_y = mouse_y - self.drag_offset[1]

            # Масштабируем изображение предмета для перетаскивания (используем размер инвентарного слота для единообразия)
            item_image = self.dragging_item.image
            img_width, img_height = item_image.get_size()
            drag_size = 50 # Размер для перетаскивания (можно сделать настраиваемым)
            scale_factor = min(drag_size / img_width, drag_size / img_height)
            scaled_width = int(img_width * scale_factor)
            scaled_height = int(img_height * scale_factor)

            # Масштабируем изображение
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

            # Отображаем количество, если предмет стакается и количество > 1
            if item.stackable and item.quantity > 1:
                quantity_text = self.game_manager.fonts['small'].render(str(item.quantity), True, (255, 255, 255))
                text_rect = quantity_text.get_rect(bottomright=(slot_x + slot_size - 5, slot_y + slot_size - 5))
                screen.blit(quantity_text, text_rect)

    def remove_item_from_inventory(self, item_to_remove, quantity=1):
        """
        Удаляет указанное количество предмета из инвентаря или хотбара.
        Возвращает True, если удаление успешно, False в противном случае.
        """
        removed_count = 0
        # Сначала пытаемся удалить из хотбара
        for i in range(len(self.hotbar_slots)):
            current_item = self.hotbar_slots[i]
            if current_item and current_item.name == item_to_remove.name:
                # В упрощенном варианте просто обнуляем слот
                self.hotbar_slots[i] = None
                removed_count += 1
                print(f"Удален 1 {item_to_remove.name} из хотбара.")
                if removed_count >= quantity:
                    return True  # Успешно удалили нужное количество
        # Если нужно удалить больше, чем есть в хотбаре, ищем в основном инвентаре
        # В текущей простой реализации инвентаря это может быть сложно.
        # В более продвинутой системе инвентаря нужно будет учитывать стаки предметов.
        # В текущей структуре, где каждый слот - отдельный предмет,
        # просто ищем и удаляем нужное количество экземпляров.
        if removed_count < quantity:
            print(
                f"Нужно удалить еще {quantity - removed_count} {item_to_remove.name} из основного инвентаря (пока не реализовано).")
            # TODO: Реализовать поиск и удаление из основного инвентаря
            # Простая заглушка: если удалили из хотбара, считаем успешным.
            # Если не удалили из хотбара, но нужно удалить, это ошибка в этой реализации.
            if removed_count > 0:
                return True  # Если что-то удалили из хотбара, считаем успешным для данного запроса
            else:
                print(f"Не удалось найти {item_to_remove.name} в инвентаре для удаления.")
                return False  # Не найдено предмета для удаления
        return removed_count >= quantity  # Возвращаем True, если удалили нужное количество
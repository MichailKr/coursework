# shop.py
import pygame
import os
from src.item import Item, Tool, Seed, Mater

class ShopItem:
    """Класс для предметов в магазине"""
    def __init__(self, item, buy_price, sell_price=None):
        self.item = item
        self.buy_price = buy_price
        self.sell_price = sell_price if sell_price is not None else buy_price // 2
        self.quantity = 999  # Бесконечное количество в магазине


class Shop:
    """Класс магазина"""
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.is_open = False
        self.current_tab = "buy"  # "buy" или "sell"
        self.selected_item_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 6  # Максимальное количество видимых предметов
        self.shop_x, self.shop_y = 1000, 1000
        self.shop_range = 35
        self.position_set = False
        self.shop_items = self.init_shop_items()
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 12)

    def toggle_shop(self):
        """Открывает/закрывает магазин"""
        self.is_open = not self.is_open
        self.selected_item_index = 0
        self.scroll_offset = 0

    def set_position_from_spawn(self):
        """Устанавливает позицию магазина относительно точки спавна"""
        if not self.position_set:
            try:
                self.shop_x, self.shop_y = 500, 1010
                self.position_set = True
            except AttributeError:
                pass

    def init_shop_items(self):
        """Инициализация товаров магазина"""
        items = []
        
        if hasattr(self.game_manager, 'tools') and 'hoe' in self.game_manager.tools:
            items.append(ShopItem(self.game_manager.tools['hoe'], 100))
        
        item_sprites_seed_path = os.path.join("sprites", "items")
        item_sprites_plants = os.path.join("sprites", "plants", "grownPlants")
        item_sprites_mat_path = os.path.join("sprites", "materials")

        try:
            wheat_seed_image = pygame.image.load(os.path.join(item_sprites_seed_path, "wheat_plant.png")).convert_alpha()
            tomato_seed_image = pygame.image.load(os.path.join(item_sprites_seed_path, "tomato_plant.png")).convert_alpha()
            brick_image = pygame.image.load(os.path.join(item_sprites_mat_path, "brick.png")).convert_alpha()
            wood_image = pygame.image.load(os.path.join(item_sprites_mat_path, "wood.png")).convert_alpha()

            bricks = Mater("Кирпичи", brick_image, "brick")
            wood = Mater("Доски", wood_image, "wood")
            wheat_seed = Seed("Семена пшеницы", wheat_seed_image, "wheat")
            tomato_seed = Seed("Семена томатов", tomato_seed_image, "tomato")
            
            items.append(ShopItem(wheat_seed, 20))
            items.append(ShopItem(tomato_seed, 30))
            items.append(ShopItem(bricks, 200))
            items.append(ShopItem(wood, 150))

            wheat_plant_image = pygame.image.load(os.path.join(item_sprites_plants, "wheat.png")).convert_alpha()
            tomato_plant_image = pygame.image.load(os.path.join(item_sprites_plants, "tomato.png")).convert_alpha()
            
            wheat_plant = Item("Пшеница", wheat_plant_image, "plant")
            tomato_plant = Item("Томаты", tomato_plant_image, "plant")
            
            # Фиксированные цены продажи для растений
            items.append(ShopItem(wheat_plant, 0, 100))
            items.append(ShopItem(tomato_plant, 0, 150))
            
        except Exception as e:
            print(f"Ошибка при создании предметов для магазина: {e}")
            wheat_plant_image = pygame.Surface((32, 32))
            wheat_plant_image.fill((210, 180, 140))
            tomato_plant_image = pygame.Surface((32, 32))
            tomato_plant_image.fill((255, 99, 71))
            
            wheat_plant = Item("Пшеница", wheat_plant_image, "plant")
            tomato_plant = Item("Томаты", tomato_plant_image, "plant")
            
            items.append(ShopItem(wheat_plant, 0, 100))
            items.append(ShopItem(tomato_plant, 0, 150))
        
        return items

    def is_player_in_range(self):
        """Проверяет, находится ли игрок в радиусе действия магазина"""
        if not self.position_set:
            self.set_position_from_spawn()
        player = self.game_manager.player
        distance = ((player.rect.centerx - self.shop_x) ** 2 +
                   (player.rect.centery - self.shop_y) ** 2) ** 0.5
        return distance <= self.shop_range

    def handle_input(self, keys, events):
        """Обработка ввода для магазина"""
        if not self.is_open:
            if self.is_player_in_range():
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        self.toggle_shop()
                        return True
            return False
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_shop()
                    return True
                elif event.key == pygame.K_TAB:
                    self.switch_tab()
                    return True
                elif event.key == pygame.K_UP:
                    if self.selected_item_index > 0:
                        self.selected_item_index -= 1
                        # Прокрутка вверх, если выбранный элемент вышел за пределы видимой области
                        if self.selected_item_index < self.scroll_offset:
                            self.scroll_offset = self.selected_item_index
                    return True
                elif event.key == pygame.K_DOWN:
                    items = self.get_current_items()
                    if self.selected_item_index < len(items) - 1:
                        self.selected_item_index += 1
                        # Прокрутка вниз, если выбранный элемент вышел за пределы видимой области
                        if self.selected_item_index >= self.scroll_offset + self.max_visible_items:
                            self.scroll_offset += 1
                    return True
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.execute_transaction()
                    return True
        return False

    def get_current_items(self):
        """Возвращает список предметов для текущей вкладки"""
        if self.current_tab == "buy":
            return [item for item in self.shop_items if item.buy_price > 0]
        else:
            # Получаем реальные предметы из инвентаря игрока
            inventory_items = []
            if hasattr(self.game_manager, 'inventory_manager'):
                # Добавляем предметы из хотбара
                for item in self.game_manager.inventory_manager.hotbar_slots:
                    if item:
                        inventory_items.append(item)
                # Добавляем предметы из основного инвентаря
                for row in self.game_manager.inventory_manager.inventory:
                    for item in row:
                        if item:
                            inventory_items.append(item)
            
            # Добавляем предметы из магазина, которые можно продать (sell_price > 0)
            shop_sellable_items = [item.item for item in self.shop_items if item.sell_price > 0]
            
            # Объединяем списки и убираем дубликаты
            all_items = inventory_items + shop_sellable_items
            unique_items = []
            seen_names = set()
            for item in all_items:
                if item.name not in seen_names:
                    seen_names.add(item.name)
                    unique_items.append(item)
            
            return unique_items

    def get_player_item_quantity(self, item_name):
        """Возвращает общее количество предмета у игрока"""
        total = 0
        if hasattr(self.game_manager, 'inventory_manager'):
            # Проверяем хотбар
            for item in self.game_manager.inventory_manager.hotbar_slots:
                if item and item.name == item_name:
                    total += item.quantity if hasattr(item, 'quantity') else 1
            
            # Проверяем основной инвентарь
            for row in self.game_manager.inventory_manager.inventory:
                for item in row:
                    if item and item.name == item_name:
                        total += item.quantity if hasattr(item, 'quantity') else 1
        return total

    def switch_tab(self):
        """Переключение между вкладками покупки и продажи"""
        self.current_tab = "sell" if self.current_tab == "buy" else "buy"
        self.selected_item_index = 0
        self.scroll_offset = 0

    def execute_transaction(self):
        """Выполнение покупки или продажи"""
        items = self.get_current_items()
        if not items or self.selected_item_index >= len(items):
            return
            
        if self.current_tab == "buy":
            self.buy_item(items[self.selected_item_index])
        else:
            self.sell_item(items[self.selected_item_index])

    def buy_item(self, shop_item):
        """Покупка предмета из магазина"""
        player = self.game_manager.player
        if player.coins >= shop_item.buy_price:
            player.remove_coins(shop_item.buy_price)
            if hasattr(self.game_manager, 'inventory_manager'):
                new_item = type(shop_item.item)(shop_item.item.name, shop_item.item.image, shop_item.item.type)
                for attr, value in shop_item.item.__dict__.items():
                    if attr not in ['name', 'image', 'type', 'stackable', 'max_stack', 'quantity']:
                        setattr(new_item, attr, value)
                new_item.quantity = 1  # Покупаем по одному предмету
                
                success = self.game_manager.inventory_manager.add_item_to_inventory(new_item)
                if not success:
                    player.add_coins(shop_item.buy_price)
                    print("Не удалось добавить предмет в инвентарь")

    def sell_item(self, item_to_sell):
        """Продажа предмета из инвентаря игрока"""
        # Находим предмет в магазине для определения цены
        shop_item = None
        for si in self.shop_items:
            if si.item.name == item_to_sell.name:
                shop_item = si
                break
        
        # Если предмет не найден в магазине, но есть в списке для покупки
        if not shop_item:
            for si in self.shop_items:
                if si.item.name == item_to_sell.name and si.buy_price > 0:
                    shop_item = ShopItem(si.item, si.buy_price, si.buy_price // 2)
                    break
        
        if not shop_item or shop_item.sell_price <= 0:
            print(f"Предмет {item_to_sell.name} не может быть продан")
            return

        # Получаем количество этого предмета у игрока
        player_quantity = self.get_player_item_quantity(item_to_sell.name)
        if player_quantity <= 0:
            print(f"У игрока нет предмета {item_to_sell.name} для продажи")
            return

        # Продаем по одному предмету
        if hasattr(self.game_manager, 'inventory_manager'):
            # Находим первый слот с этим предметом
            item_found = None
            inventory_manager = self.game_manager.inventory_manager
            
            # Проверяем хотбар
            for i, item in enumerate(inventory_manager.hotbar_slots):
                if item and item.name == item_to_sell.name:
                    item_found = ('hotbar', i)
                    break
            
            # Если не нашли в хотбаре, проверяем основной инвентарь
            if not item_found:
                for row in range(len(inventory_manager.inventory)):
                    for col in range(len(inventory_manager.inventory[row])):
                        item = inventory_manager.inventory[row][col]
                        if item and item.name == item_to_sell.name:
                            item_found = ('inventory', row, col)
                            break
                    if item_found:
                        break
            
            if item_found:
                # Уменьшаем количество или удаляем предмет
                if item_found[0] == 'hotbar':
                    slot_item = inventory_manager.hotbar_slots[item_found[1]]
                    if slot_item.quantity > 1:
                        slot_item.quantity -= 1
                    else:
                        inventory_manager.hotbar_slots[item_found[1]] = None
                else:  # inventory
                    slot_item = inventory_manager.inventory[item_found[1]][item_found[2]]
                    if slot_item.quantity > 1:
                        slot_item.quantity -= 1
                    else:
                        inventory_manager.inventory[item_found[1]][item_found[2]] = None
                
                # Начисляем деньги
                self.game_manager.player.add_coins(shop_item.sell_price)
                print(f"Продан 1 {item_to_sell.name} за {shop_item.sell_price} монет")
            else:
                print(f"Не удалось найти предмет {item_to_sell.name} в инвентаре")

    def draw(self, screen):
        """Отрисовка магазина"""
        if not self.is_open and self.is_player_in_range():
            self.draw_shop_hint(screen)
        if self.is_open:
            self.draw_shop_window(screen)

    def draw_shop_hint(self, screen):
        """Отрисовка подсказки об открытии магазина"""
        hint_text = "Нажмите E для открытия магазина"
        text_surface = self.font.render(hint_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.centerx = screen.get_width() // 2
        text_rect.y = screen.get_height() - 150
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        screen.blit(text_surface, text_rect)

    def draw_shop_window(self, screen):
        """Отрисовка окна магазина с исправленными отступами"""
        window_width = 620  # Немного увеличим ширину для лучшего отображения
        window_height = 540  # Увеличим высоту для всех элементов
        window_x = (screen.get_width() - window_width) // 2
        window_y = (screen.get_height() - window_height) // 2
        
        # Фон окна
        pygame.draw.rect(screen, (40, 40, 40), (window_x, window_y, window_width, window_height), border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), (window_x, window_y, window_width, window_height), 3, border_radius=10)
        
        # Заголовок
        title = "МАГАЗИН"
        title_surface = self.font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=window_x + window_width // 2, y=window_y + 15)
        screen.blit(title_surface, title_rect)
        
        # Вкладки
        self.draw_tabs(screen, window_x + 10, window_y + 50, window_width - 20)
        
        # Область списка предметов (оставляем больше места снизу)
        list_area_height = window_height - 170  # 170px отступ снизу
        list_area = pygame.Rect(
            window_x + 15, 
            window_y + 100, 
            window_width - 30, 
            list_area_height
        )
        pygame.draw.rect(screen, (30, 30, 30), list_area, border_radius=5)
        
        # Список предметов с обрезкой по области
        self.draw_item_list(screen, list_area)
        
        # Инструкции в правом нижнем углу (с фиксированным положением)
        instructions = "↑/↓: Выбор | ENTER/SPACE: Действие | TAB: Вкладки | E: Закрыть"
        instruction_text = self.small_font.render(instructions, True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(centerx=window_x + window_width // 2, 
                                                bottom=window_y + window_height - 10)
        # Фон для текста
        pygame.draw.rect(screen, (0, 0, 0, 180), 
                        (instruction_rect.x - 10, instruction_rect.y - 5,
                        instruction_rect.width + 20, instruction_rect.height + 10),
                        border_radius=5)
        screen.blit(instruction_text, instruction_rect)
        
        

    def draw_tabs(self, screen, x, y, width):
        """Отрисовка вкладок магазина"""
        tab_width = width // 2
        buy_color = (60, 60, 60) if self.current_tab == "buy" else (30, 30, 30)
        pygame.draw.rect(screen, buy_color, (x, y, tab_width, 40), border_radius=5)
        if self.current_tab == "buy":
            pygame.draw.rect(screen, (0, 255, 0), (x, y, tab_width, 40), 2, border_radius=5)
        buy_text = self.font.render("ПОКУПКА", True, (255, 255, 255))
        buy_rect = buy_text.get_rect(center=(x + tab_width // 2, y + 20))
        screen.blit(buy_text, buy_rect)
        
        sell_color = (60, 60, 60) if self.current_tab == "sell" else (30, 30, 30)
        pygame.draw.rect(screen, sell_color, (x + tab_width, y, tab_width, 40), border_radius=5)
        if self.current_tab == "sell":
            pygame.draw.rect(screen, (0, 255, 0), (x + tab_width, y, tab_width, 40), 2, border_radius=5)
        sell_text = self.font.render("ПРОДАЖА", True, (255, 255, 255))
        sell_rect = sell_text.get_rect(center=(x + tab_width + tab_width // 2, y + 20))
        screen.blit(sell_text, sell_rect)

    def draw_item_list(self, screen, list_area):
        """Отрисовка списка предметов с прокруткой"""
        items = self.get_current_items()
        if not items:
            no_items_text = "Нет предметов" if self.current_tab == "sell" else "Магазин пуст"
            text = self.font.render(no_items_text, True, (200, 200, 200))
            text_rect = text.get_rect(center=list_area.center)
            screen.blit(text, text_rect)
            return
        
        item_height = 60
        visible_items = min(self.max_visible_items, len(items) - self.scroll_offset)
        
        # Обрезаем область отрисовки
        old_clip = screen.get_clip()
        screen.set_clip(list_area)
        
        for i in range(visible_items):
            item_index = i + self.scroll_offset
            if item_index >= len(items):
                break
                
            item_y = list_area.y + i * item_height
            is_selected = item_index == self.selected_item_index
            
            # Фон элемента
            if is_selected:
                pygame.draw.rect(screen, (80, 80, 80), 
                                (list_area.x, item_y, list_area.width, item_height - 5), border_radius=5)
            else:
                pygame.draw.rect(screen, (50, 50, 50), 
                                (list_area.x, item_y, list_area.width, item_height - 5), border_radius=5)
            
            # Отрисовка предмета
            if self.current_tab == "buy":
                self.draw_shop_item(screen, self.shop_items[item_index], list_area.x + 10, item_y, list_area.width - 20)
            else:
                self.draw_inventory_item(screen, items[item_index], list_area.x + 10, item_y, list_area.width - 20)
        
        # Восстанавливаем область отрисовки
        screen.set_clip(old_clip)
        
        # Полоса прокрутки, если нужно
        if len(items) > self.max_visible_items:
            scroll_height = list_area.height * self.max_visible_items / len(items)
            scroll_y = list_area.y + (list_area.height - scroll_height) * self.scroll_offset / (len(items) - self.max_visible_items)
            pygame.draw.rect(screen, (100, 100, 100), (list_area.right - 10, scroll_y, 8, scroll_height), border_radius=4)

    def draw_shop_item(self, screen, shop_item, x, y, width):
        """Отрисовка предмета в магазине"""
        if hasattr(shop_item.item, 'image') and shop_item.item.image:
            item_image = pygame.transform.scale(shop_item.item.image, (40, 40))
            screen.blit(item_image, (x, y + 10))
        else:
            pygame.draw.rect(screen, (100, 100, 100), (x, y + 10, 40, 40))
        
        name_text = self.font.render(shop_item.item.name, True, (255, 255, 255))
        screen.blit(name_text, (x + 60, y + 10))
        
        price_text = f"Цена: {shop_item.buy_price} монет"
        price_surface = self.small_font.render(price_text, True, (255, 215, 0))
        screen.blit(price_surface, (x + 60, y + 35))

    def draw_inventory_item(self, screen, item, x, y, width):
        """Отрисовка предмета из инвентаря для продажи"""
        if hasattr(item, 'image') and item.image:
            item_image = pygame.transform.scale(item.image, (40, 40))
            screen.blit(item_image, (x, y + 10))
        else:
            pygame.draw.rect(screen, (100, 100, 100), (x, y + 10, 40, 40))
        
        name_text = self.font.render(item.name, True, (255, 255, 255))
        screen.blit(name_text, (x + 60, y + 10))
        
        # Получаем цену продажи
        sell_price = 0
        for si in self.shop_items:
            if si.item.name == item.name:
                sell_price = si.sell_price if si.sell_price > 0 else si.buy_price // 2
                break
        
        # Получаем количество у игрока
        quantity = self.get_player_item_quantity(item.name)
        
        if sell_price > 0 and quantity > 0:
            price_text = f"Цена: {sell_price} монет (есть: {quantity})"
            price_surface = self.small_font.render(price_text, True, (0, 255, 0))
        elif sell_price > 0:
            price_text = f"Цена: {sell_price} монет (нет в инвентаре)"
            price_surface = self.small_font.render(price_text, True, (255, 0, 0))
        else:
            price_text = "Нельзя продать"
            price_surface = self.small_font.render(price_text, True, (255, 0, 0))
        
        screen.blit(price_surface, (x + 60, y + 35))
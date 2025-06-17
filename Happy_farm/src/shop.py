# shop.py
import pygame
import os
from src.item import Item, Tool, Seed, Mater

class ShopItem:
    """Класс для предметов в магазине"""
    def __init__(self, item, buy_price, sell_price=None):
        self.item = item
        self.buy_price = buy_price
        self.sell_price = sell_price if sell_price else buy_price // 2
        self.quantity = 999  # Бесконечное количество в магазине


class Shop:
    """Класс магазина"""
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.is_open = False
        self.current_tab = "buy"  # "buy" или "sell"
        self.selected_item_index = 0
        self.scroll_offset = 0
        # Позиция магазина - устанавливаем позицию по умолчанию
        # Позиция будет обновлена после загрузки карты
        self.shop_x, self.shop_y = 1000, 1000
        self.shop_range = 35  # Радиус действия магазина
        self.position_set = False  # Флаг для отслеживания установки позиции
        # Товары магазина
        self.shop_items = self.init_shop_items()
        # UI параметры
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 12)

    def toggle_shop(self):
        """Открывает/закрывает магазин"""
        self.is_open = not self.is_open
        print("Магазин открыт/закрыт")

    def set_position_from_spawn(self):
        """Устанавливает позицию магазина относительно точки спавна"""
        if not self.position_set:
            try:
                self.shop_x, self.shop_y = 500, 1010
                self.position_set = True
                print(f"Позиция магазина установлена: ({self.shop_x}, {self.shop_y})")
            except AttributeError:
                # Карта еще не загружена, используем позицию по умолчанию
                pass

    def init_shop_items(self):
        """Инициализация товаров магазина"""
        items = []
        
        # Добавляем инструменты из game_manager (только для покупки)
        if hasattr(self.game_manager, 'tools') and 'hoe' in self.game_manager.tools:
            items.append(ShopItem(self.game_manager.tools['hoe'], 100, 0))  # sell_price=0 - нельзя продать
        
        # Пути к спрайтам
        item_sprites_seed_path = os.path.join("sprites", "items")
        item_sprites_plants = os.path.join("sprites", "plants", "grownPlants")
        item_sprites_m_path = os.path.join("sprites", "materials")


        try:
            # Загружаем изображения для семян (только для покупки)
            wheat_seed_image = pygame.image.load(os.path.join(item_sprites_seed_path, "wheat_plant.png")).convert_alpha()
            tomato_seed_image = pygame.image.load(os.path.join(item_sprites_seed_path, "tomato_plant.png")).convert_alpha()
            brick_image = pygame.image.load(os.path.join(item_sprites_m_path, "brick.png")).convert_alpha()
            wood_image = pygame.image.load(os.path.join(item_sprites_m_path, "wood.png")).convert_alpha()

            # Предположим, что у вас есть ресурсы "Кирпичи" и "Доски"
            bricks = Mater("Кирпичи", brick_image, "brick")
            wood = Mater("Доски", wood_image, "wood")
            # Создаем экземпляры семян для магазина
            wheat_seed = Seed("Семена пшеницы", wheat_seed_image, "wheat")
            tomato_seed = Seed("Семена томатов", tomato_seed_image, "tomato")
            
            # Добавляем в магазин семена (только для покупки)
            items.append(ShopItem(wheat_seed, 20, 0))  # sell_price=0 - нельзя продать
            items.append(ShopItem(tomato_seed, 30, 0))  # sell_price=0 - нельзя продать
            items.append(ShopItem(bricks, 200, 0))  # sell_price=0 - нельзя продать
            items.append(ShopItem(wood, 150, 0))  # sell_price=0 - нельзя продать
            
            # Загружаем изображения растений (только для продажи)
            wheat_plant_image = pygame.image.load(os.path.join(item_sprites_plants, "wheat.png")).convert_alpha()
            tomato_plant_image = pygame.image.load(os.path.join(item_sprites_plants, "tomato.png")).convert_alpha()
            
            # Создаем экземпляры растений для продажи
            wheat_plant = Item("Пшеница", wheat_plant_image, "plant")
            tomato_plant = Item("Томаты", tomato_plant_image, "plant")
            
            # Добавляем растения (только для продажи - buy_price=0)
            items.append(ShopItem(wheat_plant, 0, 100))  # Цена продажи 100
            items.append(ShopItem(tomato_plant, 0, 150))  # Цена продажи 150
            
        except Exception as e:
            print(f"Ошибка при создании предметов для магазина: {e}")
            # Создаем заглушки для растений
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
        # Обновляем позицию магазина если она еще не установлена
        if not self.position_set:
            self.set_position_from_spawn()
        player = self.game_manager.player
        distance = ((player.rect.centerx - self.shop_x) ** 2 +
                   (player.rect.centery - self.shop_y) ** 2) ** 0.5
        return distance <= self.shop_range

    def handle_input(self, keys, events):
        """Обработка ввода для магазина"""
        if not self.is_open:
            # Проверяем, нужно ли показать подсказку об открытии магазина
            if self.is_player_in_range():
                # Обработка открытия магазина
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        self.toggle_shop()
                        return True 
            return False
        # Обработка ввода когда магазин открыт
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_shop()
                    return True
                elif event.key == pygame.K_TAB:
                    self.switch_tab()
                    return True
                elif event.key == pygame.K_UP:
                    self.selected_item_index = max(0, self.selected_item_index - 1)
                    return True
                elif event.key == pygame.K_DOWN:
                    max_index = len(self.get_current_items()) - 1
                    self.selected_item_index = min(max_index, self.selected_item_index + 1)
                    return True
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.execute_transaction()
                    return True
        return False

    def get_current_items(self):
        """Возвращает список предметов для текущей вкладки"""
        if self.current_tab == "buy":
            # Возвращаем только предметы для покупки (buy_price > 0)
            return [item for item in self.shop_items if item.buy_price > 0]
        else:  # sell tab
            # Возвращаем только предметы для продажи (sell_price > 0 и buy_price == 0)
            return [item.item for item in self.shop_items if item.sell_price > 0 and item.buy_price == 0]

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
        player = self.game_manager.player
        if player.coins >= shop_item.buy_price:
            player.remove_coins(shop_item.buy_price)
            if hasattr(self.game_manager, 'inventory_manager'):
                # Создаем копию предмета с начальным количеством
                new_item = type(shop_item.item)(shop_item.item.name, shop_item.item.image, shop_item.item.item_type)
                # Копируем все атрибуты из исходного предмета
                for attr, value in shop_item.item.__dict__.items():
                    if attr not in ['name', 'image', 'type', 'stackable', 'max_stack', 'quantity']:
                        setattr(new_item, attr, value)
                new_item.quantity = 5  # Например, покупаем 5 семян за раз
                
                success = self.game_manager.inventory_manager.add_item_by_slot_or_find(new_item)
                if not success:
                    player.add_coins(shop_item.buy_price)

    def sell_item(self, item):
        """Продажа предмета из инвентаря игрока"""
        if not item:
            print("Ошибка: Предмет не указан")
            return

        # Находим соответствующий товар в магазине для определения цены
        shop_item = None
        for si in self.shop_items:
            if si.item.name == item.name:
                shop_item = si
                break

        if not shop_item:
            print("Этот предмет нельзя продать в магазине")
            return

        # Проверяем, есть ли InventoryManager
        if not hasattr(self.game_manager, 'inventory_manager'):
            print("Ошибка: InventoryManager не найден")
            return

        # Удаляем предмет из инвентаря через InventoryManager
        inventory_manager = self.game_manager.inventory_manager
        if hasattr(inventory_manager, 'remove_item_from_inventory'):
            success = inventory_manager.remove_item_from_inventory(item)
            if success:
                # Начисляем деньги игроку
                self.game_manager.player.add_coins(shop_item.sell_price)
                print(f"Продан предмет: {item.name} за {shop_item.sell_price} монет")
            else:
                print("Не удалось продать предмет (предмет не найден в инвентаре)")
        else:
            print("Ошибка: У InventoryManager нет метода remove_item_from_inventory")

    def draw(self, screen):
        """Отрисовка магазина"""
        # Отрисовка подсказки об открытии магазина
        if not self.is_open and self.is_player_in_range():
            self.draw_shop_hint(screen)
        # Отрисовка окна магазина
        if self.is_open:
            self.draw_shop_window(screen)

    def draw_shop_hint(self, screen):
        """Отрисовка подсказки об открытии магазина"""
        hint_text = "Нажмите E для открытия магазина"
        text_surface = self.font.render(hint_text, True, (255, 255, 255))
        # Позиционируем текст по центру экрана внизу
        text_rect = text_surface.get_rect()
        text_rect.centerx = screen.get_width() // 2
        text_rect.y = screen.get_height() - 150
        # Фон для текста
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        screen.blit(text_surface, text_rect)

    def draw_shop_window(self, screen):
        """Отрисовка окна магазина"""
        # Размеры окна магазина
        window_width = 600
        window_height = 500
        window_x = (screen.get_width() - window_width) // 2
        window_y = (screen.get_height() - window_height) // 2
        # Фон окна
        pygame.draw.rect(screen, (40, 40, 40), (window_x, window_y, window_width, window_height), border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), (window_x, window_y, window_width, window_height), 3, border_radius=10)
        # Заголовок
        title = "МАГАЗИН"
        title_surface = self.font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=window_x + window_width // 2, y=window_y + 10)
        screen.blit(title_surface, title_rect)
        # Вкладки
        self.draw_tabs(screen, window_x, window_y + 50, window_width)
        # Список предметов
        self.draw_item_list(screen, window_x, window_y + 100, window_width, window_height - 150)
        # Инструкции
        instructions = [
            "↑/↓ - выбор предмета",
            "ENTER/SPACE - купить/продать",
            "TAB - сменить вкладку",
            "E - закрыть"
        ]
        y_offset = window_y + window_height - 80
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (window_x + 10, y_offset))
            y_offset += 15

    def draw_tabs(self, screen, x, y, width):
        """Отрисовка вкладок магазина"""
        tab_width = width // 2
        # Вкладка покупки
        buy_color = (60, 60, 60) if self.current_tab == "buy" else (30, 30, 30)
        pygame.draw.rect(screen, buy_color, (x, y, tab_width, 40), border_radius=5)
        if self.current_tab == "buy":
            pygame.draw.rect(screen, (0, 255, 0), (x, y, tab_width, 40), 2, border_radius=5)
        buy_text = self.font.render("ПОКУПКА", True, (255, 255, 255))
        buy_rect = buy_text.get_rect(center=(x + tab_width // 2, y + 20))
        screen.blit(buy_text, buy_rect)
        # Вкладка продажи
        sell_color = (60, 60, 60) if self.current_tab == "sell" else (30, 30, 30)
        pygame.draw.rect(screen, sell_color, (x + tab_width, y, tab_width, 40), border_radius=5)
        if self.current_tab == "sell":
            pygame.draw.rect(screen, (0, 255, 0), (x + tab_width, y, tab_width, 40), 2, border_radius=5)
        sell_text = self.font.render("ПРОДАЖА", True, (255, 255, 255))
        sell_rect = sell_text.get_rect(center=(x + tab_width + tab_width // 2, y + 20))
        screen.blit(sell_text, sell_rect)

    def draw_item_list(self, screen, x, y, width, height):
        """Отрисовка списка предметов"""
        items = self.get_current_items()
        if not items:
            no_items_text = "Нет предметов" if self.current_tab == "sell" else "Магазин пуст"
            text = self.font.render(no_items_text, True, (200, 200, 200))
            text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
            screen.blit(text, text_rect)
            return
        item_height = 60
        visible_items = height // item_height
        for i in range(min(visible_items, len(items))):
            item_index = i + self.scroll_offset
            if item_index >= len(items):
                break
            item_y = y + i * item_height
            # Выделение выбранного предмета
            if item_index == self.selected_item_index:
                pygame.draw.rect(screen, (80, 80, 80), (x + 10, item_y, width - 20, item_height - 5), border_radius=5)
            if self.current_tab == "buy":
                self.draw_shop_item(screen, self.shop_items[item_index], x + 20, item_y, width - 40)
            else:
                self.draw_inventory_item(screen, items[item_index], x + 20, item_y, width - 40)

    def draw_shop_item(self, screen, shop_item, x, y, width):
        """Отрисовка предмета в магазине"""
        # Изображение предмета
        if hasattr(shop_item.item, 'image') and shop_item.item.image:
            item_image = pygame.transform.scale(shop_item.item.image, (40, 40))
            screen.blit(item_image, (x, y + 10))
        else:
            # Заглушка
            pygame.draw.rect(screen, (100, 100, 100), (x, y + 10, 40, 40))
        # Название предмета
        name_text = self.font.render(shop_item.item.name, True, (255, 255, 255))
        screen.blit(name_text, (x + 60, y + 10))
        # Цена
        price_text = f"Цена: {shop_item.buy_price} монет"
        price_surface = self.small_font.render(price_text, True, (255, 215, 0))
        screen.blit(price_surface, (x + 60, y + 35))

    def draw_inventory_item(self, screen, item, x, y, width):
        """Отрисовка предмета из инвентаря для продажи"""
        # Изображение предмета
        if hasattr(item, 'image') and item.image:
            item_image = pygame.transform.scale(item.image, (40, 40))
            screen.blit(item_image, (x, y + 10))
        else:
            # Заглушка
            pygame.draw.rect(screen, (100, 100, 100), (x, y + 10, 40, 40))
        # Название предмета
        name_text = self.font.render(item.name, True, (255, 255, 255))
        screen.blit(name_text, (x + 60, y + 10))
        # Цена продажи
        shop_item = None
        for si in self.shop_items:
            if si.item.name == item.name:
                shop_item = si
                break
        if shop_item:
            price_text = f"Цена: {shop_item.sell_price} монет"
            price_surface = self.small_font.render(price_text, True, (0, 255, 0))
        else:
            price_text = "Нельзя продать"
            price_surface = self.small_font.render(price_text, True, (255, 0, 0))
        screen.blit(price_surface, (x + 60, y + 35))
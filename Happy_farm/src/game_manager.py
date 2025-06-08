import pygame
from src.game_state import GameState
from src.screen_manager import ScreenManager
from src.event_handler import EventHandler
from src.render_manager import RenderManager
from src.player import Player
from src.camera import Camera
from src.item import Tool, Item # Импортируем также базовый класс Item
import pytmx
import os
import math
import time

class GameManager:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen_manager = ScreenManager()
        self.event_handler = EventHandler(self)
        self.render_manager = RenderManager(self.screen_manager)

        self.state = GameState.MENU
        self.running = True
        self.paused = False

        self.clock = pygame.time.Clock()
        self.clock_size = 75
        self.clock_bg = None
        self.clock_arrow = None
        self.clock_pos = None

        # игровое время
        self.game_time = 300 # Начинаем с начала дня для отладки
        self.last_time_update = 0 # последнее обновление

        # затемнение
        self.night_overlay = None
        self.is_night = False

        self.settings = {
            'sound_volume': 0.7,
            'music_volume': 0.5,
            'fullscreen': False,
            'fps_limit': 60,
            'vsync': True,
            'language': 'en',
            'controls': {
                'up': pygame.K_w,
                'down': pygame.K_s,
                'left': pygame.K_a,
                'right': pygame.K_d,
                'interact': pygame.K_e,
                'inventory': pygame.K_i,
                'menu': pygame.K_ESCAPE
            }
        }

        self.fonts = {
            'small': pygame.font.Font(None, 24),
            'medium': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 48)
        }

        # Инициализация инструментов
        self.tools = {} # Инициализируем пустой словарь инструментов

        # --- Загрузка изображений инструментов и создание объектов Tool ---
        # Используем более надежный способ формирования пути
        base_sprites_path = os.path.join("sprites", "player", "sprites_tools")
        hoe_image_path = os.path.join(base_sprites_path, 'hoe.png')

        try:
             hoe_image = pygame.image.load(hoe_image_path).convert_alpha()
             print(f"Изображение мотыги успешно загружено по пути: {hoe_image_path}")
             self.tools['hoe'] = Tool('Мотыга', hoe_image, 'hoe')
        except pygame.error as e:
             print(f"Ошибка загрузки изображения мотыги: {e}")
             print(f"Проверьте путь к файлу: {hoe_image_path}")
        except Exception as e:
             print(f"Произошла другая ошибка при создании объекта Tool для мотыги: {e}")


        # Добавьте загрузку и создание объектов для других инструментов аналогично
        # axe_image_path = os.path.join(base_sprites_path, 'axe.png')
        # try:
        #      axe_image = pygame.image.load(axe_image_path).convert_alpha()
        #      self.tools['axe'] = Tool('Топор', axe_image, 'axe')
        # except pygame.error as e:
        #      print(f"Ошибка загрузки изображения топора: {e}")
        #      print(f"Проверьте путь к файлу: {axe_image_path}")


        self.inventory_open = False
        self.selected_item_index = 0 # Индекс выбранного слота в хотбаре
        self.hotbar_slots = [None] * 8 # Список для хотбара (8 слотов)
        self.inventory = [[None for _ in range(3)] for _ in range(8)] # Основной инвентарь (8x3 слота)


        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        # Загрузка карты
        self.map_loaded = False
        self.tmx_data = None # Инициализируем до try/except

        self.soil_layer = 'Песочек' # Будет содержать объект слоя TiledTileLayer
        self.grass_layer = 'Травка' # Будет содержать объект слоя TiledTileLayer
        self.dirt_tile_gid = None # Будет содержать GID тайла земли

        # Слои коллизий (имена слоев из Tiled)
        self.collision_layers_names = ["Коллизия лес", "Колилзия горок", "Дом"]
        self.collision_layers = [] # Будет содержать объекты TiledTileLayer для коллизий


        try:
            # Используем более надежный способ формирования пути к карте
            map_path = os.path.join('maps', 'maps.tmx')
            self.tmx_data = pytmx.load_pygame(map_path)
            self.map_loaded = True
            print(f"Карта успешно загружена по пути: {map_path}")

            # Получаем объекты слоев после успешной загрузки карты
            self.soil_layer = self.tmx_data.get_layer_by_name('Песочек')
            self.grass_layer = self.tmx_data.get_layer_by_name('Травка')

            # Получаем объекты слоев коллизий
            for layer_name in self.collision_layers_names:
                 layer = self.tmx_data.get_layer_by_name(layer_name)
                 if layer and isinstance(layer, pytmx.TiledTileLayer):
                      self.collision_layers.append(layer)
                 else:
                     print(f"Предупреждение: Слой коллизии '{layer_name}' не найден или не является тайловым слоем.")


            # Получаем GID тайла земли по свойству
            self.dirt_tile_gid = self.get_tile_gid_by_property('type', 'dirt')

            # Проверки наличия слоев и GID
            if not self.soil_layer:
                print("Внимание: Слой 'Песочек' не найден в карте. Вспашка не будет работать корректно.")
            if not self.grass_layer:
                 print("Внимание: Слой 'Травка' не найден в карте. Вспашка не будет работать корректно.")
            if self.dirt_tile_gid is None:
                 print("Внимание: GID тайла земли не найден по свойству 'type'='dirt'. Вспашка не будет работать корректно.")

        except FileNotFoundError:
             print(f"Ошибка загрузки карты: Файл карты не найден по пути: {map_path}")
             self.map_loaded = False
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            self.map_loaded = False


        screen = self.screen_manager.get_screen()
        self.camera = Camera(screen.get_width(), screen.get_height())
        print(f"Камера создана с размерами {screen.get_width()}x{screen.get_height()}")

        self.init_clock(screen)

        if self.map_loaded and hasattr(self, 'tmx_data'):
            map_width = self.tmx_data.width * self.tmx_data.tilewidth
            map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.camera.set_map_size(map_width, map_height)
            print(f"Размеры карты для камеры установлены: {map_width}x{map_height}")

        self.init_game_objects()

        # Счётчик FPS
        self.fps = 0
        self.fps_counter = 0
        self.fps_timer = pygame.time.get_ticks()

        print("GameManager инициализирован успешно")

    # --- Методы для мотыги и инвентаря ---

    def get_tile_gid_by_property(self, property_name, property_value):
        """
        Вспомогательный метод для поиска GID тайла по его свойству,
        используя get_tile_properties_by_gid.
        """
        if not self.tmx_data:
            print("tmx_data не загружена в get_tile_gid_by_property")
            return None

        # Собираем все уникальные GID, используемые в карте и тайлсетах
        used_gids = set()

        # Собираем GIDы из слоев карты (это может быть полезно, но не обязательно для поиска по тайлсету)
        # for layer in self.tmx_data.visible_layers:
        #     if hasattr(layer, 'data'):
        #         # Используем метод tiles() слоя, который итерирует по (x, y, gid)
        #         for x, y, gid in layer.tiles():
        #             if gid != 0:
        #                 used_gids.add(gid)

        # Добавляем GIDы из всех тайлсетов - это основной способ найти GID по свойству тайлсета
        for tileset in self.tmx_data.tilesets:
            # Проверяем, что tileset имеет firstgid и tilecount
            if hasattr(tileset, 'firstgid') and hasattr(tileset, 'tilecount'):
                 # Итерируем по всем локальным ID тайлов в тайлсете
                 for tile_id in range(tileset.tilecount):
                      # Вычисляем глобальный GID
                      gid = tileset.firstgid + tile_id
                      used_gids.add(gid)


        # Проверяем свойства для каждого уникального GID, используя get_tile_properties_by_gid
        for gid in sorted(list(used_gids)): # Сортируем для предсказуемого порядка
            # !!! ИСПОЛЬЗУЕМ ПРАВИЛЬНЫЙ МЕТОД: get_tile_properties_by_gid !!!
            tile_properties = self.tmx_data.get_tile_properties_by_gid(gid)

            # Проверяем свойства тайла
            if tile_properties and property_name in tile_properties and tile_properties[property_name] == property_value:
                 print(f"  Найден тайл с нужным свойством: GID {gid}")
                 return gid # Возвращаем глобальный GID

        print(f"Не найден тайл со свойством '{property_name}'='{property_value}'")
        return None


    def init_game_objects(self):
        spawn_point = self.get_spawn_point()
        if spawn_point:
            start_x, start_y = spawn_point
        else:
            screen = self.screen_manager.get_screen()
            start_x = screen.get_width() // 2
            start_y = screen.get_height() // 2

        # При создании игрока передаем ссылку на GameManager
        self.player = Player(self, start_x, start_y)
        self.all_sprites.add(self.player)
        self.players.add(self.player)
        print(f"Игрок создан на позиции ({start_x}, {start_y})")

        # --- Добавляем мотыгу в инвентарь игрока ---
        if 'hoe' in self.tools:
            print("Мотыга найдена в self.tools.") # Отладочный вывод
            # Проверяем, что у игрока есть метод add_item_to_inventory
            if hasattr(self.player, 'add_item_to_inventory'):
                print("У игрока есть метод add_item_to_inventory.") # Отладочный вывод
                # Добавляем мотыгу в первый слот хотбара (или другое место)
                self.player.add_item_to_inventory(self.tools['hoe'], slot_index=0)  # Добавляем в 1-й слот хотбара
                print("Мотыга добавлена в инвентарь игрока.")
            else:
                print("Ошибка: У игрока нет метода 'add_item_to_inventory'.")
        else:
            print("Ошибка: Мотыга не найдена в словаре self.tools или не была загружена.")


    def till_tile(self, tile_x, tile_y):
        """
        Изменяет тайл травы на тайл земли по указанным координатам.
        """
        print(f"Попытка вспахать клетку: ({tile_x}, {tile_y})") # Начало метода

        if not self.tmx_data or not self.soil_layer or not isinstance(self.soil_layer, pytmx.TiledTileLayer) or \
           not self.grass_layer or not isinstance(self.grass_layer, pytmx.TiledTileLayer) or self.dirt_tile_gid is None:
            print("Ошибка в till_tile: Не все необходимые данные карты загружены или имеют правильный тип. Возврат.")
            return

        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight
        map_width_tiles = self.tmx_data.width
        map_height_tiles = self.tmx_data.height

        # Проверяем границы карты
        if not (0 <= tile_x < map_width_tiles and 0 <= tile_y < map_height_tiles):
            print(f"Предупреждение в till_tile: Координаты ({tile_x}, {tile_y}) вне границ карты. Возврат.")
            return

        # Получаем GID тайла на слое травы по координатам
        # Используем метод get_tile_gid, который получает GID на конкретной позиции слоя
        # Доступ к данным слоя через .data (двумерный список GIDов)
        # Индексирование: [y][x]
        gid = self.grass_layer.data[tile_y][tile_x]
        print(f"GID тайла на слое '{self.grass_layer.name}' по координатам ({tile_x}, {tile_y}): {gid}") # Отладочный вывод


        if gid != 0: # Проверяем, что на этой клетке есть тайл (не пустая)
            print(f"Найдена непустая клетка с GID: {gid}") # Отладочный вывод

            # Получаем свойства тайла травы на этой позиции
            try:
                # Вручную находим индекс слоя grass_layer
                grass_layer_index = -1
                for i, layer in enumerate(self.tmx_data.layers):
                    if layer is self.grass_layer:
                        grass_layer_index = i
                        break

                if grass_layer_index == -1:
                    print(f"Ошибка в till_tile: Объект слоя травы не найден в списке слоев карты. Возврат.")
                    return

                # Теперь вызываем get_tile_properties с индексом слоя
                tile_properties = self.tmx_data.get_tile_properties(tile_x, tile_y, grass_layer_index)
                print(f"Свойства тайла (GID {gid}): {tile_properties}") # Отладочный вывод


            except Exception as e:
                 print(f"Ошибка при получении свойств тайла травы в till_tile на ({tile_x}, {tile_y}): {e}")
                 tile_properties = None # Устанавливаем свойства в None в случае ошибки


            # Проверяем, является ли тайл травой (по свойству)
            # Убедимся, что tile_properties не None и содержит нужный ключ
            if tile_properties and isinstance(tile_properties, dict) and tile_properties.get('type') == 'grass':
                print("Тайл является травой. Производим вспашку.") # Отладочный вывод

                # --- Изменяем тайл на слое ТРАВКИ на тайл земли ---
                # Обращаемся к данным слоя ТРАВКИ через .data, используя координаты
                self.grass_layer.data[tile_y][tile_x] = self.dirt_tile_gid
                print(f"Вспахана клетка: ({tile_x}, {tile_y})")

                # !!! ВАЖНО: Здесь нужно добавить логику для перерисовки карты или только измененной области !!!
                # Ваш текущий метод draw_map отрисовывает видимую часть карты каждый кадр,
                # что должно быть достаточно для отображения изменений.
                # Убедитесь, что draw_map вызывается после update.
                # Это уже происходит в цикле run: self.update() -> self.draw()

            else:
                 print(f"Тайл не является травой или не имеет нужного свойства. Свойства: {tile_properties}. Требуется: {{'type': 'grass'}}") # Отладочный вывод

        else:
             print("Клетка пустая (GID 0). Вспашка не требуется.") # Отладочный вывод

    # --- Методы обработки событий и отрисовки ---

    def handle_events(self):
        if not self.event_handler.handle_events():
            self.running = False
            return False

        keys = pygame.key.get_pressed()
        # Обработка выбора слота хотбара клавишами 1-8
        for i in range(8):
            if keys[getattr(pygame, f'K_{i + 1}')]:
                self.selected_item_index = i
                print(f"Выбран слот хотбара: {self.selected_item_index}") # Отладочный вывод

        # Обработка открытия/закрытия инвентаря клавишей T
        if keys[pygame.K_t] and not hasattr(self, '_t_pressed'): # Добавил проверку, чтобы избежать многократного переключения при удержании
             self._t_pressed = True
             self.inventory_open = not self.inventory_open
             print(f"Инвентарь {'открыт' if self.inventory_open else 'закрыт'}")
        elif not keys[pygame.K_t] and hasattr(self, '_t_pressed'):
             del self._t_pressed # Сбрасываем флаг после отпускания клавиши


        return True

    def init_game_objects(self):
        spawn_point = self.get_spawn_point()
        if spawn_point:
            start_x, start_y = spawn_point
        else:
            screen = self.screen_manager.get_screen()
            start_x = screen.get_width() // 2
            start_y = screen.get_height() // 2

        # При создании игрока передаем ссылку на GameManager
        self.player = Player(self, start_x, start_y)
        self.all_sprites.add(self.player)
        self.players.add(self.player)
        print(f"Игрок создан на позиции ({start_x}, {start_y})")

        # --- Добавляем мотыгу в инвентарь игрока ---
        if 'hoe' in self.tools:
            print("Мотыга найдена в self.tools.") # Отладочный вывод
            # Проверяем, что у игрока есть метод add_item_to_inventory
            if hasattr(self.player, 'add_item_to_inventory'):
                print("У игрока есть метод add_item_to_inventory.") # Отладочный вывод
                # Добавляем мотыгу в первый слот хотбара (или другое место)
                self.player.add_item_to_inventory(self.tools['hoe'], slot_index=0)  # Добавляем в 1-й слот хотбара
                print("Мотыга добавлена в инвентарь игрока.")
            else:
                print("Ошибка: У игрока нет метода 'add_item_to_inventory'.")
        else:
            print("Ошибка: Мотыга не найдена в словаре self.tools или не была загружена.")

    def update(self):
        """Обновляет состояние игры"""
        delta_time = self.clock.tick(self.settings['fps_limit']) / 1000.0

        if self.state == GameState.GAME and not self.paused:
            # Сначала обновляем спрайты (включая игрока)
            self.all_sprites.update(delta_time)

            # Обновляем камеру, привязывая её к игроку
            self.camera.update(self.player)

            self.update_clock()

            # Подсчёт FPS
            self.fps_counter += 1
            current_time = pygame.time.get_ticks()
            if current_time - self.fps_timer >= 1000:
                self.fps = self.fps_counter
                self.fps_counter = 0
                self.fps_timer = current_time

    def draw(self):
        """Отрисовка текущего состояния игры"""
        screen = self.screen_manager.get_screen()

        if self.state == GameState.MENU:
            self.render_manager.draw_menu(self)
        elif self.state == GameState.SETTINGS:
            self.render_manager.draw_settings(self)
        elif self.state == GameState.GAME:
            # Очистка экрана
            screen.fill((50, 50, 50))  # Серый фон

            # Отрисовка только видимой части карты
            if self.map_loaded:
                self.render_map(screen)

            # Отрисовка всех спрайтов
            # Сортируем спрайты по Y координате для правильного отображения (игрок перед объектами и т.д.)
            # Это базовая сортировка, для сложных карт может потребоваться более сложная логика
            all_sprites_sorted = sorted(self.all_sprites, key=lambda sprite: sprite.rect.bottom)

            for sprite in all_sprites_sorted:
                pos = self.camera.apply(sprite)
                screen.blit(sprite.image, pos.topleft)


            self.draw_clock(screen)

            # Отрисовка интерфейса (всегда поверх всего остального)
            self.draw_inventory_and_hotbar(screen)

            # Отрисовка FPS (для отладки)
            fps_text = self.fonts['small'].render(f"FPS: {self.fps}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))

        # Обновление экрана
        pygame.display.flip()

    def draw_inventory_and_hotbar(self, screen):
        panel_width = len(self.hotbar_slots) * 60 + 20
        panel_height = 70
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = screen.get_height() - panel_height - 10

        # Отрисовка панели хотбара
        pygame.draw.rect(screen, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=10) # Добавлен border_radius

        for index, item in enumerate(self.hotbar_slots):
            slot_x = panel_x + 10 + index * 60
            slot_y = panel_y + 10

            # Отрисовка рамки выбранного слота
            if index == self.selected_item_index:
                pygame.draw.rect(screen, (255, 215, 0), (slot_x - 5, slot_y - 5, 50 + 10, 50 + 10), 3, border_radius=10)

            # Отрисовка фона слота
            pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, 50, 50), border_radius=5) # Добавлен border_radius

            # Отрисовка предмета в слоте
            if item:
                # Проверяем, является ли item экземпляром класса Item (или его подкласса) и имеет ли изображение
                if isinstance(item, Item) and hasattr(item, 'image') and item.image:
                    # Масштабируем изображение предмета до размера слота хотбара (например, 40x40)
                    # Сохраняем исходное соотношение сторон при масштабировании
                    item_image = item.image
                    img_width, img_height = item_image.get_size()
                    slot_size = 40
                    scale_factor = min(slot_size / img_width, slot_size / img_height)
                    scaled_width = int(img_width * scale_factor)
                    scaled_height = int(img_height * scale_factor)
                    scaled_image = pygame.transform.scale(item_image, (scaled_width, scaled_height))

                    # Вычисляем позицию для центрирования изображения в слоте
                    img_x = slot_x + (50 - scaled_width) // 2
                    img_y = slot_y + (50 - scaled_height) // 2

                    screen.blit(scaled_image, (img_x, img_y))
                else:
                    # Если изображения нет или item не является предметом, отрисовать маленькую заглушку
                    dummy = pygame.Surface((40, 40))
                    dummy.fill((255, 0, 0)) # Красная заглушка для отсутствующего изображения/неправильного объекта
                    screen.blit(dummy, (slot_x + 5, slot_y + 5))


        # Отрисовка инвентаря (если открыт)
        if self.inventory_open:
            inventory_width = 3 * 70 + 20
            inventory_height = 8 * 70 + 20
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2

            pygame.draw.rect(screen, (50, 50, 50), (inventory_x, inventory_y, inventory_width, inventory_height), border_radius=10) # Добавлен border_radius

            for row in range(8):
                for col in range(3):
                    slot_x = inventory_x + 10 + col * 70
                    slot_y = inventory_y + 10 + row * 70

                    # Отрисовка фона слота инвентаря
                    pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, 60, 60), border_radius=5) # Добавлен border_radius

                    item = self.inventory[row][col]
                    if item:
                        # Отрисовка предмета в слоте инвентаря
                        if isinstance(item, Item) and hasattr(item, 'image') and item.image:
                             # Масштабируем изображение предмета до размера слота инвентаря (например, 50x50)
                             item_image = item.image
                             img_width, img_height = item_image.get_size()
                             slot_size = 50 # Размер для инвентаря
                             scale_factor = min(slot_size / img_width, slot_size / img_height)
                             scaled_width = int(img_width * scale_factor)
                             scaled_height = int(img_height * scale_factor)
                             scaled_image = pygame.transform.scale(item_image, (scaled_width, scaled_height))

                             # Вычисляем позицию для центрирования изображения в слоте
                             img_x = slot_x + (60 - scaled_width) // 2
                             img_y = slot_y + (60 - scaled_height) // 2

                             screen.blit(scaled_image, (img_x, img_y))
                        else:
                            # Заглушка для отсутствующего изображения/неправильного объекта в инвентаре
                             dummy = pygame.Surface((50, 50))
                             dummy.fill((255, 0, 0)) # Красная заглушка
                             screen.blit(dummy, (slot_x + 5, slot_y + 5))


    def init_clock(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        offset = 10
        self.clock_pos = (screen_width - self.clock_size - offset, offset)

        # Загрузка изображений часов
        try:
            clock_bg_path = os.path.join("sprites", "clock", "clock_bg.png")
            clock_arrow_path = os.path.join("sprites", "clock", "clock_arrow.png")
            self.clock_bg = pygame.image.load(clock_bg_path).convert_alpha()
            self.clock_arrow = pygame.image.load(clock_arrow_path).convert_alpha()
            print("Изображения часов успешно загружены.")
        except pygame.error as e:
            print(f"Ошибка загрузки изображений часов: {e}")
            print("Создаются заглушки для часов.")
            # Создаем заглушки, если изображения не найдены
            self.clock_bg = pygame.Surface((self.clock_size, self.clock_size), pygame.SRCALPHA)
            pygame.draw.circle(self.clock_bg, (200, 200, 200), (self.clock_size//2, self.clock_size//2), self.clock_size//2)
            self.clock_arrow = pygame.Surface((self.clock_size, self.clock_size), pygame.SRCALPHA)
            pygame.draw.rect(self.clock_arrow, (50, 50, 50),
                            (self.clock_size//2 - 2, 10, 4, self.clock_size//2))
        except Exception as e:
             print(f"Произошла другая ошибка при инициализации часов: {e}")
             # Создаем заглушки в случае других ошибок
             self.clock_bg = pygame.Surface((self.clock_size, self.clock_size), pygame.SRCALPHA)
             pygame.draw.circle(self.clock_bg, (200, 200, 200), (self.clock_size//2, self.clock_size//2), self.clock_size//2)
             self.clock_arrow = pygame.Surface((self.clock_size, self.clock_size), pygame.SRCALPHA)
             pygame.draw.rect(self.clock_arrow, (50, 50, 50),
                            (self.clock_size//2 - 2, 10, 4, self.clock_size//2))


        # если нужен будет рескейл
        # self.clock_bg = pygame.transform.scale(self.clock_bg, (self.clock_size, self.clock_size))
        # self.clock_arrow = pygame.transform.scale(self.clock_arrow, (self.clock_size, self.clock_size))

        self.night_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.night_overlay.fill((0, 0, 0, 180))


    def draw_clock(self, screen):
        if self.clock_bg: # Проверяем, что изображение фона часов загружено
            screen.blit(self.clock_bg, self.clock_pos)

            if self.clock_arrow: # Проверяем, что изображение стрелки часов загружено
                angle = math.radians(self.game_time * -0.5) # Угол в радианах (умножаем на -0.5 для вращения по часовой стрелке)
                # Вращаем стрелку
                rotated_arrow = pygame.transform.rotate(self.clock_arrow, math.degrees(angle))
                # Получаем прямоугольник повернутой стрелки и центрируем его по центру фона часов
                arrow_rect = rotated_arrow.get_rect(center=(
                    self.clock_pos[0] + self.clock_size // 2,
                    self.clock_pos[1] + self.clock_size // 2
                ))
                screen.blit(rotated_arrow, arrow_rect)
            else:
                 print("Предупреждение: Изображение стрелки часов не загружено.")

        else:
            print("Предупреждение: Изображение фона часов не загружено.")


        # Отрисовка затемнения (ночи)
        if self.is_night and self.night_overlay: # Проверяем наличие night_overlay
            screen.blit(self.night_overlay, (0, 0))
        elif self.is_night and not self.night_overlay:
            print("Предупреждение: night_overlay не инициализирован, но is_night = True.")


    def update_clock(self):
        # для дебага
        # print(f"Time: {self.game_time}, Minute: {(self.game_time // 60) % 12}, Night: {self.is_night}")

        current_time = time.time()
        # Обновляем игровое время каждую секунду реального времени
        if current_time - self.last_time_update >= 1:
            self.game_time += 1 # Увеличиваем на 1 секунду
            self.last_time_update = current_time

        # Пример: день 12 минут (720 секунд) игрового времени = 12 реальных минут
        # 12 игровых часов = 720 секунд игрового времени
        # 1 игровой час = 60 секунд игрового времени

        max_game_time = 720 # Максимальное игровое время в цикле

        if self.game_time >= max_game_time:
            self.game_time = 0 # Сбрасываем игровое время в начало нового дня

        # Пример: ночь с 11-го до 5-го часа (по циферблату)
        # 11-й час начинается с (11 * 60) = 660 секунды
        # 5-й час заканчивается в (5 * 60) = 300 секунд (на следующий день)
        # То есть ночь с 660 до 720 (конец дня) и с 0 до 300 (начало дня)
        self.is_night = (self.game_time >= 660) or (self.game_time < 300) # Исправлено условие для начала дня

    def render_map(self, screen):
        """Отрисовка карты"""
        if not self.map_loaded or not self.tmx_data:
            return

        # Получаем смещение камеры
        camera_offset = self.camera.offset

        # Размер тайла
        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight

        # Вычисляем видимую область в тайлах (с небольшим запасом)
        start_x = int(camera_offset.x) // tile_width
        end_x = start_x + (screen.get_width() // tile_width) + 2
        start_y = int(camera_offset.y) // tile_height
        end_y = start_y + (screen.get_height() // tile_height) + 2

        # Ограничиваем индексы границами карты
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.tmx_data.width, end_x)
        end_y = min(self.tmx_data.height, end_y)

        # Отрисовка видимых тайлов слоев с данными
        for layer in self.tmx_data.visible_layers:
            # Отрисовываем только тайловые слои с данными
            if isinstance(layer, pytmx.TiledTileLayer): # Проверяем, что это тайловый слой
                 for y in range(start_y, end_y):
                     for x in range(start_x, end_x):
                         # Используем .tile для доступа к GID на позиции (x, y) в слое
                         gid = layer.data[y][x] # Исправлено: доступ к данным слоя через .tile

                         if gid != 0: # Проверяем, что это не пустая клетка
                             # Получаем изображение тайла по GID
                             tile_image = self.tmx_data.get_tile_image_by_gid(gid)

                             if tile_image:
                                 # Вычисляем позицию на экране
                                 screen_x = x * tile_width - int(camera_offset.x)
                                 screen_y = y * tile_height - int(camera_offset.y)
                                 screen.blit(tile_image, (screen_x, screen_y))

    def toggle_fullscreen(self):
        self.settings['fullscreen'] = not self.settings['fullscreen']
        self.screen_manager.toggle_screen_mode()
        screen = self.screen_manager.get_screen()
        self.camera = Camera(screen.get_width(), screen.get_height())
        if self.map_loaded and hasattr(self, 'tmx_data'):
            map_width = self.tmx_data.width * self.tmx_data.tilewidth
            map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.camera.set_map_size(map_width, map_height)
            self.init_clock(screen) # Переинициализируем часы после смены размера экрана
        print(f"Переключен режим экрана, новые размеры: {screen.get_width()}x{screen.get_height()}")

    def set_sound_volume(self, volume):
        self.settings['sound_volume'] = max(0.0, min(1.0, volume))
        print(f"Установлена громкость звука: {volume}")

    def set_music_volume(self, volume):
        self.settings['music_volume'] = max(0.0, min(1.0, volume))
        print(f"Установлена громкость музыки: {volume}")

    def save_settings(self):
        print("Настройки сохранены")

    def load_settings(self):
        print("Настройки загружены")

    def run(self):
        self.load_settings()
        while self.running:
            self.handle_events()
            self.update()
            self.draw() # Метод draw теперь отвечает за отрисовку изменений

        self.save_settings()
        pygame.quit()

    def get_spawn_point(self):
        """Ищет точку спавна игрока на слое объектов карты."""
        if self.map_loaded and self.tmx_data:
            for layer in self.tmx_data.layers:
                # Проверяем, является ли слой слоем объектов
                if isinstance(layer, pytmx.TiledObjectGroup):
                    for obj in layer:
                        # Проверяем свойства объекта для определения точки спавна
                        if hasattr(obj, 'type') and obj.type == 'spawn' or \
                           hasattr(obj, 'name') and obj.name == 'player_spawn':
                            print(f"Найдена точка спавна игрока на ({obj.x}, {obj.y})")
                            return obj.x, obj.y
        print("Предупреждение: Точка спавна игрока не найдена на карте. Игрок будет размещен по центру экрана.")
        return None # Возвращаем None, если точка спавна не найдена

    def reset_game(self):
        self.all_sprites.empty()
        self.players.empty()
        self.npcs.empty()
        self.obstacles.empty()
        self.items.empty()
        self.init_game_objects() # Повторно инициализируем объекты игры
        self.state = GameState.MENU
        self.paused = False
        print("Игра сброшена в начальное состояние")

    def check_collision(self, rect):
        """
        Проверяет коллизии данного прямоугольника с тайлами на слоях коллизий.
        Принимает прямоугольник (обычно self.player.collision_rect).
        """
        if not self.map_loaded or not self.tmx_data or not self.collision_layers:
             return False # Нет карты, данных или слоев коллизий

        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight

        for layer in self.collision_layers:
            # Итерируем по тайлам в пределах видимой области прямоугольника коллизии
            # Определяем область в тайлах, которую пересекает прямоугольник
            start_x = int(rect.left // tile_width)
            end_x = int(rect.right // tile_width) + 1
            start_y = int(rect.top // tile_height)
            end_y = int(rect.bottom // tile_height) + 1

            # Ограничиваем область границами слоя
            start_x = max(0, start_x)
            start_y = max(0, start_y)
            end_x = min(layer.width, end_x)
            end_y = min(layer.height, end_y)


            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                     # Используем .tile для доступа к GID на позиции (x, y) в слое
                     gid = layer.data[y][x] # Исправлено: доступ к данным слоя через .tile

                     if gid != 0: # Если тайл не пустой, это коллизия
                        # Создаем прямоугольник для тайла коллизии
                        tile_rect = pygame.Rect(
                            x * tile_width,
                            y * tile_height,
                            tile_width,
                            tile_height,
                        )
                        # Проверяем пересечение прямоугольников
                        if rect.colliderect(tile_rect):
                            # print(f"Коллизия с тайлом на ({x}, {y}) на слое {layer.name}") # Отладочный вывод
                            return True # Найдена коллизия

        return False # Коллизий не найдено
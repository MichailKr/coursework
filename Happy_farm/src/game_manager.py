import pygame
from src.shop import Shop
from src.game_state import GameState
from src.screen_manager import ScreenManager
from src.event_handler import EventHandler
from src.render_manager import RenderManager
from src.player import Player
from src.camera import Camera
from src.plant import Plant
from src.Bridges import Bridge
from src.item import Tool, Item, Seed # Импортируем также базовый класс Item
import pytmx
import os
import math
import time
from src.inventory_manager import InventoryManager

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
                'menu': pygame.K_ESCAPE #настройки
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

        self.inventory_manager = InventoryManager(self)

        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        
        self.npcs = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.plants = pygame.sprite.Group()

        # Загрузка карты
        self.map_loaded = False
        self.tmx_data = None # Инициализируем до try/except

        self.soil_layer = 'Песочек' # Будет содержать объект слоя TiledTileLayer
        self.grass_layer = 'Травка' # Будет содержать объект слоя TiledTileLayer
        self.dirt_tile_gid = None # Будет содержать GID тайла земли

        # Слои коллизий (имена слоев из Tiled)
        self.collision_layers_names = ["Коллизия лес", "Колилзия горок", "Дом", "Коллизия кусты","Коллизии Мосты", "Коллизия камней", "Коллизии река и Озеро"]
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
        self.shop = Shop(self)
        self.bridge1 = Bridge(self, 1000, 1000, 15, 10)

        self.tile_states = {}  # Словарь или двумерный список для хранения состояния тайлов

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
        # Важно: Игрок может нуждаться в ссылке на InventoryManager для использования предметов
        self.player = Player(self, start_x, start_y)
        self.all_sprites.add(self.player)
        self.players.add(self.player)
        print(f"Игрок создан на позиции ({start_x}, {start_y})")

        if 'hoe' in self.tools:
            print("Мотыга найдена в self.tools.")
            if hasattr(self, 'inventory_manager') and isinstance(self.inventory_manager, InventoryManager):
                success = self.inventory_manager.add_item_to_inventory(self.tools['hoe'], slot_index=0)
                if success:
                    print("Мотыга добавлена в инвентарь игрока через InventoryManager.")
                else:
                    print("Ошибка: Не удалось добавить мотыгу в инвентарь через InventoryManager.")
            else:
                print("Ошибка: InventoryManager не инициализирован или имеет неправильный тип.")
        else:
            print("Ошибка: Мотыга не найдена в словаре self.tools или не была загружена.")
            # --- Конец блока изменения для мотыги ---
            # --- Добавляем семена пшеницы и томатов в инвентарь игрока ---
        try:
            # Путь к спрайтам предметов (семян)
            item_sprites_path = os.path.join("sprites", "items")  # Предполагаем, что спрайты предметов тут
            # Загружаем изображения для семян пшеницы и томатов
            wheat_seed_image_path = os.path.join(item_sprites_path, "wheat_plant.png")  # Используем wheat_plant.png
            tomato_seed_image_path = os.path.join(item_sprites_path, "tomato_plant.png")  # Используем tomato_plant.png
            wheat_seed_image = None
            tomato_seed_image = None
            try:
                wheat_seed_image = pygame.image.load(wheat_seed_image_path).convert_alpha()
                print(f"Изображение семян пшеницы успешно загружено: {wheat_seed_image_path}")
            except pygame.error as e:
                print(f"Ошибка загрузки изображения семян пшеницы: {e}")
                print(f"Проверьте путь к файлу: {wheat_seed_image_path}")
                # Используем заглушку, если изображение не найдено
                wheat_seed_image = pygame.Surface((32, 32))
                wheat_seed_image.fill((210, 180, 140))  # Цвет пшеницы для заглушки
            try:
                tomato_seed_image = pygame.image.load(tomato_seed_image_path).convert_alpha()
                print(f"Изображение семян томатов успешно загружено: {tomato_seed_image_path}")
            except pygame.error as e:
                print(f"Ошибка загрузки изображения семян томатов: {e}")
                print(f"Проверьте путь к файлу: {tomato_seed_image_path}")
                # Используем заглушку, если изображение не найдено
                tomato_seed_image = pygame.Surface((32, 32))
                tomato_seed_image.fill((255, 99, 71))  # Цвет томата для заглушки
            # Создаем экземпляры семян, передавая тип растения
            wheat_seed = Seed("Семена пшеницы", wheat_seed_image, "wheat")  # Тип растения 'wheat'
            tomato_seed = Seed("Семена томатов", tomato_seed_image, "tomato")  # Тип растения 'tomato'
            # Добавляем семена в инвентарь (например, в следующие слоты хотбара)
            if hasattr(self, 'inventory_manager') and isinstance(self.inventory_manager, InventoryManager):
                # Добавляем пшеницу во 2-й слот (индекс 1)
                self.inventory_manager.add_item_to_inventory(wheat_seed, slot_index=1)
                # Добавляем томаты в 3-й слот (индекс 2)
                self.inventory_manager.add_item_to_inventory(tomato_seed, slot_index=2)
                print("Семена пшеницы и томатов добавлены в инвентарь игрока.")
            else:
                print("Ошибка: InventoryManager не инициализирован при попытке добавить семена.")
        except Exception as e:
            print(f"Произошла ошибка при создании или добавлении семян в инвентарь: {e}")

    def is_tile_plantable(self, tile_x, tile_y):
        """Проверяет, можно ли посадить семя на данном тайле."""
        if not self.tmx_data:
             print("Ошибка в is_tile_plantable: tmx_data не загружена.")
             return False
        map_width_tiles = self.tmx_data.width
        map_height_tiles = self.tmx_data.height
        if not (0 <= tile_x < map_width_tiles and 0 <= tile_y < map_height_tiles):
            # print(f"Координаты тайла ({tile_x}, {tile_y}) вне границ карты.") # Можно убрать для чистоты лога
            return False # Вне границ карты сажать нельзя
        # Проверяем состояние тайла в нашей структуре tile_states
        tile_coords = (tile_x, tile_y)
        state = self.tile_states.get(tile_coords, {}) # Получаем состояние или пустой словарь
        # Можно сажать, если земля вспахана ('is_tilled' == True) И на ней нет растения ('has_plant' == False или отсутствует)
        return state.get('is_tilled', False) and not state.get('has_plant', False)

    def till_tile(self, tile_x, tile_y):
        """
        Изменяет тайл травы на тайл земли по указанным координатам и
        обновляет состояние тайла для посадки.
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
        if not (0 <= tile_x < map_width_tiles and 0 <= tile_y < map_height_tiles):
            print(f"Предупреждение в till_tile: Координаты ({tile_x}, {tile_y}) вне границ карты. Возврат.")
            return
        # Получаем GID тайла на слое травы по координатам
        gid = self.grass_layer.data[tile_y][tile_x]
        # print(f"GID тайла на слое '{self.grass_layer.name}' по координатам ({tile_x}, {tile_y}): {gid}") # Отладочный вывод
        if gid != 0: # Проверяем, что на этой клетке есть тайл (не пустая)
            # print(f"Найдена непустая клетка с GID: {gid}") # Отладочный вывод
            # Получаем свойства тайла травы на этой позиции
            try:
                grass_layer_index = -1
                for i, layer in enumerate(self.tmx_data.layers):
                    if layer is self.grass_layer:
                        grass_layer_index = i
                        break
                if grass_layer_index == -1:
                    print(f"Ошибка в till_tile: Объект слоя травы не найден в списке слоев карты. Возврат.")
                    return
                tile_properties = self.tmx_data.get_tile_properties(tile_x, tile_y, grass_layer_index)
                # print(f"Свойства тайла (GID {gid}): {tile_properties}") # Отладочный вывод
            except Exception as e:
                 print(f"Ошибка при получении свойств тайла травы в till_tile на ({tile_x}, {tile_y}): {e}")
                 tile_properties = None
            # Проверяем, является ли тайл травой (по свойству)
            if tile_properties and isinstance(tile_properties, dict) and tile_properties.get('type') == 'grass':
                print("Тайл является травой. Производим вспашку.") # Отладочный вывод
                # Изменяем тайл на слое травы на тайл земли (или просто удаляем тайл травы, если земля находится на другом слое)
                if self.soil_layer and isinstance(self.soil_layer, pytmx.TiledTileLayer) and self.dirt_tile_gid is not None:
                    self.grass_layer.data[tile_y][tile_x] = 0 # Удаляем тайл травы
                    # Опционально: ставим тайл вспаханной земли на слой "Песочек"
                    # self.soil_layer.data[tile_y][tile_x] = self.dirt_tile_gid
                    print(f"Тайл травы на ({tile_x}, {tile_y}) удален.")
                else:
                     self.grass_layer.data[tile_y][tile_x] = self.dirt_tile_gid
                     print(f"Тайл на ({tile_x}, {tile_y}) изменен на GID земли ({self.dirt_tile_gid}).")
                # --- Обновляем состояние тайла для посадки ---
                tile_coords = (tile_x, tile_y)
                if tile_coords not in self.tile_states:
                     self.tile_states[tile_coords] = {}
                self.tile_states[tile_coords]['is_tilled'] = True
                # Убедимся, что нет растения при вспашке
                self.tile_states[tile_coords]['has_plant'] = False
                print(f"Состояние тайла ({tile_x}, {tile_y}) обновлено: {self.tile_states[tile_coords]}")
            else:
                 # print(f"Тайл не является травой или не имеет нужного свойства. Свойства: {tile_properties}. Требуется: {{'type': 'grass'}}") # Отладочный вывод
                 pass # Нет необходимости в отладочном выводе для каждого не-травяного тайла
        else:
             # print("Клетка пустая (GID 0). Вспашка не требуется.") # Отладочный вывод
             pass # Нет необходимости в отладочном выводе для пустых клеток

    def update_tile_state(self, tile_x, tile_y, **kwargs):
        """Обновляет состояние тайла по указанным координатам."""
        tile_coords = (tile_x, tile_y)
        if tile_coords not in self.tile_states:
            self.tile_states[tile_coords] = {}
        self.tile_states[tile_coords].update(kwargs)
        # print(f"Состояние тайла ({tile_x}, {tile_y}) обновлено: {self.tile_states[tile_coords]}") # Отладочный вывод

    # --- Методы обработки событий и отрисовки ---

    def handle_events(self):
        """
        Обработка всех событий Pygame и их распределение по соответствующим менеджерам.
        Включает обработку общих событий, инвентаря, взаимодействия с магазином и мостом.
        """
        events = pygame.event.get()
        keys = pygame.key.get_pressed()  # Получаем состояние клавиш
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return False  # Сигнализируем, что игра должна завершиться

            # --- Передача события Event Handler ---
            if not self.event_handler.handle_events(event):
                return False

            # --- Передача события игроку ---
            if self.state == GameState.GAME and hasattr(self, 'player') and self.player:
                self.player.handle_input(event)

            # --- Передача события инвентарю ---
            if hasattr(self, 'inventory_manager') and self.inventory_manager:
                self.inventory_manager.handle_input(event)

            # --- Обработка взаимодействия с магазином ---
            if hasattr(self, 'shop') and isinstance(self.shop, Shop):
                if event.type == pygame.KEYDOWN and event.key == self.settings['controls']['interact']:
                    if not self.inventory_manager.inventory_open and self.shop.is_player_in_range():
                        self.shop.toggle_shop()
                        print("Магазин открыт/закрыт")
                    elif self.shop.is_open:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pass  # Можно добавить логику обработки кликов в магазине

            # --- Обработка взаимодействия с мостом ---
            # Предположим, что у вас есть список мостов self.bridges
            if hasattr(self, 'bridge1'):
                # Обработка открытия диалога отдачи ресурсов
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e and self.bridge1.is_player_in_range():
                        self.bridge1.toggle_dialog()
                        print("Диалог отдачи ресурсов для моста открыт/закрыт")
                # Обработка кликов мыши внутри диалога моста
                if self.bridge1.show_dialog:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Здесь можно добавить логику для обработки кликов по интерфейсу моста
                        # например, выбор ресурса или подтверждение отдачи
                        pass

                # Обработка ввода с клавиатуры для интерфейса моста
                if self.bridge1.show_dialog:
                    self.bridge1.handle_input(keys, events)

        # Вызов handle_input для магазина, если он открыт
        if hasattr(self, 'shop') and self.shop.is_open:
            self.shop.handle_input(keys, events)

        if self.bridge1.is_open:
            self.bridge1.handle_input(keys, events)

        return True  # Продолжаем игру

    def update(self):
        """Обновляет состояние игры"""
        delta_time = self.clock.tick(self.settings['fps_limit']) / 1000.0
        if self.state == GameState.GAME and not self.paused:
            # Сначала обновляем спрайты (включая игрока и растения)
            self.all_sprites.update(delta_time)
            self.plants.update(delta_time) # !!! Обновляем группу растений !!!
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
            # Отрисовка всех спрайтов (включая игрока)
            # Сортируем спрайты по нижней границе для правильной отрисовки (персонажи перед растениями)
            all_sprites_except_plants = [s for s in self.all_sprites if
                                         not isinstance(s, Plant)]  # Исключаем растения из основной группы отрисовки
            all_sprites_sorted = sorted(all_sprites_except_plants, key=lambda sprite: sprite.rect.bottom)
            for sprite in all_sprites_sorted:
                pos = self.camera.apply(sprite)
                screen.blit(sprite.image, pos.topleft)
            # !!! Отрисовка растений !!!
            # Растения также являются спрайтами и будут отрисовываться вместе с all_sprites
            # Если нужно отдельное управление отрисовкой растений, можно отрисовывать self.plants здесь
            self.draw_clock(screen)
            # Отрисовка интерфейса (всегда поверх всего остального)
            self.inventory_manager.draw(screen)
            self.shop.draw(screen)
            self.bridge1.draw(screen)
            self.player.draw_coins(screen)
            # Отрисовка FPS (для отладки)
            fps_text = self.fonts['small'].render(f"FPS: {self.fps}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))
        # Обновление экрана
        pygame.display.flip()

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
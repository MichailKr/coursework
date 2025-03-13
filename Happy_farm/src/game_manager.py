import pygame
from Happy_farm.src.game_state import GameState
from Happy_farm.src.screen_manager import ScreenManager
from Happy_farm.src.event_handler import EventHandler
from Happy_farm.src.render_manager import RenderManager
from Happy_farm.src.player import Player
from Happy_farm.src.camera import Camera
import pytmx
import os


class GameManager:
    def __init__(self):
        # Инициализация pygame
        pygame.init()
        pygame.font.init()

        # Создаем менеджер экрана
        self.screen_manager = ScreenManager()

        # Инициализация менеджеров
        self.event_handler = EventHandler(self)
        self.render_manager = RenderManager(self.screen_manager)

        # Основные компоненты
        self.state = GameState.MENU
        self.running = True
        self.paused = False
        self.clock = pygame.time.Clock()

        # Настройки игры - рабочие настройки
        self.settings = {
            'sound_volume': 0.7,  # Звук будет добавлен позже
            'music_volume': 0.5,  # Музыка будет добавлена позже
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

        # Загрузка шрифтов
        self.fonts = {
            'small': pygame.font.Font(None, 24),
            'medium': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 48)
        }

        self.inventory_open = False
        self.selected_item_index = 0
        self.hotbar_slots = [None, None, None, None, None, None, None, None]
        self.inventory = [[None for _ in range(0)] for _ in range(8)]  # Инвентарь 8x3

        # Инициализация групп спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        # Загрузка карты
        self.map_loaded = False
        try:
            self.tmx_data = pytmx.load_pygame('maps/maps.tmx')
            self.map_loaded = True
            print("Карта успешно загружена")
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            self.map_loaded = False

        # Создаем камеру
        screen = self.screen_manager.get_screen()
        self.camera = Camera(screen.get_width(), screen.get_height())
        print(f"Камера создана с размерами {screen.get_width()}x{screen.get_height()}")

        # Если карта успешно загружена, устанавливаем размеры для камеры
        if self.map_loaded and hasattr(self, 'tmx_data'):
            map_width = self.tmx_data.width * self.tmx_data.tilewidth
            map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.camera.set_map_size(map_width, map_height)
            print(f"Размеры карты для камеры установлены: {map_width}x{map_height}")

        # Инициализация игровых объектов
        self.init_game_objects()

        # Метрики производительности
        self.fps = 0
        self.frame_times = []
        self.last_update_time = pygame.time.get_ticks()

        print("GameManager инициализирован успешно")

    def handle_inventory_events(self, event):
        keys = pygame.key.get_pressed()

        # Переключение слотов панели предметов
        for i in range(8):
            if keys[getattr(pygame, f'K_{i + 1}')]:
                self.selected_item_index = i

        # Открытие/закрытие инвентаря
        if keys[pygame.K_t]:
            self.inventory_open = not self.inventory_open

    # Отображение панели предметов и инвентаря
    def draw_inventory_and_hotbar(self, screen):
        # Панель предметов
        panel_width = len(self.hotbar_slots) * 60 + 20
        panel_height = 70
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = screen.get_height() - panel_height - 10

        # Фон панели
        pygame.draw.rect(screen, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height))

        # Слоты панели
        for index, item in enumerate(self.hotbar_slots):
            slot_x = panel_x + 10 + index * 60
            slot_y = panel_y + 10

            # Рамка выделенного слота
            if index == self.selected_item_index:
                pygame.draw.rect(screen, (255, 215, 0), (slot_x - 5, slot_y - 5, 50 + 10, 50 + 10), 3)

            # Слот
            pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, 50, 50))

            # Отображение предмета
            if item:
                item_surface = pygame.Surface((40, 40))  # Заглушка для предметов
                item_surface.fill((0, 255, 0))  # Зеленый цвет / заменить на изображение
                screen.blit(item_surface, (slot_x + 5, slot_y + 5))

        # Инвентарь
        if self.inventory_open:
            inventory_width = 3 * 70 + 20
            inventory_height = 8 * 70 + 20
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2

            # Фон инвентаря
            pygame.draw.rect(screen, (50, 50, 50), (inventory_x, inventory_y, inventory_width, inventory_height))

            # Слоты инвентаря
            for row in range(8):
                for col in range(3):
                    slot_x = inventory_x + 10 + col * 70
                    slot_y = inventory_y + 10 + row * 70

                    pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, 60, 60))

                    if self.inventory[row][col]:
                        item_surface = pygame.Surface((40, 40))  # Заглушка для предметов
                        item_surface.fill((0, 0, 255))  # Синий цвет / заменить на изображение
                        screen.blit(item_surface, (slot_x + 10, slot_y + 10))

    # Добавьте этот метод в EventHandler или аналогичный обработчик событий
    def handle_inventory_events(self, event):
        keys = pygame.key.get_pressed()

        # Переключение слотов панели предметов
        for i in range(8):
            if keys[getattr(pygame, f'K_{i + 1}')]:
                self.selected_item_index = i

        # Открытие/закрытие инвентаря
        if keys[pygame.K_t]:
            self.inventory_open = not self.inventory_open

    def init_game_objects(self):
        """Инициализация игровых объектов"""
        # Создание игрока
        spawn_point = self.get_spawn_point()
        if spawn_point:
            start_x, start_y = spawn_point
        else:
            # Если точка спавна не найдена, размещаем в центре экрана
            screen = self.screen_manager.get_screen()
            start_x = screen.get_width() // 2
            start_y = screen.get_height() // 2

        self.player = Player(self, start_x, start_y)
        self.all_sprites.add(self.player)
        self.players.add(self.player)
        print(f"Игрок создан на позиции ({start_x}, {start_y})")

    def update(self):
        """Обновление состояния игры"""
        delta_time = self.clock.tick(self.settings['fps_limit']) / 1000.0

        if self.state == GameState.GAME and not self.paused:
            # Обновление всех спрайтов
            self.all_sprites.update(delta_time)

            # Обновление камеры - передаем ей игрока для слежения
            self.camera.update(self.player)

            # Обновление FPS счетчика
            self.frame_times.append(delta_time)
            if len(self.frame_times) > 100:
                self.frame_times.pop(0)

            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time > 500:  # Обновляем каждые 500 мс
                if self.frame_times:
                    self.fps = int(1.0 / (sum(self.frame_times) / len(self.frame_times)))
                self.last_update_time = current_time

    def draw(self):
        """Отрисовка текущего состояния игры"""
        screen = self.screen_manager.get_screen()

        if self.state == GameState.MENU:
            self.render_manager.draw_menu(self)
        elif self.state == GameState.SETTINGS:
            self.render_manager.draw_settings(self)
        elif self.state == GameState.GAME:
            # Очистка экрана
            screen.fill((0, 0, 0))
            self.draw_inventory_and_hotbar(self.screen_manager.get_screen())

            # Отрисовка карты с учетом камеры
            if self.map_loaded:
                self.render_map(screen)

            # Отрисовка спрайтов с учетом камеры
            for sprite in self.all_sprites:
                camera_rect = self.camera.apply(sprite)
                screen.blit(sprite.image, camera_rect.topleft)

            # Отрисовка FPS (для отладки)
            fps_text = self.fonts['small'].render(f"FPS: {self.fps}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))

        pygame.display.flip()

    def render_map(self, screen):
        """Отрисовка карты с учетом камеры"""
        if not self.map_loaded:
            return

        # Получаем видимую область
        cam_x, cam_y = self.camera.camera.topleft
        view_width, view_height = self.camera.camera.size

        # Отрисовка каждого слоя карты
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):  # Если это слой тайлов
                # Определяем диапазон тайлов для отрисовки
                tile_w, tile_h = self.tmx_data.tilewidth, self.tmx_data.tileheight
                start_x = max(0, cam_x // tile_w)
                start_y = max(0, cam_y // tile_h)
                end_x = min(self.tmx_data.width, (cam_x + view_width) // tile_w + 1)
                end_y = min(self.tmx_data.height, (cam_y + view_height) // tile_h + 1)

                # Отрисовываем только видимые тайлы
                for y in range(int(start_y), int(end_y)):
                    for x in range(int(start_x), int(end_x)):
                        try:
                            gid = layer.data[y][x]
                            if gid:
                                tile = self.tmx_data.get_tile_image_by_gid(gid)
                                if tile:
                                    # Применяем смещение камеры
                                    pos_x, pos_y = self.camera.apply_point(
                                        x * tile_w, y * tile_h
                                    )
                                    screen.blit(tile, (pos_x, pos_y))
                        except IndexError:
                            # Пропускаем тайлы за пределами карты
                            pass
            elif hasattr(layer, 'objects'):  # Если это слой объектов
                for obj in layer:
                    if hasattr(obj, 'image') and obj.image:
                        # Применяем смещение камеры
                        pos_x, pos_y = self.camera.apply_point(obj.x, obj.y)
                        screen.blit(obj.image, (pos_x, pos_y))

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        self.screen_manager.toggle_screen_mode('fullscreen')

        # Пересоздаем камеру с новыми размерами экрана
        screen = self.screen_manager.get_screen()
        self.camera = Camera(screen.get_width(), screen.get_height())

        # Если карта загружена, устанавливаем размеры карты для камеры
        if self.map_loaded and hasattr(self, 'tmx_data'):
            map_width = self.tmx_data.width * self.tmx_data.tilewidth
            map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.camera.set_map_size(map_width, map_height)

        print(f"Переключен режим экрана, новые размеры: {screen.get_width()}x{screen.get_height()}")

    def set_sound_volume(self, volume):
        """Установка громкости звука"""
        self.settings['sound_volume'] = max(0.0, min(1.0, volume))
        # Звук будет реализован позже
        print(f"Установлена громкость звука: {volume}")

    def set_music_volume(self, volume):
        """Установка громкости музыки"""
        self.settings['music_volume'] = max(0.0, min(1.0, volume))
        # Музыка будет реализована позже
        print(f"Установлена громкость музыки: {volume}")

    def save_settings(self):
        """Сохранение настроек"""
        # Заглушка - настройки будут сохраняться позже
        print("Настройки сохранены")

    def load_settings(self):
        """Загрузка настроек"""
        # Заглушка - настройки будут загружаться позже
        print("Настройки загружены")

    def handle_events(self):
        """Обработка событий"""
        return self.event_handler.handle_events()

    def run(self):
        """Главный игровой цикл"""
        self.load_settings()  # Загрузка настроек при старте

        while self.running:
            # Обработка событий
            self.handle_events()

            # Обновление состояния
            self.update()

            # Отрисовка
            self.draw()

        # Сохранение настроек и выход
        self.save_settings()
        pygame.quit()

    def get_spawn_point(self):
        """Получение точки появления игрока из карты"""
        if self.map_loaded:
            # Поиск слоя с объектами спавна
            for layer in self.tmx_data.layers:
                if hasattr(layer, 'objects'):
                    for obj in layer:
                        if hasattr(obj, 'type') and (obj.type == 'spawn' or obj.name == 'player_spawn'):
                            return obj.x, obj.y
        # Если точка спавна не найдена, возвращаем None
        return None

    def reset_game(self):
        """Сброс игры в начальное состояние"""
        # Очищаем группы спрайтов
        self.all_sprites.empty()
        self.players.empty()
        self.npcs.empty()
        self.obstacles.empty()
        self.items.empty()

        # Инициализируем игровые объекты заново
        self.init_game_objects()

        # Сбрасываем состояние игры
        self.state = GameState.MENU
        self.paused = False

        print("Игра сброшена в начальное состояние")

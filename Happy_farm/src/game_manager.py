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
        pygame.init()
        pygame.font.init()

        self.screen_manager = ScreenManager()
        self.event_handler = EventHandler(self)
        self.render_manager = RenderManager(self.screen_manager)

        self.state = GameState.MENU
        self.running = True
        self.paused = False
        self.clock = pygame.time.Clock()

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

        #self.tools = {
        #    'hoe': Tool('Мотыга', pygame.image.load('sprites/tools/hoe.png'), 'hoe'),
        #    'axe': Tool('Топор', pygame.image.load('sprites/tools/axe.png'), 'axe'),
        #    'wateringcan': Tool('Лейка', pygame.image.load('sprites/tools/wateringcan.png'), 'wateringcan')
        #}

        self.inventory_open = False
        self.selected_item_index = 0
        self.hotbar_slots = [None] * 8
        self.inventory = [[None for _ in range(3)] for _ in range(8)]

        self.all_sprites = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        self.map_loaded = False
        try:
            self.tmx_data = pytmx.load_pygame('maps/maps.tmx')
            self.map_loaded = True
            print("Карта успешно загружена")
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            self.map_loaded = False

        screen = self.screen_manager.get_screen()
        self.camera = Camera(screen.get_width(), screen.get_height())
        print(f"Камера создана с размерами {screen.get_width()}x{screen.get_height()}")

        if self.map_loaded and hasattr(self, 'tmx_data'):
            map_width = self.tmx_data.width * self.tmx_data.tilewidth
            map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.camera.set_map_size(map_width, map_height)
            print(f"Размеры карты для камеры установлены: {map_width}x{map_height}")

        self.init_game_objects()

        self.fps = 0
        self.frame_times = []
        self.last_update_time = pygame.time.get_ticks()

        print("GameManager инициализирован успешно")

    def handle_events(self):
        if not self.event_handler.handle_events():
            self.running = False
            return False

        keys = pygame.key.get_pressed()

        for i in range(8):
            if keys[getattr(pygame, f'K_{i + 1}')]:
                self.selected_item_index = i

        if keys[pygame.K_t]:
            self.inventory_open = not self.inventory_open

        return True

    def init_game_objects(self):
        spawn_point = self.get_spawn_point()
        if spawn_point:
            start_x, start_y = spawn_point
        else:
            screen = self.screen_manager.get_screen()
            start_x = screen.get_width() // 2
            start_y = screen.get_height() // 2

        self.player = Player(self, start_x, start_y)
        self.all_sprites.add(self.player)
        self.players.add(self.player)
        print(f"Игрок создан на позиции ({start_x}, {start_y})")

    def update(self):
        """Обновляет состояние игры"""
        delta_time = self.clock.tick(self.settings['fps_limit']) / 1000.0

        if self.state == GameState.GAME and not self.paused:
            # Сначала обновляем спрайты
            self.all_sprites.update(delta_time)

            # Обновляем камеру, привязывая её к игроку
            self.camera.update(self.player)

            # Отображение производительности (FPS)
            self.frame_times.append(delta_time)
            if len(self.frame_times) > 100:
                self.frame_times.pop(0)

            # Обновляем FPS каждые 500 мс
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time > 500:
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
            screen.fill((50, 50, 50))  # Серый фон, чтобы видеть, что экран очищается

            # Отрисовка карты
            if self.map_loaded:
                # Отрисовка каждого слоя карты
                for layer in self.tmx_data.visible_layers:
                    if hasattr(layer, 'data'):  # Если это слой тайлов
                        for x in range(layer.width):
                            for y in range(layer.height):
                                tile = layer.data[y][x]
                                if tile:
                                    # Получаем изображение тайла
                                    tile_image = self.tmx_data.get_tile_image_by_gid(tile)
                                    if tile_image:
                                        # Применяем смещение камеры к координатам тайла
                                        pos = self.camera.apply_rect(pygame.Rect(
                                            x * self.tmx_data.tilewidth,
                                            y * self.tmx_data.tileheight,
                                            self.tmx_data.tilewidth,
                                            self.tmx_data.tileheight
                                        ))
                                        screen.blit(tile_image, pos)

            # Отрисовка всех спрайтов
            for sprite in self.all_sprites:
                pos = self.camera.apply(sprite)
                screen.blit(sprite.image, pos.topleft)

            # Отрисовка интерфейса (не зависит от камеры)
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

        pygame.draw.rect(screen, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height))

        for index, item in enumerate(self.hotbar_slots):
            slot_x = panel_x + 10 + index * 60
            slot_y = panel_y + 10

            if index == self.selected_item_index:
                pygame.draw.rect(screen, (255, 215, 0), (slot_x - 5, slot_y - 5, 50 + 10, 50 + 10), 3)

            pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, 50, 50))

            if item:
                item_surface = pygame.Surface((40, 40))
                item_surface.fill((0, 255, 0))
                screen.blit(item_surface, (slot_x + 5, slot_y + 5))

        if self.inventory_open:
            inventory_width = 3 * 70 + 20
            inventory_height = 8 * 70 + 20
            inventory_x = (screen.get_width() - inventory_width) // 2
            inventory_y = (screen.get_height() - inventory_height) // 2

            pygame.draw.rect(screen, (50, 50, 50), (inventory_x, inventory_y, inventory_width, inventory_height))

            for row in range(8):
                for col in range(3):
                    slot_x = inventory_x + 10 + col * 70
                    slot_y = inventory_y + 10 + row * 70

                    pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, 60, 60))

                    if self.inventory[row][col]:
                        item_surface = pygame.Surface((40, 40))
                        item_surface.fill((0, 0, 255))
                        screen.blit(item_surface, (slot_x + 10, slot_y + 10))

    def render_map(self, screen):
        """Отрисовка карты"""
        if not self.map_loaded:
            return

        # Получаем смещение камеры
        camera_offset = self.camera.offset

        # Размер тайла
        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight

        # Вычисляем видимую область в тайлах
        start_x = int(camera_offset.x) // tile_width
        end_x = start_x + (screen.get_width() // tile_width) + 2
        start_y = int(camera_offset.y) // tile_height
        end_y = start_y + (screen.get_height() // tile_height) + 2

        # Ограничиваем индексы границами карты
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.tmx_data.width, end_x)
        end_y = min(self.tmx_data.height, end_y)

        # Отрисовка видимых тайлов
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for y in range(start_y, end_y):
                    for x in range(start_x, end_x):
                        tile = layer.data[y][x]
                        if tile:
                            # Получаем изображение тайла
                            tile_image = self.tmx_data.get_tile_image_by_gid(tile)
                            if tile_image:
                                # Вычисляем позицию на экране
                                screen_x = x * tile_width - int(camera_offset.x)
                                screen_y = y * tile_height - int(camera_offset.y)
                                screen.blit(tile_image, (screen_x, screen_y))

    def toggle_fullscreen(self):
        self.settings['fullscreen'] = not self.settings['fullscreen']
        self.screen_manager.toggle_screen_mode('fullscreen')

        screen = self.screen_manager.get_screen()
        self.camera = Camera(screen.get_width(), screen.get_height())

        if self.map_loaded and hasattr(self, 'tmx_data'):
            map_width = self.tmx_data.width * self.tmx_data.tilewidth
            map_height = self.tmx_data.height * self.tmx_data.tileheight
            self.camera.set_map_size(map_width, map_height)

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
            self.draw()

        self.save_settings()
        pygame.quit()

    def get_spawn_point(self):
        if self.map_loaded:
            for layer in self.tmx_data.layers:
                if hasattr(layer, 'objects'):
                    for obj in layer:
                        if hasattr(obj, 'type') and (obj.type == 'spawn' or obj.name == 'player_spawn'):
                            return obj.x, obj.y
        return None

    def reset_game(self):
        self.all_sprites.empty()
        self.players.empty()
        self.npcs.empty()
        self.obstacles.empty()
        self.items.empty()

        self.init_game_objects()
        self.state = GameState.MENU
        self.paused = False

        print("Игра сброшена в начальное состояние")

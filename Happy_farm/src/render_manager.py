import pygame
from Happy_farm.src.map_renderer import MapRenderer

class RenderManager:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
        self.map_renderer = MapRenderer()

        # Инициализация шрифтов
        self.title_font = pygame.font.Font(None, 64)
        self.menu_font = pygame.font.Font(None, 36)
        self.ui_font = pygame.font.Font(None, 24)

        # Цветовая палитра
        self.COLORS = {
            'WHITE': (255, 255, 255),
            'BLACK': (0, 0, 0),
            'GRAY': (128, 128, 128),
            'LIGHT_GRAY': (192, 192, 192),
            'GREEN': (0, 255, 0),
            'RED': (255, 0, 0),
            'BLUE': (0, 0, 255),
            'TRANSPARENT_BLACK': (0, 0, 0, 128)
        }

        # Размеры кнопок и отступы
        self.BUTTON_SIZE = (200, 50)
        self.BUTTON_SPACING = 20
        self.SLIDER_SIZE = (200, 20)
        self.CHECKBOX_SIZE = (20, 20)

    def draw_menu(self, game_manager):
        """Отрисовка главного меню"""
        screen = self.screen_manager.get_screen()
        screen.fill(self.COLORS['BLACK'])

        # Заголовок
        title = self.title_font.render("Happy Farm", True, self.COLORS['WHITE'])
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)

        # Кнопки меню
        buttons = ["Начать игру", "Настройки", "Выход"]
        button_y = 250

        for text in buttons:
            button_rect = pygame.Rect(
                (screen.get_width() - self.BUTTON_SIZE[0]) // 2,
                button_y,
                self.BUTTON_SIZE[0],
                self.BUTTON_SIZE[1]
            )

            # Проверка наведения мыши
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.COLORS['GRAY'], button_rect)
                color = self.COLORS['WHITE']
            else:
                pygame.draw.rect(screen, self.COLORS['WHITE'], button_rect, 2)
                color = self.COLORS['WHITE']

            # Текст кнопки
            text_surface = self.menu_font.render(text, True, color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

            button_y += self.BUTTON_SIZE[1] + self.BUTTON_SPACING

    def draw_settings(self, game_manager):
        """Отрисовка меню настроек"""
        screen = self.screen_manager.get_screen()
        screen.fill(self.COLORS['BLACK'])

        # Заголовок
        title = self.title_font.render("Настройки", True, self.COLORS['WHITE'])
        title_rect = title.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title, title_rect)

        # Настройки звука
        self.draw_slider(screen, "Громкость звука", game_manager.settings['sound_volume'], 150)
        self.draw_slider(screen, "Громкость музыки", game_manager.settings['music_volume'], 220)

        # Настройки экрана
        self.draw_checkbox(screen, "Полный экран", game_manager.settings['fullscreen'], 290)

        # Настройки FPS
        self.draw_slider(screen, "Ограничение FPS", game_manager.settings['fps_limit'] / 120, 360)

        # Кнопка "Назад"
        back_rect = pygame.Rect(
            (screen.get_width() - self.BUTTON_SIZE[0]) // 2,
            screen.get_height() - 80,
            self.BUTTON_SIZE[0],
            self.BUTTON_SIZE[1]
        )

        mouse_pos = pygame.mouse.get_pos()
        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.COLORS['GRAY'], back_rect)
            color = self.COLORS['WHITE']
        else:
            pygame.draw.rect(screen, self.COLORS['WHITE'], back_rect, 2)
            color = self.COLORS['WHITE']

        back_text = self.menu_font.render("Назад", True, color)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, back_text_rect)

    def draw_game(self, screen, game_manager):
        """Отрисовка игрового экрана"""
        screen.fill((0, 0, 0))  # Заливка экрана черным цветом

        # Отрисовка карты с учетом камеры
        if game_manager.map_loaded:
            # Получаем видимую область
            camera_rect = game_manager.camera.camera

            # Отрисовываем видимые тайлы
            for layer in game_manager.tmx_data.visible_layers:
                if hasattr(layer, 'data'):
                    # Определяем видимую область в тайлах
                    startx = max(0, camera_rect.x // game_manager.tmx_data.tilewidth)
                    starty = max(0, camera_rect.y // game_manager.tmx_data.tileheight)
                    endx = min(game_manager.tmx_data.width,
                               (camera_rect.x + camera_rect.width) // game_manager.tmx_data.tilewidth + 1)
                    endy = min(game_manager.tmx_data.height,
                               (camera_rect.y + camera_rect.height) // game_manager.tmx_data.tileheight + 1)

                    # Отрисовываем только видимые тайлы
                    for x in range(startx, endx):
                        for y in range(starty, endy):
                            gid = layer.data[y][x]
                            if gid:
                                tile = game_manager.tmx_data.get_tile_image_by_gid(gid)
                                if tile:
                                    # Применяем смещение камеры
                                    pos = game_manager.camera.apply_point(
                                        x * game_manager.tmx_data.tilewidth,
                                        y * game_manager.tmx_data.tileheight
                                    )
                                    screen.blit(tile, pos)

        # Отрисовка спрайтов с учетом камеры
        for sprite in game_manager.all_sprites:
            # Применяем камеру к позиции спрайта
            camera_rect = game_manager.camera.apply(sprite)
            screen.blit(sprite.image, camera_rect)

            # Если это игрок, рисуем его имя
            if sprite == game_manager.player:
                # Отрисовка таблички с именем игрока
                name_tag_bg_rect = pygame.Rect(
                    camera_rect.centerx - sprite.name_tag_bg.get_width() // 2,
                    camera_rect.top - sprite.name_tag_bg.get_height() - 5,
                    sprite.name_tag_bg.get_width(),
                    sprite.name_tag_bg.get_height()
                )
                screen.blit(sprite.name_tag_bg, name_tag_bg_rect)

                name_tag_rect = pygame.Rect(
                    camera_rect.centerx - sprite.name_tag.get_width() // 2,
                    camera_rect.top - sprite.name_tag.get_height() - 7,
                    sprite.name_tag.get_width(),
                    sprite.name_tag.get_height()
                )
                screen.blit(sprite.name_tag, name_tag_rect)

    def draw_map(self, screen, game_manager):
        """Отрисовка игровой карты"""
        for layer in game_manager.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = game_manager.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * game_manager.tmx_data.tilewidth,
                                           y * game_manager.tmx_data.tileheight))

    def draw_game_ui(self, screen, game_manager):
        """Отрисовка игрового интерфейса"""
        # Отображение FPS
        fps = str(int(game_manager.clock.get_fps()))
        fps_text = self.ui_font.render(f"FPS: {fps}", True, self.COLORS['WHITE'])
        screen.blit(fps_text, (10, 10))

    def draw_slider(self, screen, text, value, y_pos):
        """Отрисовка слайдера настроек"""
        # Текст настройки
        text_surface = self.menu_font.render(text, True, self.COLORS['WHITE'])
        screen.blit(text_surface, (50, y_pos))

        # Слайдер
        slider_rect = pygame.Rect(300, y_pos, self.SLIDER_SIZE[0], self.SLIDER_SIZE[1])
        pygame.draw.rect(screen, self.COLORS['WHITE'], slider_rect, 2)

        # Заполнение слайдера
        fill_rect = pygame.Rect(301, y_pos + 1, (self.SLIDER_SIZE[0] - 2) * value, self.SLIDER_SIZE[1] - 2)
        pygame.draw.rect(screen, self.COLORS['WHITE'], fill_rect)

        # Значение
        value_text = self.menu_font.render(f"{int(value * 100)}%", True, self.COLORS['WHITE'])
        screen.blit(value_text, (520, y_pos))

    def draw_checkbox(self, screen, text, checked, y_pos):
        """Отрисовка чекбокса настроек"""
        # Текст настройки
        text_surface = self.menu_font.render(text, True, self.COLORS['WHITE'])
        screen.blit(text_surface, (50, y_pos))

        # Чекбокс
        checkbox_rect = pygame.Rect(300, y_pos, self.CHECKBOX_SIZE[0], self.CHECKBOX_SIZE[1])
        pygame.draw.rect(screen, self.COLORS['WHITE'], checkbox_rect, 2)

        # Отметка
        if checked:
            inner_rect = pygame.Rect(
                checkbox_rect.x + 4,
                checkbox_rect.y + 4,
                checkbox_rect.width - 8,
                checkbox_rect.height - 8
            )
            pygame.draw.rect(screen, self.COLORS['WHITE'], inner_rect)

    def draw_loading_screen(self, screen, progress=0):
        """Отрисовка экрана загрузки"""
        screen.fill(self.COLORS['BLACK'])

        # Текст загрузки
        loading_text = self.title_font.render("Загрузка...", True, self.COLORS['WHITE'])
        text_rect = loading_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
        screen.blit(loading_text, text_rect)

        # Полоса загрузки
        bar_rect = pygame.Rect(
            screen.get_width() // 4,
            screen.get_height() // 2 + 20,
            screen.get_width() // 2,
            20
        )
        pygame.draw.rect(screen, self.COLORS['WHITE'], bar_rect, 2)

        # Заполнение полосы загрузки
        fill_rect = pygame.Rect(
            bar_rect.x + 2,
            bar_rect.y + 2,
            (bar_rect.width - 4) * progress,
            bar_rect.height - 4
        )
        pygame.draw.rect(screen, self.COLORS['WHITE'], fill_rect)

        pygame.display.flip()

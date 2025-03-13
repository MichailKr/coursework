import pygame
from Happy_farm.src.game_state import GameState


class EventHandler:
    def __init__(self, game_manager):
        self.game_manager = game_manager

        # Области кнопок меню
        self.menu_buttons = {
            'play': pygame.Rect(0, 0, 200, 50),
            'settings': pygame.Rect(0, 0, 200, 50),
            'exit': pygame.Rect(0, 0, 200, 50)
        }

        # Области элементов настроек
        self.settings_elements = {
            'sound_slider': pygame.Rect(300, 150, 200, 20),
            'music_slider': pygame.Rect(300, 220, 200, 20),
            'fullscreen': pygame.Rect(300, 290, 20, 20),
            'fps_slider': pygame.Rect(300, 360, 200, 20),
            'back': pygame.Rect(0, 0, 200, 50)  # Кнопка "Назад"
        }

        self.dragging = None

    def update_button_positions(self, screen):
        """Обновление позиций кнопок меню"""
        screen_center_x = screen.get_width() // 2

        # Обновление позиций кнопок меню
        self.menu_buttons['play'].centerx = screen_center_x
        self.menu_buttons['play'].top = 250

        self.menu_buttons['settings'].centerx = screen_center_x
        self.menu_buttons['settings'].top = 320

        self.menu_buttons['exit'].centerx = screen_center_x
        self.menu_buttons['exit'].top = 390

        # Обновление позиции кнопки "Назад"
        self.settings_elements['back'].centerx = screen_center_x
        self.settings_elements['back'].bottom = screen.get_height() - 30

    def handle_events(self):
        """Обработка всех событий"""
        screen = self.game_manager.screen_manager.get_screen()
        self.update_button_positions(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_manager.state == GameState.GAME:
                        self.game_manager.state = GameState.MENU

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.handle_mouse_down(event.pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.handle_mouse_up(event.pos)

            if event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.handle_mouse_motion(event.pos)

        return True

    def handle_mouse_down(self, pos):
        """Обработка нажатия кнопки мыши"""
        if self.game_manager.state == GameState.MENU:
            # Проверка кнопок меню
            if self.menu_buttons['play'].collidepoint(pos):
                self.game_manager.state = GameState.GAME
            elif self.menu_buttons['settings'].collidepoint(pos):
                self.game_manager.state = GameState.SETTINGS
            elif self.menu_buttons['exit'].collidepoint(pos):
                exit()

        elif self.game_manager.state == GameState.SETTINGS:
            # Проверка элементов настроек
            if self.settings_elements['back'].collidepoint(pos):
                self.game_manager.state = GameState.MENU
            elif self.settings_elements['sound_slider'].collidepoint(pos):
                self.dragging = 'sound'
                self.update_slider_value('sound', pos[0])
            elif self.settings_elements['music_slider'].collidepoint(pos):
                self.dragging = 'music'
                self.update_slider_value('music', pos[0])
            elif self.settings_elements['fps_slider'].collidepoint(pos):
                self.dragging = 'fps'
                self.update_slider_value('fps', pos[0])
            elif self.settings_elements['fullscreen'].collidepoint(pos):
                self.toggle_fullscreen()

        return True

    def handle_mouse_up(self, pos):
        """Обработка отпускания кнопки мыши"""
        self.dragging = None

    def handle_mouse_motion(self, pos):
        """Обработка движения мыши"""
        if self.dragging:
            self.update_slider_value(self.dragging, pos[0])

    def update_slider_value(self, slider_type, x_pos):
        """Обновление значения слайдера"""
        if slider_type in ['sound', 'music', 'fps']:
            slider_rect = self.settings_elements[f'{slider_type}_slider']
            relative_x = max(0, min(1, (x_pos - slider_rect.x) / slider_rect.width))

            if slider_type == 'sound':
                self.game_manager.settings['sound_volume'] = relative_x
            elif slider_type == 'music':
                self.game_manager.settings['music_volume'] = relative_x
            elif slider_type == 'fps':
                self.game_manager.settings['fps_limit'] = int(relative_x * 120) + 30  # 30-150 FPS

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        self.game_manager.settings['fullscreen'] = not self.game_manager.settings['fullscreen']
        self.game_manager.toggle_fullscreen()

import pygame
from src.game_state import GameState


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

    def handle_mouse_down_inventory(self, pos):
        if self.game_manager.state == GameState.GAME:
            # Check hotbar slots
            for i, item in enumerate(self.game_manager.hotbar_slots):
                slot_rect = self.get_hotbar_slot_rect(i)
                if slot_rect.collidepoint(pos) and item:
                    self.game_manager.dragged_item = item
                    item.dragging = True
                    item.original_pos = (i, None)  # (hotbar_index, None)
                    return

            # Check inventory slots if inventory is open
            if self.game_manager.inventory_open:
                for row in range(8):
                    for col in range(3):
                        slot_rect = self.get_inventory_slot_rect(row, col)
                        if slot_rect.collidepoint(pos):
                            item = self.game_manager.inventory_slots[row][col]
                            if item:
                                self.game_manager.dragged_item = item
                                item.dragging = True
                                item.original_pos = (row, col)
                                return

    def handle_mouse_up_inventory(self, pos):
        if self.game_manager.dragged_item:
            item = self.game_manager.dragged_item

            # Check hotbar slots
            for i in range(len(self.game_manager.hotbar_slots)):
                slot_rect = self.get_hotbar_slot_rect(i)
                if slot_rect.collidepoint(pos):
                    self.place_item_in_hotbar(item, i)
                    return

            # Check inventory slots
            if self.game_manager.inventory_open:
                for row in range(8):
                    for col in range(3):
                        slot_rect = self.get_inventory_slot_rect(row, col)
                        if slot_rect.collidepoint(pos):
                            self.place_item_in_inventory(item, row, col)
                            return

            # If dropped outside, return to original position
            if item.original_pos[1] is None:  # Was in hotbar
                self.game_manager.hotbar_slots[item.original_pos[0]] = item
            else:  # Was in inventory
                row, col = item.original_pos
                self.game_manager.inventory_slots[row][col] = item

            item.dragging = False
            self.game_manager.dragged_item = None

    def get_hotbar_slot_rect(self, index):
        screen = self.game_manager.screen_manager.get_screen()
        slot_size = 60
        start_x = (screen.get_width() - (8 * slot_size)) // 2
        return pygame.Rect(start_x + (index * slot_size), screen.get_height() - 80, slot_size, slot_size)

    def get_inventory_slot_rect(self, row, col):
        screen = self.game_manager.screen_manager.get_screen()
        slot_size = 70
        start_x = (screen.get_width() - (3 * slot_size)) // 2
        start_y = (screen.get_height() - (8 * slot_size)) // 2
        return pygame.Rect(start_x + (col * slot_size), start_y + (row * slot_size), slot_size, slot_size)

    def place_item_in_hotbar(self, item, slot_index):
        # Swap items if slot is occupied
        current_item = self.game_manager.hotbar_slots[slot_index]
        self.game_manager.hotbar_slots[slot_index] = item

        if current_item:
            row, col = item.original_pos
            if col is None:  # Was in hotbar
                self.game_manager.hotbar_slots[row] = current_item
            else:  # Was in inventory
                self.game_manager.inventory_slots[row][col] = current_item

        item.dragging = False
        self.game_manager.dragged_item = None

    def place_item_in_inventory(self, item, row, col):
        # Swap items if slot is occupied
        current_item = self.game_manager.inventory_slots[row][col]
        self.game_manager.inventory_slots[row][col] = item

        if current_item:
            old_row, old_col = item.original_pos
            if old_col is None:  # Was in hotbar
                self.game_manager.hotbar_slots[old_row] = current_item
            else:  # Was in inventory
                self.game_manager.inventory_slots[old_row][old_col] = current_item

        item.dragging = False
        self.game_manager.dragged_item = None


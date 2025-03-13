import pygame
from Happy_farm.src.settings import WINDOW_SIZE
from Happy_farm.src.settings import FULLSCREEN_SIZE

class ScreenManager:
    def __init__(self):
        self.current_mode = 'windowed'
        self.screen = pygame.display.set_mode(WINDOW_SIZE[self.current_mode])
        pygame.display.set_caption("Happy Farm")

    def toggle_screen_mode(self, mode):
        if mode != self.current_mode:
            self.current_mode = mode
            if mode == 'fullscreen':
                self.screen = pygame.display.set_mode(WINDOW_SIZE[mode], pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode(WINDOW_SIZE[mode])

    def get_screen(self):
        return self.screen

    def get_center_x(self):
        return WINDOW_SIZE[self.current_mode][0] // 2

    def get_center_y(self):
        return WINDOW_SIZE[self.current_mode][1] // 2

    def get_current_mode(self):
        return self.current_mode

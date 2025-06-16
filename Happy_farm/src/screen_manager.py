import pygame
from src.settings import WINDOW_SIZE
from src.settings import FULLSCREEN_SIZE
from src.save_manager import SaveManager

class ScreenManager:
    def __init__(self):
        self.save_manager = SaveManager()
        self.current_mode = 'windowed'
        if self.save_manager.saved_data['fullscreen'] == True:
            self.current_mode = 'fullscreen'

        self.screen = pygame.display.set_mode(WINDOW_SIZE[self.current_mode])
        pygame.display.set_caption("Happy Farm")

    def toggle_screen_mode(self):
        if self.current_mode == 'windowed':
            self.current_mode = 'fullscreen'
            self.screen = pygame.display.set_mode(WINDOW_SIZE['fullscreen'], pygame.FULLSCREEN)
        else:
            self.current_mode = 'windowed'
            self.screen = pygame.display.set_mode(WINDOW_SIZE['windowed'])

    def get_screen(self):
        return self.screen

    def get_center_x(self):
        return WINDOW_SIZE[self.current_mode][0] // 2

    def get_center_y(self):
        return WINDOW_SIZE[self.current_mode][1] // 2

    def get_current_mode(self):
        return self.current_mode

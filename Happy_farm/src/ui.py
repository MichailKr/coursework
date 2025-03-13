import pygame
from settings import WHITE, BLACK, GRAY, DARK_GRAY


class Button:
    def __init__(self, x, y, width, height, text, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False

    def draw(self, surface):
        color = DARK_GRAY if self.is_hovered else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class Slider:
    def __init__(self, x, y, width, height, start_value=0.7):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = start_value
        self.grabbed = False

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        slider_x = self.rect.x + (self.rect.width * self.value) - 5
        slider_rect = pygame.Rect(slider_x, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(surface, WHITE, slider_rect)
        pygame.draw.rect(surface, BLACK, slider_rect, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.grabbed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False
        elif event.type == pygame.MOUSEMOTION and self.grabbed:
            relative_x = event.pos[0] - self.rect.x
            self.value = max(0, min(1, relative_x / self.rect.width))
            return True
        return False

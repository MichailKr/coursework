import pygame

def load_animations(sprite_sheet, sprite_size=32):
    """Разделяет спрайтшит персонажа на анимации."""
    rows = 6  # Количество строк на спрайтшите
    cols = 4  # Количество кадров в каждой строке
    animations = {
        "down_idle": [],     # 1 строка, 1 кадр
        "down_walk": [],     # 2 строка, 4 кадра
        "up_walk": [],       # 3 строка, 4 кадра
        "left_walk": [],     # 4 строка, 4 кадра
        "right_walk": []     # 5 строка, 4 кадра
    }

    for row in range(rows):
        for col in range(cols):
            # Извлекаем кадр из спрайтшита
            x = col * sprite_size
            y = row * sprite_size
            frame = sprite_sheet.subsurface((x, y, sprite_size, sprite_size))

            # Добавляем кадры в соответствующие анимации
            if row == 0 and col == 0:
                animations["down_idle"].append(frame)
            elif row == 1:
                animations["down_walk"].append(frame)
            elif row == 2:
                animations["up_walk"].append(frame)
            elif row == 3:
                animations["left_walk"].append(frame)
            elif row == 4:
                animations["right_walk"].append(frame)
    return animations

# Использование:
sprite_sheet = pygame.image.load("player_action_sprite_heet.png").convert_alpha()
animations = load_animations(sprite_sheet, sprite_size=32)

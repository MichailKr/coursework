from PIL import Image
import numpy as np


def split_spritesheet(filename, output_folder='tools_sprites'):
    # Создаем папку для сохранения спрайтов, если ее нет
    import os
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Открываем изображение
    img = Image.open(filename)
    img_data = np.array(img)

    # Получаем альфа-канал, если он есть
    if img.mode == 'RGBA':
        alpha = img_data[:, :, 3]
    else:
        # Если нет альфа-канала, считаем все пиксели непрозрачными
        alpha = np.ones((img.height, img.width), dtype=np.uint8) * 255

    # Подсчитываем количество строк и столбцов
    rows = 6  # В вашем случае 6 строки
    cols = 6  # В вашем случае 6 столбца

    sprite_width = img.width // cols
    sprite_height = img.height // rows

    count = 0
    for row in range(rows):
        for col in range(cols):
            # Обрезаем спрайт
            left = col * sprite_width
            upper = row * sprite_height
            right = left + sprite_width
            lower = upper + sprite_height

            sprite = img.crop((left, upper, right, lower))

            # Сохраняем спрайт
            sprite.save(f'{output_folder}/sprite_{count}.png')
            count += 1

    print(f"Сохранено {count} спрайтов в папку {output_folder}")


# Используем функцию
split_spritesheet('Tools.png')

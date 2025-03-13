import os
import pygame
import pytmx


class ResourceLoader:
    @staticmethod
    def load_resources():
        resources = {
            'loaded': False,
            'sprites': {},
            'sounds': {},
            'tilemap': None
        }

        try:
            # Проверяем, существуют ли необходимые файлы
            required_files = ["maps.tmx", "player_action_sprite_heet.png", "gra.tsx"]  # Добавили gra.tsx
            missing_files = [f for f in required_files if not os.path.exists(f)]

            if missing_files:
                print(f"Отсутствуют файлы: {', '.join(missing_files)}")
                return resources

            # Создаем проверку для grass.png, если она требуется
            if not os.path.exists("grass.png") and os.path.exists("gra.tsx"):
                print("Файл grass.png не найден, но найден gra.tsx. Используем его вместо grass.png")
                # Можно сделать симлинк или копию файла, если система ожидает определенное имя
                # Пример: os.symlink("gra.tsx", "grass.png")

            # Загрузка TMX карты с указанием базового пути к тайлсетам
            resources['tilemap'] = pytmx.load_pygame("maps.tmx", pixelalpha=True)

            # Загрузка спрайта игрока
            resources['sprites']['player'] = pygame.image.load("character_move_sprite_sheet.png").convert_alpha()

            resources['loaded'] = True
            return resources

        except Exception as e:
            print(f"Ошибка при загрузке ресурсов: {e}")
            return resources
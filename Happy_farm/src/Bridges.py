#  мост.py
import pygame
import os
from src.item import Item, Mater


class ShopItem:
    """Класс для предметов, нужных при создании моста"""

    def __init__(self, item, quantity):
        self.item = item
        self.quantity = quantity

class Bridge:

    """Класс моста с интерфейсом отдачи ресурсов"""

    def __init__(self, game_manager, x, y, q1, q2):
        self.build = False  # Статус построенности моста
        self.game_manager = game_manager
        self.x = x
        self.y = y
        self.quantity_wood = q1
        self.quantity_brick = q2
        self.is_open = True
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 14)
        self.resources_needed = []  # Список ресурсов для построения
        self.selected_resource_index = 0
        self.show_dialog = False

        # Инициализация ресурсов, необходимых для построения
        self.init_resources()

    def init_resources(self):
        """Задаем ресурсы, необходимые для постройки моста"""

        item_sprites_seed_path = os.path.join("sprites", "materials")

        brick_image = pygame.image.load(os.path.join(item_sprites_seed_path, "brick.png")).convert_alpha()
        wood_image = pygame.image.load(os.path.join(item_sprites_seed_path, "wood.png")).convert_alpha()

        # Предположим, что у вас есть ресурсы "Кирпичи" и "Доски"
        bricks = Mater("Кирпичи", brick_image, "brick")
        wood = Mater("Доски", wood_image, "wood")
        self.resources_needed = [
        ShopItem(bricks, self.quantity_brick),
        ShopItem(wood, self.quantity_wood)
        ]

    def toggle_dialog(self):
        self.show_dialog = not self.show_dialog

    def is_player_in_range(self):
        """Проверка, в радиусе ли игрок"""
        player = self.game_manager.player
        distance = ((player.rect.centerx - self.x) ** 2 +
                    (player.rect.centery - self.y) ** 2) ** 0.5
        return distance <= 50  # радиус для взаимодействия

    def handle_input(self, keys, events):
        """Обработка ввода для интерфейса отдачи ресурсов"""
        if not self.build:
            if self.is_player_in_range():
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_e:
                            # Переключаем состояние диалога (открываем или закрываем)
                            self.toggle_dialog()
                            return True
        else:
            # После постройки мост
            pass

        if self.show_dialog:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_resource_index = max(0, self.selected_resource_index - 1)
                        return True
                    elif event.key == pygame.K_DOWN:
                        self.selected_resource_index = min(len(self.resources_needed) - 1,
                                                           self.selected_resource_index + 1)
                        return True
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.attempt_give_resource()
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        # Закрываем диалог при нажатии ESC
                        self.toggle_dialog()
                        return True
                    elif event.key == pygame.K_e:
                        # Закрываем диалог при нажатии E
                        self.toggle_dialog()
                        return True

        return False

    def attempt_give_resource(self):
        """Пытаемся отдать все необходимые ресурсы одновременно."""
        inventory = self.game_manager.inventory_manager
        all_resources_sufficient = True  # Флаг для проверки достаточности ресурсов

        # Проверяем, есть ли у игрока все необходимые ресурсы
        for resource in self.resources_needed:
            if not inventory.has_item(resource.item, resource.quantity):
                all_resources_sufficient = False
                print(f"Недостаточно ресурсов: {resource.quantity} {resource.item.name}")
                break  # Прерываем цикл, если хотя бы одного ресурса не хватает

        # Если все ресурсы есть, удаляем их из инвентаря
        if all_resources_sufficient:
            for resource in self.resources_needed:
                inventory.remove_item_from_inventory(resource.item, resource.quantity)
                print(f"Отдано {resource.quantity} {resource.item.name}")

            self.build = True
            print("Мост построен!")
            self.toggle_dialog()
        else:
            print("Недостаточно ресурсов для отдачи.")

    def draw(self, screen):
        """Отрисовка интерфейса"""
        if not self.build:
            if self.is_player_in_range():
                self.draw_hint(screen)
            if self.show_dialog:
                self.draw_dialog(screen)

            else:
                # Мост построен, можно показывать его
                pass

    def draw_hint(self, screen):
        """Отрисовка подсказки об открытии магазина"""
        hint_text = "Нажмите E для открытия моста"
        text_surface = self.font.render(hint_text, True, (255, 255, 255))
        # Позиционируем текст по центру экрана внизу
        text_rect = text_surface.get_rect()
        text_rect.centerx = screen.get_width() // 2
        text_rect.y = screen.get_height() - 150
        # Фон для текста
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        screen.blit(text_surface, text_rect)

    def draw_dialog(self, screen):
        # Окно отдачи ресурсов
        width, height = 400, 200
        x = (screen.get_width() - width) // 2
        y = (screen.get_height() - height) // 2
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)

        title = self.font.render("Отдайте ресурсы для моста", True, (255, 255, 255))
        screen.blit(title, (x + 10, y + 10))

        for idx, res in enumerate(self.resources_needed):
            item_image = pygame.transform.scale(res.item.image, (40, 40))

            # Определяем координаты для изображения и текста
            image_x = x + 10  # Отступ слева
            image_y = y + 50 + idx * 30  # Вертикальная позиция для изображения

            # Рисуем изображение
            screen.blit(item_image, (image_x, image_y))

            # Рисуем текст рядом с изображением
            text_str = f"{res.item.name}: {res.quantity}"
            text = self.small_font.render(text_str, True, (255, 255, 0))

            # Вычисляем позицию текста так, чтобы он был на одном уровне с изображением
            text_x = image_x + item_image.get_width() + 10  # Позиция текста справа от изображения
            text_y = image_y + (item_image.get_height() - text.get_height()) // 2  # Центрируем текст по вертикали

            screen.blit(text, (text_x, text_y))

        instructions = self.small_font.render("UP/DOWN - выбрать, ENTER - отдать, ESC - отмена", True, (200, 200, 200))
        screen.blit(instructions, (x + 10, y + height - 30))

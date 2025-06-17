# item.py
import pygame
import os


class Item(pygame.sprite.Sprite):
    def __init__(self, name, image_path_or_surface, item_type, stackable=False, max_stack=1, quantity=1, description="",
                 scale_to_size=None):
        super().__init__()
        self.name = name
        # Изменено: image_path_or_surface может быть как строкой, так и pygame.Surface
        self.image_path = None  # Будет хранить путь, если был передан путь
        self.image = self._load_image(image_path_or_surface, scale_to_size)  # Вызываем _load_image

        if isinstance(image_path_or_surface, str):  # Если был передан путь, сохраняем его
            self.image_path = image_path_or_surface

        if self.image:
            self.rect = self.image.get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 32, 32)  # Заглушка, если нет изображения

        self.item_type = item_type
        self.stackable = stackable
        self.max_stack = max_stack
        self.quantity = quantity  # Добавлено quantity в __init__ Item
        self.description = description

    def _load_image(self, path_or_surface, scale_to_size):
        """
        Внутренний метод для загрузки и масштабирования изображения.
        Принимает либо путь к файлу (строку), либо уже загруженный pygame.Surface.
        """
        if isinstance(path_or_surface, pygame.Surface):
            # Если уже передан Surface, просто используем его
            image = path_or_surface
            if scale_to_size:
                if image.get_size() != scale_to_size:  # Масштабируем только если размер отличается
                    image = pygame.transform.scale(image, scale_to_size)
            return image

        if not path_or_surface:  # Если ни Surface, ни пути нет
            print(f"Предупреждение: для предмета '{self.name}' не указан путь к изображению или Surface.")
            return None

        # Если path_or_surface - это строка (путь)
        try:
            image = pygame.image.load(path_or_surface).convert_alpha()
            if scale_to_size:
                image = pygame.transform.scale(image, scale_to_size)
            return image
        except pygame.error as e:
            print(f"Ошибка загрузки изображения '{path_or_surface}' для предмета '{self.name}': {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка при загрузке изображения '{path_or_surface}' для предмета '{self.name}': {e}")
            return None

    def use(self, target):
        pass

    def __str__(self):
        if self.stackable:
            return f"{self.name} (x{self.quantity}/{self.max_stack})"
        else:
            return self.name


class Tool(Item):
    # Добавил quantity=1 в __init__, чтобы соответствовать базовому Item
    def __init__(self, name, image_path_or_surface, tool_type, durability=100, quantity=1, description="",
                 scale_to_size=None):
        super().__init__(name, image_path_or_surface, 'tool', stackable=False, max_stack=1, quantity=quantity,
                         description=description, scale_to_size=scale_to_size)
        self.tool_type = tool_type
        self.durability = durability
        self.max_durability = durability


class Seed(Item):
    # Добавил quantity=1 в __init__, чтобы соответствовать базовому Item
    def __init__(self, name, image_path_or_surface, plant_type, quantity=1, description="", scale_to_size=None):
        super().__init__(name, image_path_or_surface, 'seed', stackable=True, max_stack=20, quantity=quantity,
                         description=description, scale_to_size=scale_to_size)
        self.plant_type = plant_type
        # self.quantity уже устанавливается в super().__init__


class Tomato(Item):
    # Добавил image_path_or_surface=None, чтобы можно было передать Surface при инициализации
    def __init__(self, quantity=1, description="Сочный красный помидор.", scale_to_size=None,
                 image_path_or_surface=None):
        # Используем image_path_or_surface если он передан, иначе наш дефолтный путь
        path = "sprites/plants/grownPlants/tomato.png" if image_path_or_surface is None else image_path_or_surface
        super().__init__("Томаты", path, "crop", stackable=True, max_stack=99, quantity=quantity,
                         description=description, scale_to_size=scale_to_size)
        # self.quantity уже устанавливается в super().__init__


class Wheat(Item):
    # Добавил image_path_or_surface=None, чтобы можно было передать Surface при инициализации
    def __init__(self, quantity=1, description="Золотистый колосок пшеницы.", scale_to_size=None,
                 image_path_or_surface=None):
        # Используем image_path_or_surface если он передан, иначе наш дефолтный путь
        path = "sprites/plants/grownPlants/wheat.png" if image_path_or_surface is None else image_path_or_surface
        super().__init__("Пшеница", path, "crop", stackable=True, max_stack=99, quantity=quantity,
                         description=description, scale_to_size=scale_to_size)
        # self.quantity уже устанавливается в super().__init__

class Mater(Item):
    def __init__(self, name, image, mat_type):
        # Семена стакаются (например, до 20 штук)
        super().__init__(name, image, 'mat', stackable=True, max_stack=10)
        self.mat_type = mat_type
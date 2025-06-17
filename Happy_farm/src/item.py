import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, name, image, item_type, stackable=False, max_stack=1):
        super().__init__()
        self.name = name
        self.image = image
        self.rect = self.image.get_rect()
        self.type = item_type
        self.stackable = stackable  # Можно ли стакать предмет
        self.max_stack = max_stack  # Максимальное количество в стаке
        self.quantity = 1  # Текущее количество в стаке

    def use(self, target):
        pass  # Реализуем в подклассах

class Tool(Item):
    def __init__(self, name, image, tool_type, durability=100):
        # Инструменты не стакаются
        super().__init__(name, image, tool_type, stackable=False, max_stack=1)
        self.durability = durability
        self.max_durability = durability

class Seed(Item):
    def __init__(self, name, image, plant_type):
        # Семена стакаются (например, до 20 штук)
        super().__init__(name, image, 'seed', stackable=True, max_stack=20)
        self.plant_type = plant_type

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
    def plant(self, location):
        # Метод для посадки семени. Пока просто заглушка.
        print(f"Посажено семя {self.name} в {location}")
        pass

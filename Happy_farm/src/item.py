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

    def plant(self, location):
        # Метод для посадки семени. Пока просто заглушка.
        print(f"Посажено семя {self.name} в {location}")
        pass


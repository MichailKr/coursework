import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, name, image, item_type): # Изменил tool_type на item_type для более общего названия
        super().__init__()
        self.name = name
        self.image = image # Добавлено сохранение изображения
        self.rect = self.image.get_rect()
        self.type = item_type  # Сохраняем тип предмета (или инструмента)

    def use(self, target):
        pass  # Реализуем в подклассах

class Tool(Item):
    def __init__(self, name, image, tool_type, durability=100):
        # Вызываем конструктор базового класса Item, передавая tool_type как item_type
        super().__init__(name, image, tool_type)
        self.durability = durability
        self.max_durability = durability

class Seed(Item):
    def __init__(self, name, image, plant_type):
        # Указываем тип предмета как 'seed' и добавляем тип растения (cucumber, tomato, potato)
        super().__init__(name, image, 'seed')
        self.plant_type = plant_type # Тип растения, которое вырастет из семени
        # Здесь можно добавить другие атрибуты, связанные с ростом, если понадобится

    def plant(self, location):
        # Метод для посадки семени. Пока просто заглушка.
        print(f"Посажено семя {self.name} в {location}")
        pass
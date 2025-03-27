import pygame


class Item(pygame.sprite.Sprite):
    def __init__(self, name, image, tool_type):
        super().__init__()
        self.name = name
        self.image = image
        self.rect = self.image.get_rect()
        self.tool_type = tool_type  # hoe, axe, wateringcan

    def use(self, target):
        pass  # Реализуем в подклассах


class Tool(Item):
    def __init__(self, name, image, tool_type, durability=100):
        super().__init__(name, image, tool_type)
        self.durability = durability
        self.max_durability = durability

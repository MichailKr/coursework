import pygame


class TiledMap:
    def __init__(self, tmx_data):
        self.tmx_data = tmx_data
        self.width = tmx_data.width * tmx_data.tilewidth
        self.height = tmx_data.height * tmx_data.tileheight
        self.render_surface = self.make_map()

    def render(self, surface, pos=(0, 0)):
        surface.blit(self.render_surface, pos)

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        temp_surface.set_colorkey((0, 0, 0))

        # Отрисовка каждого слоя
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):  # Это слой тайлов
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        temp_surface.blit(
                            tile,
                            (x * self.tmx_data.tilewidth,
                             y * self.tmx_data.tileheight)
                        )

        return temp_surface

    def get_tile_properties(self, x, y, layer):
        """Получение свойств тайла по координатам"""
        tile = self.tmx_data.get_tile_properties(x, y, layer)
        return tile if tile else None

    def get_object_layer(self, layer_name):
        """Получение слоя объектов по имени"""
        return self.tmx_data.get_layer_by_name(layer_name)

import pygame
from Happy_farm.src.tilemap import TiledMap  # Импортируем класс Tilemap


def render_map(screen):
    """Отрисовка карты."""
    clock = pygame.time.Clock()

    # Загрузка карты
    try:
        tilemap = TiledMap("maps.tmx")
    except Exception as e:
        print(f"Ошибка загрузки карты: {e}")
        pygame.quit()
        raise SystemExit

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Закрытие окна
                pygame.quit()
                return

        # Отрисовка карты
        screen.fill((0, 0, 0))  # Очистка экрана
        tilemap.draw(screen)

        pygame.display.flip()
        clock.tick(60)

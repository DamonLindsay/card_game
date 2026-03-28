import pygame
from card import Unit

# --- Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
FPS = 60
BG_COLOUR = (30, 60, 40)

# --- Card Dimensions ---
CARD_WIDTH = 120
CARD_HEIGHT = 180


def draw_unit_card(surface, unit: Unit, x: int, y: int):
    """
    Draws a placeholder unit card at position (x, y).
    """
    # Card background
    pygame.draw.rect(surface, (60, 60, 80), (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
    # Card border
    pygame.draw.rect(surface, (200, 200, 220), (x, y, CARD_WIDTH, CARD_HEIGHT), width=2, border_radius=8)

    font_name = pygame.font.SysFont(None, 20)
    font_stats = pygame.font.SysFont(None, 22)

    # Name
    name_surf = font_name.render(unit.name, True, (255, 200, 50))
    surface.blit(name_surf, (x + 8, y + 8))

    # Art Placeholder (grey box)
    pygame.draw.rect(surface, (100, 100, 120), (x + 8, y + 30, CARD_WIDTH - 16, 80))

    # Attack (bottom left)
    atk_surf = font_stats.render(str(unit.attack), True, (255, 200, 50))
    surface.blit(atk_surf, (x + 8, y + CARD_HEIGHT - 28))

    # Health (bottom right)
    hp_surf = font_stats.render(str(unit.health), True, (200, 80, 80))
    surface.blit(hp_surf, (x + CARD_WIDTH - 20, y + CARD_HEIGHT - 20))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Card Game")
    clock = pygame.time.Clock()

    # Create a test unit
    test_unit = Unit(name="Angry Ooze", attack=2, health=3, tribes=["Ooze"])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOUR)
        draw_unit_card(screen, test_unit, x=100, y=100)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

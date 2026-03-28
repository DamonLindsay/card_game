import pygame
from card import Unit
from deck import Deck
from hand import Hand

# --- Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
FPS = 60
BACKGROUND_COLOUR = (30, 30, 40)

# --- Card Dimensions ---
CARD_WIDTH = 140
CARD_HEIGHT = 200
CARD_SPACING = 20
HAND_Y_POSITION = SCREEN_HEIGHT - CARD_HEIGHT - 20


def draw_unit_card(surface: pygame.Surface, unit: Unit, x: int, y: int):
    """Draws a placeholder unit card at the given position."""
    # Card background
    pygame.draw.rect(surface, (60, 60, 80), (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
    # Card border
    pygame.draw.rect(surface, (200, 200, 220), (x, y, CARD_WIDTH, CARD_HEIGHT), width=2, border_radius=8)

    font_name_text = pygame.font.SysFont(None, 19)
    font_stats_text = pygame.font.SysFont(None, 24)

    # Art Placeholder
    art_padding = 8
    art_height = 90
    pygame.draw.rect(surface, (100, 100, 120), (x + art_padding, y + 24, CARD_WIDTH - art_padding * 2, art_height))

    # Name banner background
    name_banner_y = y + 24 + art_height + 4
    pygame.draw.rect(surface, (40, 40, 60), (x + 4, name_banner_y, CARD_WIDTH - 8, 22))

    # Name text centred in banner
    name_surface = font_name_text.render(unit.name, True, (255, 255, 255))
    name_x = x + (CARD_WIDTH - name_surface.get_width()) // 2
    surface.blit(name_surface, (name_x, name_banner_y + 3))

    # Mana cost (top left circle)
    mana_circle_x = x + 14
    mana_circle_y = y + 14
    pygame.draw.circle(surface, (30, 80, 200), (mana_circle_x, mana_circle_y), 12)
    pygame.draw.circle(surface, (100, 150, 255), (mana_circle_x, mana_circle_y), 12, width=2)
    mana_surface = font_stats_text.render(str(unit.mana_cost), True, (255, 255, 255))
    mana_text_x = mana_circle_x - mana_surface.get_width() // 2
    mana_text_y = mana_circle_y - mana_surface.get_height() // 2
    surface.blit(mana_surface, (mana_text_x, mana_text_y))

    # Attack (bottom left)
    attack_circle_x = x + 14
    attack_circle_y = y + CARD_HEIGHT - 14
    pygame.draw.circle(surface, (180, 140, 20), (attack_circle_x, attack_circle_y), 12)
    pygame.draw.circle(surface, (255, 200, 50), (attack_circle_x, attack_circle_y), 12, width=2)
    attack_surface = font_stats_text.render(str(unit.attack), True, (255, 255, 255))
    attack_text_x = attack_circle_x - attack_surface.get_width() // 2
    attack_text_y = attack_circle_y - attack_surface.get_height() // 2
    surface.blit(attack_surface, (attack_text_x, attack_text_y))

    # Health (bottom right)
    health_circle_x = x + CARD_WIDTH - 14
    health_circle_y = y + CARD_HEIGHT - 14
    pygame.draw.circle(surface, (160, 30, 30), (health_circle_x, health_circle_y), 12)
    pygame.draw.circle(surface, (220, 80, 80), (health_circle_x, health_circle_y), 12, width=2)
    health_surface = font_stats_text.render(str(unit.health), True, (255, 255, 255))
    health_text_x = health_circle_x - health_surface.get_width() // 2
    health_text_y = health_circle_y - health_surface.get_height() // 2
    surface.blit(health_surface, (health_text_x, health_text_y))


def draw_hand(surface: pygame.Surface, hand: Hand):
    """Draws all cards in the hand evenly spaced across the bottom of the screen."""
    total_hand_width = len(hand.cards) * CARD_WIDTH + (len(hand.cards) - 1) * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_hand_width) // 2

    for index, card in enumerate(hand.cards):
        card_x = start_x + index * (CARD_WIDTH + CARD_SPACING)
        if isinstance(card, Unit):
            draw_unit_card(surface, card, card_x, HAND_Y_POSITION)


def build_test_deck() -> Deck:
    """Creates a small test deck of units for development purposes."""
    test_cards = [
        Unit(name="Angry Ooze", attack=2, health=3, mana_cost=2, tribes=["Ooze"]),
        Unit(name="Stone Golem", attack=4, health=6, mana_cost=5),
        Unit(name="Swift Fox", attack=3, health=2, mana_cost=2, tribes=["Beast"]),
        Unit(name="Cave Troll", attack=5, health=2, mana_cost=4, tribes=["Troll"]),
        Unit(name="Fire Sprite", attack=2, health=2, mana_cost=1, tribes=["Elemental"]),
        Unit(name="Iron Shield", attack=1, health=7, mana_cost=3),
        Unit(name="Bog Witch", attack=2, health=3, mana_cost=3),
    ]
    deck = Deck(cards=test_cards)
    deck.shuffle()
    return deck


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Card Game")
    clock = pygame.time.Clock()

    deck = build_test_deck()
    hand = Hand()

    # Draw 4 cards into the starting hand
    for _ in range(4):
        drawn_card = deck.draw()
        if drawn_card is not None:
            hand.add_card(drawn_card)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOUR)
        draw_hand(screen, hand)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

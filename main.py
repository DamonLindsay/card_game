import pygame
from card import Unit
from deck import Deck
from hand import Hand
from game_state import GameState
from combat import build_combat_event_queue
from boss import Boss

# --- Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
FPS = 60
BACKGROUND_COLOUR = (30, 30, 40)
COMBAT_EVENT_DELAY_MILLISECONDS = 600

# --- Card Dimensions ---
CARD_WIDTH = 140
CARD_HEIGHT = 200
CARD_SPACING = 20

# --- Board Layout ---
PLAYER_BOARD_Y = SCREEN_HEIGHT // 2 + 30
BOSS_BOARD_Y = 60
BOARD_ZONE_HEIGHT = 150
HAND_Y_POSITION = SCREEN_HEIGHT - CARD_HEIGHT - 10

# --- Colours ---
COLOUR_MANA_FILL = (30, 80, 200)
COLOUR_MANA_EMPTY = (20, 20, 50)
COLOUR_HEALTH_PLAYER = (60, 180, 60)
COLOUR_HEALTH_BOSS = (180, 60, 60)
COLOUR_BUTTON_ACTIVE = (60, 140, 60)
COLOUR_BUTTON_INACTIVE = (80, 80, 80)
COLOUR_TEXT_DEFAULT = (255, 255, 255)
COLOUR_STAT_ATTACK = (255, 200, 50)
COLOUR_STAT_HEALTH = (220, 80, 80)
COLOUR_STAT_MANA = (100, 150, 255)
COLOUR_CARD_SELECTED = (255, 255, 100)
COLOUR_CARD_UNAFFORDABLE = (120, 60, 60)


def draw_unit_card(surface: pygame.Surface, unit: Unit, x: int, y: int, is_selected: bool = False,
                   is_affordable: bool = True):
    """Draws a unit card at the given position with optional selection and affordability highlights."""
    background_colour = (60, 60, 80)
    if is_selected:
        border_colour = COLOUR_CARD_SELECTED
        border_width = 3
    elif not is_affordable:
        background_colour = (45, 35, 45)
        border_colour = COLOUR_CARD_UNAFFORDABLE
        border_width = 2
    else:
        border_colour = (200, 200, 220)
        border_width = 2

    pygame.draw.rect(surface, background_colour, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
    pygame.draw.rect(surface, border_colour, (x, y, CARD_WIDTH, CARD_HEIGHT), width=border_width, border_radius=8)

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
    name_surface = font_name_text.render(unit.name, True, COLOUR_TEXT_DEFAULT)
    name_x = x + (CARD_WIDTH - name_surface.get_width()) // 2
    surface.blit(name_surface, (name_x, name_banner_y + 3))

    # Mana cost (top left circle)
    draw_stat_circle(surface, unit.mana_cost, x + 14, y + 14, COLOUR_MANA_FILL, COLOUR_STAT_MANA, font_stats_text)

    # Attack (bottom left)
    draw_stat_circle(surface, unit.attack, x + 14, y + CARD_HEIGHT - 14, (180, 140, 20), COLOUR_STAT_ATTACK,
                     font_stats_text)

    # Health (bottom right)
    draw_stat_circle(surface, unit.health, x + CARD_WIDTH - 14, y + CARD_HEIGHT - 14, (160, 30, 30), COLOUR_STAT_HEALTH,
                     font_stats_text)


def draw_stat_circle(surface: pygame.Surface, value: int, center_x: int, center_y: int, fill_colour: tuple,
                     border_colour: tuple, font: pygame.font.Font):
    """Draws a filled circle with a number inside, used for card stats."""
    pygame.draw.circle(surface, fill_colour, (center_x, center_y), 12)
    pygame.draw.circle(surface, border_colour, (center_x, center_y), 12, width=2)
    value_surface = font.render(str(value), True, COLOUR_TEXT_DEFAULT)
    value_x = center_x - value_surface.get_width() // 2
    value_y = center_y - value_surface.get_height() // 2
    surface.blit(value_surface, (value_x, value_y))


def draw_hand(surface: pygame.Surface, hand: Hand, selected_card: Unit, current_mana: int) -> list[tuple]:
    """Draws all cards in the hand and returns a list of (card, rect) for click detection."""
    total_hand_width = len(hand.cards) * CARD_WIDTH + (len(hand.cards) - 1) * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_hand_width) // 2
    card_rects = []

    for index, card in enumerate(hand.cards):
        card_x = start_x + index * (CARD_WIDTH + CARD_SPACING)
        is_selected = card is selected_card
        is_affordable = current_mana >= card.mana_cost
        if isinstance(card, Unit):
            draw_unit_card(surface, card, card_x, HAND_Y_POSITION, is_selected=is_selected, is_affordable=is_affordable)
        card_rects.append((card, pygame.Rect(card_x, HAND_Y_POSITION, CARD_WIDTH, CARD_HEIGHT)))

    return card_rects


def draw_player_board(surface: pygame.Surface, board: list) -> list[tuple]:
    """Draws all units on the player board and returns a list of (card, rect)."""
    total_board_width = len(board) * CARD_WIDTH + (len(board) - 1) * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_board_width) // 2
    card_rects = []

    for index, unit in enumerate(board):
        card_x = start_x + index * (CARD_WIDTH + CARD_SPACING)
        card_y = PLAYER_BOARD_Y + (BOARD_ZONE_HEIGHT - CARD_HEIGHT) // 2
        draw_unit_card(surface, unit, card_x, card_y)
        card_rects.append((unit, pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)))

    return card_rects


def draw_boss_board(surface: pygame.Surface, board: list) -> list[tuple]:
    """Draws all units on the boss board and returns a list of (unit, rect)."""
    total_board_width = len(board) * CARD_WIDTH + (len(board) - 1) * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_board_width) // 2
    card_rects = []

    for index, unit in enumerate(board):
        card_x = start_x + index * (CARD_WIDTH + CARD_SPACING)
        card_y = BOSS_BOARD_Y + (BOARD_ZONE_HEIGHT - CARD_HEIGHT) // 2
        draw_unit_card(surface, unit, card_x, card_y)
        card_rects.append((unit, pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)))

    return card_rects


def draw_mana_bar(surface: pygame.Surface, current_mana: int, maximum_mana: int):
    """Draws the mana pip bar in the bottom right corner."""
    font = pygame.font.SysFont(None, 22)
    pip_radius = 10
    pip_spacing = 4
    pip_y = SCREEN_HEIGHT // 2

    # Draw pips right to left, anchored from the End Turn button edge.
    anchor_x = SCREEN_WIDTH - 180  # leaves room for End Turn button
    total_width = maximum_mana * (pip_radius * 2 + pip_spacing)
    start_x = anchor_x - total_width

    for index in range(maximum_mana):
        pip_x = start_x + index * (pip_radius * 2 + pip_spacing) + pip_radius
        colour = COLOUR_MANA_FILL if index < current_mana else COLOUR_MANA_EMPTY
        pygame.draw.circle(surface, colour, (pip_x, pip_y), pip_radius)
        pygame.draw.circle(surface, COLOUR_STAT_MANA, (pip_x, pip_y), pip_radius, width=2)

    mana_label = font.render(f"{current_mana} / {maximum_mana}", True, COLOUR_TEXT_DEFAULT)
    label_x = start_x + (total_width - mana_label.get_width()) // 2
    surface.blit(mana_label, (label_x, pip_y + pip_radius + 4))


def draw_health(surface: pygame.Surface, health: int, label: str, x: int, y: int, colour: tuple):
    """Draws a health display for the player or boss."""
    font_label = pygame.font.SysFont(None, 22)
    font_value = pygame.font.SysFont(None, 36)

    label_surface = font_label.render(label, True, COLOUR_TEXT_DEFAULT)
    surface.blit(label_surface, (x, y))

    health_surface = font_value.render(str(health), True, colour)
    surface.blit(health_surface, (x, y + 20))


def draw_end_turn_button(surface: pygame.Surface, is_player_turn: bool) -> pygame.Rect:
    """Draws the End Turn button and returns its rect for click detection."""
    button_width = 140
    button_height = 50
    button_x = SCREEN_WIDTH - button_width - 20
    button_y = SCREEN_HEIGHT // 2 - button_height // 2

    colour = COLOUR_BUTTON_ACTIVE if is_player_turn else COLOUR_BUTTON_INACTIVE
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(surface, colour, button_rect, border_radius=8)
    pygame.draw.rect(surface, COLOUR_TEXT_DEFAULT, button_rect, width=2, border_radius=8)

    font = pygame.font.SysFont(None, 26)
    label = "End Turn" if is_player_turn else "Boss Turn..."
    label_surface = font.render(label, True, COLOUR_TEXT_DEFAULT)
    label_x = button_x + (button_width - label_surface.get_width()) // 2
    label_y = button_y + (button_height - label_surface.get_height()) // 2
    surface.blit(label_surface, (label_x, label_y))

    return button_rect


def draw_board_zones(surface: pygame.Surface):
    """Draws the player and boss board zone outlines."""
    player_zone = pygame.Rect(60, PLAYER_BOARD_Y, SCREEN_WIDTH - 140, BOARD_ZONE_HEIGHT)
    boss_zone = pygame.Rect(60, BOSS_BOARD_Y, SCREEN_WIDTH - 140, BOARD_ZONE_HEIGHT)
    pygame.draw.rect(surface, (50, 50, 70), player_zone, border_radius=8)
    pygame.draw.rect(surface, (70, 50, 50), boss_zone, border_radius=8)
    pygame.draw.rect(surface, (80, 80, 100), player_zone, width=1, border_radius=8)
    pygame.draw.rect(surface, (100, 80, 80), boss_zone, width=1, border_radius=8)

    font = pygame.font.SysFont(None, 20)
    player_label = font.render("Your Board", True, (120, 120, 150))
    boss_label = font.render("Boss Board", True, (150, 120, 120))
    surface.blit(player_label, (70, PLAYER_BOARD_Y + 6))
    surface.blit(boss_label, (70, BOSS_BOARD_Y + 6))


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


def get_player_board_zone_rect() -> pygame.Rect:
    """Returns the clickable rect for the player board zone."""
    return pygame.Rect(60, PLAYER_BOARD_Y, SCREEN_WIDTH - 140, BOARD_ZONE_HEIGHT)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Card Game")
    clock = pygame.time.Clock()

    game_state = GameState(player_deck=build_test_deck())
    selected_card = None
    hand_card_rects = []
    end_turn_button_rect = pygame.Rect(0, 0, 0, 0)

    combat_event_queue = []
    last_combat_event_time = 0
    is_in_combat = False

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selected_card = None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_position = event.pos

                if end_turn_button_rect.collidepoint(mouse_position):
                    if game_state.is_player_turn() and not is_in_combat:
                        selected_card = None
                        game_state.end_player_turn()
                        game_state.boss.take_turn(game_state.boss_board)
                        game_state.save_board_snapshot()
                        combat_event_queue = build_combat_event_queue(game_state)
                        last_combat_event_time = current_time
                        is_in_combat = True

                if not is_in_combat:
                    clicked_hand_card = None
                    for card, card_rect in hand_card_rects:
                        if card_rect.collidepoint(mouse_position):
                            clicked_hand_card = card
                            break

                    if clicked_hand_card is not None:
                        if clicked_hand_card is selected_card:
                            selected_card = None
                        else:
                            selected_card = clicked_hand_card

                    elif selected_card is not None:
                        if get_player_board_zone_rect().collidepoint(mouse_position):
                            success = game_state.play_card_to_board(selected_card)
                            if success:
                                selected_card = None

        # Process one combat event per tick based on delay timer
        if is_in_combat and current_time - last_combat_event_time >= COMBAT_EVENT_DELAY_MILLISECONDS:
            if combat_event_queue:
                combat_event = combat_event_queue.pop(0)

                if combat_event["type"] == "combat_end":
                    game_state.restore_boards_from_snapshot()
                    is_in_combat = False
                    game_state.begin_player_turn()

                last_combat_event_time = current_time

        screen.fill(BACKGROUND_COLOUR)
        draw_board_zones(screen)
        draw_boss_board(screen, game_state.boss_board)
        draw_player_board(screen, game_state.player_board)
        hand_card_rects = draw_hand(screen, game_state.player_hand, selected_card, game_state.current_mana)
        draw_mana_bar(screen, game_state.current_mana, game_state.maximum_mana)
        draw_health(screen, game_state.player_health, "Your Health", 20, PLAYER_BOARD_Y - 52, COLOUR_HEALTH_PLAYER)
        draw_health(screen, game_state.boss_health, "Boss Health", 20, BOSS_BOARD_Y + BOARD_ZONE_HEIGHT + 8,
                    COLOUR_HEALTH_BOSS)
        end_turn_button_rect = draw_end_turn_button(screen, game_state.is_player_turn() and not is_in_combat)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

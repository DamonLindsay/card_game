import pygame
from card import Unit
from deck import Deck
from hand import Hand
from game_state import GameState
from combat import build_combat_event_queue
from settings import Settings
from menu import draw_main_menu, draw_settings_menu

# --- Settings ---
game_settings = Settings()
SCREEN_WIDTH = game_settings.screen_width
SCREEN_HEIGHT = game_settings.screen_height
FPS = 60
BACKGROUND_COLOUR = (30, 30, 40)
COMBAT_EVENT_DELAY_MILLISECONDS = 800
COMBAT_SLIDE_DURATION_MILLISECONDS = 500
DAMAGE_POPUP_DURATION_MILLISECONDS = 1500
TOKEN_DAMAGE_POPUP_DURATION_MILLISECONDS = 800
DRAG_THRESHOLD = 8  # pixels mouse must move before drag begins

# --- Card Dimensions ---
CARD_WIDTH = 140
CARD_HEIGHT = 200
CARD_SPACING = 20
CARD_ZOOM_SCALE = 1.6
CARD_ZOOM_WIDTH = int(CARD_WIDTH * CARD_ZOOM_SCALE)
CARD_ZOOM_HEIGHT = int(CARD_HEIGHT * CARD_ZOOM_SCALE)

# --- Board Layout ---
BOARD_CENTRE_Y = SCREEN_HEIGHT // 2
BOSS_BOARD_Y = BOARD_CENTRE_Y - 195
PLAYER_BOARD_Y = BOARD_CENTRE_Y + 15
BOARD_ZONE_HEIGHT = 175
BOSS_PORTRAIT_Y = 120
PLAYER_PORTRAIT_Y = BOARD_CENTRE_Y + 210
HAND_Y_POSITION = SCREEN_HEIGHT - CARD_HEIGHT + 60
HAND_Y_POSITION_HOVERED = SCREEN_HEIGHT - CARD_HEIGHT - 10
hand_y = PLAYER_BOARD_Y - CARD_HEIGHT - 20

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


def draw_unit_card(surface: pygame.Surface, unit: Unit, x: int, y: int,
                   is_selected: bool = False, is_affordable: bool = True,
                   display_health: int = None):
    """Draws a unit card at the given position."""
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

    # Health (bottom right) - use display_health if provided
    shown_health = display_health if display_health is not None else unit.health
    draw_stat_circle(surface, shown_health, x + CARD_WIDTH - 14, y + CARD_HEIGHT - 14,
                     (160, 30, 30), COLOUR_STAT_HEALTH, font_stats_text)


def draw_unit_card_zoomed(surface: pygame.Surface, unit: Unit, x: int, y: int):
    """Draws an enlarged version of a unit card for hover zoom effect."""
    width = CARD_ZOOM_WIDTH
    height = CARD_ZOOM_HEIGHT
    scale = CARD_ZOOM_SCALE

    background_colour = (60, 60, 80)
    border_colour = (220, 220, 240)
    border_width = 3

    pygame.draw.rect(surface, background_colour, (x, y, width, height), border_radius=10)
    pygame.draw.rect(surface, border_colour, (x, y, width, height), width=border_width, border_radius=10)

    font_name_text = pygame.font.SysFont(None, int(19 * scale))
    font_stats_text = pygame.font.SysFont(None, int(24 * scale))

    # Art placeholder
    art_padding = int(8 * scale)
    art_height = int(90 * scale)
    pygame.draw.rect(surface, (100, 100, 120),
                     (x + art_padding, y + int(24 * scale),
                      width - art_padding * 2, art_height))

    # Name banner
    name_banner_y = y + int(24 * scale) + art_height + int(4 * scale)
    pygame.draw.rect(surface, (40, 40, 60),
                     (x + int(4 * scale), name_banner_y,
                      width - int(8 * scale), int(22 * scale)))

    name_surface = font_name_text.render(unit.name, True, COLOUR_TEXT_DEFAULT)
    name_x = x + (width - name_surface.get_width()) // 2
    surface.blit(name_surface, (name_x, name_banner_y + int(3 * scale)))

    # Mana cost (top left)
    mana_circle_x = x + int(14 * scale)
    mana_circle_y = y + int(14 * scale)
    mana_radius = int(12 * scale)
    pygame.draw.circle(surface, COLOUR_MANA_FILL, (mana_circle_x, mana_circle_y), mana_radius)
    pygame.draw.circle(surface, COLOUR_STAT_MANA, (mana_circle_x, mana_circle_y), mana_radius, width=2)
    mana_surface = font_stats_text.render(str(unit.mana_cost), True, COLOUR_TEXT_DEFAULT)
    surface.blit(mana_surface, (mana_circle_x - mana_surface.get_width() // 2,
                                mana_circle_y - mana_surface.get_height() // 2))

    # Attack (bottom left)
    attack_circle_x = x + int(14 * scale)
    attack_circle_y = y + height - int(14 * scale)
    attack_radius = int(12 * scale)
    pygame.draw.circle(surface, (180, 140, 20), (attack_circle_x, attack_circle_y), attack_radius)
    pygame.draw.circle(surface, COLOUR_STAT_ATTACK, (attack_circle_x, attack_circle_y), attack_radius, width=2)
    attack_surface = font_stats_text.render(str(unit.attack), True, COLOUR_TEXT_DEFAULT)
    surface.blit(attack_surface, (attack_circle_x - attack_surface.get_width() // 2,
                                  attack_circle_y - attack_surface.get_height() // 2))

    # Health (bottom right)
    health_circle_x = x + width - int(14 * scale)
    health_circle_y = y + height - int(14 * scale)
    health_radius = int(12 * scale)
    pygame.draw.circle(surface, (160, 30, 30), (health_circle_x, health_circle_y), health_radius)
    pygame.draw.circle(surface, COLOUR_STAT_HEALTH, (health_circle_x, health_circle_y), health_radius, width=2)
    health_surface = font_stats_text.render(str(unit.health), True, COLOUR_TEXT_DEFAULT)
    surface.blit(health_surface, (health_circle_x - health_surface.get_width() // 2,
                                  health_circle_y - health_surface.get_height() // 2))


def draw_stat_circle(surface: pygame.Surface, value: int, center_x: int, center_y: int, fill_colour: tuple,
                     border_colour: tuple, font: pygame.font.Font):
    """Draws a filled circle with a number inside, used for card stats."""
    pygame.draw.circle(surface, fill_colour, (center_x, center_y), 12)
    pygame.draw.circle(surface, border_colour, (center_x, center_y), 12, width=2)
    value_surface = font.render(str(value), True, COLOUR_TEXT_DEFAULT)
    value_x = center_x - value_surface.get_width() // 2
    value_y = center_y - value_surface.get_height() // 2
    surface.blit(value_surface, (value_x, value_y))


def draw_player_board(surface: pygame.Surface, board: list,
                      animation_states: list = None,
                      drag_insert_index: int = -1,
                      dragged_card=None) -> list[tuple]:
    """Draws all units on the player board, with optional gap for drag indicator."""
    token_width = 120
    token_height = 140
    token_spacing = 16

    display_board = [u for u in board if u is not dragged_card]
    display_length = len(display_board) + (1 if drag_insert_index >= 0 else 0)
    total_board_width = display_length * token_width + (display_length - 1) * token_spacing
    start_x = (SCREEN_WIDTH - total_board_width) // 2
    card_rects = []

    draw_index = 0
    board_index = 0

    for position in range(display_length):
        if position == drag_insert_index:
            draw_board_drop_indicator(surface, draw_index, display_length - 1, PLAYER_BOARD_Y)
            draw_index += 1
            continue

        if board_index >= len(display_board):
            break

        unit = display_board[board_index]
        state = None
        if animation_states:
            state = next((s for s in animation_states if s.unit is unit), None)

        card_x = start_x + draw_index * (token_width + token_spacing)
        card_y = PLAYER_BOARD_Y + (BOARD_ZONE_HEIGHT - token_height) // 2
        if state:
            card_x = state.current_x
            card_y = state.current_y

        display_health = state.display_health if state else None
        draw_unit_token(surface, unit, card_x, card_y, display_health=display_health)
        card_rects.append((unit, pygame.Rect(card_x, card_y, token_width, token_height)))

        draw_index += 1
        board_index += 1

    return card_rects


def draw_boss_board(surface: pygame.Surface, board: list,
                    animation_states: list = None) -> list[tuple]:
    """Draws all units on the boss board as Battlegrounds-style tokens."""
    token_width = 120
    token_height = 140
    token_spacing = 16
    total_board_width = len(board) * token_width + (len(board) - 1) * token_spacing
    start_x = (SCREEN_WIDTH - total_board_width) // 2
    card_rects = []

    for index, unit in enumerate(board):
        state = None
        if animation_states:
            state = next((s for s in animation_states if s.unit is unit), None)

        card_x = state.current_x if state else start_x + index * (token_width + token_spacing)
        card_y = state.current_y if state else BOSS_BOARD_Y + (BOARD_ZONE_HEIGHT - token_height) // 2
        display_health = state.display_health if state else None

        draw_unit_token(surface, unit, card_x, card_y, display_health=display_health)
        card_rects.append((unit, pygame.Rect(card_x, card_y, token_width, token_height)))

    return card_rects


def draw_teardrop(surface: pygame.Surface, centre_x: int, centre_y: int,
                  radius: int, colour: tuple, border_colour: tuple):
    """Draws a single teardrop shape — circle on top with a point at the bottom."""
    pygame.draw.circle(surface, colour, (centre_x, centre_y), radius)
    pygame.draw.circle(surface, border_colour, (centre_x, centre_y), radius, width=2)
    point_x = centre_x
    point_y = centre_y + radius + radius // 2
    triangle_points = [
        (centre_x - radius, centre_y),
        (centre_x + radius, centre_y),
        (point_x, point_y),
    ]
    pygame.draw.polygon(surface, colour, triangle_points)
    # Border lines for the point
    pygame.draw.line(surface, border_colour, (centre_x - radius, centre_y), (point_x, point_y), 2)
    pygame.draw.line(surface, border_colour, (centre_x + radius, centre_y), (point_x, point_y), 2)


def draw_player_mana_bar(surface: pygame.Surface, current_mana: int, maximum_mana: int):
    """Draws the player mana bar to the right of the player portrait, wrapping at 5 gems."""
    font = pygame.font.SysFont(None, 24)
    gem_radius = 12
    gem_spacing = 6
    gems_per_column = 5

    bar_x_start = SCREEN_WIDTH // 2 + 100
    bar_y_start = PLAYER_PORTRAIT_Y + 10

    for index in range(maximum_mana):
        column = index // gems_per_column
        row = index % gems_per_column
        gem_x = bar_x_start + column * (gem_radius * 2 + gem_spacing + 4)
        gem_y = bar_y_start + row * (gem_radius * 2 + gem_spacing)
        is_filled = index < current_mana
        fill_colour = (30, 80, 200) if is_filled else (20, 20, 50)
        border_colour = (100, 150, 255) if is_filled else (40, 40, 80)
        draw_teardrop(surface, gem_x, gem_y, gem_radius, fill_colour, border_colour)

    mana_label = font.render(f"{current_mana}/{maximum_mana}", True, (150, 180, 255))
    surface.blit(mana_label, (bar_x_start, bar_y_start + gems_per_column * (gem_radius * 2 + gem_spacing) + 4))


def draw_boss_mana_bar(surface: pygame.Surface, current_mana: int, maximum_mana: int):
    """Draws the boss mana bar to the right of the boss portrait, wrapping at 5 gems."""
    font = pygame.font.SysFont(None, 24)
    gem_radius = 12
    gem_spacing = 6
    gems_per_column = 5

    bar_x_start = SCREEN_WIDTH // 2 + 80
    bar_y_start = BOSS_PORTRAIT_Y + 10

    for index in range(maximum_mana):
        column = index // gems_per_column
        row = index % gems_per_column
        gem_x = bar_x_start + column * (gem_radius * 2 + gem_spacing + 4)
        gem_y = bar_y_start + row * (gem_radius * 2 + gem_spacing)
        is_filled = index < current_mana
        fill_colour = (180, 30, 30) if is_filled else (50, 20, 20)
        border_colour = (255, 100, 100) if is_filled else (80, 40, 40)
        draw_teardrop(surface, gem_x, gem_y, gem_radius, fill_colour, border_colour)

    mana_label = font.render(f"{current_mana}/{maximum_mana}", True, (255, 150, 150))
    surface.blit(mana_label, (bar_x_start, bar_y_start + gems_per_column * (gem_radius * 2 + gem_spacing) + 4))


def draw_menu_button(surface: pygame.Surface, mouse_position: tuple) -> pygame.Rect:
    """Draws a small Menu button in the top left corner of the game screen."""
    button_width = 80
    button_height = 30
    button_x = 10
    button_y = 10
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    is_hovered = button_rect.collidepoint(mouse_position)
    colour = (70, 70, 100) if is_hovered else (50, 50, 70)
    pygame.draw.rect(surface, colour, button_rect, border_radius=6)
    pygame.draw.rect(surface, (100, 100, 140), button_rect, width=1, border_radius=6)
    font = pygame.font.SysFont(None, 22)
    label_surface = font.render("Menu", True, (255, 255, 255))
    label_x = button_x + (button_width - label_surface.get_width()) // 2
    label_y = button_y + (button_height - label_surface.get_height()) // 2
    surface.blit(label_surface, (label_x, label_y))
    return button_rect


def draw_game_board_background(surface: pygame.Surface, is_planning: bool = True):
    """Draws the full game board background. Top zone shows shop label during planning."""
    surface.fill((25, 22, 35))

    pygame.draw.line(surface, (60, 55, 80),
                     (200, SCREEN_HEIGHT // 2),
                     (SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2), 2)

    boss_zone_rect = pygame.Rect(220, BOSS_BOARD_Y, SCREEN_WIDTH - 440, BOARD_ZONE_HEIGHT)
    player_zone_rect = pygame.Rect(220, PLAYER_BOARD_Y, SCREEN_WIDTH - 440, BOARD_ZONE_HEIGHT)

    # Top zone is warmer during planning (shop), cooler during combat (boss board)
    boss_fill = (30, 35, 50) if is_planning else (45, 30, 30)
    boss_border = (55, 65, 90) if is_planning else (90, 55, 55)
    pygame.draw.rect(surface, boss_fill, boss_zone_rect, border_radius=12)
    pygame.draw.rect(surface, boss_border, boss_zone_rect, width=1, border_radius=12)

    pygame.draw.rect(surface, (30, 35, 50), player_zone_rect, border_radius=12)
    pygame.draw.rect(surface, (55, 65, 90), player_zone_rect, width=1, border_radius=12)

    font = pygame.font.SysFont(None, 20)
    top_label = font.render("Tavern", True, (100, 120, 160)) if is_planning else font.render("Boss Board", True,
                                                                                             (100, 70, 70))
    player_label = font.render("Your Board", True, (70, 80, 110))
    surface.blit(top_label, (230, BOSS_BOARD_Y + 8))
    surface.blit(player_label, (230, PLAYER_BOARD_Y + 8))


def draw_boss_hand(surface: pygame.Surface, hand_size: int):
    """Draws face-down cards for the boss hand so the player can see how many cards they hold."""
    if hand_size == 0:
        return

    face_down_width = CARD_WIDTH
    face_down_height = CARD_HEIGHT
    face_down_spacing = CARD_SPACING
    total_width = hand_size * face_down_width + (hand_size - 1) * face_down_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2

    # Mirror the hand — sits above the boss portrait, peeking down from the top
    card_y = -(CARD_HEIGHT - 60)

    for index in range(hand_size):
        card_x = start_x + index * (face_down_width + face_down_spacing)

        card_rect = pygame.Rect(card_x, card_y, face_down_width, face_down_height)
        pygame.draw.rect(surface, (35, 30, 55), card_rect, border_radius=8)
        pygame.draw.rect(surface, (70, 55, 110), card_rect, width=2, border_radius=8)

        inner_rect = pygame.Rect(card_x + 6, card_y + 6,
                                 face_down_width - 12, face_down_height - 12)
        pygame.draw.rect(surface, (55, 45, 85), inner_rect, width=1, border_radius=6)

        # Diamond pattern in centre
        centre_x = card_x + face_down_width // 2
        centre_y = card_y + face_down_height // 2
        diamond_size = 14
        diamond_points = [
            (centre_x, centre_y - diamond_size),
            (centre_x + diamond_size, centre_y),
            (centre_x, centre_y + diamond_size),
            (centre_x - diamond_size, centre_y),
        ]
        pygame.draw.polygon(surface, (80, 60, 130), diamond_points)
        pygame.draw.polygon(surface, (110, 85, 170), diamond_points, width=2)


def build_test_deck() -> Deck:
    """Creates a test card pool for development purposes."""
    test_cards = [
        Unit(name="Angry Ooze", attack=2, health=3, mana_cost=2, tribes=["Ooze"]),
        Unit(name="Angry Ooze", attack=2, health=3, mana_cost=2, tribes=["Ooze"]),
        Unit(name="Stone Golem", attack=4, health=6, mana_cost=5),
        Unit(name="Stone Golem", attack=4, health=6, mana_cost=5),
        Unit(name="Swift Fox", attack=3, health=2, mana_cost=2, tribes=["Beast"]),
        Unit(name="Swift Fox", attack=3, health=2, mana_cost=2, tribes=["Beast"]),
        Unit(name="Cave Troll", attack=5, health=4, mana_cost=4, tribes=["Troll"]),
        Unit(name="Fire Sprite", attack=2, health=2, mana_cost=1, tribes=["Elemental"]),
        Unit(name="Fire Sprite", attack=2, health=2, mana_cost=1, tribes=["Elemental"]),
        Unit(name="Iron Shield", attack=1, health=7, mana_cost=3),
        Unit(name="Bog Witch", attack=3, health=3, mana_cost=3),
        Unit(name="Bog Witch", attack=3, health=3, mana_cost=3),
        Unit(name="Cave Troll", attack=5, health=4, mana_cost=4, tribes=["Troll"]),
    ]
    deck = Deck(cards=test_cards)
    deck.shuffle()
    return deck


def get_player_board_zone_rect() -> pygame.Rect:
    """Returns the clickable rect for the player board zone."""
    return pygame.Rect(220, PLAYER_BOARD_Y, SCREEN_WIDTH - 440, BOARD_ZONE_HEIGHT)


class DragState:
    def __init__(self):
        self.is_dragging = False
        self.dragged_card = None
        self.drag_source = None  # "hand" or "board"
        self.drag_x = 0
        self.drag_y = 0
        self.origin_index = 0  # index in hand or board before drag started


class UnitAnimationState:
    def __init__(self, unit: Unit, base_x: int, base_y: int):
        self.unit = unit
        self.base_x = base_x
        self.base_y = base_y
        self.current_x = base_x
        self.current_y = base_y
        self.is_animating = False
        self.animation_start_time = 0
        self.animation_direction_x = 0
        self.animation_direction_y = 0
        self.slide_distance = 0
        self.damage_applied = False
        self.display_health = unit.health  # ← shown before collision
        self.pending_display_health = unit.health  # ← shown after collision
        self.hero_hit_target = None  # "boss" or "player" if this is a hero hit
        self.hero_hit_damage = 0  # damage to apply at collision midpoint
        self.damage_popup_amount = 0  # damage to show as popup at collision
        self.damage_popup_triggered = False  # whether popup has been spawned yet


def build_animation_states(board: list, board_y: int) -> list[UnitAnimationState]:
    """Builds a list of UnitAnimationState objects for each unit on a board."""
    token_width = 120
    token_height = 140
    token_spacing = 16
    total_board_width = len(board) * token_width + (len(board) - 1) * token_spacing
    start_x = (SCREEN_WIDTH - total_board_width) // 2
    animation_states = []

    for index, unit in enumerate(board):
        card_x = start_x + index * (token_width + token_spacing)
        card_y = board_y + (BOARD_ZONE_HEIGHT - token_height) // 2
        animation_states.append(UnitAnimationState(unit, card_x, card_y))

    return animation_states


def update_animation_states(animation_states: list[UnitAnimationState],
                            pending_damage_map: dict, current_time: int,
                            game_state=None, damage_popup_queue: list = None,
                            token_damage_popups: list = None):
    """Updates all unit animation positions and reveals damage at collision point."""
    for animation_state in animation_states:
        if not animation_state.is_animating:
            continue

        elapsed = current_time - animation_state.animation_start_time
        progress = min(elapsed / COMBAT_SLIDE_DURATION_MILLISECONDS, 1.0)

        if progress < 0.5:
            slide_amount = progress * 2 * animation_state.slide_distance
        else:
            slide_amount = (1.0 - progress) * 2 * animation_state.slide_distance

        animation_state.current_x = animation_state.base_x + int(
            animation_state.animation_direction_x * slide_amount)
        animation_state.current_y = animation_state.base_y + int(
            animation_state.animation_direction_y * slide_amount)

        if progress >= 0.5 and not animation_state.damage_applied:
            animation_state.display_health = animation_state.pending_display_health
            animation_state.damage_applied = True

            if game_state is not None and animation_state.hero_hit_target is not None:
                game_state.apply_single_unit_damage(
                    animation_state.hero_hit_target, animation_state.hero_hit_damage)
                if damage_popup_queue is not None:
                    damage_popup_queue.append({
                        "target": animation_state.hero_hit_target,
                        "amount": animation_state.hero_hit_damage,
                    })
                animation_state.hero_hit_target = None
                animation_state.hero_hit_damage = 0

            # Spawn token damage popup at current animated position
            if (token_damage_popups is not None and
                    animation_state.damage_popup_amount > 0 and
                    not animation_state.damage_popup_triggered):
                token_damage_popups.append({
                    "animation_state": animation_state,
                    "amount": animation_state.damage_popup_amount,
                    "start_time": current_time,
                    "track": animation_state.slide_distance > 20,  # True for attacker, False for defender
                    "fixed_x": animation_state.current_x + 60,
                    "fixed_y": animation_state.current_y + 70,
                })
                animation_state.damage_popup_triggered = True

        if progress >= 1.0:
            animation_state.current_x = animation_state.base_x
            animation_state.current_y = animation_state.base_y
            animation_state.is_animating = False


def trigger_attack_animation(animation_states: list[UnitAnimationState], attacking_unit: Unit,
                             target_unit: Unit, target_states: list[UnitAnimationState],
                             start_time: int):
    """Triggers a slide animation for the attacker toward the target card position."""
    attacker_state = next((state for state in animation_states if state.unit is attacking_unit), None)
    target_state = next((state for state in target_states if state.unit is target_unit), None)

    if attacker_state is None or target_state is None:
        return

    direction_x = target_state.base_x - attacker_state.base_x
    direction_y = target_state.base_y - attacker_state.base_y
    distance = max(1, (direction_x ** 2 + direction_y ** 2) ** 0.5)

    attacker_state.animation_direction_x = direction_x / distance
    attacker_state.animation_direction_y = direction_y / distance
    attacker_state.slide_distance = distance  # travel the full distance to the target
    attacker_state.is_animating = True
    attacker_state.animation_start_time = start_time


def trigger_defender_animation(animation_states: list, defending_unit: Unit, start_time: int):
    """Triggers a small recoil animation on the defending unit when hit."""
    defender_state = next((state for state in animation_states if state.unit is defending_unit), None)
    if defender_state is None:
        return
    defender_state.animation_direction_x = 0
    defender_state.animation_direction_y = 0.15
    defender_state.slide_distance = 8
    defender_state.is_animating = True
    defender_state.animation_start_time = start_time


def apply_new_resolution(new_width: int, new_height: int, screen: pygame.Surface):
    """Recalculates all layout constants and resizes the window when resolution changes."""
    global SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_CENTRE_Y, BOSS_BOARD_Y, PLAYER_BOARD_Y
    global BOARD_ZONE_HEIGHT, BOSS_PORTRAIT_Y, PLAYER_PORTRAIT_Y
    global HAND_Y_POSITION, HAND_Y_POSITION_HOVERED

    SCREEN_WIDTH = new_width
    SCREEN_HEIGHT = new_height
    BOARD_CENTRE_Y = SCREEN_HEIGHT // 2
    BOSS_BOARD_Y = BOARD_CENTRE_Y - 195
    PLAYER_BOARD_Y = BOARD_CENTRE_Y + 15
    BOARD_ZONE_HEIGHT = 175
    BOSS_PORTRAIT_Y = 120
    PLAYER_PORTRAIT_Y = BOARD_CENTRE_Y + 210
    HAND_Y_POSITION = SCREEN_HEIGHT - CARD_HEIGHT + 60
    HAND_Y_POSITION_HOVERED = SCREEN_HEIGHT - CARD_HEIGHT - 10

    new_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    return new_screen


def draw_end_turn_button(surface: pygame.Surface, is_player_turn: bool,
                         mouse_position: tuple = (0, 0)) -> pygame.Rect:
    """Draws the Start Combat button with hover and active states."""
    button_width = 160
    button_height = 56
    button_x = SCREEN_WIDTH - button_width - 20
    button_y = SCREEN_HEIGHT // 2 - button_height // 2

    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    is_hovered = button_rect.collidepoint(mouse_position) and is_player_turn

    if not is_player_turn:
        background_colour = (40, 40, 50)
        border_colour = (70, 70, 80)
        text_colour = (80, 80, 90)
        label = "In Combat..."
    elif is_hovered:
        background_colour = (80, 180, 80)
        border_colour = (140, 255, 140)
        text_colour = (255, 255, 255)
        label = "Start Combat"
    else:
        background_colour = (50, 140, 50)
        border_colour = (80, 200, 80)
        text_colour = (220, 255, 220)
        label = "Start Combat"

    # Button shadow
    shadow_rect = pygame.Rect(button_x + 3, button_y + 3, button_width, button_height)
    pygame.draw.rect(surface, (15, 15, 20), shadow_rect, border_radius=10)

    # Button body
    pygame.draw.rect(surface, background_colour, button_rect, border_radius=10)

    # Top highlight for depth
    if is_player_turn:
        highlight_rect = pygame.Rect(button_x + 2, button_y + 2, button_width - 4, button_height // 2)
        highlight_colour = (min(background_colour[0] + 30, 255),
                            min(background_colour[1] + 30, 255),
                            min(background_colour[2] + 30, 255))
        pygame.draw.rect(surface, highlight_colour, highlight_rect,
                         border_top_left_radius=9, border_top_right_radius=9)

    # Border
    pygame.draw.rect(surface, border_colour, button_rect, width=2, border_radius=10)

    # Sword icon to the left of text
    icon_x = button_x + 18
    icon_y = button_y + button_height // 2
    if is_player_turn:
        pygame.draw.line(surface, text_colour, (icon_x - 6, icon_y - 8),
                         (icon_x + 6, icon_y + 8), 2)
        pygame.draw.line(surface, text_colour, (icon_x - 4, icon_y - 6),
                         (icon_x - 8, icon_y - 2), 2)

    font = pygame.font.SysFont(None, 26)
    label_surface = font.render(label, True, text_colour)
    label_x = button_x + (button_width - label_surface.get_width()) // 2 + 8
    label_y = button_y + (button_height - label_surface.get_height()) // 2
    surface.blit(label_surface, (label_x, label_y))

    return button_rect


def draw_unit_token(surface: pygame.Surface, unit: Unit, x: int, y: int,
                    display_health: int = None, border_colour_override: tuple = None):
    """Draws a Battlegrounds-style oval unit token for the board.
    Shows art, attack, health, and a taunt shield behind the token if applicable."""
    token_width = 120
    token_height = 140

    # Draw taunt shield shape behind the token
    if unit.has_taunt:
        shield_colour_fill = (50, 55, 75)
        shield_colour_border = (150, 155, 190)

        cx = x + token_width // 2
        left = x - 24
        left = x - 24
        left = x - 24
        right = x + token_width + 24
        top = y - 20
        bottom = y + token_height + 30

        # Trace the shield outline with many points to simulate curves
        shield_points = []

        # Top left curve (convex outward)
        for i in range(11):
            t = i / 10
            px = left + (cx - left) * t
            py = top + 18 * (t * (1 - t)) * (-3)
            shield_points.append((px, py))

        # Top centre dip (concave inward)
        for i in range(11):
            t = i / 10
            px = cx + (right - cx) * t
            py = top + 18 * (t * (1 - t)) * (-3)
            shield_points.append((px, py))

        # Right side curve
        for i in range(11):
            t = i / 10
            px = right - 6 * (1 - (2 * t - 1) ** 2)
            py = top + (bottom - top) * 0.55 * t
            shield_points.append((px, py))

        # Bottom right to point
        for i in range(11):
            t = i / 10
            px = right - (right - cx) * t
            py = top + (bottom - top) * 0.55 + (bottom - (top + (bottom - top) * 0.55)) * t
            shield_points.append((px, py))

        # Bottom point to left
        for i in range(11):
            t = i / 10
            px = cx - (cx - left) * t
            py = bottom - (bottom - (top + (bottom - top) * 0.55)) * t
            shield_points.append((px, py))

        # Left side curve
        for i in range(11):
            t = i / 10
            px = left + 6 * (1 - (2 * t - 1) ** 2)
            py = top + (bottom - top) * 0.55 * (1 - t)
            shield_points.append((px, py))

        pygame.draw.polygon(surface, shield_colour_fill, shield_points)
        pygame.draw.polygon(surface, shield_colour_border, shield_points, width=3)

        # Inner inset border line
        inset = 6
        cx2 = cx
        left2 = left + inset
        right2 = right - inset
        top2 = top + inset
        bottom2 = bottom - inset

        inner_points = []
        for i in range(11):
            t = i / 10
            px = left2 + (cx2 - left2) * t
            py = top2 + 14 * (t * (1 - t)) * (-3)
            inner_points.append((px, py))
        for i in range(11):
            t = i / 10
            px = cx2 + (right2 - cx2) * t
            py = top2 + 14 * (t * (1 - t)) * (-3)
            inner_points.append((px, py))
        for i in range(11):
            t = i / 10
            px = right2 - 4 * (1 - (2 * t - 1) ** 2)
            py = top2 + (bottom2 - top2) * 0.55 * t
            inner_points.append((px, py))
        for i in range(11):
            t = i / 10
            px = right2 - (right2 - cx2) * t
            py = top2 + (bottom2 - top2) * 0.55 + (bottom2 - (top2 + (bottom2 - top2) * 0.55)) * t
            inner_points.append((px, py))
        for i in range(11):
            t = i / 10
            px = cx2 - (cx2 - left2) * t
            py = bottom2 - (bottom2 - (top2 + (bottom2 - top2) * 0.55)) * t
            inner_points.append((px, py))
        for i in range(11):
            t = i / 10
            px = left2 + 4 * (1 - (2 * t - 1) ** 2)
            py = top2 + (bottom2 - top2) * 0.55 * (1 - t)
            inner_points.append((px, py))

        pygame.draw.polygon(surface, shield_colour_border, inner_points, width=2)

    # Token background oval
    token_rect = pygame.Rect(x, y, token_width, token_height)
    pygame.draw.ellipse(surface, (100, 90, 110), token_rect)

    # Art placeholder — slightly inset oval
    art_rect = pygame.Rect(x + 6, y + 6, token_width - 12, token_height - 12)
    pygame.draw.ellipse(surface, (100, 100, 120), art_rect)

    # Token border
    # Token border
    if border_colour_override is not None:
        border_colour = border_colour_override
    else:
        border_colour = (200, 180, 120) if unit.has_taunt else (160, 140, 100)
    pygame.draw.ellipse(surface, border_colour, token_rect, width=3)

    font_stats = pygame.font.SysFont(None, 30)

    # Attack circle (bottom left)
    attack_circle_x = x + 14
    attack_circle_y = y + token_height - 10
    attack_colour = COLOUR_TEXT_DEFAULT
    if unit.attack < unit.base_attack:
        attack_colour = (220, 80, 80)
    elif unit.attack > unit.base_attack:
        attack_colour = (80, 220, 80)
    pygame.draw.circle(surface, (180, 140, 20), (attack_circle_x, attack_circle_y), 16)
    pygame.draw.circle(surface, (255, 200, 50), (attack_circle_x, attack_circle_y), 16, width=2)
    attack_surface = font_stats.render(str(unit.attack), True, attack_colour)
    surface.blit(attack_surface, (attack_circle_x - attack_surface.get_width() // 2,
                                  attack_circle_y - attack_surface.get_height() // 2))

    # Health circle (bottom right)
    shown_health = display_health if display_health is not None else unit.health
    health_circle_x = x + token_width - 14
    health_circle_y = y + token_height - 10
    health_colour_text = COLOUR_TEXT_DEFAULT
    if shown_health < unit.max_health:
        health_colour_text = (220, 80, 80)
    elif shown_health > unit.max_health:
        health_colour_text = (80, 220, 80)
    health_colour_fill = (160, 30, 30) if shown_health > 0 else (80, 80, 80)
    pygame.draw.circle(surface, health_colour_fill, (health_circle_x, health_circle_y), 16)
    pygame.draw.circle(surface, (220, 80, 80), (health_circle_x, health_circle_y), 16, width=2)
    health_surface = font_stats.render(str(shown_health), True, health_colour_text)
    surface.blit(health_surface, (health_circle_x - health_surface.get_width() // 2,
                                  health_circle_y - health_surface.get_height() // 2))

    # Mana cost (top left)
    font_mana = pygame.font.SysFont(None, 22)
    mana_circle_x = x + 14
    mana_circle_y = y + 14
    pygame.draw.circle(surface, (30, 80, 200), (mana_circle_x, mana_circle_y), 10)
    pygame.draw.circle(surface, (100, 150, 255), (mana_circle_x, mana_circle_y), 10, width=2)
    mana_surface = font_mana.render(str(unit.mana_cost), True, COLOUR_TEXT_DEFAULT)
    surface.blit(mana_surface, (mana_circle_x - mana_surface.get_width() // 2,
                                mana_circle_y - mana_surface.get_height() // 2))


def draw_hero_portrait(surface: pygame.Surface, name: str, health: int,
                       centre_x: int, top_y: int, is_player: bool = True):
    """Draws an arched hero portrait frame with name and health."""
    portrait_width = 110
    portrait_height = 130
    portrait_x = centre_x - portrait_width // 2

    border_colour = (180, 150, 80) if is_player else (180, 80, 80)
    background_colour = (40, 35, 50)
    health_colour = (60, 200, 60) if is_player else (220, 60, 60)

    # Portrait background — rounded rect with more curve at top for arch effect
    portrait_rect = pygame.Rect(portrait_x, top_y, portrait_width, portrait_height)
    pygame.draw.rect(surface, background_colour, portrait_rect,
                     border_top_left_radius=portrait_width // 3,
                     border_top_right_radius=portrait_width // 3,
                     border_bottom_left_radius=8,
                     border_bottom_right_radius=8)

    # Art placeholder
    art_rect = pygame.Rect(portrait_x + 6, top_y + 6, portrait_width - 12, portrait_height - 12)
    pygame.draw.rect(surface, (70, 65, 85), art_rect,
                     border_top_left_radius=portrait_width // 2,
                     border_top_right_radius=portrait_width // 2,
                     border_bottom_left_radius=4,
                     border_bottom_right_radius=4)

    # Portrait border
    pygame.draw.rect(surface, border_colour, portrait_rect, width=3,
                     border_top_left_radius=portrait_width // 2,
                     border_top_right_radius=portrait_width // 2,
                     border_bottom_left_radius=8,
                     border_bottom_right_radius=8)

    # Name label above portrait
    font_name = pygame.font.SysFont(None, 22)
    name_surface = font_name.render(name, True, (200, 200, 200))
    name_x = centre_x - name_surface.get_width() // 2
    surface.blit(name_surface, (name_x, top_y - 18))

    # Health circle below portrait
    health_circle_y = top_y + portrait_height + 20
    pygame.draw.circle(surface, (30, 30, 45), (centre_x, health_circle_y), 22)
    pygame.draw.circle(surface, health_colour, (centre_x, health_circle_y), 22, width=3)
    font_health = pygame.font.SysFont(None, 36)
    health_surface = font_health.render(str(health), True, health_colour)
    surface.blit(health_surface, (centre_x - health_surface.get_width() // 2,
                                  health_circle_y - health_surface.get_height() // 2))


def draw_damage_popup(surface: pygame.Surface, popup: dict, current_time: int):
    """Draws a floating damage number after combat resolves."""
    if popup is None:
        return

    elapsed = current_time - popup["start_time"]
    if elapsed > DAMAGE_POPUP_DURATION_MILLISECONDS:
        return

    # Fade out over the last 500ms
    alpha = 255
    if elapsed > DAMAGE_POPUP_DURATION_MILLISECONDS - 500:
        alpha = int(255 * (DAMAGE_POPUP_DURATION_MILLISECONDS - elapsed) / 500)

    # Float upward over time
    float_offset = int(elapsed / 4)

    if popup["target"] == "boss":
        base_x = SCREEN_WIDTH // 2
        base_y = BOSS_PORTRAIT_Y + 80
        colour = (255, 100, 100)
    else:
        base_x = SCREEN_WIDTH // 2
        base_y = PLAYER_PORTRAIT_Y + 80
        colour = (255, 100, 100)

    font = pygame.font.SysFont(None, 64)
    text = f"-{popup['amount']}"
    text_surface = font.render(text, True, colour)
    text_surface.set_alpha(alpha)
    surface.blit(text_surface, (base_x - text_surface.get_width() // 2,
                                base_y - float_offset))


def trigger_hero_hit_animation(animation_states: list, attacking_unit: Unit,
                               target: str, start_time: int, damage: int):
    """Triggers a slide animation for a unit attacking the hero portrait directly."""
    attacker_state = next((s for s in animation_states if s.unit is attacking_unit), None)
    if attacker_state is None:
        return

    if target == "boss":
        target_x = SCREEN_WIDTH // 2
        target_y = BOSS_PORTRAIT_Y + 60
    else:
        target_x = SCREEN_WIDTH // 2
        target_y = PLAYER_PORTRAIT_Y + 60

    direction_x = target_x - attacker_state.base_x
    direction_y = target_y - attacker_state.base_y
    distance = max(1, (direction_x ** 2 + direction_y ** 2) ** 0.5)

    attacker_state.animation_direction_x = direction_x / distance
    attacker_state.animation_direction_y = direction_y / distance
    attacker_state.slide_distance = distance * 0.6
    attacker_state.is_animating = True
    attacker_state.animation_start_time = start_time
    attacker_state.damage_applied = False
    attacker_state.pending_display_health = attacking_unit.health
    attacker_state.hero_hit_target = target
    attacker_state.hero_hit_damage = damage


def draw_token_damage_popup(surface: pygame.Surface, popup: dict, current_time: int):
    """Draws a damage number that follows the attacker or stays fixed for the defender."""
    elapsed = current_time - popup["start_time"]
    if elapsed < 0 or elapsed > TOKEN_DAMAGE_POPUP_DURATION_MILLISECONDS:
        return

    alpha = int(255 * (1 - elapsed / TOKEN_DAMAGE_POPUP_DURATION_MILLISECONDS))

    if popup["track"]:
        animation_state = popup["animation_state"]
        draw_x = animation_state.current_x + 60
        draw_y = animation_state.current_y + 70
    else:
        draw_x = popup["fixed_x"]
        draw_y = popup["fixed_y"]

    font = pygame.font.SysFont(None, 42)
    text = f"-{popup['amount']}"
    text_surface = font.render(text, True, (255, 80, 80))
    text_surface.set_alpha(alpha)
    surface.blit(text_surface, (
        draw_x - text_surface.get_width() // 2,
        draw_y - text_surface.get_height() // 2
    ))


def get_board_insert_index(mouse_x: int, board_length: int) -> int:
    """Returns the index at which a card would be inserted based on mouse x position."""
    token_width = 120
    token_spacing = 16
    total_width = board_length * token_width + (board_length - 1) * token_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2

    for index in range(board_length):
        slot_centre_x = start_x + index * (token_width + token_spacing) + token_width // 2
        if mouse_x < slot_centre_x:
            return index
    return board_length


def draw_board_drop_indicator(surface: pygame.Surface, insert_index: int,
                              board_length: int, board_y: int):
    """Draws a glowing slot indicator and gap on the board at the insert position."""
    token_width = 120
    token_height = 140
    token_spacing = 16
    gap_width = token_width + token_spacing

    # Calculate positions with gap inserted
    display_length = board_length + 1
    total_width = display_length * token_width + (display_length - 1) * token_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2

    slot_x = start_x + insert_index * (token_width + token_spacing)
    slot_y = board_y + (BOARD_ZONE_HEIGHT - token_height) // 2

    # Glowing placeholder slot
    slot_rect = pygame.Rect(slot_x, slot_y, token_width, token_height)
    pygame.draw.ellipse(surface, (40, 60, 80), slot_rect)
    pygame.draw.ellipse(surface, (80, 140, 200), slot_rect, width=2)

    # Pulsing inner glow
    inner_rect = pygame.Rect(slot_x + 8, slot_y + 8, token_width - 16, token_height - 16)
    pygame.draw.ellipse(surface, (60, 100, 160), inner_rect, width=1)


def draw_tavern(surface: pygame.Surface, tavern_cards: list,
                current_mana: int, mouse_position: tuple,
                dragged_card=None) -> tuple[list, pygame.Rect, tuple | None]:
    """Draws the tavern shop inside the boss board zone during planning phase.
    Returns card rects, refresh button rect, and hovered zoom info."""
    if not tavern_cards:
        return [], pygame.Rect(0, 0, 0, 0), None

    token_width = 120
    token_height = 140
    token_spacing = 16
    total_width = len(tavern_cards) * token_width + (len(tavern_cards) - 1) * token_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2 - 60
    token_y = BOSS_BOARD_Y + (BOARD_ZONE_HEIGHT - token_height) // 2
    card_rects = []
    hovered_zoom_info = None

    for index, card in enumerate(tavern_cards):
        card_x = start_x + index * (token_width + token_spacing)
        can_afford = current_mana >= card.mana_cost
        token_rect = pygame.Rect(card_x, token_y, token_width, token_height)
        is_hovered = token_rect.collidepoint(mouse_position)

        if isinstance(card, Unit):
            # Draw glow FIRST so it appears behind the token
            if can_afford:
                for glow_size in range(8, 0, -2):
                    glow_alpha = int(60 * (glow_size / 8))
                    glow_surface = pygame.Surface(
                        (token_width + glow_size * 2, token_height + glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(glow_surface, (80, 180, 255, glow_alpha),
                                        pygame.Rect(0, 0, token_width + glow_size * 2,
                                                    token_height + glow_size * 2))
                    surface.blit(glow_surface, (card_x - glow_size, token_y - glow_size))

            # Draw token ONCE with border override if being dragged
            is_being_dragged = card is dragged_card
            token_border = (80, 220, 80) if is_being_dragged else None
            draw_unit_token(surface, card, card_x, token_y, border_colour_override=token_border)

            # Dim if unaffordable
            if not can_afford:
                dim_surface = pygame.Surface((token_width, token_height), pygame.SRCALPHA)
                pygame.draw.ellipse(dim_surface, (0, 0, 0, 100),
                                    pygame.Rect(0, 0, token_width, token_height))
                surface.blit(dim_surface, (card_x, token_y))

            # Track hover for zoom
            if is_hovered:
                zoom_x = card_x + (token_width - CARD_ZOOM_WIDTH) // 2
                zoom_x = max(10, min(zoom_x, SCREEN_WIDTH - CARD_ZOOM_WIDTH - 10))
                zoom_y = token_y - CARD_ZOOM_HEIGHT - 10
                hovered_zoom_info = (card, zoom_x, zoom_y)

        card_rects.append((card, token_rect))

    # Refresh button
    refresh_button_x = start_x + len(tavern_cards) * (token_width + token_spacing) + 10
    refresh_button_y = BOSS_BOARD_Y + BOARD_ZONE_HEIGHT // 2 - 25
    refresh_rect = pygame.Rect(refresh_button_x, refresh_button_y, 100, 50)
    can_afford_refresh = current_mana >= 1
    is_hovered = refresh_rect.collidepoint(mouse_position)
    refresh_colour = (70, 130, 200) if (is_hovered and can_afford_refresh) else (
        50, 100, 160) if can_afford_refresh else (40, 40, 55)
    pygame.draw.rect(surface, refresh_colour, refresh_rect, border_radius=8)
    pygame.draw.rect(surface, (100, 150, 220), refresh_rect, width=2, border_radius=8)
    font = pygame.font.SysFont(None, 22)
    surface.blit(font.render("Refresh", True, COLOUR_TEXT_DEFAULT),
                 (refresh_button_x + (100 - font.size("Refresh")[0]) // 2, refresh_button_y + 8))
    surface.blit(font.render("(1 mana)", True, (160, 180, 220)),
                 (refresh_button_x + (100 - font.size("(1 mana)")[0]) // 2, refresh_button_y + 26))

    return card_rects, refresh_rect, hovered_zoom_info


def draw_hand(surface: pygame.Surface, hand: Hand, selected_card: Unit,
              current_mana: int, mouse_position: tuple = (0, 0)) -> tuple[list, tuple | None]:
    """Draws all cards in the hand above the tavern. Returns card rects and hovered zoom info."""
    total_hand_width = len(hand.cards) * CARD_WIDTH + (len(hand.cards) - 1) * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_hand_width) // 2
    card_rects = []
    hovered_zoom_info = None

    hand_y = PLAYER_BOARD_Y - CARD_HEIGHT - 20

    for index, card in enumerate(hand.cards):
        card_x = start_x + index * (CARD_WIDTH + CARD_SPACING)

        peek_rect = pygame.Rect(card_x, hand_y, CARD_WIDTH, CARD_HEIGHT)
        is_hovered = peek_rect.collidepoint(mouse_position)
        is_selected = card is selected_card

        is_affordable = current_mana >= card.mana_cost
        if isinstance(card, Unit):
            draw_unit_card(surface, card, card_x, hand_y,
                           is_selected=is_selected, is_affordable=is_affordable)
            if is_hovered and not is_selected:
                dim_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
                dim_surface.fill((0, 0, 0, 160))
                surface.blit(dim_surface, (card_x, hand_y))

        card_rects.append((card, pygame.Rect(card_x, hand_y, CARD_WIDTH, CARD_HEIGHT)))

        if is_hovered and not is_selected and isinstance(card, Unit):
            zoom_x = card_x + (CARD_WIDTH - CARD_ZOOM_WIDTH) // 2
            zoom_x = max(10, min(zoom_x, SCREEN_WIDTH - CARD_ZOOM_WIDTH - 10))
            zoom_y = hand_y - CARD_ZOOM_HEIGHT + CARD_HEIGHT - 20
            hovered_zoom_info = (card, zoom_x, zoom_y)

    return card_rects, hovered_zoom_info


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Card Game")
    clock = pygame.time.Clock()
    drag_state = DragState()

    current_scene = "menu"

    # --- Game state ---
    game_state = None
    selected_card = None
    hand_card_rects = []
    tavern_card_rects = []

    # --- Button rects ---
    end_turn_button_rect = pygame.Rect(0, 0, 0, 0)
    menu_button_rect = pygame.Rect(0, 0, 0, 0)
    refresh_button_rect = pygame.Rect(0, 0, 0, 0)

    # --- Combat state ---
    combat_event_queue = []
    last_combat_event_time = 0
    is_in_combat = False
    pending_damage_map = {}
    player_animation_states = []
    boss_animation_states = []

    # --- Damage popups ---
    round_damage_popup = None
    damage_popup_queue = []
    last_damage_popup_time = 0
    token_damage_popups = []

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_position = pygame.mouse.get_pos()

        # =====================
        # --- Event Handling ---
        # =====================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_scene == "game":
                        selected_card = None
                    elif current_scene == "settings":
                        current_scene = "menu"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # --- Menu ---
                if current_scene == "menu":
                    menu_rects = draw_main_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, mouse_position)
                    if menu_rects["play"].collidepoint(mouse_position):
                        game_state = GameState(player_deck=build_test_deck())
                        selected_card = None
                        hand_card_rects = []
                        combat_event_queue = []
                        is_in_combat = False
                        pending_damage_map = {}
                        player_animation_states = []
                        boss_animation_states = []
                        round_damage_popup = None
                        damage_popup_queue = []
                        current_scene = "game"
                    elif menu_rects["settings"].collidepoint(mouse_position):
                        current_scene = "settings"
                    elif menu_rects["exit"].collidepoint(mouse_position):
                        running = False

                # --- Settings ---
                elif current_scene == "settings":
                    settings_rects = draw_settings_menu(
                        screen, SCREEN_WIDTH, SCREEN_HEIGHT, mouse_position, game_settings)
                    if settings_rects["back"].collidepoint(mouse_position):
                        current_scene = "menu"
                    elif settings_rects["apply"].collidepoint(mouse_position):
                        game_settings.apply_pending_resolution()
                        screen = apply_new_resolution(
                            game_settings.screen_width, game_settings.screen_height, screen)
                    else:
                        for index, resolution_rect in enumerate(settings_rects["resolutions"]):
                            if resolution_rect.collidepoint(mouse_position):
                                game_settings.select_pending_resolution(index)

                # --- Game ---
                elif current_scene == "game" and game_state is not None:

                    if menu_button_rect.collidepoint(mouse_position):
                        current_scene = "menu"
                        selected_card = None
                        is_in_combat = False

                    elif end_turn_button_rect.collidepoint(mouse_position):
                        if game_state.is_player_turn() and not is_in_combat:
                            selected_card = None
                            game_state.end_player_turn()
                            game_state.boss.take_turn(
                                game_state.boss_board, game_state.boss_maximum_mana)
                            game_state.save_board_snapshot()
                            player_animation_states = build_animation_states(
                                game_state.player_board, PLAYER_BOARD_Y)
                            boss_animation_states = build_animation_states(
                                game_state.boss_board, BOSS_BOARD_Y)
                            combat_event_queue = build_combat_event_queue(game_state)
                            last_combat_event_time = current_time
                            is_in_combat = True


                    elif not is_in_combat:
                        # Check for click on tavern card to begin drag-to-buy
                        clicked_tavern_card = None
                        for card, card_rect in tavern_card_rects:
                            if card_rect.collidepoint(mouse_position):
                                clicked_tavern_card = card
                                break

                        if clicked_tavern_card is not None and game_state.can_afford(clicked_tavern_card.mana_cost):
                            drag_state.is_dragging = True
                            drag_state.dragged_card = clicked_tavern_card
                            drag_state.drag_source = "tavern"
                            drag_state.drag_x = mouse_position[0]
                            drag_state.drag_y = mouse_position[1]

                        # Check for click on hand card to begin potential drag
                        clicked_hand_card = None
                        for card, card_rect in hand_card_rects:
                            if card_rect.collidepoint(mouse_position):
                                clicked_hand_card = card
                                break

                        # Check for click on board card
                        clicked_board_card = None
                        for index, unit in enumerate(game_state.player_board):
                            token_width = 120
                            token_height = 140
                            token_spacing = 16
                            total_width = len(game_state.player_board) * token_width + (
                                    len(game_state.player_board) - 1) * token_spacing
                            start_x = (SCREEN_WIDTH - total_width) // 2
                            card_x = start_x + index * (token_width + token_spacing)
                            card_y = PLAYER_BOARD_Y + (BOARD_ZONE_HEIGHT - token_height) // 2
                            if pygame.Rect(card_x, card_y, token_width, token_height).collidepoint(mouse_position):
                                clicked_board_card = (unit, index)
                                break

                        if clicked_board_card is not None:
                            unit, index = clicked_board_card
                            drag_state.is_dragging = True
                            drag_state.dragged_card = unit
                            drag_state.drag_source = "board"
                            drag_state.origin_index = index
                            drag_state.drag_x = mouse_position[0]
                            drag_state.drag_y = mouse_position[1]
                        elif clicked_hand_card is not None:
                            if clicked_hand_card is selected_card:
                                selected_card = None
                            else:
                                drag_state.is_dragging = True
                                drag_state.dragged_card = clicked_hand_card
                                drag_state.drag_source = "hand"
                                drag_state.origin_index = game_state.player_hand.cards.index(clicked_hand_card)
                                drag_state.drag_x = mouse_position[0]
                                drag_state.drag_y = mouse_position[1]
                                selected_card = clicked_hand_card

                        # Check refresh button
                        if refresh_button_rect.collidepoint(mouse_position):
                            game_state.pay_for_refresh()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drag_state.is_dragging and current_scene == "game" and not is_in_combat:
                    board_zone = get_player_board_zone_rect()
                    tavern_zone = pygame.Rect(220, BOSS_BOARD_Y, SCREEN_WIDTH - 440, BOARD_ZONE_HEIGHT)
                    dropped_on_board = board_zone.collidepoint(mouse_position)
                    dropped_on_tavern = tavern_zone.collidepoint(mouse_position)

                    if drag_state.drag_source == "hand":
                        if dropped_on_board:
                            insert_index = get_board_insert_index(
                                mouse_position[0], len(game_state.player_board))
                            insert_index = min(insert_index, game_state.MAXIMUM_BOARD_SIZE - 1)
                            game_state.player_hand.remove_card(drag_state.dragged_card)
                            game_state.player_board.insert(insert_index, drag_state.dragged_card)
                            selected_card = None
                        elif dropped_on_tavern:
                            # Sell hand card by dropping into tavern
                            game_state.sell_card_from_hand(drag_state.dragged_card)
                            selected_card = None
                        else:
                            selected_card = None

                    elif drag_state.drag_source == "board":
                        if dropped_on_tavern:
                            # Sell board card by dropping into tavern
                            game_state.sell_card_from_board(drag_state.dragged_card)
                        elif dropped_on_board:
                            insert_index = get_board_insert_index(
                                mouse_position[0], len(game_state.player_board) - 1)
                            game_state.player_board.remove(drag_state.dragged_card)
                            insert_index = min(insert_index, len(game_state.player_board))
                            game_state.player_board.insert(insert_index, drag_state.dragged_card)

                    elif drag_state.drag_source == "tavern":
                        hand_zone = pygame.Rect(0, PLAYER_BOARD_Y - CARD_HEIGHT - 20,
                                                SCREEN_WIDTH, CARD_HEIGHT + 20)
                        if hand_zone.collidepoint(mouse_position) and not game_state.player_hand.is_full():
                            game_state.buy_card(drag_state.dragged_card)

                    drag_state.is_dragging = False
                    drag_state.dragged_card = None
                    drag_state.drag_source = None

            if event.type == pygame.MOUSEMOTION:
                if drag_state.is_dragging:
                    drag_state.drag_x = mouse_position[0]
                    drag_state.drag_y = mouse_position[1]

        # ===========================
        # --- Combat Processing ---
        # ===========================
        if current_scene == "game" and game_state is not None and is_in_combat:
            any_animation_active = any(
                state.is_animating for state in player_animation_states + boss_animation_states)

            if not any_animation_active:
                if current_time - last_combat_event_time >= COMBAT_EVENT_DELAY_MILLISECONDS:
                    if combat_event_queue:
                        combat_event = combat_event_queue.pop(0)

                        if combat_event["type"] == "attack":
                            attacker = combat_event["attacker"]
                            target = combat_event["target"]

                            pending_damage_map = {
                                attacker: {"damage_received": combat_event["damage_to_attacker"]},
                                target: {"damage_received": combat_event["damage_to_target"]},
                            }

                            # Add token damage popups at the unit positions
                            for state in player_animation_states + boss_animation_states:
                                if state.unit is attacker:
                                    state.display_health = combat_event["attacker_health_before"]
                                    state.pending_display_health = combat_event["attacker_health_after"]
                                    state.damage_applied = False
                                    state.damage_popup_amount = combat_event["damage_to_attacker"]
                                    state.damage_popup_triggered = False
                                elif state.unit is target:
                                    state.display_health = combat_event["target_health_before"]
                                    state.pending_display_health = combat_event["target_health_after"]
                                    state.damage_applied = False
                                    state.damage_popup_amount = combat_event["damage_to_target"]
                                    state.damage_popup_triggered = False

                            trigger_attack_animation(
                                player_animation_states, attacker, target,
                                boss_animation_states, current_time)
                            trigger_attack_animation(
                                boss_animation_states, attacker, target,
                                player_animation_states, current_time)

                            target_in_player = any(
                                s.unit is target for s in player_animation_states)
                            if target_in_player:
                                trigger_defender_animation(
                                    player_animation_states, target, current_time)
                            else:
                                trigger_defender_animation(
                                    boss_animation_states, target, current_time)

                        elif combat_event["type"] == "unit_will_die":
                            dead_unit = combat_event["unit"]
                            for state in player_animation_states + boss_animation_states:
                                if state.unit is dead_unit:
                                    state.display_health = 0
                            game_state.player_board = [
                                u for u in game_state.player_board if u is not dead_unit]
                            game_state.boss_board = [
                                u for u in game_state.boss_board if u is not dead_unit]
                            player_animation_states = [
                                s for s in player_animation_states if s.unit is not dead_unit]
                            boss_animation_states = [
                                s for s in boss_animation_states if s.unit is not dead_unit]



                        elif combat_event["type"] == "hero_hit":
                            attacker = combat_event["attacker"]
                            target = combat_event["target"]
                            trigger_hero_hit_animation(
                                player_animation_states, attacker, target, current_time, combat_event["damage"])
                            trigger_hero_hit_animation(
                                boss_animation_states, attacker, target, current_time, combat_event["damage"])
                            # ← popup is now triggered at collision midpoint, not here


                        elif combat_event["type"] == "combat_end":
                            game_state.restore_boards_from_snapshot()
                            player_animation_states = []
                            boss_animation_states = []
                            pending_damage_map = {}
                            is_in_combat = False
                            game_state.begin_player_turn()

                        last_combat_event_time = current_time

            update_animation_states(player_animation_states, pending_damage_map, current_time,
                                    game_state, damage_popup_queue, token_damage_popups)
            update_animation_states(boss_animation_states, pending_damage_map, current_time,
                                    game_state, damage_popup_queue, token_damage_popups)

        # ===========================
        # --- Popup Processing ---
        # ===========================
        if current_scene == "game":
            if round_damage_popup is not None:
                if current_time - round_damage_popup["start_time"] > DAMAGE_POPUP_DURATION_MILLISECONDS:
                    round_damage_popup = None

            if damage_popup_queue and current_time - last_damage_popup_time >= 400:
                next_popup = damage_popup_queue.pop(0)
                round_damage_popup = {
                    "target": next_popup["target"],
                    "amount": next_popup["amount"],
                    "start_time": current_time,
                }
                last_damage_popup_time = current_time

            # Remove expired token damage popups
            token_damage_popups = [
                popup for popup in token_damage_popups
                if current_time - popup["start_time"] < TOKEN_DAMAGE_POPUP_DURATION_MILLISECONDS
            ]

        # =====================
        # --- Drawing ---
        # =====================
        if current_scene == "menu":
            draw_main_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, mouse_position)

        elif current_scene == "settings":
            draw_settings_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, mouse_position, game_settings)



        elif current_scene == "game" and game_state is not None:
            is_planning = not is_in_combat
            draw_game_board_background(screen, is_planning=is_planning)
            draw_boss_hand(screen, game_state.boss_hand_size)

            if is_planning:
                tavern_card_rects, refresh_button_rect, tavern_hovered_zoom = draw_tavern(
                    screen, game_state.tavern_cards,
                    game_state.current_mana, mouse_position,
                    dragged_card=drag_state.dragged_card if drag_state.drag_source == "tavern" else None)
            else:
                tavern_card_rects = []
                tavern_hovered_zoom = None
                draw_boss_board(screen, game_state.boss_board, boss_animation_states)

            # Player board with drag support
            drag_insert_index = -1
            dragged_card_display = None
            if drag_state.is_dragging and not is_in_combat:
                board_zone = get_player_board_zone_rect()
                if board_zone.collidepoint(mouse_position):
                    source_board_length = len(game_state.player_board)
                    if drag_state.drag_source == "board":
                        source_board_length -= 1
                    drag_insert_index = get_board_insert_index(mouse_position[0], source_board_length)
                dragged_card_display = drag_state.dragged_card

            draw_player_board(screen, game_state.player_board, player_animation_states,
                              drag_insert_index=drag_insert_index,
                              dragged_card=dragged_card_display)

            for popup in token_damage_popups:
                draw_token_damage_popup(screen, popup, current_time)

            draw_hero_portrait(
                screen, name="The Swamp King", health=game_state.boss_health,
                centre_x=SCREEN_WIDTH // 2, top_y=BOSS_PORTRAIT_Y, is_player=False)
            draw_hero_portrait(
                screen, name="Hero", health=game_state.player_health,
                centre_x=SCREEN_WIDTH // 2, top_y=PLAYER_PORTRAIT_Y, is_player=True)

            draw_player_mana_bar(screen, game_state.current_mana, game_state.maximum_mana)
            draw_boss_mana_bar(screen, game_state.boss_current_mana, game_state.boss_maximum_mana)
            end_turn_button_rect = draw_end_turn_button(
                screen, game_state.is_player_turn() and not is_in_combat, mouse_position)
            menu_button_rect = draw_menu_button(screen, mouse_position)
            draw_damage_popup(screen, round_damage_popup, current_time)

            # Dragged card drawn after board but before hand
            if drag_state.is_dragging and drag_state.dragged_card is not None:
                drag_draw_x = drag_state.drag_x - CARD_WIDTH // 2
                drag_draw_y = drag_state.drag_y - CARD_HEIGHT // 2
                if isinstance(drag_state.dragged_card, Unit):
                    draw_unit_card(screen, drag_state.dragged_card, drag_draw_x, drag_draw_y)

            # Draw hand above tavern
            hand_card_rects, hovered_zoom_info = draw_hand(
                screen, game_state.player_hand, selected_card,
                game_state.current_mana, mouse_position)
            if hovered_zoom_info is not None:
                hovered_card, zoom_x, zoom_y = hovered_zoom_info
                draw_unit_card_zoomed(screen, hovered_card, zoom_x, zoom_y)

            # Draw tavern hover zoom on top of everything
            if tavern_hovered_zoom is not None:
                hovered_card, zoom_x, zoom_y = tavern_hovered_zoom
                draw_unit_card_zoomed(screen, hovered_card, zoom_x, zoom_y)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

import pygame

COLOUR_BACKGROUND = (20, 20, 30)
COLOUR_BUTTON_DEFAULT = (50, 50, 70)
COLOUR_BUTTON_HOVER = (70, 70, 100)
COLOUR_BUTTON_DISABLED = (35, 35, 45)
COLOUR_BUTTON_SELECTED = (30, 80, 200)
COLOUR_BUTTON_BORDER = (100, 100, 140)
COLOUR_TEXT_DEFAULT = (255, 255, 255)
COLOUR_TEXT_DISABLED = (80, 80, 100)
COLOUR_TITLE = (180, 140, 60)


def draw_button(surface: pygame.Surface, label: str, x: int, y: int,
                width: int, height: int, is_hovered: bool = False,
                is_disabled: bool = False, is_selected: bool = False) -> pygame.Rect:
    """Draws a menu button and returns its rect for click detection."""
    if is_disabled:
        background_colour = COLOUR_BUTTON_DISABLED
        text_colour = COLOUR_TEXT_DISABLED
    elif is_selected:
        background_colour = COLOUR_BUTTON_SELECTED
        text_colour = COLOUR_TEXT_DEFAULT
    elif is_hovered:
        background_colour = COLOUR_BUTTON_HOVER
        text_colour = COLOUR_TEXT_DEFAULT
    else:
        background_colour = COLOUR_BUTTON_DEFAULT
        text_colour = COLOUR_TEXT_DEFAULT

    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, background_colour, button_rect, border_radius=8)
    pygame.draw.rect(surface, COLOUR_BUTTON_BORDER, button_rect, width=2, border_radius=8)

    font = pygame.font.SysFont(None, 32)
    label_surface = font.render(label, True, text_colour)
    label_x = x + (width - label_surface.get_width()) // 2
    label_y = y + (height - label_surface.get_height()) // 2
    surface.blit(label_surface, (label_x, label_y))

    return button_rect


def draw_main_menu(surface: pygame.Surface, screen_width: int,
                   screen_height: int, mouse_position: tuple) -> dict:
    """Draws the main menu and returns a dict of button rects for click detection."""
    surface.fill(COLOUR_BACKGROUND)

    # Title
    font_title = pygame.font.SysFont(None, 80)
    title_surface = font_title.render("Card Game", True, COLOUR_TITLE)
    title_x = (screen_width - title_surface.get_width()) // 2
    surface.blit(title_surface, (title_x, screen_height // 4))

    # Subtitle
    font_subtitle = pygame.font.SysFont(None, 28)
    subtitle_surface = font_subtitle.render("A PvE Deckbuilding Adventure", True, (120, 120, 150))
    subtitle_x = (screen_width - subtitle_surface.get_width()) // 2
    surface.blit(subtitle_surface, (subtitle_x, screen_height // 4 + 80))

    button_width = 240
    button_height = 55
    button_x = (screen_width - button_width) // 2

    play_button_y = screen_height // 2
    collection_button_y = screen_height // 2 + 75
    settings_button_y = screen_height // 2 + 150

    play_rect = draw_button(
        surface, "Play", button_x, play_button_y, button_width, button_height,
        is_hovered=pygame.Rect(button_x, play_button_y, button_width, button_height).collidepoint(mouse_position)
    )
    collection_rect = draw_button(
        surface, "Collection", button_x, collection_button_y, button_width, button_height,
        is_disabled=True
    )
    settings_rect = draw_button(
        surface, "Settings", button_x, settings_button_y, button_width, button_height,
        is_hovered=pygame.Rect(button_x, settings_button_y, button_width, button_height).collidepoint(mouse_position)
    )

    exit_button_y = screen_height // 2 + 225
    exit_rect = draw_button(
        surface, "Exit", button_x, exit_button_y, button_width, button_height,
        is_hovered=pygame.Rect(button_x, exit_button_y, button_width, button_height).collidepoint(mouse_position)
    )

    return {
        "play": play_rect,
        "collection": collection_rect,
        "settings": settings_rect,
        "exit": exit_rect,
    }


def draw_settings_menu(surface: pygame.Surface, screen_width: int, screen_height: int,
                       mouse_position: tuple, settings) -> dict:
    """Draws the settings screen and returns a dict of button rects for click detection."""
    surface.fill(COLOUR_BACKGROUND)

    font_title = pygame.font.SysFont(None, 60)
    title_surface = font_title.render("Settings", True, COLOUR_TITLE)
    title_x = (screen_width - title_surface.get_width()) // 2
    surface.blit(title_surface, (title_x, screen_height // 6))

    font_label = pygame.font.SysFont(None, 30)
    resolution_label = font_label.render("Screen Resolution", True, COLOUR_TEXT_DEFAULT)
    resolution_label_x = (screen_width - resolution_label.get_width()) // 2
    surface.blit(resolution_label, (resolution_label_x, screen_height // 6 + 80))

    button_width = 200
    button_height = 48
    resolution_rects = []

    total_resolution_width = len(settings.AVAILABLE_RESOLUTIONS) * (button_width + 20) - 20
    resolution_start_x = (screen_width - total_resolution_width) // 2

    for index in range(len(settings.AVAILABLE_RESOLUTIONS)):
        button_x = resolution_start_x + index * (button_width + 20)
        button_y = screen_height // 6 + 120
        is_selected = index == settings.pending_resolution_index
        is_hovered = pygame.Rect(button_x, button_y, button_width, button_height).collidepoint(mouse_position)
        rect = draw_button(
            surface, settings.get_resolution_label(index),
            button_x, button_y, button_width, button_height,
            is_hovered=is_hovered, is_selected=is_selected
        )
        resolution_rects.append(rect)

    # Apply button
    apply_button_width = 160
    apply_button_height = 48
    apply_button_x = (screen_width - apply_button_width) // 2
    apply_button_y = screen_height // 6 + 200
    apply_rect = draw_button(
        surface, "Apply", apply_button_x, apply_button_y,
        apply_button_width, apply_button_height,
        is_hovered=pygame.Rect(apply_button_x, apply_button_y,
                               apply_button_width, apply_button_height).collidepoint(mouse_position)
    )

    # Back button
    back_button_width = 160
    back_button_height = 48
    back_button_x = (screen_width - back_button_width) // 2
    back_button_y = screen_height // 6 + 270
    back_rect = draw_button(
        surface, "Back", back_button_x, back_button_y,
        back_button_width, back_button_height,
        is_hovered=pygame.Rect(back_button_x, back_button_y,
                               back_button_width, back_button_height).collidepoint(mouse_position)
    )

    return {
        "resolutions": resolution_rects,
        "apply": apply_rect,
        "back": back_rect,
    }

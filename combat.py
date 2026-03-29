import random
import copy
from card import Unit


def get_valid_targets(board: list[Unit]) -> list[Unit]:
    """Returns valid attack targets from a board.
    Taunt units must be targeted first if any are present."""
    taunt_units = [unit for unit in board if unit.has_taunt]
    if taunt_units:
        return taunt_units
    return list(board)


def remove_dead_units(board: list[Unit]) -> list[Unit]:
    """Returns a new list with all dead units removed."""
    return [unit for unit in board if unit.is_alive()]


def determine_first_attacker(player_board: list[Unit], boss_board: list[Unit]) -> str:
    """Determines which side attacks first.
    The side with more units goes first. Ties are broken by coin flip.
    Returns 'player' or 'boss'."""
    if len(player_board) > len(boss_board):
        return "player"
    elif len(boss_board) > len(player_board):
        return "boss"
    else:
        return random.choice(["player", "boss"])


def build_combat_event_queue(game_state) -> list[dict]:
    """Pre-calculates the full alternating combat sequence and returns it as a list of events.
    Works on copies of units so original unit health values are never mutated."""
    events = []

    # Work on copies so originals are untouched
    player_originals = list(game_state.player_board)
    boss_originals = list(game_state.boss_board)
    player_board = [copy.copy(unit) for unit in player_originals]
    boss_board = [copy.copy(unit) for unit in boss_originals]

    # Map copies back to originals so events reference the real units
    copy_to_original = {}
    for original, copied in zip(player_originals, player_board):
        copy_to_original[id(copied)] = original
    for original, copied in zip(boss_originals, boss_board):
        copy_to_original[id(copied)] = original

    current_attacker_side = determine_first_attacker(player_board, boss_board)
    player_attack_index = 0
    boss_attack_index = 0

    while player_board and boss_board:
        if current_attacker_side == "player":
            player_attack_index = player_attack_index % len(player_board)
            attacker_copy = player_board[player_attack_index]
            valid_targets = get_valid_targets(boss_board)
            target_copy = random.choice(valid_targets)

            attacker_original = copy_to_original[id(attacker_copy)]
            target_original = copy_to_original[id(target_copy)]

            attack_events = resolve_attack_on_copies(
                attacker_copy, target_copy, attacker_original, target_original)
            events.extend(attack_events)
            player_board = remove_dead_units(player_board)
            boss_board = remove_dead_units(boss_board)
            player_attack_index += 1
            current_attacker_side = "boss"
        else:
            boss_attack_index = boss_attack_index % len(boss_board)
            attacker_copy = boss_board[boss_attack_index]
            valid_targets = get_valid_targets(player_board)
            target_copy = random.choice(valid_targets)

            attacker_original = copy_to_original[id(attacker_copy)]
            target_original = copy_to_original[id(target_copy)]

            attack_events = resolve_attack_on_copies(
                attacker_copy, target_copy, attacker_original, target_original)
            events.extend(attack_events)
            player_board = remove_dead_units(player_board)
            boss_board = remove_dead_units(boss_board)
            boss_attack_index += 1
            current_attacker_side = "player"

    surviving_player_originals = [copy_to_original[id(u)] for u in player_board if u.is_alive()]
    surviving_boss_originals = [copy_to_original[id(u)] for u in boss_board if u.is_alive()]

    for unit in surviving_player_originals:
        events.append({
            "type": "hero_hit",
            "attacker": unit,
            "target": "boss",
            "damage": unit.mana_cost,
        })

    for unit in surviving_boss_originals:
        events.append({
            "type": "hero_hit",
            "attacker": unit,
            "target": "player",
            "damage": unit.mana_cost,
        })

    events.append({
        "type": "combat_end",
        "surviving_player_units": surviving_player_originals,
        "surviving_boss_units": surviving_boss_originals,
    })

    return events


def resolve_attack_on_copies(attacker_copy: Unit, target_copy: Unit,
                             attacker_original: Unit, target_original: Unit) -> list[dict]:
    """Resolves an attack on copy units for calculation purposes."""
    events = []

    attacker_damage = attacker_copy.attack
    target_damage = target_copy.attack

    # Capture health BEFORE damage is applied
    attacker_health_before = attacker_copy.health
    target_health_before = target_copy.health

    # Apply damage to copies only
    target_copy.take_damage(attacker_damage)
    attacker_copy.take_damage(target_damage)

    # Capture health AFTER damage is applied
    attacker_health_after = attacker_copy.health
    target_health_after = target_copy.health

    events.append({
        "type": "attack",
        "attacker": attacker_original,
        "target": target_original,
        "damage_to_target": attacker_damage,
        "damage_to_attacker": target_damage,
        "attacker_health_before": attacker_health_before,
        "attacker_health_after": attacker_health_after,
        "target_health_before": target_health_before,
        "target_health_after": target_health_after,
    })

    if target_copy.health <= 0:
        events.append({
            "type": "unit_will_die",
            "unit": target_original,
            "damage_to_target": attacker_damage,
            "damage_to_attacker": target_damage,
        })

    if attacker_copy.health <= 0:
        events.append({
            "type": "unit_will_die",
            "unit": attacker_original,
            "damage_to_target": attacker_damage,
            "damage_to_attacker": target_damage,
        })

    return events

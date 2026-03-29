import random
from card import Unit


def get_valid_targets(board: list[Unit]) -> list[Unit]:
    """Returns valid attack targets from a board.
    Taunt units must be targeted first if any are present."""
    taunt_units = [unit for unit in board if unit.has_taunt]
    if taunt_units:
        return taunt_units
    return list(board)


def resolve_attack(attacker: Unit, target: Unit) -> list[dict]:
    """Resolves a single attack between two units.
    Returns a list of combat events describing what happened."""
    events = []

    attacker_damage = attacker.attack
    target_damage = target.attack

    target.take_damage(attacker_damage)
    attacker.take_damage(target_damage)

    events.append({
        "type": "attack",
        "attacker": attacker,
        "target": target,
        "damage_dealt": attacker_damage,
        "damage_received": target_damage,
    })

    if not target.is_alive():
        events.append({"type": "unit_died", "unit": target})

    if not attacker.is_alive():
        events.append({"type": "unit_died", "unit": attacker})

    return events


def resolve_excess_damage_to_boss(attacker: Unit, game_state) -> list[dict]:
    """Deals attacker damage directly to the boss when no targets remain."""
    game_state.boss_health -= attacker.attack
    return [{
        "type": "direct_damage",
        "target": "boss",
        "damage": attacker.attack,
    }]


def resolve_excess_damage_to_player(attacker: Unit, game_state) -> list[dict]:
    """Deals attacker damage directly to the player when no targets remain."""
    game_state.player_health -= attacker.attack
    return [{
        "type": "direct_damage",
        "target": "player",
        "damage": attacker.attack,
    }]


def remove_dead_units(board: list[Unit]) -> list[Unit]:
    """Returns a new list with all dead units removed."""
    return [unit for unit in board if unit.is_alive()]


def build_combat_event_queue(game_state) -> list[dict]:
    """Pre-calculates the full combat sequence and returns it as a list of events.
    Does not modify the game state directly, all mutations happen during event playback."""
    events = []

    # Work on copies of the boards so we can mutate freely
    player_board = list(game_state.player_board)
    boss_board = list(game_state.boss_board)

    # Player units attack left to right
    for attacker in list(player_board):
        if not attacker.is_alive():
            continue
        valid_targets = get_valid_targets(boss_board)
        if valid_targets:
            target = random.choice(valid_targets)
            attack_events = resolve_attack(attacker, target)
            events.extend(attack_events)
            boss_board = remove_dead_units(boss_board)
            player_board = remove_dead_units(player_board)
        else:
            events.extend(resolve_excess_damage_to_boss(attacker, game_state))

    # Boss units attack left to right
    for attacker in list(boss_board):
        if not attacker.is_alive():
            continue
        valid_targets = get_valid_targets(player_board)
        if valid_targets:
            target = random.choice(valid_targets)
            attack_events = resolve_attack(attacker, target)
            events.extend(attack_events)
            player_board = remove_dead_units(player_board)
            boss_board = remove_dead_units(boss_board)
        else:
            events.extend(resolve_excess_damage_to_player(attacker, game_state))

    events.append({"type": "combat_end"})
    return events

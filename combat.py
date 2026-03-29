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
    """Records an attack between two units without applying damage yet.
    Damage is applied visually during animation playback."""
    events = []

    attacker_damage = attacker.attack
    target_damage = target.attack

    events.append({
        "type": "attack",
        "attacker": attacker,
        "target": target,
        "damage_to_target": attacker_damage,
        "damage_to_attacker": target_damage,
    })

    # Pre-calculate deaths based on pending damage so we can queue the events
    if target.health - attacker_damage <= 0:
        events.append({"type": "unit_will_die", "unit": target,
                       "damage_to_target": attacker_damage, "damage_to_attacker": target_damage})
    if attacker.health - target_damage <= 0:
        events.append({"type": "unit_will_die", "unit": attacker,
                       "damage_to_target": attacker_damage, "damage_to_attacker": target_damage})

    # Still apply damage to the actual units so subsequent combat logic is correct
    target.take_damage(attacker_damage)
    attacker.take_damage(target_damage)

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
    Attacks alternate between sides, with the side that has more units going first.
    Excess attackers deal damage directly to the opposing hero."""
    events = []

    player_board = list(game_state.player_board)
    boss_board = list(game_state.boss_board)

    current_attacker_side = determine_first_attacker(player_board, boss_board)

    player_attack_index = 0
    boss_attack_index = 0

    while player_board and boss_board:
        if current_attacker_side == "player":
            # Wrap attack index if it exceeds current board length
            player_attack_index = player_attack_index % len(player_board)
            attacker = player_board[player_attack_index]
            valid_targets = get_valid_targets(boss_board)
            target = random.choice(valid_targets)
            attack_events = resolve_attack(attacker, target)
            events.extend(attack_events)
            player_board = remove_dead_units(player_board)
            boss_board = remove_dead_units(boss_board)
            player_attack_index += 1
            current_attacker_side = "boss"
        else:
            boss_attack_index = boss_attack_index % len(boss_board)
            attacker = boss_board[boss_attack_index]
            valid_targets = get_valid_targets(player_board)
            target = random.choice(valid_targets)
            attack_events = resolve_attack(attacker, target)
            events.extend(attack_events)
            player_board = remove_dead_units(player_board)
            boss_board = remove_dead_units(boss_board)
            boss_attack_index += 1
            current_attacker_side = "player"

    # Any remaining player units deal damage directly to the boss
    for remaining_attacker in player_board:
        events.extend(resolve_excess_damage_to_boss(remaining_attacker, game_state))

    # Any remaining boss units deal damage directly to the player
    for remaining_attacker in boss_board:
        events.extend(resolve_excess_damage_to_player(remaining_attacker, game_state))

    events.append({"type": "combat_end"})
    return events

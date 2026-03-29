from card import Unit
from deck import Deck


class Boss:
    STARTING_HEALTH = 30
    MAXIMUM_BOARD_SIZE = 7

    def __init__(self, name: str, deck: Deck):
        self.name = name
        self.deck = deck
        self.health = self.STARTING_HEALTH

    def take_turn(self, boss_board: list[Unit]) -> Unit | None:
        """Plays one unit from the boss deck onto the board if space allows.
        Returns the unit played, or None if the board is full or deck is empty."""
        if len(boss_board) >= self.MAXIMUM_BOARD_SIZE:
            return None
        card = self.deck.draw()
        if card is None:
            return None
        boss_board.append(card)
        return card


def build_boss_deck() -> Deck:
    """Creates a simple starting boss deck."""
    cards = [
        Unit(name="Cave Grunt", attack=2, health=2, mana_cost=1),
        Unit(name="Stone Wall", attack=1, health=6, mana_cost=3, has_taunt=True),
        Unit(name="Bog Beast", attack=3, health=3, mana_cost=3),
        Unit(name="Marsh Crawler", attack=2, health=4, mana_cost=2),
        Unit(name="Rock Elemental", attack=4, health=4, mana_cost=5),
        Unit(name="Swamp Toad", attack=1, health=2, mana_cost=1),
        Unit(name="Vine Lurker", attack=3, health=6, mana_cost=4, has_taunt=True),
    ]
    deck = Deck(cards=cards)
    deck.shuffle()
    return deck

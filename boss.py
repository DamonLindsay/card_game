from card import Unit
from deck import Deck


class Boss:
    STARTING_HEALTH = 30
    MAXIMUM_BOARD_SIZE = 7

    def __init__(self, name: str, deck: Deck):
        self.name = name
        self.deck = deck
        self.health = self.STARTING_HEALTH

    def take_turn(self, boss_board: list, available_mana: int) -> list:
        """Plays units from the boss deck onto the board based on available mana.
        Returns a list of units played this turn."""
        units_played = []
        remaining_mana = available_mana

        while len(boss_board) < self.MAXIMUM_BOARD_SIZE:
            card = self.deck.draw()
            if card is None:
                break
            if card.mana_cost > remaining_mana:
                # Put the card back and stop
                self.deck.add_card(card)
                break
            boss_board.append(card)
            remaining_mana -= card.mana_cost
            units_played.append(card)

        return units_played


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

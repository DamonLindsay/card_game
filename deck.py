import random
from card import Card


class Deck:
    def __init__(self, cards: list[Card] = None):
        self.cards = cards if cards is not None else []

    def shuffle(self):
        """Randomly shuffles the cards in the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        """Removes and returns the top card of the deck.
        Returns None if the deck is empty."""
        if self.is_empty():
            return None
        return self.cards.pop()

    def add_card(self, card: Card):
        """Adds a single card to the bottom of the deck."""
        self.cards.insert(0, card)

    def is_empty(self) -> bool:
        """Returns True if there are no cards remaining in the deck."""
        return len(self.cards) == 0

    def __len__(self) -> int:
        """Returns the number of cards remaining in the deck."""
        return len(self.cards)

    def __str__(self) -> str:
        return f"Deck({len(self.cards)} cards."

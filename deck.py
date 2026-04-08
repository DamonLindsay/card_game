import random
from card import Card


class Deck:
    def __init__(self, cards: list[Card] = None):
        self.cards = cards if cards is not None else []

    def shuffle(self):
        """Randomly shuffles the cards in the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        """Removes and returns a random card from the pool.
        Returns None if the pool is empty."""
        if self.is_empty():
            return None
        index = random.randint(0, len(self.cards) - 1)
        return self.cards.pop(index)

    def draw_multiple(self, count: int, exclude: list = None) -> list[Card]:
        """Draws multiple random cards from the pool, excluding specified cards.
        Returns as many as available up to count."""
        exclude = exclude or []
        available = [card for card in self.cards if card not in exclude]
        draw_count = min(count, len(available))
        drawn = random.sample(available, draw_count)
        for card in drawn:
            self.cards.remove(card)
        return drawn

    def add_card(self, card: Card):
        """Adds a single card to the pool."""
        self.cards.append(card)

    def is_empty(self) -> bool:
        """Returns True if there are no cards remaining in the pool."""
        return len(self.cards) == 0

    def __len__(self) -> int:
        """Returns the number of cards remaining in the pool."""
        return len(self.cards)

    def __str__(self) -> str:
        return f"Deck({len(self.cards)} cards)"

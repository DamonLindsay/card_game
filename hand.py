from card import Card


class Hand:
    MAXIMUM_HAND_SIZE = 10

    def __init__(self):
        self.cards = []

    def add_card(self, card: Card):
        """Adds a card to the hand.  Returns False if the hand is full."""
        if self.is_full():
            return False
        self.cards.append(card)
        return True

    def remove_card(self, card: Card) -> bool:
        """Removes a specific card from the hand.  Returns False if not found."""
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False

    def is_full(self) -> bool:
        """Returns True if the hand is at maximum capacity."""
        return len(self.cards) >= self.MAXIMUM_HAND_SIZE

    def __len__(self) -> int:
        """Returns the number of cards currently in hand."""
        return len(self.cards)

    def __str__(self) -> str:
        return f"Hand({len(self.cards)} cards)"

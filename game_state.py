from deck import Deck
from hand import Hand
from card import Unit
from boss import Boss, build_boss_deck


class GameState:
    MAXIMUM_MANA = 10
    MAXIMUM_BOARD_SIZE = 7
    STARTING_PLAYER_HEALTH = 30
    STARTING_BOSS_HEALTH = 30

    def __init__(self, player_deck: Deck):
        self.player_health = self.STARTING_PLAYER_HEALTH
        self.boss_health = self.STARTING_BOSS_HEALTH

        self.current_mana = 1
        self.maximum_mana = 1
        self.boss_current_mana = 1
        self.boss_maximum_mana = 1
        self.turn_number = 1
        self.current_turn = "player"
        self.boss_hand_size = 0

        self.player_deck = player_deck
        self.player_hand = Hand()
        self.player_board = []
        self.boss_board = []

        self.player_board_snapshot = []
        self.boss_board_snapshot = []

        self.boss = Boss(name="The Swamp King", deck=build_boss_deck())

        self.draw_opening_hand()

    def draw_opening_hand(self):
        """Draws the starting hand of 4 cards at the beginning of the game."""
        for _ in range(4):
            self.draw_card()

    def draw_card(self):
        """Draws a single card from the player deck into the hand.
        Does nothing if the deck is empty or the hand is full."""
        drawn_card = self.player_deck.draw()
        if drawn_card is not None:
            self.player_hand.add_card(drawn_card)

    def end_player_turn(self):
        """Ends the player's turn and transitions to the boss turn."""
        self.current_turn = "boss"

    def begin_player_turn(self):
        """Begins a new player turn, incrementing mana and drawing a card."""
        self.turn_number += 1
        self.maximum_mana = min(self.turn_number, self.MAXIMUM_MANA)
        self.current_mana = self.maximum_mana
        self.boss_maximum_mana = min(self.turn_number, self.MAXIMUM_MANA)
        self.boss_current_mana = self.boss_maximum_mana
        self.current_turn = "player"
        self.draw_card()
        if self.boss_hand_size < Hand.MAXIMUM_HAND_SIZE:
            self.boss_hand_size += 1

    def is_player_turn(self) -> bool:
        """Returns True if it is currently the player's turn."""
        return self.current_turn == "player"

    def can_afford(self, mana_cost: int) -> bool:
        """Returns True if the player has enough mana to play the given cost."""
        return self.current_mana >= mana_cost

    def spend_mana(self, amount: int):
        """Deducts the given amount from the current mana pool."""
        self.current_mana -= amount

    def is_player_dead(self) -> bool:
        """Returns True if the player has no health remaining."""
        return self.player_health <= 0

    def is_boss_dead(self) -> bool:
        """Returns True if the boss has no health remaining."""
        return self.boss_health <= 0

    def play_card_to_board(self, card: Unit) -> bool:
        """Attempts to play a unit card from hand to the player board.
        Returns True if successful, False if board is full or insufficient mana."""
        if len(self.player_board) >= self.MAXIMUM_BOARD_SIZE:
            return False
        if not self.can_afford(card.mana_cost):
            return False
        self.spend_mana(card.mana_cost)
        self.player_hand.remove_card(card)
        self.player_board.append(card)
        return True

    def apply_combat_results(self):
        """Removes dead units from both boards after combat resolves."""
        self.player_board = [unit for unit in self.player_board if unit.is_alive()]
        self.boss_board = [unit for unit in self.boss_board if unit.is_alive()]

    def save_board_snapshot(self):
        """Saves a copy of both boards before combat begins."""
        self.player_board_snapshot = [unit.copy() for unit in self.player_board]
        self.boss_board_snapshot = [unit.copy() for unit in self.boss_board]

    def restore_boards_from_snapshot(self):
        """Restores both boards to their pre-combat state after combat ends."""
        self.player_board = self.player_board_snapshot
        self.boss_board = self.boss_board_snapshot

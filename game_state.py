from deck import Deck
from hand import Hand
from card import Unit
from boss import Boss, build_boss_deck


class GameState:
    MAXIMUM_MANA = 10
    MAXIMUM_BOARD_SIZE = 7
    STARTING_PLAYER_HEALTH = 30
    STARTING_BOSS_HEALTH = 30
    STARTING_SHOP_SIZE = 3
    MAXIMUM_SHOP_SIZE = 6
    TAVERN_REFRESH_COST = 1

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
        self.previous_boss_board = []

        self.player_board_snapshot = []
        self.boss_board_snapshot = []

        self.tavern_cards = []

        self.boss = Boss(name="The Swamp King", deck=build_boss_deck())

        self.refresh_tavern()

    def get_current_shop_size(self) -> int:
        """Returns the current shop size based on turn number."""
        return min(self.STARTING_SHOP_SIZE + self.turn_number // 3, self.MAXIMUM_SHOP_SIZE)

    def get_excluded_cards(self) -> list:
        """Returns all cards currently on the board or in hand — excluded from shop draws."""
        return list(self.player_board) + list(self.player_hand.cards)

    def refresh_tavern(self) -> bool:
        """Refreshes the tavern with new random cards from the pool.
        Cards currently in the tavern are returned to the pool first.
        Returns False if player cannot afford the refresh cost (except on turn start)."""
        for card in self.tavern_cards:
            self.player_deck.add_card(card)
        self.tavern_cards = []

        shop_size = self.get_current_shop_size()
        excluded = self.get_excluded_cards()
        self.tavern_cards = self.player_deck.draw_multiple(shop_size, exclude=excluded)
        return True

    def pay_for_refresh(self) -> bool:
        """Attempts to refresh the tavern for 1 mana.
        Returns False if the player cannot afford it."""
        if self.current_mana < self.TAVERN_REFRESH_COST:
            return False
        self.current_mana -= self.TAVERN_REFRESH_COST
        self.refresh_tavern()
        return True

    def buy_card(self, card: Unit) -> bool:
        """Attempts to buy a card from the tavern.
        Returns False if the player cannot afford it or hand is full."""
        if card not in self.tavern_cards:
            return False
        if self.current_mana < card.mana_cost:
            return False
        if self.player_hand.is_full():
            return False
        self.current_mana -= card.mana_cost
        self.tavern_cards.remove(card)
        self.player_hand.add_card(card)
        return True

    def sell_card_from_hand(self, card: Unit) -> bool:
        """Sells a card from hand back to the pool for 1 mana.
        Returns False if card not in hand."""
        if card not in self.player_hand.cards:
            return False
        self.player_hand.remove_card(card)
        self.player_deck.add_card(card)
        self.current_mana = min(self.current_mana + 1, self.maximum_mana)
        return True

    def sell_card_from_board(self, card: Unit) -> bool:
        """Sells a card from the board back to the pool for 1 mana.
        Returns False if card not on board."""
        if card not in self.player_board:
            return False
        self.player_board.remove(card)
        self.player_deck.add_card(card)
        self.current_mana = min(self.current_mana + 1, self.maximum_mana)
        return True

    def end_player_turn(self):
        """Ends the player's turn and transitions to the boss turn."""
        self.current_turn = "boss"

    def begin_player_turn(self):
        """Begins a new player turn, incrementing mana and refreshing the tavern."""
        self.turn_number += 1
        self.maximum_mana = min(self.turn_number, self.MAXIMUM_MANA)
        self.current_mana = self.maximum_mana
        self.boss_maximum_mana = min(self.turn_number, self.MAXIMUM_MANA)
        self.boss_current_mana = self.boss_maximum_mana
        self.current_turn = "player"
        self.refresh_tavern()
        if self.boss_hand_size < Hand.MAXIMUM_HAND_SIZE:
            self.boss_hand_size += 1

    def is_player_turn(self) -> bool:
        """Returns True if it is currently the player's turn."""
        return self.current_turn == "player"

    def can_afford(self, mana_cost: int) -> bool:
        """Returns True if the player has enough mana to afford the given cost."""
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
        """Moves a unit from hand to the player board. No mana cost — already paid on buy.
        Returns False if board is full or card not in hand."""
        if len(self.player_board) >= self.MAXIMUM_BOARD_SIZE:
            return False
        if card not in self.player_hand.cards:
            return False
        self.player_hand.remove_card(card)
        self.player_board.append(card)
        return True

    def save_board_snapshot(self):
        """Saves a copy of both boards before combat begins."""
        self.player_board_snapshot = [unit.copy() for unit in self.player_board]
        self.boss_board_snapshot = [unit.copy() for unit in self.boss_board]

    def restore_boards_from_snapshot(self):
        """Restores both boards to their pre-combat state and saves boss board for display."""
        self.previous_boss_board = [unit.copy() for unit in self.boss_board_snapshot]
        self.player_board = self.player_board_snapshot
        self.boss_board = []

    def apply_single_unit_damage(self, target: str, amount: int):
        """Applies damage from a single surviving unit to the target hero."""
        if target == "boss":
            self.boss_health -= amount
        else:
            self.player_health -= amount

    def apply_combat_damage(self, surviving_player_units: list, surviving_boss_units: list):
        """Deducts health from the losing side based on surviving enemy unit mana costs."""
        if surviving_player_units and not surviving_boss_units:
            for unit in surviving_player_units:
                self.boss_health -= unit.mana_cost
        elif surviving_boss_units and not surviving_player_units:
            for unit in surviving_boss_units:
                self.player_health -= unit.mana_cost

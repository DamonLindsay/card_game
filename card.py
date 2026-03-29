class Card:
    def __init__(self, name: str, art_path: str):
        self.name = name
        self.art_path = art_path

    def __str__(self):
        return self.name


class Unit(Card):
    def __init__(self, name: str, attack: int, health: int, mana_cost: int = 0, art_path: str = "", tribes: list = None,
                 has_taunt: bool = False):
        super().__init__(name, art_path)
        self.attack = attack
        self.health = health
        self.max_health = health
        self.mana_cost = mana_cost
        self.tribes = tribes if tribes is not None else []
        self.has_taunt = has_taunt

    def take_damage(self, amount: int):
        self.health -= amount

    def is_alive(self) -> bool:
        return self.health > 0

    def copy(self):
        """Returns a new Unit with the same stats, used for board snapshots."""
        return Unit(
            name=self.name,
            attack=self.attack,
            health=self.max_health,
            mana_cost=self.mana_cost,
            art_path=self.art_path,
            tribes=list(self.tribes),
            has_taunt=self.has_taunt,
        )

    def __str__(self):
        return f"{self.name} ({self.attack}/{self.health})"

# Card Game

An auto-battler card game in the style of Hearthstone Battlegrounds, built in Python with pygame.

Buy units from the tavern, arrange them on your board, then watch them fight a boss's board automatically, round after round.

## Features

- **Tavern shop:** buy, sell and refresh, with drag-to-buy and a shopkeeper portrait
- **Board management:** drag and drop cards onto the board and rearrange them
- **Automatic combat:** attack order, targeting and damage resolved turn by turn, played back as an event queue
- **Animation:** sliding attackers, damage popups, coloured stats, hero hit effects and card hover zoom
- **Battlegrounds-style turn flow:** hero health, mana bars and a damage model between rounds
- **Main menu and settings** with configurable resolution

## Tech stack

Python 3, pygame

## Running it

```bash
pip install pygame
python main.py
```

## Code structure

| File | Purpose |
|---|---|
| `main.py` | Game loop, input and rendering |
| `game_state.py` | Board, hand and round state |
| `combat.py` | Builds the combat event queue and resolves attacks |
| `card.py`, `deck.py`, `hand.py` | Card and unit models |
| `boss.py` | Boss opponent and its board |
| `menu.py`, `settings.py` | Menus and display settings |

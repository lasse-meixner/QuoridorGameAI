# Quoridor Console

A simple console implementation of the classic strategy game **Quoridor**, where you play against a bot powered by a depth-limited Minimax search with α–β pruning.

---

## Rules of the Game

See the official rules on Wikipedia:  
https://en.wikipedia.org/wiki/Quoridor_(board_game)

---

## How to run

```
python main.py
```

You can choose who moves first.
___

## What’s in this Project

- **`game_state.py`**  
  Encodes the 9×9 board, pawn-moves (including jumps), wall-placement rules (no overlaps, must leave a path).  
- **`ai.py`**  
  A Minimax bot (default depth 3) with α–β pruning.  
  - **Heuristic**: difference of shortest‐path lengths to goal, plus a tiny bonus for progress.  
  - **Tie‐break**: at the root, with move-order preferences
- **`main.py`**  
  A curses-based UI:
  - Renders the board as a grid of dots (wall-junctions) with cells in between.  
  - Lets you flip the view (press **f**) or see wall counts and move times.  

---

## Requirements

This project doesn't require any non-default python dependencies.
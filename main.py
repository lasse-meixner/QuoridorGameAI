# main.py
import curses, time
from game_state import GameState
from ai import MinimaxAI

# how many rows/cols to indent the maze
GRID_OFFSET_Y = 1
GRID_OFFSET_X = 2

# arrow‐key → (dr,dc)
DIRS = {
    'KEY_UP':    (-1,  0),
    'KEY_DOWN':  ( 1,  0),
    'KEY_LEFT':  ( 0, -1),
    'KEY_RIGHT': ( 0,  1),
}

def draw_board(stdscr, state: GameState, msg: str, flipped: bool):
    stdscr.erase()
    max_y, max_x = stdscr.getmaxyx()
    H, W = GameState.HEIGHT, GameState.WIDTH

    off_y, off_x = GRID_OFFSET_Y, GRID_OFFSET_X
    grid_h = 2 * H      # logical maze height in character rows
    grid_w = 4 * W      # logical maze width in character cols

    # helper to map logical grid‐coords → screen coords, with optional flip
    def disp_coords(y_log: int, x_log: int):
        if not flipped:
            return off_y + y_log, off_x + x_log
        else:
            return off_y + (grid_h - y_log), off_x + (grid_w - x_log)

    # 1) Draw all intersection points “.”
    for pi in range(H+1):
        for pj in range(W+1):
            y, x = disp_coords(2*pi, 4*pj)
            if y < max_y and x < max_x:
                stdscr.addstr(y, x, '.')

    # 2) Label every dot intersection (points 1..W+1 on top, 1..H+1 on left)
    #    these come *after* the dots so numbers aren’t overwritten
    # Top row of dots:
    for pj in range(W+1):
        y, x = disp_coords(0, 4*pj)
        if 0 <= y < max_y and 0 <= x < max_x:
            stdscr.addstr(y, x, str(pj+1))
    # Left column of dots:
    for pi in range(H+1):
        y, x = disp_coords(2*pi, 0)
        if 0 <= y < max_y and 0 <= x < max_x:
            stdscr.addstr(y, x, str(pi+1))

    # 3) Draw horizontal walls “-”
    for (r, c, orient) in state.walls:
        if orient == 'H':
            pi = r + 1
            for pj in (c, c+1):
                y, x = disp_coords(2*pi, 4*pj + 2)
                if y < max_y and x < max_x:
                    stdscr.addstr(y, x, '-')

    # 4) Draw vertical walls “|”
    for (r, c, orient) in state.walls:
        if orient == 'V':
            pj = c + 1
            for pi in (r, r+1):
                y, x = disp_coords(2*pi + 1, 4*pj)
                if y < max_y and x < max_x:
                    stdscr.addstr(y, x, '|')

    # 5) Draw each cell between the dots, with pawn if present
    for r in range(H):
        for c in range(W):
            if state.pawns[0] == (r, c):
                ch = '0'
            elif state.pawns[1] == (r, c):
                ch = '1'
            else:
                ch = ' '   # blank cell
            y, x = disp_coords(2*r + 1, 4*c + 2)
            if y < max_y and x < max_x:
                stdscr.addstr(y, x, ch)

    # 6) Message + walls‐remaining under the maze (static bottom lines)
    base_msg_row   = off_y + grid_h + 1
    base_walls_row = off_y + grid_h + 2
    msg_row   = min(base_msg_row,   max_y - 2)
    walls_row = min(base_walls_row, max_y - 1)
    try:
        stdscr.addstr(msg_row,   0, msg[:max_x-1])
        rem = f"Walls → You: {state.walls_remaining[0]}   AI: {state.walls_remaining[1]}"
        stdscr.addstr(walls_row, 0, rem[:max_x-1])
    except curses.error:
        pass

    stdscr.refresh()


def parse_wall_input(s: str):
    try:
        part, o = s[:-1], s[-1].upper()
        rp, cp = map(int, part.split(','))
        if o not in ('H', 'V'):
            return None
        # convert midpoint (1-based) → cell‐based (0-based)
        return (rp - 2, cp - 2, o)
    except:
        return None


def main(stdscr):
    curses.curs_set(0)

    # ── ask who goes first ─────────────────────────────────────────────
    stdscr.clear()
    stdscr.addstr(0, 0, "Who moves first? (p=Player, b=Bot): ")
    curses.echo()
    choice = stdscr.getkey().lower()
    curses.noecho()
    first_player = 0 if choice == 'p' else 1
    # ──────────────────────────────────────────────────────────────────

    state = GameState()
    state.current_player = first_player
    ai    = MinimaxAI(depth=3)
    msg   = "Arrows to move, w=wall, f=flip, q=quit."
    flipped = False

    while True:
        draw_board(stdscr, state, msg, flipped)

        # game‐over?
        if state.is_game_over():
            w = state.get_winner()
            msg = f"Game over! Player {w} wins. (q=quit)"
            draw_board(stdscr, state, msg, flipped)
            if stdscr.getkey() == 'q':
                break
            continue

        # PLAYER TURN
        if state.current_player == 0:
            key = stdscr.getkey()

            # toggle flip
            if key == 'f':
                flipped = not flipped
                msg = "Board flipped!"
                draw_board(stdscr, state, msg, flipped)
                continue

            if key == 'q':
                break

            if key in DIRS:
                dr, dc = DIRS[key]
                if state.is_valid_move(('pawn', dr, dc)):
                    state.apply_move(('pawn', dr, dc));   msg = ""
                elif state.is_valid_move(('pawn', 2*dr, 2*dc)):
                    state.apply_move(('pawn', 2*dr, 2*dc)); msg = ""
                else:
                    msg = "Invalid pawn move!"
                draw_board(stdscr, state, msg, flipped)

            elif key == 'w':
                msg = "Enter wall (r,cH/V): "
                draw_board(stdscr, state, msg, flipped)
                max_y, _ = stdscr.getmaxyx()
                prompt_row = min(GRID_OFFSET_Y + 2*GameState.HEIGHT + 1, max_y-2)
                stdscr.move(prompt_row, len(msg))
                stdscr.refresh()

                curses.echo()
                inp = stdscr.getstr().decode().strip()
                curses.noecho()

                parsed = parse_wall_input(inp)
                if parsed and state.is_valid_wall(parsed):
                    state.apply_move(('wall', *parsed)); msg = ""
                else:
                    msg = "Invalid wall!"
                draw_board(stdscr, state, msg, flipped)

            else:
                msg = "Use arrows, w, f or q."
                draw_board(stdscr, state, msg, flipped)

        # AI TURN
        else:
            msg = "AI thinking..."
            draw_board(stdscr, state, msg, flipped)
            t0 = time.time()
            mv = ai.choose_move(state)
            dur = time.time() - t0
            state.apply_move(mv)
            msg = f"AI moved in {dur:.2f}s"
            draw_board(stdscr, state, msg, flipped)


if __name__ == '__main__':
    curses.wrapper(main)

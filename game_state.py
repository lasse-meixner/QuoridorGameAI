from collections import deque

class GameState:
    WIDTH = 9
    HEIGHT = 9

    def __init__(self):
        # Pawns: player 0 at bottom middle, player 1 at top middle
        self.pawns = [(self.HEIGHT-1, self.WIDTH//2), (0, self.WIDTH//2)]
        # Walls: set of tuples (row, col, orient) where orient is 'H' or 'V'
        # (row,col) is the upper‐left cell of the 2‐space wall
        self.walls = set()
        # Each player has 10 walls remaining
        self.walls_remaining = [10, 10]
        # Current player: 0 or 1
        self.current_player = 0

    def clone(self):
        new = GameState()
        new.pawns = list(self.pawns)
        new.walls = set(self.walls)
        new.walls_remaining = list(self.walls_remaining)
        new.current_player = self.current_player
        return new

    def apply_move(self, move):
        player = self.current_player
        if move[0] == 'pawn':
            _, dr, dc = move
            r, c = self.pawns[player]
            self.pawns[player] = (r + dr, c + dc)
        else:
            _, r, c, orient = move
            self.walls.add((r, c, orient))
            self.walls_remaining[player] -= 1
        self.current_player = 1 - player

    def is_game_over(self):
        r0, _ = self.pawns[0]
        r1, _ = self.pawns[1]
        return (r0 == 0) or (r1 == self.HEIGHT - 1)

    def get_winner(self):
        if not self.is_game_over():
            return None
        r0, _ = self.pawns[0]
        return 0 if r0 == 0 else 1

    def get_legal_moves(self):
        moves = []
        # Pawn moves
        for dr, dc in self.get_legal_pawn_moves(self.current_player):
            moves.append(('pawn', dr, dc))
        # Wall placements
        if self.walls_remaining[self.current_player] > 0:
            for r in range(self.HEIGHT - 1):
                for c in range(self.WIDTH - 1):
                    for orient in ('H', 'V'):
                        if self.is_valid_wall((r, c, orient)):
                            moves.append(('wall', r, c, orient))
        return moves

    def is_valid_move(self, move):
        if move[0] == 'pawn':
            return (move[1], move[2]) in self.get_legal_pawn_moves(self.current_player)
        else:
            _, r, c, orient = move
            return self.is_valid_wall((r, c, orient))

    def get_legal_pawn_moves(self, player):
        r, c = self.pawns[player]
        opp_r, opp_c = self.pawns[1 - player]
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        moves = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not self._in_bounds(nr, nc):
                continue
            if self._is_blocked((r, c), (nr, nc)):
                continue
            if (nr, nc) == (opp_r, opp_c):
                # Jump or side‐step
                jr, jc = nr + dr, nc + dc
                if self._in_bounds(jr, jc) and not self._is_blocked((nr, nc), (jr, jc)):
                    moves.append((2*dr, 2*dc))
                else:
                    for ldr, ldc in ((-dc, dr), (dc, -dr)):
                        lr, lc = nr + ldr, nc + ldc
                        if not self._in_bounds(lr, lc):
                            continue
                        if self._is_blocked((nr, nc), (lr, lc)):
                            continue
                        moves.append((dr + ldr, dc + ldc))
            else:
                moves.append((dr, dc))
        return moves

    def _in_bounds(self, r, c):
        return 0 <= r < self.HEIGHT and 0 <= c < self.WIDTH

    def _is_blocked(self, a, b):
        r1, c1 = a
        r2, c2 = b
        # Vertical movement (up/down)
        if r1 == r2 + 1 and c1 == c2:
            # moving up: check horizontal walls at (r2, c1) and (r2, c1-1)
            for dc in (0, -1):
                if (r2, c1+dc, 'H') in self.walls:
                    return True
            return False
        if r2 == r1 + 1 and c1 == c2:
            # moving down: check at (r1, c1) and (r1, c1-1)
            for dc in (0, -1):
                if (r1, c1+dc, 'H') in self.walls:
                    return True
            return False
        # Horizontal movement (left/right)
        if c1 == c2 + 1 and r1 == r2:
            # moving left: check vertical walls at (r1, c2) and (r1-1, c2)
            for dr in (0, -1):
                if (r1+dr, c2, 'V') in self.walls:
                    return True
            return False
        if c2 == c1 + 1 and r1 == r2:
            # moving right: check at (r1, c1) and (r1-1, c1)
            for dr in (0, -1):
                if (r1+dr, c1, 'V') in self.walls:
                    return True
            return False
        return False

    def is_valid_wall(self, wall):
        r, c, orient = wall
        # Must fit inside grooves
        if not (0 <= r < self.HEIGHT - 1 and 0 <= c < self.WIDTH - 1):
            return False
        # No overlap or cross
        if (r, c, orient) in self.walls:
            return False
        if orient == 'H' and (r, c, 'V') in self.walls:
            return False
        if orient == 'V' and (r, c, 'H') in self.walls:
            return False
        # No partial overlap of the two‐segment span
        if orient == 'H':
            for dc in (-1, 1):
                if (r, c + dc, 'H') in self.walls:
                    return False
        else:  # orient == 'V'
            for dr in (-1, 1):
                if (r + dr, c, 'V') in self.walls:
                    return False

        # Must not cut off any path
        self.walls.add(wall)
        ok = self._path_exists(0) and self._path_exists(1)
        self.walls.remove(wall)
        return ok

    def _path_exists(self, player):
        start = self.pawns[player]
        goal_rows = {0} if player == 0 else {self.HEIGHT - 1}
        visited = {start}
        dq = deque([start])
        while dq:
            r, c = dq.popleft()
            if r in goal_rows:
                return True
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if not self._in_bounds(nr, nc) or (nr, nc) in visited:
                    continue
                if self._is_blocked((r, c), (nr, nc)):
                    continue
                visited.add((nr, nc))
                dq.append((nr, nc))
        return False

    def shortest_path_length(self, player):
        start = self.pawns[player]
        goal_rows = {0} if player == 0 else {self.HEIGHT - 1}
        visited = {start: 0}
        dq = deque([start])
        while dq:
            r, c = dq.popleft()
            d = visited[(r, c)]
            if r in goal_rows:
                return d
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if not self._in_bounds(nr, nc) or (nr, nc) in visited:
                    continue
                if self._is_blocked((r, c), (nr, nc)):
                    continue
                visited[(nr, nc)] = d + 1
                dq.append((nr, nc))
        return float('inf')

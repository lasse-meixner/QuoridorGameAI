import math
import random
from game_state import GameState

class MinimaxAI:
    def __init__(self, depth=4):
        # `depth` now serves as your base depth (used when many walls remain)
        self.depth = depth
        H, W = GameState.HEIGHT, GameState.WIDTH

        # ── Zobrist keys ──────────────────────────────────────────────
        self.pawns_z = [
            [[random.getrandbits(64) for _ in range(W)] for _ in range(H)]
            for _ in range(2)
        ]
        self.walls_z = {}
        for r in range(H-1):
            for c in range(W-1):
                self.walls_z[(r, c, 'H')] = random.getrandbits(64)
                self.walls_z[(r, c, 'V')] = random.getrandbits(64)
        self.player_z = random.getrandbits(64)

        # transposition table
        self.tt = {}

    def hash_state(self, state: GameState):
        h = 0
        for p in (0, 1):
            r, c = state.pawns[p]
            h ^= self.pawns_z[p][r][c]
        for wall in state.walls:
            h ^= self.walls_z[wall]
        if state.current_player == 1:
            h ^= self.player_z
        return h

    def choose_move(self, state: GameState):
        # ── Adaptive depth based on walls remaining ───────────────
        total_walls = sum(state.walls_remaining)
        if total_walls < 6:
            depth_limit = 6
        elif total_walls < 10:
            depth_limit = 5
        else:
            depth_limit = self.depth
        # ───────────────────────────────────────────────────────────

        # clear TT per search
        self.tt.clear()

        root_player = state.current_player
        root_dist   = state.shortest_path_length(root_player)
        eps         = 1e-3

        # static lateral-preference at root
        pref = {
            ('pawn', 0, -1): 0,
            ('pawn', -1, 0): 1,
            ('pawn', 0,  1): 2,
            ('pawn', 1,  0): 3,
        }
        def rank(m): return pref.get(m, 10)

        def minimax(node, depth, alpha, beta, maximizing, is_root=False):
            # TT lookup
            key = (self.hash_state(node), depth, maximizing)
            if key in self.tt:
                return self.tt[key]

            # leaf or terminal
            if depth == 0 or node.is_game_over():
                my   = node.shortest_path_length(root_player)
                opp  = node.shortest_path_length(1 - root_player)
                base = opp - my
                prog = root_dist - my
                val  = base + eps * prog
                self.tt[key] = (val, None)
                return val, None

            if maximizing:
                best_val, best_mv = -math.inf, None
                moves = node.get_legal_moves()
                if is_root:
                    moves = sorted(moves, key=rank)
                for mv in moves:
                    child = node.clone()
                    child.apply_move(mv)
                    v, _ = minimax(child, depth-1, alpha, beta, False, False)
                    if v > best_val:
                        best_val, best_mv = v, mv
                    alpha = max(alpha, v)
                    if beta <= alpha:
                        break
                self.tt[key] = (best_val, best_mv)
                return best_val, best_mv
            else:
                worst_val, worst_mv = math.inf, None
                for mv in node.get_legal_moves():
                    child = node.clone()
                    child.apply_move(mv)
                    v, _ = minimax(child, depth-1, alpha, beta, True, False)
                    if v < worst_val:
                        worst_val, worst_mv = v, mv
                    beta = min(beta, v)
                    if beta <= alpha:
                        break
                self.tt[key] = (worst_val, worst_mv)
                return worst_val, worst_mv

        # single α–β call with adaptive depth
        _, move = minimax(state.clone(), depth_limit, -math.inf, math.inf, True, True)
        return move

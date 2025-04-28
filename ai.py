import math
from game_state import GameState

class MinimaxAI:
    def __init__(self, depth=3):
        self.depth = depth

    def choose_move(self, state: GameState):
        # Remember root info for leaf‐node heuristic
        root_player = state.current_player
        root_dist   = state.shortest_path_length(root_player)
        eps         = 1e-3

        # Static lateral‐preference ordering for root‐moves
        pref_order = {
            ('pawn', 0, -1): 0,   # left
            ('pawn', -1, 0): 1,   # up
            ('pawn', 0,  1): 2,   # right
            ('pawn', 1,  0): 3    # down
        }
        def rank(move):
            # walls get lowest priority (10)
            return pref_order.get(move, 10)

        def minimax(node, depth, alpha, beta, maximizing, is_root=False):
            # Leaf or terminal
            if depth == 0 or node.is_game_over():
                my   = node.shortest_path_length(root_player)
                opp  = node.shortest_path_length(1 - root_player)
                base = opp - my
                prog = root_dist - my
                return base + eps * prog, None

            if maximizing:
                best_val, best_mv = -math.inf, None
                # Single pass over root‐moves, ordered if is_root
                moves = node.get_legal_moves()
                if is_root:
                    moves = sorted(moves, key=rank)
                for mv in moves:
                    child = node.clone()
                    child.apply_move(mv)
                    val, _ = minimax(child, depth-1, alpha, beta, False, False)
                    if val > best_val:
                        best_val, best_mv = val, mv
                    alpha = max(alpha, val)
                    if beta <= alpha:
                        break
                return best_val, best_mv
            else:
                worst_val, worst_mv = math.inf, None
                for mv in node.get_legal_moves():
                    child = node.clone()
                    child.apply_move(mv)
                    val, _ = minimax(child, depth-1, alpha, beta, True, False)
                    if val < worst_val:
                        worst_val, worst_mv = val, mv
                    beta = min(beta, val)
                    if beta <= alpha:
                        break
                return worst_val, worst_mv

        # Single α–β call: root pass will apply our tie‐break ordering
        _, move = minimax(state.clone(), self.depth, -math.inf, math.inf, True, True)
        return move

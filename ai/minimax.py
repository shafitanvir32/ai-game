"""
ai/minimax.py
=============

Depth-limited minimax with alpha–beta pruning *and* a safeguard that prevents
the search from declaring a winner before both colours have appeared on the
board.

Key points
----------
* `started` flag (bool) tells the search whether *both* Red and Blue have ever
  had at least one orb.  Only after that may we treat “no Blues” or “no Reds”
  as a terminal win.
* Always returns **a legal move**.  If, for any reason, the search cannot find
  one (rare corner cases at depth 0), the caller should fall back to a random
  move—`main.py` already does this for you in `ai_move()`.
"""
from __future__ import annotations
import math, time
from typing import Callable, Tuple, Optional

from core.board import Board, RED, BLUE


def minimax(
    board: Board,
    depth: int,
    player: int,
    eval_fn: Callable[[Board, int], float],
    started: bool,
    alpha: float = -math.inf,
    beta: float = math.inf,
    start_time: Optional[float] = None,
    time_limit: Optional[float] = None,
) -> Tuple[float, Optional[tuple[int, int]]]:
    """
    Parameters
    ----------
    board      : current position (immutable Board)
    depth      : ply to search (0 = evaluate leaf)
    player     : id of the side to move (RED = 0, BLUE = 1)
    eval_fn    : heuristic(board, player) → float
    started    : **True once both colours have appeared at least once**
    alpha/beta : usual α-β window (maximiser’s perspective)
    start_time : wall-clock at root (for optional time_limit)
    time_limit : in seconds; None → ignore

    Returns
    -------
    (score, best_move)
      best_move is (row, col) or None at terminal nodes
    """
    if start_time is None:
        start_time = time.perf_counter()

    # --- Terminal tests ---------------------------------------------------
    winner = board.winner() if started else None
    if winner is not None:
        score = math.inf if winner == player else -math.inf
        return score, None

    if depth == 0 or (time_limit and time.perf_counter() - start_time > time_limit):
        return eval_fn(board, player), None

    # --- Search -----------------------------------------------------------
    best_val: float = -math.inf
    best_move: Optional[tuple[int, int]] = None

    for move in board.legal_moves(player):
        child = board.place(player, move)

        # Has the game 'officially' started in this subtree?
        child_started = started or (child.has_player(RED) and child.has_player(BLUE))

        val, _ = minimax(
            child,
            depth - 1,
            1 - player,          # opponent’s turn
            eval_fn,
            child_started,
            -beta,               # note: Negamax style
            -alpha,
            start_time,
            time_limit,
        )
        val = -val               # back to our perspective

        if val > best_val:
            best_val, best_move = val, move
        alpha = max(alpha, val)
        if alpha >= beta:        # β-cutoff
            break

    return best_val, best_move

"""
ai/heuristics.py
----------------
Five evaluation functions the minimax agent can choose from.
"""

from core.board import Board, RED, BLUE, CRITS


def orb_difference(b: Board, p: int) -> float:
    """Simple material balance (your orbs – opponent’s)."""
    return b.score(p) - b.score(1 - p)


def weighted_orb(b: Board, p: int) -> float:
    """
    Give extra weight to safer squares (corners / edges).

    • Corners: weight 3   (critical-mass 2 → 5-2 = 3)  
    • Edges:   weight 2   (critical-mass 3 → 5-3 = 2)  
    • Centers: weight 1   (critical-mass 4 → 5-4 = 1)
    """
    score = 0
    for r, row in enumerate(b.grid):
        for c, cell in enumerate(row):
            w = 5 - CRITS[r][c]          # compute once, use for both colours
            if cell.owner == p:
                score += cell.count * w
            elif cell.owner == 1 - p:
                score -= cell.count * w
    return score


def frontier(b: Board, p: int) -> float:
    """Net frontier advantage for ``p``.

    Each border between adjacent cells is considered exactly once by only
    looking to the right and down.  Borders with empty cells are ignored.
    """

    rows, cols = len(b.grid), len(b.grid[0])
    f = 0
    for r, row in enumerate(b.grid):
        for c, cell in enumerate(row):
            for dr, dc in ((1, 0), (0, 1)):  # count each shared edge once
                nr, nc = r + dr, c + dc
                if nr >= rows or nc >= cols:
                    continue
                n_owner = b.grid[nr][nc].owner
                # only count borders where the players face each other
                if cell.owner == p and n_owner == 1 - p:
                    f += 1
                elif cell.owner == 1 - p and n_owner == p:
                    f -= 1
    return f


def mobility(b: Board, p: int) -> float:
    """How many legal moves you have versus the opponent."""
    return len(b.legal_moves(p)) - len(b.legal_moves(1 - p))


def imminent_explosions(b: Board, p: int) -> float:
    """
    Prefer cells that are close to exploding while penalising the opponent’s.

    A cell that needs `need` more orbs contributes ±(4/need).  The smaller
    `need`, the larger the magnitude.
    """
    val = 0
    for r, row in enumerate(b.grid):
        for c, cell in enumerate(row):
            need = CRITS[r][c] - cell.count  # 1 ≤ need ≤ 4  (board is stable)
            if cell.owner == p:
                val += 4 / need
            elif cell.owner == 1 - p:
                val -= 4 / need
    return val


# registry
HEURISTICS = {
    "difference": orb_difference,
    "weighted": weighted_orb,
    "frontier": frontier,
    "mobility": mobility,
    "imminent": imminent_explosions,
}

DEFAULT = "weighted"

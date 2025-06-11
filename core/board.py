from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional

ROWS, COLS = 9, 6
RED, BLUE, EMPTY = 0, 1, -1   # player ids

# Pre-compute critical mass for every cell (orthogonal neighbours)
CRITS = [[4]*COLS for _ in range(ROWS)]
for r in range(ROWS):
    for c in range(COLS):
        neighbours = 4 - (r in (0, ROWS-1)) - (c in (0, COLS-1))
        CRITS[r][c] = neighbours

@dataclass(frozen=True, slots=True)
class Cell:
    owner: int   # -1 for empty, 0 red, 1 blue
    count: int   # number of stacked orbs

@dataclass(frozen=True, slots=True)
class Board:
    grid: Tuple[Tuple[Cell, ...], ...]   # immutable 2-D tuple

    # -------- construction helpers -------- #
    @staticmethod
    def empty() -> "Board":
        g = tuple(tuple(Cell(EMPTY, 0) for _ in range(COLS)) for _ in range(ROWS))
        return Board(g)

    def copy_mutable(self):
        return [[Cell(c.owner, c.count) for c in row] for row in self.grid]

    # -------- game rules -------- #
    def legal_moves(self, player: int) -> List[Tuple[int, int]]:
        moves = []
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                if cell.owner in (player, EMPTY):
                    moves.append((r, c))
        return moves

    def place(self, player: int, rc: Tuple[int, int]) -> "Board":
        r, c = rc
        g = self.copy_mutable()
        # add orb
        cell = g[r][c]
        g[r][c] = Cell(player, cell.count + 1)
        # resolve chain reactions
        changed = True
        while changed:
            changed = False
            for rr in range(ROWS):
                for cc in range(COLS):
                    cell = g[rr][cc]
                    if cell.count >= CRITS[rr][cc] and cell.owner != EMPTY:
                        # explode
                        changed = True
                        owner = cell.owner
                        g[rr][cc] = Cell(EMPTY, 0)
                        for dr, dc in ((1,0), (-1,0), (0,1), (0,-1)):
                            nr, nc = rr+dr, cc+dc
                            if 0 <= nr < ROWS and 0 <= nc < COLS:
                                ncell = g[nr][nc]
                                g[nr][nc] = Cell(owner, ncell.count+1)
        # freeze immutable
        return Board(tuple(tuple(row) for row in g))

    def score(self, player: int) -> int:
        return sum(c.count for row in self.grid for c in row if c.owner == player)

    def has_player(self, player: int) -> bool:
        return any(c.owner == player for row in self.grid for c in row)

    def winner(self) -> Optional[int]:
        """Return RED or BLUE when only one colour is left; otherwise None."""
        red  = self.has_player(RED)
        blue = self.has_player(BLUE)
        if red and not blue:
            return RED
        if blue and not red:
            return BLUE
        return None          # either both colours present, or board empty

import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai.heuristics import orb_difference, frontier
from core.board import Board, Cell, RED, BLUE, EMPTY, ROWS, COLS


def make_board(mapping):
    """Return a Board with specific cells set.

    mapping maps (r, c) -> (owner, count).
    """
    grid = [[Cell(EMPTY, 0) for _ in range(COLS)] for _ in range(ROWS)]
    for (r, c), (owner, count) in mapping.items():
        grid[r][c] = Cell(owner, count)
    return Board(tuple(tuple(row) for row in grid))


def test_orb_difference_positive_negative():
    board = make_board({(0, 0): (RED, 2), (0, 1): (BLUE, 1)})
    assert orb_difference(board, RED) == 1
    assert orb_difference(board, BLUE) == -1


def test_frontier_negative_for_red_positive_for_blue():
    board = make_board({(0, 0): (RED, 1), (0, 1): (BLUE, 1), (1, 0): (BLUE, 1)})
    assert frontier(board, RED) == -1
    assert frontier(board, BLUE) == 1


def test_frontier_positive_for_red_negative_for_blue():
    board = make_board({(0, 0): (BLUE, 1), (0, 1): (RED, 1), (1, 0): (RED, 1)})
    assert frontier(board, RED) == 1
    assert frontier(board, BLUE) == -1

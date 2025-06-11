#!/usr/bin/env python3
"""
main.py  –  Chain-Reaction driver with a *background* AI thread

• Human-v-AI, AI-v-AI, tournaments, CSV logging – all still supported.
• No “Not Responding” any more: the search runs in a separate thread while
  the main thread keeps pumping Pygame events and redrawing the board.
• Thread uses Python’s `queue.Queue` for a clean hand-off of the chosen move.
"""
from __future__ import annotations
import argparse, csv, random, threading, queue, sys
from pathlib import Path

import pygame

from core.board import Board, RED, BLUE
from ai.minimax import minimax
from ai.heuristics import HEURISTICS, DEFAULT
from ui.pygame_view import PygameView


# ---------------------------------------------------------------------- #
# CLI                                                                     #
# ---------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--ai-depth", type=int, default=3,
                   help="search depth – ignored if --time-limit is given")
    p.add_argument("--time-limit", type=float, default=None,
                   help="seconds the AI may think per move "
                        "(enables iterative deepening)")
    p.add_argument("--heuristic", choices=HEURISTICS, default=DEFAULT)
    p.add_argument("--ai-vs-ai", action="store_true",
                   help="blue is AI too (for tournaments)")
    p.add_argument("--games", type=int, default=1,
                   help="number of consecutive games")
    p.add_argument("--csv", type=Path, help="write results to CSV")
    return p.parse_args()


# ---------------------------------------------------------------------- #
# Background worker                                                      #
# ---------------------------------------------------------------------- #
def _worker(board: Board,
            player: int,
            depth: int,
            hname: str,
            started: bool,
            time_limit: float | None,
            out: "queue.Queue[tuple[int,int]]",
            ) -> None:
    """
    Runs in a background **thread**.
    Computes the best move and puts it in `out`.
    """
    _, move = minimax(board, depth, player,
                      HEURISTICS[hname], started,
                      time_limit=time_limit)
    out.put(move)


def ai_move_threaded(board: Board,
                     player: int,
                     depth: int,
                     hname: str,
                     started: bool,
                     time_limit: float | None,
                     ui: PygameView) -> tuple[int, int]:
    """
    Runs minimax in a background thread *but* never waits more than
    MAX_WALL_TIME seconds.  If that limit is exceeded we immediately
    fall back to a random legal move so the game never stalls.
    """
    MAX_WALL_TIME = 5.0          # ← hard ceiling in seconds

    q: "queue.Queue[tuple[int,int]]" = queue.Queue(maxsize=1)
    th = threading.Thread(target=_worker,
                          args=(board, player, depth, hname,
                                started, time_limit, q),
                          daemon=True)
    th.start()

    start_ms = pygame.time.get_ticks()
    while th.is_alive():
        ui.draw_board(board, player, "AI thinking…  (Esc to quit)")

        # pump events so the window stays responsive
        for e in pygame.event.get():
            if e.type == pygame.QUIT \
               or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        ui.clock.tick(60)

        # ---- PANIC TIMER ----------------------------------------------
        elapsed = (pygame.time.get_ticks() - start_ms) / 1000.0
        if elapsed > MAX_WALL_TIME:
            print("⚠️  AI exceeded hard wall-time; using fallback move.")
            # detach the worker (it will finish in background, then die)
            th.join(timeout=0)
            return random.choice(board.legal_moves(player))

    # normal case: thread finished in time
    move = q.get()
    return move


# ---------------------------------------------------------------------- #
# Single game loop                                                       #
# ---------------------------------------------------------------------- #
def run_game(args: argparse.Namespace,
             gnum: int = 0,
             csv_writer: csv.writer | None = None) -> int:
    board = Board.empty()
    ui = PygameView(f"Chain Reaction – game {gnum + 1}")
    turn: int = RED                    # red starts (human or AI)
    both_seen = False                  # becomes True once red & blue exist

    while True:
        # --- draw current position ---------------------------------------
        ui.draw_board(board, turn)

        # --- victory check -----------------------------------------------
        winner = board.winner() if both_seen else None
        if winner is not None:
            ui.draw_board(board, turn,
                          "Red wins!" if winner == RED else "Blue wins!")
            if csv_writer:
                csv_writer.writerow([gnum + 1, winner,
                                     board.score(RED), board.score(BLUE)])
            # wait 2 s then quit (or Esc)
            pygame.time.wait(2000)
            return winner

        # --- play the turn -----------------------------------------------
        if turn == RED and not args.ai_vs_ai:
            # Human input
            while True:
                r, c = ui.wait_click()
                if (r, c) in board.legal_moves(RED):
                    break              # legal
            board = board.place(RED, (r, c))

        else:
            # AI – run in background thread
            move = ai_move_threaded(board, turn,
                                    args.ai_depth, args.heuristic,
                                    both_seen, args.time_limit, ui)
            board = board.place(turn, move)

        # --- update flags & switch turn ----------------------------------
        if board.has_player(RED) and board.has_player(BLUE):
            both_seen = True
        turn = 1 - turn


# ---------------------------------------------------------------------- #
# Driver                                                                 #
# ---------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()

    # CSV?
    csv_file = args.csv.open("w", newline="") if args.csv else None
    csv_writer = csv.writer(csv_file) if csv_file else None
    if csv_writer:
        csv_writer.writerow(["game", "winner", "red_orbs", "blue_orbs"])

    for g in range(args.games):
        run_game(args, g, csv_writer)

    if csv_file:
        csv_file.close()


if __name__ == "__main__":
    main()

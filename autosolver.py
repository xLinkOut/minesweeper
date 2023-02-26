#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from argparse import ArgumentParser
from random import randint

from minesweeper import MinesweeperTk


class AutoSolver:
    def __init__(self, game: MinesweeperTk, debug: bool = False):
        self.game: MinesweeperTk = game
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        self.logger = logging.getLogger("AutoSolver")

    class FakeEvent:
        """Fake event class for the button click event.
        Instead of using some kind of hacky-way to interact with the
        Tkinter GUI, here we mock the event object that is passed to
        the callback function of the button click event.
        """

        def __init__(self, button):
            self.widget: MinesweeperTk.CellButton = button

    def _first_move(self):
        last_index: int = self.game.rows * self.game.columns - 1
        cell: MinesweeperTk.CellButton = self.game.game_grid[randint(0, last_index)]
        self.game.open_cell(self.FakeEvent(cell))
        self.logger.info(f"First move: {cell}")

    def _flag_cells(self):
        """Scan game grid to find cells that are safe to flag.

        If a cell has the same number of nearby mines as the number of
        unopened cells around it, then all of those cells need to be flagged.
        """

        for cell in self.game.game_grid:
            # Game is finished, no need to continue (recursion safe)
            if self.game.finished:
                break

            # Skip cells that are not opened
            if not cell.is_opened:
                continue

            # Skip cells that are flagged
            if cell.is_flagged:
                continue

            # Find nearby cells that are not opened
            nearby_closed_cells = [
                self.game.game_grid[coords[0] * self.game.columns + coords[1]]
                for coords in self.game.get_nearby_cells_coords(cell.row, cell.column)
                if not self.game.game_grid[coords[0] * self.game.columns + coords[1]].is_opened
            ]

            if cell.nearby_mines == len(nearby_closed_cells):
                for nearby_closed_cell in nearby_closed_cells:
                    if not nearby_closed_cell.is_flagged:
                        self.game.put_flag(self.FakeEvent(nearby_closed_cell))
                        self.logger.info(f"Flagged cell: {nearby_closed_cell}")

    def solve(self):
        # First move
        self._first_move()

        # While the game is not finished
        while not self.game.finished:
            self._flag_cells()


if __name__ == "__main__":
    parser = ArgumentParser(description="Minesweeper game")

    grid_size = parser.add_argument_group("Grid size")
    grid_size.add_argument(
        "-d",
        "--difficulty",
        type=str,
        choices=["beginner", "intermediate", "expert"],
        help="Game difficulty",
    )

    custom_grid = parser.add_argument_group("Custom grid")
    custom_grid.add_argument(
        "-r",
        "--rows",
        type=int,
        help="Number of rows in the game grid",
    )
    custom_grid.add_argument(
        "-c",
        "--columns",
        type=int,
        help="Number of columns in the game grid",
    )
    custom_grid.add_argument(
        "-m",
        "--mines",
        type=int,
        help="Number of mines in the game grid",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode",
    )

    args = parser.parse_args()

    # Check on arguments
    if not args.difficulty and not args.rows and not args.columns and not args.mines:
        parser.error("No arguments provided")

    if args.difficulty and (args.rows or args.columns or args.mines):
        parser.error("Cannot use difficulty and custom mode at the same time")

    if not args.difficulty and (args.rows <= 0 or args.columns <= 0 or args.mines <= 0):
        parser.error("Invalid number of rows, columns or mines")

    if not args.difficulty and (args.mines >= args.rows * args.columns):
        parser.error("Number of mines must be less than number of cells")

    # Create a window with Tkinter
    game = MinesweeperTk(
        difficulty=args.difficulty,
        rows=args.rows,
        columns=args.columns,
        mines=args.mines,
        debug=args.debug,
    )

    autosolver = AutoSolver(game=game, debug=args.debug)
    autosolver.solve()

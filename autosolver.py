#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from argparse import ArgumentParser
from random import randint, choice

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
        self.logger.debug(f"First move: {cell}")

    def _random_move(self):
        self.logger.info("Using random move")
        cell = choice([cell for cell in self.game.game_grid if not cell.is_opened and not cell.is_flagged])
        self.game.open_cell(self.FakeEvent(cell))
        self.logger.debug(f"Random move: {cell}")

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
                nearby_cell
                for nearby_cell in cell.neighbors
                if not nearby_cell.is_opened
            ]

            if cell.nearby_mines == len(nearby_closed_cells):
                for nearby_closed_cell in nearby_closed_cells:
                    if not nearby_closed_cell.is_flagged:
                        self.game.put_flag(self.FakeEvent(nearby_closed_cell))
                        self.logger.debug(f"Flagged cell: {nearby_closed_cell}")

    def _open_cells(self):
        """Scan game grid to find cells that are safe to be opened.

        If a cell has the same number of nearby mines as the number of flagged cells around it,
        then all of those cells are safe to be opened.
        """

        for cell in self.game.game_grid:
            # Game is finished, no need to continue (recursion safe)
            if self.game.finished:
                break

            # Skip cells that are not opened or flagged
            if not cell.is_opened or cell.is_flagged:
                continue

            # Find nearby cells that are flagged
            nearby_flagged_cells = [
                nearby_cell
                for nearby_cell in cell.neighbors
                if nearby_cell.is_flagged
            ]

            # Skip cells that do not have the same number of nearby mines
            # as the number of nearby flagged cells
            if cell.nearby_mines != len(nearby_flagged_cells):
                continue

            # Open all nearby cells that are not flagged and not opened
            for nearby_cell in cell.neighbors:
                if not nearby_cell.is_opened and not nearby_cell.is_flagged:
                    self.game.open_cell(self.FakeEvent(nearby_cell))
                    self.logger.debug(f"Opened cell: {nearby_cell}")

    def _count_opened_or_flagged_cells(self) -> int:
        """Count the number of opened or flagged cells in the game grid."""

        return sum(1 for cell in self.game.game_grid if cell.is_opened or cell.is_flagged)

    def _sets_strategy(self):
        """Use mathematical sets-based strategy to overcome difficult situation."""

        self.game.update()
        self.logger.info("Using sets strategy")
        did_something = False

        # For each pair of cells in the game grid
        for (cell_a, cell_b) in [pair for pair in zip(self.game.game_grid, self.game.game_grid[1:])]:
            # Game is finished, no need to continue (recursion safe)
            if self.game.finished:
                break

            # Skip pairs where cells:
            # - are not both opened
            # - at least one them is flagged
            # - at least one of them has no nearby mines
            if (
                (not (cell_a.is_opened and cell_b.is_opened)) or
                (cell_a.is_flagged or cell_b.is_flagged) or
                (cell_a.nearby_mines == 0 or cell_b.nearby_mines == 0)
            ):
                continue

            # Swap cells if cell_b has more nearby mines than cell_a
            if cell_a.nearby_mines < cell_b.nearby_mines:
                cell_a, cell_b = cell_b, cell_a

            # Non flagged (and not opened) nearby cells of cell_a
            nfn_a = [
                nearby_cell
                for nearby_cell in cell_a.neighbors
                if not nearby_cell.is_flagged and not nearby_cell.is_opened
            ]

            # Non flagged (and not opened) nearby cells of cell_b
            nfn_b = [
                nearby_cell
                for nearby_cell in cell_b.neighbors
                if not nearby_cell.is_flagged and not nearby_cell.is_opened
            ]

            # Recalculate nearby mines of cell_a and cell_b subtracting the number of nearby
            # flagged cells
            nearby_mines_a = cell_a.nearby_mines - sum(
                1 for cell in cell_a.neighbors if cell.is_flagged
            )
            nearby_mines_b = cell_b.nearby_mines - sum(
                1 for cell in cell_b.neighbors if cell.is_flagged
            )

            # If the difference between the number of nearby mines of cell_a and cell_b
            # is equal to the size of the difference between the sets of non flagged nearby
            # cells of cell_a and cell_b, then:
            # - flag all cells in the difference between the sets of nfn_a and nfn_b
            # - open all cells in the difference between the sets of nfn_b and nfn_a
            
            nfn_a_difference_nfn_b = set(nfn_a).difference(set(nfn_b))
            nfn_b_difference_nfn_a = set(nfn_b).difference(set(nfn_a))

            if nearby_mines_a - nearby_mines_b == len(nfn_a_difference_nfn_b):
                for cell in nfn_a_difference_nfn_b:
                    did_something = True
                    self.game.put_flag(self.FakeEvent(cell))
                    self.logger.debug(f"Flagged cell: {cell}")

                for cell in nfn_b_difference_nfn_a:
                    did_something = True
                    self.game.open_cell(self.FakeEvent(cell))
                    self.logger.debug(f"Opened cell: {cell}")
        
        if did_something:
            self.game.update()
            self.logger.info("Sets strategy did something!")
        return did_something

    def solve(self):
        # First move
        self._first_move()

        # Track number of opened or flagged cells
        # so we can detect when the game is stuck
        opened_or_flagged_cells = self._count_opened_or_flagged_cells()

        # While the game is not finished
        while not self.game.finished:
            self._flag_cells()
            self.game.update()
            self._open_cells()
            self.game.update()

            # Check if the game is stuck
            if opened_or_flagged_cells == self._count_opened_or_flagged_cells():
                self.logger.warning("Game is stuck, using another strategy")
                if not self._sets_strategy():
                    self.logger.warning("Game is stuck, random move")
                    self._random_move()

            # Update number of opened or flagged cells
            opened_or_flagged_cells = self._count_opened_or_flagged_cells()


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

    parser.add_argument(
        "-n",
        type=int,
        default=1,
        help="Number of games to play",
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

    if args.n <= 0:
        parser.error("Invalid number of games")

    for i in range(args.n):
        # Create a window with Tkinter
        game = MinesweeperTk(
            difficulty=args.difficulty,
            rows=args.rows,
            columns=args.columns,
            mines=args.mines,
            debug=args.debug,
            non_interactive=True,
        )

        autosolver = AutoSolver(game=game, debug=args.debug)
        autosolver.solve()

        game.destroy()

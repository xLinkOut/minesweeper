#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from argparse import ArgumentParser
from random import choice

from minesweeper import MinesweeperTk


class AutoSolver:
    """AutoSolver class for the Minesweeper game.

    The AutoSolver tries to solve the game by using a combination of strategies.

    A bit of terminology:
        - a 'cell' is a button in the game grid.;
        - each cell has 8 'nearby cells' (or neighbors) in its 3x3 grid;
        - consequentially, a 'nearby cell' is a cell that is adjacent to (touch) another cell.
        - a cell is 'opened' if the user (or the AutoSolver) 'step' on it;
        - a cell is 'flagged' if there is a flag on it, and can't be opened (until is 'unflagged');
        - a cell is 'closed' if it is not opened and not flagged;
        - a cell value is the number ([0, 8]) of nearby mines, that is the number of nearby cells
            that are mines, and is only visible after the cell is opened;
        - a cell is 'safe to be opened' if it is closed and it is 'completed', that is, if it has
            the same number of nearby mines (its value) as the number of nearby flagged cells;

    After the first move, the AutoSolver will use the following strategies:
        * Scan the game grid to find cells that are safe to flag
        * Scan the game grid to find cells that are safe to be opened
        * Repeat the above two strategies until grid is completed or a deadlock is reached
        * If a deadlock is reached, use a mathematical sets-based strategy to solve the situation.
        * If neither of the above strategies can solve the game, use a random move and hope for the best.

    Those strategies are based on the two following observation:
        1. If a cell has the same number of nearby mines as the number of closed cells around it,
            then all of those cells need to be flagged. In other words, if a cell’s value equals its
            neighbors count, those neighbors are mines. E.g.: if a cell has value 3, and there are 3
            closed cells around it, then all of those cells need to be flagged.
        2. If a cell has the same number of nearby mines as the number of flagged cells around it,
            then all of those cells are safe to be opened. In other words, if a cell’s value equals
            its flagged neighbors count, those neighbors are safe to be opened. E.g.: if a cell has
            value 3, and there are 3 flagged cells around it, then all the other nearby cells are
            safe to be opened.
    """

    class FakeEvent:
        """Fake event class for the button click event.
        Instead of using some kind of hacky-way to interact with the
        Tkinter GUI, here we mock the event object that is passed to
        the callback function of the button click event.
        """

        def __init__(self, button: MinesweeperTk.CellButton):
            self.widget: MinesweeperTk.CellButton = button

    def __init__(self, game: MinesweeperTk, debug: bool = False):
        """Constructor for the AutoSolver class.

        Args:
            game (MinesweeperTk): a Minesweeper game instance.
            debug (bool, optional): toggle debug mode. Defaults to False.
        """

        self.game: MinesweeperTk = game
        self.debug: bool = debug

        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        self.logger = logging.getLogger("AutoSolver")

    def _count_opened_or_flagged_cells(self) -> int:
        """Count the number of opened or flagged cells in the game grid.

        Used to check if from the last move the game grid has changed.
        """

        return sum(1 for cell in self.game.game_grid if cell.is_opened or cell.is_flagged)

    def _open_random_cell(self):
        """Open a random cell.

        This is a fallback strategy in case the other strategies fail. Also used
        to start the game, since the first move is always random.
        """

        cell = choice(
            [cell for cell in self.game.game_grid if not cell.is_opened and not cell.is_flagged]
        )
        self.logger.debug(f"open_random_cell: {cell}")
        self.game.open_cell(self.FakeEvent(cell))

    def _flag_cells(self):
        """Scan game grid to find cells that are safe to flag.

        If a cell has the same number of nearby mines as the number of closed cells around it,
        then all of those cells need to be flagged.
        """

        for cell in self.game.game_grid:
            # Game is finished, no need to continue
            if self.game.finished:
                break

            # Skip cells that are not opened or flagged
            if not cell.is_opened or cell.is_flagged:
                continue

            # Find nearby cells that are not opened
            nearby_closed_cells = [
                nearby_cell for nearby_cell in cell.neighbors if not nearby_cell.is_opened
            ]

            # Skip cells that do not have the same number of nearby mines
            # as the number of nearby closed cells
            if cell.nearby_mines != len(nearby_closed_cells):
                continue

            # Flag all the nearby cells that are not already flagged
            for nearby_closed_cell in nearby_closed_cells:
                if not nearby_closed_cell.is_flagged:
                    self.logger.debug(f"flag_cells: {nearby_closed_cell}")
                    self.game.put_flag(self.FakeEvent(nearby_closed_cell))

    def _open_cells(self):
        """Scan game grid to find cells that are safe to be opened.

        If a cell has the same number of nearby mines as the number of flagged cells around it,
        then all the other cells are safe to be opened.
        """

        for cell in self.game.game_grid:
            # Game is finished, no need to continue
            if self.game.finished:
                break

            # Skip cells that are not opened or flagged
            if not cell.is_opened or cell.is_flagged:
                continue

            # Find nearby cells that are flagged
            nearby_flagged_cells = [
                nearby_cell for nearby_cell in cell.neighbors if nearby_cell.is_flagged
            ]

            # Skip cells that do not have the same number of nearby mines
            # as the number of nearby flagged cells
            if cell.nearby_mines != len(nearby_flagged_cells):
                continue

            # Open all the nearby cells that are closed and not flagged
            for nearby_cell in cell.neighbors:
                if not nearby_cell.is_opened and not nearby_cell.is_flagged:
                    self.logger.debug(f"open_cells: {nearby_cell}")
                    self.game.open_cell(self.FakeEvent(nearby_cell))

    def _sets_strategy(self):
        """Use mathematical sets-based strategy to overcome difficult situation."""

        did_something = False

        cell_pairs: list[tuple[self.game.CellButton, self.game.CellButton]] = [
            pair for pair in zip(self.game.game_grid, self.game.game_grid[1:])
        ]

        # For each pair of cells in the game grid
        for (cell_a, cell_b) in cell_pairs:
            # Game is finished, no need to continue
            if self.game.finished:
                break

            # Skip pairs where cells:
            # - are not both opened
            # - at least one them is flagged
            # - at least one of them has no nearby mines
            if (
                (not (cell_a.is_opened and cell_b.is_opened))
                or (cell_a.is_flagged or cell_b.is_flagged)
                or (cell_a.nearby_mines == 0 or cell_b.nearby_mines == 0)
            ):
                continue

            # Swap cells if cell_b has more nearby mines than cell_a
            if cell_a.nearby_mines < cell_b.nearby_mines:
                cell_a, cell_b = cell_b, cell_a

            # Recalculate nearby mines value of both cells, subtracting the number of nearby
            # flagged cells
            nearby_mines_a: int = cell_a.nearby_mines - sum(
                1 for cell in cell_a.neighbors if cell.is_flagged
            )
            nearby_mines_b: int = cell_b.nearby_mines - sum(
                1 for cell in cell_b.neighbors if cell.is_flagged
            )

            # If, after the subtraction, both cells have no nearby mines, skip the pair
            if nearby_mines_a == 0 and nearby_mines_b == 0:
                continue

            # Nearby cells of cell_a that are not flagged and not opened (nfn_a)
            non_flagged_neighbors_a: set[self.game.CellButton] = {
                nearby_cell
                for nearby_cell in cell_a.neighbors
                if not nearby_cell.is_flagged and not nearby_cell.is_opened
            }

            # Nearby cells of cell_b that are not flagged and not opened (nfn_b)
            non_flagged_neighbors_b: set[self.game.CellButton] = {
                nearby_cell
                for nearby_cell in cell_b.neighbors
                if not nearby_cell.is_flagged and not nearby_cell.is_opened
            }

            # If nfn_a and nfn_b are equal, skip the pair
            if non_flagged_neighbors_a == non_flagged_neighbors_b:
                continue

            # If the difference between the number of nearby mines of cell_a and cell_b is equal to
            # the size of the difference between nfn_a and nfn_b (|nfn_a \ nfn_b|), then:
            # - flag all cells in the difference between nfn_a and nfn_b (nfn_a \ nfn_b)
            # - open all cells in the difference between nfn_b and nfn_a (nfn_b \ nfn_a)

            if nearby_mines_a - nearby_mines_b == len(
                non_flagged_neighbors_a.difference(non_flagged_neighbors_b)
            ):

                for cell in non_flagged_neighbors_a.difference(non_flagged_neighbors_b):
                    did_something = True
                    self.logger.debug(f"sets_strategy_flag: {cell}")
                    self.game.put_flag(self.FakeEvent(cell))

                for cell in non_flagged_neighbors_b.difference(non_flagged_neighbors_a):
                    did_something = True
                    self.logger.debug(f"sets_strategy_open: {cell}")
                    self.game.open_cell(self.FakeEvent(cell))

        return did_something

    def solve(self):
        # First move
        self._open_random_cell()

        # Track number of opened or flagged cells
        # so we can detect when the game is stuck
        opened_or_flagged_cells = self._count_opened_or_flagged_cells()

        # While the game is not finished
        while not self.game.finished:
            self._flag_cells()
            if self.debug:
                self.game.update()

            self._open_cells()
            if self.debug:
                self.game.update()

            # Check if the game is stuck
            if opened_or_flagged_cells == self._count_opened_or_flagged_cells():
                self.logger.warning("Game is stuck, using another strategy")
                if not self._sets_strategy():
                    self.logger.warning("Game is stuck, random move")
                    self._open_random_cell()

            # Update number of opened or flagged cells
            opened_or_flagged_cells = self._count_opened_or_flagged_cells()

            if self.debug:
                self.game.update()

        if self.game.won:
            self.logger.info("Game won!")
        else:
            self.logger.info("Game lost!")

        return self.game.won


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

    won_counter: int = 0
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
        if autosolver.solve():
            won_counter += 1

        game.destroy()

    print(f"Games won: {won_counter}/{args.n} ({won_counter/args.n*100:.2f}%)")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import random
import time
import tkinter as tk
import tkinter.messagebox as msgbox
from argparse import ArgumentParser
from typing import Optional

class MinesweeperTk(tk.Tk):
    """Minesweeper game class. Extends tkinter.Tk."""

    # Path to sprites
    SPRITES_PATH: str = os.path.join("sprites", "emoji")
    # Path to icons
    ICON_PATH: str = os.path.join("sprites", "icons")
    # Game difficulty, same as in the original game
    CONFIG: dict[str, dict[str, int]] = {
        "beginner": {"rows": 9, "columns": 9, "mines": 10},
        "intermediate": {"rows": 16, "columns": 16, "mines": 40},
        "expert": {"rows": 16, "columns": 30, "mines": 99},
    }

    class CellButton(tk.Button):
        """Cell button class. Extends tkinter.Button.
        It keeps track of its own coordinates, if it has a mine, if it is opened, if it is flagged
        and how many mines are nearby.

        Args:
            Button (Button): tkinter.Button class
        """

        def __init__(self, master, row: int, column: int, **kwargs):
            super().__init__(master, **kwargs)
            self.row: int = row
            self.column: int = column
            self.has_mine: bool = False
            self.is_opened: bool = False
            self.is_flagged: bool = False
            self.nearby_mines: int = 0
            self.neighbors: list[self.CellButton] = []

        def __str__(self) -> str:
            return (
                f"Cell ({self.row}, {self.column}): "
                f"{self.nearby_mines} mines nearby, "
                f"has mine: {self.has_mine}, "
                f"is opened: {self.is_opened}, "
                f"is flagged: {self.is_flagged}, "
                f"has {len(self.neighbors)} neighbors"
            )

        def __repr__(self) -> str:
            return (
                f"Cell ({self.row}, {self.column}, {self.nearby_mines}, "
                f"{self.has_mine}, {self.is_opened}, {self.is_flagged})"
            )

    def __init__(
        self,
        difficulty: Optional[str] = None,
        rows: Optional[int] = None,
        columns: Optional[int] = None,
        mines: Optional[int] = None,
        debug: bool = False,
        non_interactive: bool = False,
        seed: Optional[int] = None,
    ):
        """Minesweeper game class constructor.

        Args:
            difficulty (Optional[str]): Game difficulty. Can be "beginner", "intermediate" or "expert".
            rows (Optional[int]): Number of rows in the game grid, mutually exclusive with difficulty.
            columns (Optional[int]): Number of columns in the game grid, mutually exclusive with difficulty.
            mines (Optional[int]): Number of mines in the game grid, mutually exclusive with difficulty.
            debug (bool, optional): Enable debug mode. Defaults to False.
        """

        super().__init__()

        # Logger instance
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        self.logger = logging.getLogger("Minesweeper")

        # Parse arguments
        self.logger.debug(f"Arguments: {difficulty}, {rows}, {columns}, {mines}, {debug}")
        self.rows: int = rows or self.CONFIG[difficulty]["rows"]
        self.columns: int = columns or self.CONFIG[difficulty]["columns"]
        self.mines: int = mines or self.CONFIG[difficulty]["mines"]
        self.logger.info(f"Game grid: {self.rows}x{self.columns} with {self.mines} mines")
        self.non_interactive: bool = non_interactive

        # Seed
        if not seed:
            self.logger.debug(f"No seed provided, using current timestamp as seed")
        self.seed = seed or int(time.time())
        random.seed(self.seed)
        self.logger.info(f"Seed: {self.seed}")

        # Set window title
        self.title("Minesweeper")
        # Set window icon
        self.iconphoto(True, tk.PhotoImage(file=os.path.join(self.ICON_PATH, "minesweeper.png")))

        # Load sprites
        self.sprite_bomb = tk.PhotoImage(file=os.path.join(self.SPRITES_PATH, "bomb.png"))
        self.sprite_flag = tk.PhotoImage(file=os.path.join(self.SPRITES_PATH, "flag.png"))
        self.sprite_blank = tk.PhotoImage(file=os.path.join(self.SPRITES_PATH, "blank.png"))
        self.sprite_numbers = [
            tk.PhotoImage(file=os.path.join(self.SPRITES_PATH, f"{i}.png")) for i in range(0, 9)
        ]

        # Keep track of all cells
        self.game_grid: list[self.CellButton] = []
        # Build blank, graphical game grid
        for i in range(self.rows):
            for j in range(self.columns):
                # Create a Cell button with a blank sprite
                button = self.CellButton(
                    self, row=i, column=j, image=self.sprite_blank, width=30, height=30
                )
                # Bind an handler for mouse left-click on a cell that open it
                button.bind(sequence="<Button-1>", func=self.open_cell)
                # Bind an handler for mouse right-click on a cell that put a flag on it
                button.bind(sequence="<Button-2>", func=self.put_flag)
                # Bind an handler for mouse middle-click on a cell that print the game grid in the console
                button.bind(sequence="<Button-3>", func=self.print_game_grid)
                # Bind an handler for mouse double-left-click on a cell to open nearby cells if the
                # number of flags around it is the same as the number of nearby mines (chording)
                button.bind(sequence="<Double-Button-1>", func=self.chording)
                # Place button in grid (row i and column j)
                button.grid(row=i, column=j)
                # Add button to game grid
                self.game_grid.append(button)

        # Each cell has a list of its neighbors, so we don't have to calculate it every time
        for cell in self.game_grid:
            cell.neighbors = self.get_nearby_cells(cell)

        self.logger.debug(f"Grid built with {self.rows} rows and {self.columns} columns")

        # Center window
        self.eval("tk::PlaceWindow . center")

        # On first move, generate the true game grid and place bombs
        self.first_move: bool = True
        # Track if the game is over or not (used by solver)
        self.finished: bool = False
        # Track if the game is won or not (used by solver)
        self.won: bool = False

        self.logger.info("Game started")

    def _open_single_cell(self, cell: CellButton):
        """Open a single cell, without doing any check. Kind of internal function used by
        open_cell, chording and probably others. It does not check if the game is over,
        just open the cell and change the state of a single cell (button).

        Args:
            cell (CellButton): cell to open
        """

        # Open cell and show the number of mines around it
        cell.configure(
            image=self.sprite_bomb if cell.has_mine else self.sprite_numbers[cell.nearby_mines]
        )
        # Disable button
        cell["state"] = "disabled"
        # Set cell as opened
        cell.is_opened = True

    def are_valid_coordinates(self, coords: tuple[int, int]) -> bool:
        """Check if a tuple of coordinates is valid for the game grid.

        Args:
            coords (tuple[int, int]): tuple of coordinates (x, y)

        Returns:
            bool: True if coordinates are valid, False otherwise
        """

        return 0 <= coords[0] < self.rows and 0 <= coords[1] < self.columns

    def get_nearby_cells_coords(self, x: int, y: int) -> list[tuple[int, int]]:
        """Get a list of coordinates of the 8 cells around a given cell.
        List is already filtered to remove invalid coordinates.

        Args:
            x (int): cell x coordinate.
            y (int): cell y coordinate.

        Returns:
            list[tuple[int, int]]: list of coordinates of the 8 cells around a given cell.
        """

        return list(
            filter(
                self.are_valid_coordinates,
                [
                    (x - 1, y - 1),
                    (x - 1, y),
                    (x - 1, y + 1),
                    (x, y - 1),
                    (x, y + 1),
                    (x + 1, y - 1),
                    (x + 1, y),
                    (x + 1, y + 1),
                ],
            )
        )

    def get_nearby_cells(self, cell: CellButton) -> list[CellButton]:
        """Get a list of the 8 cells around a given cell.

        Args:
            cell (CellButton): cell.

        Returns:
            list[CellButton]: list of the 8 cells around a given cell.
        """

        return [
            self.game_grid[x * self.columns + y]
            for x, y in self.get_nearby_cells_coords(cell.row, cell.column)
        ]

    def generate_game_grid(self, genesis_x: int, genesis_y: int):
        """Generate the true game grid and place bombs.

        Args:
            genesis_x (int): first move x coordinate.
            genesis_y (int): first move y coordinate.
        """

        genesis_cell_coords = (genesis_x, genesis_y)
        self.logger.debug(f"First move at {genesis_cell_coords}")
        genesis_cell_nearby_cells = self.get_nearby_cells_coords(genesis_x, genesis_y)

        # Place bombs
        for i in range(self.mines):
            x, y = random.randint(0, self.rows - 1), random.randint(0, self.columns - 1)
            # If bomb is placed on the first move cell or in it's nearby (3x3) cells, or
            # bomb is placed on another bomb, try again
            while (
                (x, y) == genesis_cell_coords
                or (x, y) in genesis_cell_nearby_cells
                or self.game_grid[x * self.columns + y].has_mine
            ):
                x, y = random.randint(0, self.rows - 1), random.randint(0, self.columns - 1)
            # Place bomb
            self.game_grid[x * self.columns + y].has_mine = True
            self.logger.debug(f"Placed bomb at ({x}, {y})")
            # Update nearby mines count for all cells around the bomb
            for cell in self.get_nearby_cells_coords(x, y):
                self.game_grid[cell[0] * self.columns + cell[1]].nearby_mines += 1
        self.logger.debug(f"Placed {self.mines} bombs")

        self.print_game_grid()

    def print_game_grid(self, event: Optional[tk.Event] = None):
        """Print the game grid in the console, if debug is enabled.
        Can be called from middle mouse click on any cell.
        If called before first move, do nothing.

        Args:
            event (Optional[Event], optional): event that triggered the function. Defaults to None.
        """

        if self.first_move:
            return

        for i in range(self.rows):
            row: list[str] = []
            for j in range(self.columns):
                cell = self.game_grid[i * self.columns + j]
                row.append(
                    "B" if cell.has_mine else "?" if cell.is_flagged else str(cell.nearby_mines)
                )
            self.logger.debug(row)

    def open_nearby_cells(self, cell: CellButton):
        """Recursively open all cells around a given blank cell.

        Args:
            cell (CellButton): first cell to open.
        """

        # If cell is already opened or has flag on it do nothing
        if cell.is_opened or cell.is_flagged:
            # self.logger.debug(f"open_nearby_empty_cells ({cell.row}, {cell.column}): is already opened or has flag on it")
            return

        self._open_single_cell(cell)
        self.logger.debug(f"open_nearby_cells ({cell.row}, {cell.column}): opened")

        # If cell has nearby mines, don't open cells around it
        if cell.nearby_mines > 0:
            return

        # Get coordinates of all cells around the current cell
        for nearby_cell in cell.neighbors:
            self.open_nearby_cells(nearby_cell)

    def check_win(self) -> bool:
        """Check if the game is won.
        A game is won if all non-bomb cells are opened or all bomb-cell have a flag on it.

        Returns:
            bool: True if the game is won, False otherwise
        """

        # Check if all non-bomb cells are opened or all bomb-cell have a flag on it
        self.won = all(cell.is_opened for cell in self.game_grid if not cell.has_mine) or all(
            cell.is_flagged for cell in self.game_grid if cell.has_mine
        )
        if self.won:
            self.finished = True
        return self.won

    def game_over(self):
        """Show all bombs and disable all cells."""
        self.finished = True
        for cell in self.game_grid:
            self._open_single_cell(cell)
        # Update window after all cells are opened
        self.update()

    def open_cell(self, event: tk.Event):
        """Open a cell. If it's the first move, generate the game grid.
        If cell is already opened or has flag on it, do nothing.
        If cell has a mine, open it and show the bomb sprite: game is lost.
        If cell is blank, open all cells around it.
        Also check if game is won after each move.

        Args:
            event (Event[CellButton]): cell button (left) click event.
        """

        # Get cell from event, just for convenience
        cell: self.CellButton = event.widget

        # If it's the first move, generate the game grid
        if self.first_move:
            self.first_move = False
            self.generate_game_grid(genesis_x=cell.row, genesis_y=cell.column)

        # If cell is already opened or has flag on it, do nothing
        if cell.is_opened or cell.is_flagged:
            self.logger.debug(
                f"open_cell ({cell.row}, {cell.column}): is already opened or has flag on it"
            )
            return

        # If cell has a mine, open it and show the bomb sprite
        if cell.has_mine:
            self.logger.debug(f"open_cell ({cell.row}, {cell.column}): has a mine")
            cell.configure(image=self.sprite_bomb)
            self.game_over()
            if not self.non_interactive:
                msgbox.showinfo("Game over!", "BOOM! 💥")
            return

        # If cell has no nearby mines, open all cells around it
        if cell.nearby_mines == 0:
            self.logger.debug(f"open_cell ({cell.row}, {cell.column}): opening nearby cells")
            self.open_nearby_cells(cell)
        else:
            self._open_single_cell(cell)
            self.logger.debug(f"open_cell ({cell.row}, {cell.column}): opened")

        # Check if player won
        if self.check_win():
            self.game_over()
            if not self.non_interactive:
                msgbox.showinfo("You won!", "Congratulations! 🎉")

    def put_flag(self, event: tk.Event):
        """Put a flag on a cell. If it's the first move, do nothing.
        If cell is already opened, do nothing.
        If cell has a flag on it, remove it.
        If cell has no flag on it, put it.
        Also check if game is won after each move.

        Args:
            event (Event[CellButton]): cell button (right) click event.
        """

        # Get cell from event, just for convenience
        cell: self.CellButton = event.widget

        # If it's the first move, do nothing
        if self.first_move:
            self.logger.debug(
                f"put_flag ({cell.row}, {cell.column}): first move, use left click to open cell"
            )
            return

        # If cell is already opened, do nothing
        if cell.is_opened:
            self.logger.debug(f"put_flag ({cell.row}, {cell.column}): is already opened")
            return

        # Toggle flag on cell
        cell.is_flagged = not cell.is_flagged
        cell.configure(image=self.sprite_flag if cell.is_flagged else self.sprite_blank)
        cell["state"] = "disabled" if cell.is_flagged else "normal"
        self.logger.debug(
            f"put_flag ({cell.row}, {cell.column}): {'flagged' if cell.is_flagged else 'unflagged'}"
        )

        # Check if player won
        if self.check_win():
            self.game_over()
            if not self.non_interactive:
                msgbox.showinfo("You won!", "Congratulations! 🎉")

    def chording(self, event: tk.Event):
        """Chording is a technique used to open cells around a cell with a number on it.
        If the number of flags around a cell is equal to the number of mines around it,
        open all cells around it.


        Args:
            event (Event[CellButton]): cell button (left) double click event.
        """

        # Get cell from event, just for convenience
        cell: self.CellButton = event.widget

        if cell.is_flagged:
            self.logger.debug(f"chording ({cell.row}, {cell.column}): has flag on it")
            return

        if cell.nearby_mines == 0:
            self.logger.debug(f"chording ({cell.row}, {cell.column}): has no nearby mines")
            return

        nearby_flags: int = sum(1 for cell in cell.neighbors if cell.is_flagged)

        self.logger.debug(
            f"chording ({cell.row}, {cell.column}): found {nearby_flags} nearby flags"
        )
        self.logger.debug(
            f"chording ({cell.row}, {cell.column}): there are {cell.nearby_mines} nearby mines"
        )

        if cell.nearby_mines == nearby_flags:
            for nearby_cell in cell.neighbors:

                if nearby_cell.is_flagged:
                    continue

                if nearby_cell.has_mine:
                    self.game_over()
                    if not self.non_interactive:
                        msgbox.showinfo("Game over!", "BOOM! 💥")
                    return

                if nearby_cell.nearby_mines == 0:
                    self.open_nearby_cells(nearby_cell)
                else:
                    self._open_single_cell(nearby_cell)
                    self.logger.debug(
                        f"chording ({nearby_cell.row}, {nearby_cell.column}): opened"
                    )

        # Check if player won
        if self.check_win():
            self.game_over()
            if not self.non_interactive:
                msgbox.showinfo("You won!", "Congratulations! 🎉")


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
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Seed used for random mines placement",
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
    window = MinesweeperTk(
        difficulty=args.difficulty,
        rows=args.rows,
        columns=args.columns,
        mines=args.mines,
        debug=args.debug,
        seed=args.seed,
    )
    # Show window
    window.mainloop()

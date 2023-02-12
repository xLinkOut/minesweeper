#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from argparse import ArgumentParser
from random import randint
from tkinter import *
from tkinter import messagebox
from typing import Optional


class MinesweeperTk(Tk):
    """Minesweeper game class. Extends tkinter.Tk."""

    # Path to sprites
    SPRITES_PATH: str = os.path.join("res", "emoji")
    # Game difficulty levels, same as in the original game
    CONFIG: dict[str, dict[str, int]] = {
        "easy": {"rows": 9, "columns": 9, "mines": 10},
        "medium": {"rows": 16, "columns": 16, "mines": 40},
        "hard": {"rows": 16, "columns": 30, "mines": 99},
    }

    class CellButton(Button):
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

    def __init__(
        self,
        level: Optional[str],
        rows: Optional[int],
        columns: Optional[int],
        mines: Optional[int],
        debug: bool = False,
    ):
        """Minesweeper game class constructor.

        Args:
            level (Optional[str]): Game difficulty level. Can be "easy", "medium" or "hard".
            rows (Optional[int]): Number of rows in the game grid, mutually exclusive with level.
            columns (Optional[int]): Number of columns in the game grid, mutually exclusive with level.
            mines (Optional[int]): Number of mines in the game grid, mutually exclusive with level.
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
        self.logger.debug(f"Arguments: {level}, {rows}, {columns}, {mines}, {debug}")
        self.rows: int = rows or self.CONFIG[level]["rows"]
        self.columns: int = columns or self.CONFIG[level]["columns"]
        self.mines: int = mines or self.CONFIG[level]["mines"]
        self.logger.info(f"Game grid: {self.rows}x{self.columns} with {self.mines} mines")

        # Set window title
        self.title("Minesweeper")

        # Load sprites
        self.sprite_bomb = PhotoImage(file=os.path.join(self.SPRITES_PATH, "bomb.png"))
        self.sprite_flag = PhotoImage(file=os.path.join(self.SPRITES_PATH, "flag.png"))
        self.sprite_blank = PhotoImage(file=os.path.join(self.SPRITES_PATH, "normal.png"))
        self.sprite_numbers = [
            PhotoImage(file=os.path.join(self.SPRITES_PATH, f"{i}.png")) for i in range(0, 10)
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
                # Place button in grid (row i and column j)
                button.grid(row=i, column=j)
                # Add button to game grid
                self.game_grid.append(button)
        self.logger.debug(f"Grid built with {self.rows} rows and {self.columns} columns")

        # Center window
        self.eval("tk::PlaceWindow . center")

        # On first move, generate the true game grid and place bombs
        self.first_move: bool = True
        self.logger.info("Game started")

    def are_valid_coordinates(self, coords: tuple[int, int]) -> bool:
        """Check if a tuple of coordinates is valid for the game grid.

        Args:
            coords (tuple[int, int]): tuple of coordinates (x, y)

        Returns:
            bool: True if coordinates are valid, False otherwise
        """

        return 0 <= coords[0] < self.rows and 0 <= coords[1] < self.columns

    def get_nearby_cells(self, x: int, y: int) -> list[tuple[int, int]]:
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

    def generate_game_grid(self, genesis_x: int, genesis_y: int):
        """Generate the true game grid and place bombs.

        Args:
            genesis_x (int): first move x coordinate.
            genesis_y (int): first move y coordinate.
        """

        genesis_cell_coords = (genesis_x, genesis_y)
        self.logger.debug(f"First move at {genesis_cell_coords}")
        genesis_cell_nearby_cells = self.get_nearby_cells(genesis_x, genesis_y)

        # Place bombs
        for i in range(self.mines):
            x, y = randint(0, self.rows - 1), randint(0, self.columns - 1)
            # If bomb is placed on the first move cell or in it's nearby (3x3) cells, or
            # bomb is placed on another bomb, try again
            while (
                (x, y) == genesis_cell_coords
                or (x, y) in genesis_cell_nearby_cells
                or self.game_grid[x * self.columns + y].has_mine
            ):
                x, y = randint(0, self.rows - 1), randint(0, self.columns - 1)
            # Place bomb
            self.game_grid[x * self.columns + y].has_mine = True
            self.logger.debug(f"Placed bomb at ({x}, {y})")
            # Update nearby mines count for all cells around the bomb
            for cell in self.get_nearby_cells(x, y):
                self.game_grid[cell[0] * self.columns + cell[1]].nearby_mines += 1
        self.logger.debug(f"Placed {self.mines} bombs")

        # Print game grid
        for i in range(self.rows):
            row: list[str] = []
            for j in range(self.columns):
                cell = self.game_grid[i * self.columns + j]
                row.append("B" if cell.has_mine else str(cell.nearby_mines))
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

        # Open cell and show the number of mines around it
        cell.configure(image=self.sprite_numbers[cell.nearby_mines])
        # Disable button
        cell["state"] = "disabled"
        # Set cell as opened
        cell.is_opened = True
        self.logger.debug(f"open_nearby_cells ({cell.row}, {cell.column}): opened")

        # If cell has nearby mines, don't open cells around it
        if cell.nearby_mines > 0:
            return

        # Get coordinates of all cells around the current cell
        for cell in self.get_nearby_cells(cell.row, cell.column):
            self.open_nearby_cells(self.game_grid[cell[0] * self.columns + cell[1]])

    def check_win(self) -> bool:
        """Check if the game is won.
        A game is won if all non-bomb cells are opened or all bomb-cell have a flag on it.

        Returns:
            bool: True if the game is won, False otherwise
        """

        # Check if all non-bomb cells are opened or all bomb-cell have a flag on it
        return all(cell.is_opened for cell in self.game_grid if not cell.has_mine) or all(
            cell.is_flagged for cell in self.game_grid if cell.has_mine
        )

    def game_over(self):
        """Show all bombs and disable all cells."""

        for cell in self.game_grid:
            cell.configure(
                image=self.sprite_bomb if cell.has_mine else self.sprite_numbers[cell.nearby_mines]
            )
            cell.is_opened = True
            cell["state"] = "disabled"
        self.update()
    
    def open_cell(self, event: Event):
        """Open a cell. If it's the first move, generate the game grid.
        If cell is already opened or has flag on it, do nothing.
        If cell has a mine, open it and show the bomb sprite: game is lost.
        If cell is blank, open all cells around it.
        Also check if game is won after each move.

        Args:
            event (Event[CellButton]): cell button (left) click event.
        """

        # If it's the first move, generate the game grid
        if self.first_move:
            self.generate_game_grid(genesis_x=event.widget.row, genesis_y=event.widget.column)
            self.first_move = False

        # If cell is already opened or has flag on it, do nothing
        if event.widget.is_opened or event.widget.is_flagged:
            self.logger.debug(
                f"open_cell ({event.widget.row}, {event.widget.column}): is already opened or has flag on it"
            )
            return

        # If cell has a mine, open it and show the bomb sprite
        if event.widget.has_mine:
            self.logger.debug(f"open_cell ({event.widget.row}, {event.widget.column}): has a mine")
            event.widget.configure(image=self.sprite_bomb)
            self.game_over()
            messagebox.showinfo("Game over!", "BOOM! 💥")
            return

        # If cell has no nearby mines, open all cells around it
        if event.widget.nearby_mines == 0:
            self.logger.debug(
                f"open_cell ({event.widget.row}, {event.widget.column}): opening nearby cells"
            )
            self.open_nearby_cells(event.widget)
        else:
            # If cell has no mine, open it and show the number of mines around it
            event.widget.configure(image=self.sprite_numbers[event.widget.nearby_mines])
            # Disable button
            event.widget["state"] = "disabled"
            # Set cell as opened
            event.widget.is_opened = True
            self.logger.debug(f"open_cell ({event.widget.row}, {event.widget.column}): opened")

        # Check if player won
        if self.check_win():
            self.game_over()
            messagebox.showinfo("You won!", "Congratulations! 🎉")

    def put_flag(self, event: Event):
        """Put a flag on a cell. If it's the first move, do nothing.
        If cell is already opened, do nothing.
        If cell has a flag on it, remove it.
        If cell has no flag on it, put it.
        Also check if game is won after each move.

        Args:
            event (Event[CellButton]): cell button (right) click event.
        """

        # If it's the first move, do nothing
        if self.first_move:
            self.logger.debug(
                f"put_flag ({event.widget.row}, {event.widget.column}): first move, use left click to open cell"
            )
            return

        # If cell is already opened, do nothing
        if event.widget.is_opened:
            self.logger.debug(
                f"put_flag ({event.widget.row}, {event.widget.column}): is already opened"
            )
            return

        # Toggle flag on cell
        event.widget.is_flagged = not event.widget.is_flagged
        event.widget.configure(
            image=self.sprite_flag if event.widget.is_flagged else self.sprite_blank
        )
        event.widget["state"] = "disabled" if event.widget.is_flagged else "normal"
        self.logger.debug(
            f"put_flag ({event.widget.row}, {event.widget.column}): {'flagged' if event.widget.is_flagged else 'unflagged'}"
        )

        # Check if player won
        if self.check_win():
            self.game_over()
            messagebox.showinfo("You won!", "Congratulations! 🎉")


if __name__ == "__main__":
    parser = ArgumentParser(description="Minesweeper game")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode",
    )

    parser.add_argument(
        "-l",
        "--level",
        type=str,
        help="Game level (easy, medium, hard)",
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

    args = parser.parse_args()

    # Check on arguments
    if not args.level and not args.rows and not args.columns and not args.mines:
        parser.error("No arguments provided")

    if args.level and (args.rows or args.columns or args.mines):
        parser.error("Cannot use level and custom mode at the same time")

    if args.level and args.level not in ["easy", "medium", "hard"]:
        parser.error("Invalid level")

    if not args.level and (args.rows <= 0 or args.columns <= 0 or args.mines <= 0):
        parser.error("Invalid number of rows, columns or mines")

    if not args.level and (args.mines >= args.rows * args.columns):
        parser.error("Number of mines must be less than number of cells")

    # Create a window with Tkinter
    window = MinesweeperTk(
        level=args.level, rows=args.rows, columns=args.columns, mines=args.mines, debug=args.debug
    )
    # Show window
    window.mainloop()

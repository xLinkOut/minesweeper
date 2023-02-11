#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from tkinter import *
from tkinter import messagebox
from random import randint

class MinesweeperTk(Tk):
    DEFAULT_ROWS: int = 4
    DEFAULT_COLUMNS: int = 4
    DEFAULT_MINES: int = 4

    SPRITES_PATH: str = os.path.join("res", "emoji")

    class CellButton(Button):
        def __init__(self, master, row: int, column: int, **kwargs):
            super().__init__(master, **kwargs)
            self.row: int = row
            self.column: int = column
            self.has_mine: bool = False
            self.is_opened: bool = False
            self.is_flagged: bool = False
            self.nearby_mines: int = 0

    def __init__(self):
        super().__init__()

        # Logger instance
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        self.logger = logging.getLogger("Minesweeper")

        # Set window title
        self.title("Minesweeper")
        # Center window
        self.eval("tk::PlaceWindow . center")

        # Load sprites
        self.sprite_bomb = PhotoImage(file=os.path.join(self.SPRITES_PATH, "bomb.png"))
        self.sprite_flag = PhotoImage(file=os.path.join(self.SPRITES_PATH, "flag.png"))
        self.sprite_blank = PhotoImage(file=os.path.join(self.SPRITES_PATH, "normal.png"))
        self.sprite_numbers = [
            PhotoImage(file=os.path.join(self.SPRITES_PATH, f"{i}.png")) for i in range(0, 10)
        ]

        # Keep track of all cells
        self.game_grid: list[self.CellButton] = []
        # Build blank game grid
        for i in range(self.DEFAULT_ROWS):
            for j in range(self.DEFAULT_COLUMNS):
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
        self.logger.debug(
            f"Grid built with {self.DEFAULT_ROWS} rows and {self.DEFAULT_COLUMNS} columns"
        )

        # On first move, generate the true game grid and place bombs
        self.first_move: bool = True
        self.logger.info("Game started")

    def are_valid_coordinates(self, x: int, y: int) -> bool:
        return 0 <= x < self.DEFAULT_ROWS and 0 <= y < self.DEFAULT_COLUMNS

    def get_nearby_cells(self, x: int, y: int) -> list[tuple[int, int]]:
        return [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]



    def generate_game_grid(self, genesis_x: int, genesis_y: int):
        genesis_cell_coords = (genesis_x, genesis_y)
        self.logger.debug(f"First move at {genesis_cell_coords}")
        genesis_cell_nearby_cells = self.get_nearby_cells(genesis_x, genesis_y)

        # Place bombs
        for i in range(self.DEFAULT_MINES):
            x, y = randint(0, self.DEFAULT_ROWS - 1), randint(0, self.DEFAULT_COLUMNS - 1)
            # If bomb is placed on the first move cell or in it's nearby (3x3) cells, or
            # bomb is placed on another bomb, try again
            while((x, y) == genesis_cell_coords or (x, y) in genesis_cell_nearby_cells or \
                self.game_grid[x * self.DEFAULT_COLUMNS + y].has_mine):
                x, y = randint(0, self.DEFAULT_ROWS - 1), randint(0, self.DEFAULT_COLUMNS - 1)
            # Place bomb
            self.game_grid[x * self.DEFAULT_COLUMNS + y].has_mine = True
            self.logger.debug(f"Placed bomb at ({x}, {y})")
            # Update nearby mines count for all cells around the bomb
            nearby_cells = self.get_nearby_cells(x, y)
            for cell in nearby_cells:
                if self.are_valid_coordinates(cell[0], cell[1]):
                    self.game_grid[cell[0] * self.DEFAULT_COLUMNS + cell[1]].nearby_mines += 1
        self.logger.debug(f"Placed {self.DEFAULT_MINES} bombs")

        # Print game grid
        for i in range(self.DEFAULT_ROWS):
            row: list[str] = []
            for j in range(self.DEFAULT_COLUMNS):
                cell = self.game_grid[i * self.DEFAULT_COLUMNS + j]
                row.append('B' if cell.has_mine else str(cell.nearby_mines))
            self.logger.debug(row)

    def check_win(self):
        # Check if all non-bomb cells are opened or all bomb-cell have a flag on it
        return (
            all(cell.is_opened for cell in self.game_grid if not cell.has_mine)
            or 
            all(cell.is_flagged for cell in self.game_grid if cell.has_mine)
        )

    def open_cell(self, event):
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
            self.logger.debug(f"open_cell ({event.widget.row}, {event.widget.column}): opening nearby cells")
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

    def open_nearby_cells(self, cell: CellButton):
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
        x, y = cell.row, cell.column
        nearby_cells = self.get_nearby_cells(x, y)
        for cell in nearby_cells:
            # If coordinates are valid and cell is not opened, open it
            if self.are_valid_coordinates(cell[0], cell[1]):
                self.open_nearby_cells(self.game_grid[cell[0] * self.DEFAULT_COLUMNS + cell[1]])

    def game_over(self):
        for cell in self.game_grid:
            cell.configure(image=self.sprite_bomb if cell.has_mine else self.sprite_numbers[cell.nearby_mines])
            cell.is_opened = True
            cell["state"] = "disabled"
        self.update()

    def put_flag(self, event):
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
    # Create a window with Tkinter
    window = MinesweeperTk()
    # Show window
    window.mainloop()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from tkinter import *
from tkinter import messagebox
from random import randint

class MinesweeperTk(Tk):
    DEFAULT_ROWS: int = 8
    DEFAULT_COLUMNS: int = 8
    DEFAULT_MINES: int = 10

    SPRITES_PATH: str = os.path.join("res", "emoji")

    class CellButton(Button):
        def __init__(self, master, row, column, **kwargs):
            super().__init__(master, **kwargs)
            self.row = row
            self.column = column
            self.has_mine = False
            self.is_opened = False
            self.is_flagged = False
            self.nearby_mines = 0

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
        self.game_grid = []
        # Build game grid
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

        # Place bombs
        for i in range(self.DEFAULT_MINES):
            x, y = randint(0, self.DEFAULT_ROWS - 1), randint(0, self.DEFAULT_COLUMNS - 1)
            self.game_grid[x * self.DEFAULT_COLUMNS + y].has_mine = True
            self.logger.debug(f"Placed bomb at ({x}, {y})")
            # Update nearby mines count for all cells around the bomb
            nearby_cells = [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]
            for cell in nearby_cells:
                if self.are_valid_coordinates(cell[0], cell[1]):
                    self.game_grid[cell[0] * self.DEFAULT_COLUMNS + cell[1]].nearby_mines += 1

        self.logger.debug(f"Placed {self.DEFAULT_MINES} bombs")

        # Print game grid
        for i in range(self.DEFAULT_ROWS):
            row = []
            for j in range(self.DEFAULT_COLUMNS):
                cell = self.game_grid[i * self.DEFAULT_COLUMNS + j]
                row.append('B' if cell.has_mine else str(cell.nearby_mines))
            self.logger.debug(row)

    def are_valid_coordinates(self, x, y):
        return 0 <= x < self.DEFAULT_ROWS and 0 <= y < self.DEFAULT_COLUMNS

    def open_cell(self, event):
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
            # TODO: open all cells and show all mines
            # TODO: disable all buttons
            #messagebox.showinfo("Game over!", "BOOM! 💥")
            return

        # If cell has no mine, open it and show the number of mines around it
        # TODO: if cell has no nearby mines, open all cells around it
        event.widget.configure(image=self.sprite_numbers[event.widget.nearby_mines])
        # Disable button
        event.widget["state"] = "disabled"
        # Set cell as opened
        event.widget.is_opened = True
        self.logger.debug(f"open_cell ({event.widget.row}, {event.widget.column}): opened")

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


if __name__ == "__main__":
    # Create a window with Tkinter
    window = MinesweeperTk()
    # Show window
    window.mainloop()

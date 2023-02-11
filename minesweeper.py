#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from tkinter import *


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

    def __init__(self):
        super().__init__()
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

        # Build game grid
        for i in range(self.DEFAULT_ROWS):
            for j in range(self.DEFAULT_COLUMNS):
                # Create a button
                button = self.CellButton(self, row=i, column=j, image=self.sprite_blank, width=30, height=30)
                # Bind an handler for mouse left-click on a cell, that 'open' the cell
                button.bind(sequence="<Button-1>", func=self.open_cell)
                # Bind an handler for mouse right-click on a cell that put a flag on the cell
                button.bind(sequence="<Button-2>", func=self.put_flag)
                # Place button in grid
                button.grid(row=i, column=j)

    def open_cell(self, event):
        event.widget.configure(image=self.sprite_numbers[0])
        event.widget["state"] = "disabled"

    def put_flag(self, event):
        event.widget.configure(image=self.sprite_flag)


if __name__ == "__main__":
    # Create a window with Tkinter
    window = MinesweeperTk()
    # Show window
    window.mainloop()

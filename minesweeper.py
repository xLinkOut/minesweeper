#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from tkinter import *


class MinesweeperTk(Tk):
    DEFAULT_ROWS: int = 8
    DEFAULT_COLUMNS: int = 8
    DEFAULT_MINES: int = 10

    SPRITES_PATH: str = os.path.join("res", "emoji")

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


if __name__ == "__main__":
    # Create a window with Tkinter
    window = MinesweeperTk()
    # Show window
    window.mainloop()

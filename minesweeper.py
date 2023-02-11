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


if __name__ == "__main__":
    # Create a window with Tkinter
    window = MinesweeperTk()
    # Show window
    window.mainloop()

# Minesweeper 💣
Python implementation of popular [Minesweeper](https://en.wikipedia.org/wiki/Minesweeper_(video_game)) game using Tk GUI toolkit. 
Known as _Campo minato_ or _Prato fiorito_ in Italian.

<p align="center"><img align="center" src="https://i.imgur.com/V2xG3QK.png" alt="Screenshot of Minesweeper"></p>

## Installation
`Tkinter` is the only dependency needed.

### macOS
```bash
brew install python-tk
```

### Debian(-based)
```bash
apt install python3-tk
```

### Arch
```bash
pacman -S tk
```

### Windows
Idk, Google it.

## How to use
It is possible to play using a predefined difficulty level, which influences the size of the game grid and the number of mines. The possible levels are listed below and follow the difficulty values of the original game:
+ `easy`: grid 9x9 with 10 mines;
+ `medium`: grid 16x16 with 40 mines;
+ `hard`: grid 16x30 with 99 mines.

To do this, use the `--level` parameter followed by the string of the chosen difficulty.

Alternatively, it is possible to build a game grid with custom values: indicate the number of rows with the `-r/--rows` parameter, the number of columns with the `-c/--columns` parameter and the number of mines with the `-m/--mines` parameter.

Obviously, the two game modes are **mutually exclusive**.

Lastly, `--debug` enable the debug mode, surprisingly: it will log a lot more information in the console like each triggered events, full game grid and so on.

## Goals
- [x] Code a working implementation of Minesweeper game with Python and Tkinter;
- [ ] Code an auto-solving mechanism using pure game logic and math;
- [ ] Build some kind of machine learning algorithm that learn and solve the game.

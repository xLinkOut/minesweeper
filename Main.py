from numpy import zeros
from tkinter import PhotoImage,Button,messagebox,Tk
from random import randint

# Create a window with Tkinter library
window = Tk()

# Number of rows
row = 16 # Fixed size, for now
# Number of columns
col = 16
# Number of bombs
bombs = (row*col) // 4 # Maybe divider (4) can be setted according to the difficoult chosen 
print("Row:",row,"Col:",col,"Bombs:",bombs)

# Create a board as a board filled with 0
board = zeros((row,col),dtype=int)

# List of current flagged cell
cellsFlagged = []

# List of bombs coordinates
bombsCoord = []

# Image imported as Tk PhotoImage object
spriteBomb = PhotoImage(file = "res/bomb.png")
spriteFlag = PhotoImage(file = "res/flagged.png")
spriteNormal = PhotoImage(file = "res/normal.png")
spriteNumbers =[
    PhotoImage(file = "res/0.png"),
    PhotoImage(file = "res/1.png"),
    PhotoImage(file = "res/2.png"),
    PhotoImage(file = "res/3.png"),
    PhotoImage(file = "res/4.png"),
    PhotoImage(file = "res/5.png")
]

# Insert bombs into the board
while(bombs):
    # Leave border without bombs for KeyError, fix later
    #x,y = randint(0,row-1),randint(0,col-1)    
    x,y = randint(1,row-2),randint(1,col-2)
    if board[x][y] == 0:
        # Set a bomb as -1 value
        board[x][y] = -1
        # Append bomb coord into bombsCoord list
        bombsCoord.append((x,y))
    bombs-=1
print("Effective bombs:",len(bombsCoord),"\n")
print(board,"\n")

# Fill other cells with numbers
# Scan rows
for x in range(0,row-1):
    # For each row, scan columns
    for y in range(0,col-1):
        if board[x][y] == -1:
            # Is a bomb, add +1 to the adjacent cells, in a sub-board 3x3 with current cell as center
            # Row up
            board[x-1][y-1] = (board[x-1][y-1] + 1) if board[x-1][y-1] != -1 else board[x-1][y-1]
            board[x-1][y] = (board[x-1][y] + 1) if board[x-1][y] != -1 else board[x-1][y] 
            board[x-1][y+1] = (board[x-1][y+1] + 1) if board[x-1][y+1] != -1 else board[x-1][y+1] 
            # Same row
            board[x][y-1] = (board[x][y-1] + 1) if board[x][y-1] != -1 else board[x][y-1] 
            board[x][y+1] = (board[x][y+1] + 1) if board[x][y+1] != -1 else board[x][y+1] 
            # Row down
            board[x+1][y-1] = (board[x+1][y-1] + 1) if board[x+1][y-1] != -1 else board[x+1][y-1] 
            board[x+1][y] = (board[x+1][y] + 1) if board[x+1][y] != -1 else board[x+1][y] 
            board[x+1][y+1] = (board[x+1][y+1] + 1) if board[x+1][y+1] != -1 else board[x+1][y+1] 
print(board,"\n")

# Linearize board to a 1D array
linearizedBoard = []
# Scan rows
for r in range(0,row):
    # For each row, scan columns
    for c in range(0,col):
        # Append current cell's value to the linearizedBoard array
        linearizedBoard.append(board[r][c])
print(linearizedBoard,"\n")
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
bombs = (row*col) // 4
print("Row:",row,"Col:",col,"Bombs:",bombs,end="\n\n")

# Create a board as a matrix filled with 0
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
print(board,"\n")
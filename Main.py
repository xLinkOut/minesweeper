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
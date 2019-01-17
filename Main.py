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
    PhotoImage(file = "res/5.png"),
    PhotoImage(file = "res/6.png")
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
for x in range(row-1):
    # For each row, scan columns
    for y in range(col-1):
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
for r in range(row):
    # For each row, scan columns
    for c in range(col):
        # Append current cell's value to the linearizedBoard array
        linearizedBoard.append(board[r][c])
print(linearizedBoard,"\n")

# Update button's image when a cell is pressed or flagged
def updateImage(button,number):
    # Idk why this is used for, but w/out doesn't work. I'll read docs
    if button in cellsList.values():
        # If is a bomb
        if number == -1:
            button.configure(image=spriteBomb,width=30,height=30)
        # Else update the button image with a number or blank image
        else:
            button.configure(image=spriteNumbers[number],width=30,height=30)
    else:
        # If is a bomb
        if number == -1:
            button.widget.configure(image=spriteBomb,width=30,height=30)
        # Else update the button image with a number or blank image
        else:
            button.widget.configure(image=spriteNumbers[number],width=30,height=30)

# Called when mouse left-click has been pressed over a cell
# Open the pressed cell
def leftClick(cellPressed,x,y):
    # If the pressed cell is not flagged
    if (x,y) not in cellsFlagged:
        # If pressed cell contain a bomb
        if board[x][y] == -1:
            # Game over
            # Update the current cell's image with a bomb
            cellPressed.widget.configure(image=spriteBomb,width=30,height=30)
            # Then openup all the remaining cells
            for index,button in enumerate(cellsList.values()):
                updateImage(button,linearizedBoard[index])
            # Show a message box (here maybe insert a time/score, later)
            messagebox.showinfo("Game over!","You lost :c")
            # Then exit
            exit() # Until create a menu
        else:
            # If pressed cell is not a bomb, update cell's image
            updateImage(cellPressed,board[x][y])

# Called when mouse right-click has been pressed over a cell
# Flag the pressed cell
def rightClick(cellPressed,x,y):
    # If cell is already flagged, remove the flag
    if (x,y) in cellsFlagged:
        # Remove cell from cellsFlagged list
        cellsFlagged.remove((x,y))
        # Update image back to normal sprite
        cellPressed.configure(image=spriteNormal,width=30,height=30)
    # If is not flagged, flag the cell
    else:
        # Insert flagged cell coord into cellsFlagged list
        cellsFlagged.append((x,y))
        # Update cell's image with flag sprite
        cellPressed.configure(image=spriteFlag,width=30,height=30)

# Dictionary that contains all the cells as Tkinter.Button object
cellsList = {}

# Scan rows
for r in range(row):
    # For each row, scan columns
    for c in range(col):
        # Create a button object with normal image, width and height equals to 30
        button = Button(window,image=spriteNormal,width=30,height=30)
        # Bind an handler for mouse left-click on a cell that call leftClick funcion with event obj, x and y coord
        button.bind("<Button-1>",lambda event,x=r,y=c : leftClick(event,x,y))
        # Bind an handler for mouse right-click on a cell that call rightClick function with event obj, x and y coord
        button.bind("Button-3>", lambda event,x=r,y=c : rightClick(event,x,y))
        # Grid the button in row r and column c
        button.grid(row=r,column=c)
        # Append the button into cellsList with indexing (x,y)
        # :to access this -> cellsList[3,4] -> button in coordinates x=3,y=4
        cellsList[r,c] = button

# Popup the window
window.mainloop()

# TODO:
#   Function that open nearby blank cells when a blank cell is pressed
#   Explain why updateImage doesnt work without distinguish between widget or just .configure method
#   Add sprite for number 6,7,8
#   Fix border key error
#   Find a formula to calculate better how meny bombs has to spawn
#   Create some kind of menu with rows and columns input, and difficulty
#   Add a timer
#   Add some kind of scoring function
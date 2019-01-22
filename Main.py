from numpy import zeros
from tkinter import PhotoImage,Button,messagebox,Tk
from random import randint

# Create a window with Tkinter library
window = Tk()

# Boolean variable to print statements if in debug mode
debug = False

# Difficulty (2=Hard,4=Medium,10=Easy)
difficulty = 4

# Number of rows
row = 16 # Fixed size, for now
# Number of columns
col = 16
# Number of bombs
bombs = (row*col) // int(difficulty)
print("Row:",row,"Col:",col,"Bombs:",bombs) if debug else None

# Create a board as a board filled with 0
board = zeros((row,col),dtype=int)
# Create a matrix to keep track of already opened cells, filled with False
marked = zeros((row,col),dtype=bool)

# List of current flagged cell
cellsFlagged = []

# List of bombs coordinates
bombsCoord = []

# Images imported as Tk PhotoImage objects
spriteBomb = PhotoImage(file = "res/emoji/bomb.png")
spriteFlag = PhotoImage(file = "res/emoji/flag.png")
spriteNormal = PhotoImage(file = "res/emoji/normal.png")
spriteNumbers =[
    PhotoImage(file = "res/emoji/0.png"),
    PhotoImage(file = "res/emoji/1.png"),
    PhotoImage(file = "res/emoji/2.png"),
    PhotoImage(file = "res/emoji/3.png"),
    PhotoImage(file = "res/emoji/4.png"),
    PhotoImage(file = "res/emoji/5.png"),
    PhotoImage(file = "res/emoji/6.png"),
    PhotoImage(file = "res/emoji/7.png"),
    PhotoImage(file = "res/emoji/8.png"),
    PhotoImage(file = "res/emoji/9.png"),

]

# Insert bombs into the board
while(bombs):
    # Leave border without bombs for KeyError, fix later    
    #x,y = randint(1,row-2),randint(1,col-2)
    
    # Seems to work...
    x,y = randint(0,row-1),randint(0,col-1)    
    
    if board[x][y] == 0:
        # Set a bomb as -1 value
        board[x][y] = -1
        # Append bomb coord into bombsCoord list
        bombsCoord.append((x,y))
    bombs-=1

print("Effective bombs:",len(bombsCoord),"\n") if debug else None
print(board,"\n") if debug else None

# Return True if x and y are valid coordinates, means that (0 =< x < row) and (0 =< y < col)
def areValidCoords(x,y):
    return x >= 0 and y >= 0 and x < row and y < col

# Fill other cells with numbers
# Scan rows
for x in range(row):
    # For each row, scan columns
    for y in range(col):
        # If is a bomb
        if board[x][y] == -1:
            # List that cointains all nearby cells, in a 3x3 sub-matrix            
            neighbor = [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]
            # For each neighbor            
            for n in neighbor:
                # If (x,y) is valid coords and cell is not a bomb
                if areValidCoords(n[0],n[1]) and board[n[0]][n[1]] != -1:
                    # Increase by 1
                    board[n[0]][n[1]] += 1
            '''
            # Row up
            board[x-1][y-1] = (board[x-1][y-1] + 1) if check(x-1,y-1) and board[x-1][y-1] != -1 else board[x-1][y-1]
            board[x-1][y] = (board[x-1][y] + 1) if check(x-1,y) and board[x-1][y] != -1 else board[x-1][y] 
            board[x-1][y+1] = (board[x-1][y+1] + 1) if check(x-1,y+1) and board[x-1][y+1] != -1 else board[x-1][y+1] 
            # Same row
            board[x][y-1] = (board[x][y-1] + 1) if check(x,y-1) and board[x][y-1] != -1 else board[x][y-1] 
            board[x][y+1] = (board[x][y+1] + 1) if check(x,y+1) and board[x][y+1] != -1 else board[x][y+1] 
            # Row down
            board[x+1][y-1] = (board[x+1][y-1] + 1) if check(x+1,y-1) and board[x+1][y-1] != -1 else board[x+1][y-1] 
            board[x+1][y] = (board[x+1][y] + 1) if check(x+1,y) and board[x+1][y] != -1 else board[x+1][y] 
            board[x+1][y+1] = (board[x+1][y+1] + 1) if check(x+1,y+1) and board[x+1][y+1] != -1 else board[x+1][y+1] 
            '''
print(board,"\n")

# Linearize board to a 1D array
linearizedBoard = []
# Scan rows
for r in range(row):
    # For each row, scan columns
    for c in range(col):
        # Append current cell's value to the linearizedBoard array
        linearizedBoard.append(board[r][c])
print(linearizedBoard,"\n") if debug else None

# Update button's image when a cell is pressed or flagged
def updateImage(button,number):
    # Idk why this is used for, but w/out doesn't work.
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

# When a blank cell is pressed, open nearby blank cells
def openBlankCells(x,y):
    # Check for under-overflow index to prevent KeyError
    if areValidCoords(x,y):
        # List that cointains all nearby cells, in a 3x3 sub-matrix
        neighbor = [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]
        # For each neighbor
        for n in neighbor:
            # Another check for under-overflow index to prevent KeyError        
            if areValidCoords(n[0],n[1]):
                # If cell is not already opened and is not flagged and is not a bomb
                if not marked[n[0]][n[1]] and (n not in cellsFlagged) and board[n[0]][n[1]] != -1 :
                    # Update cell's image
                    updateImage(cellsList[n],board[n[0]][n[1]])
                    # Mark cell as opened
                    marked[n[0]][n[1]] = True    
                    # If was an empty cell
                    if board[n[0]][n[1]] == 0:
                        # Recursively open nearby blank cells
                        openBlankCells(n[0],n[1])

            
# Called when mouse left-click has been pressed over a cell
# Open the pressed cell
def leftClick(cellPressed,x,y):
    # If pressed cell is not flagged
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
        # If pressed cell is a blank cell
        elif board[x][y] == 0:
            # Update image in current cell with blank sprite
            updateImage(cellPressed,0)
            # Recursively open nearby blank cells
            openBlankCells(x,y)
        else:
            # If pressed cell is not a bomb, update cell's image
            updateImage(cellPressed,board[x][y])
            # Mark cell as opened
            marked[x][y] = True
    
# Called when mouse right-click has been pressed over a cell
# Flag the pressed cell
def rightClick(cellPressed,x,y):
    # If cell is already flagged, remove the flag
    if (x,y) in cellsFlagged:
        # Remove cell from cellsFlagged list
        cellsFlagged.remove((x,y))
        # Update image back to normal sprite
        cellPressed.widget.configure(image=spriteNormal,width=30,height=30)
    # If is not flagged, flag the cell
    else:
        # If is not already opened
        if not marked[x][y]:
            # Insert flagged cell coord into cellsFlagged list
            cellsFlagged.append((x,y))
            # Update cell's image with flag sprite
            cellPressed.widget.configure(image=spriteFlag,width=30,height=30)

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
        button.bind("<Button-3>", lambda event,x=r,y=c : rightClick(event,x,y))
        # Grid the button in row r and column c
        button.grid(row=r,column=c)
        # Append the button into cellsList with indexing (x,y)
        # :to access this -> cellsList[3,4] -> button in coordinates x=3,y=4
        cellsList[r,c] = button

# Popup the window
window.mainloop()

# TODO:
#Find a formula to calculate better how many bombs has to spawn
#Add a timer
#Add some kind of scoring function
#Create some kind of menu with rows and columns input, and difficulty
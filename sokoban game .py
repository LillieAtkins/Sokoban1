

"""
This is an implementation of the game Sokoban using object-oriented Python 
with pyprocessing providing the visuals.
Cool things:
Initialized an empty list called LAST_MOVE that is an instance variable in the
SokobanBoard class. In the def keyPressed method in the SokobanBoard class, after
each direction is moved (each key pressed), the move, (N,S,E, or W) is appended to
the list LAST_MOVE. Then, if  the key u is pressed, temporarily stores the last move
as the last element in the list in a variable. If the last move was N, the player will
move south, and the LAST_MOVE list will change such that the move (N) is deleted from
the list. This code follows the same pattern for the other directions to UNDO A
PLAYER'S MOVE.  
"""

from pyprocessing import *

# Some constants that control the size of the window and the size of the tiles on the board
WIDTH = 600
HEIGHT = 600
CELL_SIZE=25

class Tile:
    """
    This class implements a single tile on our game board.
    
    The tile is the basic unit of the game board. A tile can be open 
    or a wall. Open tiles are allowed to have an occupant (a game piece 
    positioned on it -- note that there can be at most one occupant).
    The tile is responsible for managing the piece placed upon it, reporting 
    when the square is open on the board, and passing drawing commands 
    along to any piece currently occupying it.
    """
    
    def __init__(self, tileType, x, y, gameBoard):
        """
        Initialize the tile, setting its position and default values.
        """
        self.tileType = tileType
        self.x = x
        self.y = y
        self.gameBoard = gameBoard 
        self.goal = False
        self.occupant = None
        
    def draw(self):
        """
        Draw the tile and tell any occupant to draw itself.
        
        The drawing code is configured such that the current origin 
        of the coordinate system is in the middle of where the tile 
        should be drawn. As a result, the tile (and the pieces) 
        should draw themselves centered on (0,0).
        """
        
        rectMode(CENTER)
        if self.tileType == 'o':
            fill(255, 255, 255)    #color open spaces
            rect(0, 0, CELL_SIZE, CELL_SIZE)   #tile draws itself
        if self.tileType == 'w':
            fill(0, 0, 255)        #color walls
            rect(0, 0, CELL_SIZE, CELL_SIZE)   #tile draws itself
        if self.goal == True:      #check if there is a goal on the tile
            fill(255, 0, 0)                     #fill ellipses red
            ellipse(0, 0, CELL_SIZE-5, CELL_SIZE-5)  #draw ellipses
            
            
        # check if there is a piece here and tell it to draw itself if there is
        if self.occupant:
            self.occupant.draw()
            
    def isFree(self):
        """
        Return True if a piece could be moved on to this tile. 
        Return False if this is a wall, or there is already a piece here.
        """
        if self.tileType == 'w' or self.occupant is not None:
            return False
        else:
            return True
        
    def removePiece(self):
        """
        Remove the occupant from the tile. This sets the tile's occupant 
        property to None and also removes the occupant's reference to the 
        tile at the same time.
        """
        piece = self.occupant
        self.occupant = None
        if piece is not None:
            piece.tile = None
        return piece

    def addPiece(self, piece):
        """
        This adds a piece to the tile.
        
        It updates the tile's occupant property and gives the piece 
        a reference to itself.
        """
        self.occupant = piece
        piece.tile = self

    def getNeighbor(self, direction):
        """
        This gets the immediate neighbor of the tile in one of the 
        four cardinal directions: 'N', 'S', 'E', or 'W'. 
        
        To do this, it calculates the new x,y location of the 
        neighboring tile based on this tile's x,y position, and 
        then asks the game board which tile that location corresponds to
        using the getTile() method.
        """
        
        if direction == 'N':
            return game.getTile(self.x, self.y -1)
        if direction == 'S':
            return game.getTile(self.x, self.y +1)
        if direction == 'W':
            return game.getTile(self.x-1, self.y)
        if direction == 'E':
            return game.getTile(self.x +1, self.y)
            
           
class Box():
    """
    This class describes the Box objects.
    
    Boxes do not have much to do. They are moved around by the 
    other objects on the board. The only property that they have 
    is the tile that they are currently on.
    
    The only method they provide is draw(), which provides 
    the visual representation.
    """
    
    def __init__(self):
        """
        Initialize the Box and make it valid.
        
        We start by setting the tile to None (i.e., nothing). 
        When we put the piece on the board, this will be updated.
        """
        self.tile = None
    
    def draw(self):
        """
        Draw the visual representation of the Box.
        """
        rectMode(CENTER)
        fill(160, 160, 160)
        rect(0, 0, CELL_SIZE-2, CELL_SIZE-2)
        if self.tile.goal == True:
            fill(255, 0, 0)
            rect(0, 0, CELL_SIZE-2, CELL_SIZE-2)
        

class Player():
    """
    This class describes the Player class.
    
    The Player object has a little more functionality than the other pieces.
    In addition to the tile the player is currently on, the player also 
    maintains a reference to the main game board so that it can interact 
    with the game.
    """
    def __init__(self, gameBoard):
        """
        Initialize the player.
        """
        self.gameBoard = gameBoard
        self.tile = None
        
        
    def draw(self):
        """
        Draw the visual representation of the Player.
        """
        rectMode(CENTER)
        fill(178, 102, 255)
        rect(0, 3, CELL_SIZE-13, CELL_SIZE-13)
        fill(0, 204, 204)
        ellipse(0, -7, CELL_SIZE-16, CELL_SIZE-16)
        

    def move(self, direction):
        """
        This function is called in response to a key press event.  
        """
        
        destination = self.tile.getNeighbor(direction)  #gives you the coordinates of the neighbor tile
        if destination.isFree() == True:   #check if there is an occupant on the neighbor tile
            game.movePiece(self, direction) #moves the player 
        elif destination.tileType == 'o':
            game.movePiece(destination.occupant, direction) #moves the box 
            game.movePiece(self, direction) #need to move the box next to the player to clear the way for the player to move to the neighboring tile, this moves the player
        else:
            game.movePiece(self, direction) #try to move player if there is a wall in the way then can't move
        


class SokobanBoard:
    """
    This class represents our game.
    
    The class is responsible for reading in the data files, 
    holding the game board and managing game play.
    
    The class has four pieces of data that it maintains:
    
    grid - a 2D list of Tile objects that represents the game board; 
    The tiles are arranged in the list just as they should be drawn
    
    boxes - a list of all of the Box objects currently on the board
    
    player - a Player object
    
    level - the current level number
    
    """
    
    
    # Constants - these are used to help read the data files
    # most are providing the interpretation of the characters you will find in the files
    OPEN = ' '
    WALL = '#'
    PLAYER = '@'
    BOX = '$'
    GOAL = '.'       # should have a box on it by the end
    BOXGOAL = '*'    # a goal that already has a box on it
    MAX_LEVEL = 90
    
    def __init__(self):
        """
        Initialize the game board. This sets the first level, creates an empty list LAST_MOVE, and calls loadLevel() to read the file for the next level
        """
        
        self.level = 0   
        self.loadLevel()
        self.LAST_MOVE = []

    def loadLevel(self):
        """
        This function loads the current level, reading the description 
        from the appropriate input file.
        """

        # reinitialize the collection of tiles and the obstacles
        self.grid = []
        self.boxes = []
      
        # read the data in from the correct file
        fname = os.path.join('levels', 'level.%02d.txt' % self.level)
       
        try:
           f = open(fname)
           data = []
           self.cols = 0
           for line in f:
               line = line.rstrip('\n')
               if len(line) > self.cols:
                   self.cols = len(line)
               data.append(line)
               
           f.close()
           self.rows = len(data)

           # Use the textual data to construct the maze and place the objects.
           # At the end we should have a 2D list of tiles and all of the pieces
           # in place on the board. 
           for y in range(self.rows):
             
               row = []
               for x in range(self.cols):
                    if x < len(data[y]):
                       squareType = data[y][x]
                    else:
                       squareType = self.OPEN
                    
                    if squareType == self.WALL:
                        # tile is a wall
                        tile = Tile('w', x,y, self)
                    else:
                        # tile is open, but might have something there
                        tile = Tile('o', x,y, self)
                     
                        if squareType == self.PLAYER:
                            # tile has the player on it
                            self.player = Player(self)
                            tile.addPiece(self.player)
                            
                        if squareType == self.GOAL or squareType == self.BOXGOAL:
                            # tile is a goal
                            tile.goal = True
                            
                        if squareType == self.BOX or squareType == self.BOXGOAL:
                            # tile has a Box on it
                            box = Box()
                            tile.addPiece(box)
                            self.boxes.append(box)

                    row.append(tile)    
               self.grid.append(row)   
        

        except IOError:
            # Some error handling if the file containing the maze can't be found.
            # If you see these messages, you probably have misplaced the levels folder.
            print("Error: cannot open " + fname)
            print("You need to have the 'levels' folder in this folder")
            print("Current folder is:")
            print(os.getcwd())
            sys.exit(1) 
    
    def getTile(self, x, y):
        """
        This is a convenience function to make it easier to access a 
        particular tile in the grid.
        """
        return self.grid[y][x]
        
    def movePiece(self, piece, direction):
        """
        Move a piece (either the player or a box) one step in one of the four 
        cardinal directions: 'N','E','S', or 'W' if it is possible. 
        """
        destination = piece.tile.getNeighbor(direction)
        if destination.isFree() == True:  #check if neighbor tile is free
            piece.tile.removePiece() #remove the piece
            destination.addPiece(piece)   #add the piece

            
    def levelComplete(self):
        """
        This function returns True if the level is complete, and False if it is not.
        (The level is complete when every box is on a goal tile.)
        """
        for box in self.boxes:
            if box.tile.goal is not True:
                return False 
        return True
        
        
    def draw(self):
        """
        This is the master draw function that is called by pyprocessing's event handler.
        This sets the background color, centers the board and then draws each tile. 
        """
        background(0,0,0)  
        
        translate(WIDTH//2- (len(self.grid[0])//2)*CELL_SIZE, HEIGHT//2- (len(self.grid)//2)*CELL_SIZE)        
        
        for row in self.grid:
            for tile in row:
                pushMatrix()
                translate(tile.x*CELL_SIZE, tile.y*CELL_SIZE)
                tile.draw()
                popMatrix()
        

   
    def keyPressed(self):
        """
        This is an event handler that responds to keys being typed by the user.
        
        This is setup so that the arrow keys control the player's movements and the 'n' and 
        'p' keys can be used to visit different levels. 'u' can be used to undo the players moves.
        """
        if key.code == UP: #UP arrow
            self.player.move('N')
            self.LAST_MOVE.append('N')
            
        elif key.code == DOWN: #DOWN arrow
            self.player.move('S')
            self.LAST_MOVE.append('S')
            
        elif key.code == RIGHT: #RIGHT arrow
            self.player.move('E')
            self.LAST_MOVE.append('E')
            
        elif key.code == LEFT: #LEFT arrow
            self.player.move('W')
            self.LAST_MOVE.append('W')
            
        elif key.char in 'nN' and self.level < self.MAX_LEVEL:
            self.level += 1
            self.loadLevel()
            
        elif key.char in 'pP' and self.level > 0:
            self.level -= 1
            self.loadLevel()
            
        elif key.char in 'uU': #undo function. press u 
            if len(self.LAST_MOVE) > 0:
                print(self.LAST_MOVE)
                temp = self.LAST_MOVE[-1] #store the last move as the last element in LAST_MOVE list
                if temp == "N": #if last move is N, 
                    self.player.move ("S") #move player south
                    del self.LAST_MOVE[-1] #remove the last move from the list
                elif temp == "S":
                    self.player.move ("N")
                    del self.LAST_MOVE[-1]
                elif temp == "E":
                    self.player.move ("W")
                    del self.LAST_MOVE[-1]
                elif temp == "W":
                    self.player.move ("E")
                    del self.LAST_MOVE[-1]
           
        # Check whether the level is complete here
        if self.levelComplete() == True:
            self.level += 1
            self.loadLevel()
            
        
if __name__ == '__main__':
    """
    This makes this collection of classes into an actual application. 
    It creates a new game board and hooks up the event handlers.
    """
    frameRate(30)
    size(WIDTH, HEIGHT)
    game = SokobanBoard()
    draw = lambda: game.draw()
    keyPressed = lambda: game.keyPressed()

run()

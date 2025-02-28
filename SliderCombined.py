import pygame
from math import sin, cos, radians
import time
import ctypes
import os


pygame.init()
clock = pygame.time.Clock()



#Sets the screen dimensions
ScreenHeight = ctypes.windll.user32.GetSystemMetrics(1)
RookVertex = int(ScreenHeight/24)
WIDTH = 11 * RookVertex
HEIGHT = 21 * RookVertex

#Sets up the display screen
DisplaySurface = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Dusty Tome of Many Answers")

#Sets the gameplay loop value to be able to exit once set to False
CurrentlyRunning = True

#Abbreviations for possible directions in the grid: north, east, south, west
Direction = ["n", "e", "s", "w"]

#Easy indication in Grid to indicate edges
EDGE = [1,2,3,4]

#The graphic files
RookImage = pygame.transform.scale(pygame.image.load('Rook2Updated.png'), (RookVertex ,RookVertex))
RookBackup = RookImage.copy()
GridImage = pygame.transform.scale(pygame.image.load('BgUpdated.png'), (WIDTH, HEIGHT))
#font = pygame.font.Font('Enchant.otf', RookVertex * 2)
textY, textX = int(RookVertex/3), (RookVertex * 9)


#Button presses(WASD)
EventKeys = [pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a]

#Button lockout mechanism, I hate everything about this
KeyLock = 0


#Move counter information
MoveCounter = 0
MoveCap = 35
MovesMade = ""


"""############################################
################# THE GRID ####################
############################################"""




#Initialises the Supergrid which contains all information to execute the rook movements, animations and check legality of moves
GridLayout = [                                                                                                  
    #                                                                           Rotates by n config in direction by index (NESW)
    #                                                                                                                  Animation values as (Origin, Radius,
    #Rook config                                                                                                       degrees to turn, initial degree position, 
    #          Inhibits config NESW                           connects to cell NESW                       Y,X pos      clockwise/counterclockwise)
    [0,        [EDGE, [], EDGE, []],                          [0,2,0,7],        [-2, 3],                  [3,1],       [[3,3], 2, 180, 90, 1]         ],
    [0,        [EDGE, [], EDGE, []],                          [0,5,0,1],        [1, 1],                   [5,1],       [[5,3], 2, 90, 90, 0]          ],
    [2,        [EDGE, EDGE, [], EDGE],                        [0,0,6,0],        [0, None],                [9,1],       [None]                         ],
    
    [0,        [EDGE, [], [], EDGE],                          [0,5,8,0],        [0, None],                [5,3],       [None]                         ],
    [0,        [[], [], EDGE, []],                            [2,6,0,4],        [-1, 0],                  [7,3],       [[5,3], 2, 90, 0, 1  ]         ],
    [0,        [[], EDGE, [1,4], []],                         [3,0,10,5],        [0, None],                [9,3],       [None]                         ],
    
    [0,        [EDGE, [], EDGE, []],                          [0,8,0,1],        [2, 3],                   [3,5],       [[3,3], 2, 180, 270, 0]        ],
    [0,        [[], [1,2], EDGE, []],                         [4,9,0,7],        [0, None],                [5,5],       [None]                         ],
    [0,        [EDGE, [3,4], [2,3], [1,2]],                   [0,10,13,8],       [0, None],                [7,5],       [None]                         ],
    [0,        [[1,4], EDGE, [1,4], [3,4]],                   [6,0,14,9],       [0, None],                [9,5],       [None]                         ],
    
    [0,        [EDGE, [3,4], [], EDGE],                       [0,12,15,0],      [-1, 2],                  [3,7],       [[5,7], 2, 90, 180, 1]         ],
    [0,        [EDGE, [], [2,3], [3,4]],                      [0,13,15,11],     [0, None],                [5,7],       [None]                         ],
    [0,        [[2,3], EDGE, [], []],                         [9,0,16,12],      [0, None],                [7,7],       [None]                         ],
    [0,        [[1,4], EDGE, [], EDGE],                       [10,0,17,0],       [0, None],                [9,7],       [None]                         ],
    
    [0,        [[2,3], EDGE, [1,4], []],                      [12,0,19,11],     [1,3],                    [5,9],       [[5,7], 2, 90, 270, 0]         ],
    [0,        [[], [1,2], [2,3], EDGE],                      [13,17,20,0],     [0, None],                [7,9],       [None]                         ],
    [0,        [[], EDGE, [1,4], [1,2]],                      [14,0,21,16],     [0, None],                [9,9],       [None]                         ],
    
    [0,        [EDGE, [1,2], [], EDGE],                       [0,19,22,0],      [0, None],                [3,11],      [None]                         ],
    [0,        [[1,4], [], EDGE, [1,2]],                      [15,20,0,18],     [0, None],                [5,11],      [None]                         ],
    [0,        [[2,3], EDGE, [1,4], []],                      [16,0,24,19],     [0, None],                [7,11],      [None]                         ],
    [0,        [[1,4], EDGE, [2,3], EDGE],                    [17,0,24,0],      [1,2],                    [9,11],      [[7,11], 2, 90, 0, 0]          ],
    
    [0,        [[], [1,2], [2,3], [3,4]],                     [18,23,25,25],    [-2,3],                   [3,13],      [[3,14], 1, 180, 90, 1]        ],
    [0,        [EDGE, [1,2], [1,4], [1,2]],                   [0,24,26,22],     [0, None],                [5,13],      [None],                        ],
    [0,        [[1,4], [3,4], [], [1,2]],                     [20,21,27,23],    [-1, 1],                  [7,13],      [[7,11], 2, 90, 270, 1]        ],
    
    [0,        [[2,3], [3,4], [1,4], [1,2]],                  [22,26,28,22],    [2,3],                    [3,15],      [[3,14], 1, 180, 270, 0]       ],   
    [0,        [[1,4], [1,2], [], [3,4]],                     [23,27,29,25],    [0, None],                [5,15],      [None]                         ],
    [0,        [[], [3,4], [], [1,2]],                        [24,29,30,26],    [3,1],                    [7,15],      [[7,17], 2, 270, 90, 0]        ],
    
    [0,        [[1,4], EDGE, EDGE, EDGE],                     [25,0,0,0],       [0, None],                [3,17],      [None]                         ],
    [0,        [[], [], [2,3], EDGE],                         [26,30,27,0],     [-3,2],                   [5,17],      [[7,17], 2,  270, 180, 1]      ],
    [0,        [[], EDGE, EDGE, []],                          [27,0,0,29],      [0, None],                [7,17],      [None]                         ] 
    
    #This is my son, he might be ugly, but he is strong and will manage to complete the duties I ask of him 
    
    ]

    



def KeyPressDirectionProcesser(CheckingCell, PressedKey, BoyLeft, BoyTop, text):
    global KeyLock
    global MoveCounter
    
    if CheckingCell[2][PressedKey] != 0 and GridWalker(Direction[PressedKey]) == True:
        KeyLock = 5
        MoveCounter += 1
        
        #IF the chosen directions leads to another cell (connected cell is not 0, but 7 for example)
        #And Gridwalker returns True because the move is legal (Not inhibited by inhibitors)
         
        if CheckingCell[3][1] != PressedKey:
            #Linear animation
            for pixel in range(RookVertex):  #2 because the rook 'skips' a cell    [ROOK][VOID][ROOK]
                KeyOverride = 1 #WHYWHYWHWYHWYWHWYWHWYHWYWHWYWHWYWHYWHWYWHYWHWYWHWH
                DirectionAnimationGrid =[
                                        [(BoyLeft, BoyTop-2 * pixel)],
                                        [(BoyLeft+ 2* pixel, BoyTop)],
                                        [(BoyLeft, BoyTop + 2 * pixel)],
                                        [(BoyLeft- 2 * pixel, BoyTop)]
                                        ]
                clock.tick(RookVertex * 3)    #Why dependent on RookVertex? Don't know, but let's keep it that way to stop fucking with button lockouts
                DisplaySurface.blit(GridImage, (0,0))      
                DisplaySurface.blit(RookImage, DirectionAnimationGrid[PressedKey][0])
                DisplaySurface.blit(text, (textY, textX))
                pygame.display.flip()

            
                
        if CheckingCell[3][1] == PressedKey:
            #Rotational animation               
                
            CurrentCell = CheckingCell[5]
            Origin =         ((CurrentCell[0][0] * RookVertex), (CurrentCell[0][1] * RookVertex))
            Radius =          CurrentCell[1] * RookVertex 
            DegreesToTurn =   CurrentCell[2]
            TurningFrom =     CurrentCell[3]
            DirectionToTurn = CurrentCell[4]
                
            RotatorCount = 0
                
            for Degree in range(DegreesToTurn+1):
                clock.tick(150)
                
                SpinDirection = [360-Degree, Degree]
                RotationDirection = [360 - Degree + DegreesToTurn, Degree + (360-DegreesToTurn)]
                
                                              
                #Rotating Rook hugbox 
                RotationHugExpansion = (sin(radians(RotatorCount)) + cos(radians(RotatorCount)))
                Adjuster = ((RotationHugExpansion * RookVertex) - RookVertex)/2
                
                #Combined rotation, links back to the two lists above (SpinDirection, RotationDirection)
                RotatedRook = pygame.transform.rotate(RookImage, RotationDirection[DirectionToTurn])
                PipX = (cos(radians(SpinDirection[DirectionToTurn]+TurningFrom)) * Radius + Origin[0])
                PipY = (Origin[1] * 2) - (sin(radians(SpinDirection[DirectionToTurn]+TurningFrom)) * Radius + Origin[1])

                #Real fuckin' graceful way to reset the hugbox as soon as 90 degrees have been turned
                RotatorCount += 1
                if RotatorCount == 90:
                    RotatorCount = 0
                    

                DisplaySurface.blit(GridImage, (0,0)) 
                DisplaySurface.blit(RotatedRook, (PipX - Adjuster, PipY - Adjuster))
                DisplaySurface.blit(text, (textY, textX))
                pygame.display.flip()




    

def GridWalker(Move):
    global RookImage
    global MovesMade
    #Find the cell with a rook, which should be the only non-zero value at index 0 of any cell in the list
    #If you have two rooks, may God have mercy on your memory
    
    for Cell in GridLayout:
        if Cell[0] != 0:
            #Construct the Cell
            Rook = Cell[0]
            Inhibitors = Cell[1]
            Connectors =  Cell[2]
            Rotator = Cell[3]
                          
            #First the input is checked to confirm it is a possible NESW move
            #Then, if the configuration of the rook is evaluated together with the inhibitors of the path it wishes to travel, if it is impossible, it means the solution is a dead end
            #If the move is possible, it is made and the rook position and configuration is updated, the current cell rook value is set to 0, as the rook leaves this cell
            #Lastly, if the final cell contains a rook, it means the puzzle is solved

            if Move in Direction:
                if Rook in Inhibitors[Direction.index(Move)]:
                    break
                else:
                    MovesMade += Move
                    Cell[0] = 0
                    if Cell[3][0] != 0 and Move == Direction[Cell[3][1]]:
                        #Checks the cell for any rotational values
                        Rook = (Rook + Cell[3][0])%4
                        RookImage = pygame.transform.rotate(RookImage, -90 * int(Cell[3][0]))
                        if Rook == 0:
                            Rook = 4
                    GridLayout[Cell[2][Direction.index(Move)]-1][0] = Rook
                return True
                break




#Main Gameplay Loop
while CurrentlyRunning == True:
    text = font.render((str(MoveCap - MoveCounter) + '/' + str(MoveCap)), True, (160, 134, 75), None)

    
    
    if MoveCounter == MoveCap:
        #Resets the game if max moves are met
        for Line in GridLayout:
            #Remove all rooks
            Line[0] = 0        
        #Add the rook back at the start
        GridLayout[2][0] = 2
        #Reset MoveCounter
        MoveCounter = 0
        #Set the rook back to config 2
        RookImage = RookBackup
        MovesMade = ""



    #Draws the first layer of the scene, which is the background
    DisplaySurface.blit(GridImage, (0,0))
    if KeyLock > 0:
        KeyLock -= 1
   
    
    for CheckingCell in GridLayout:
        #As with GridWalker, this checks for the very first instance of a rook-occupied cell, then uses it as a variable, saving the x and y coordinates and drawing it
        if CheckingCell[0] != 0:
            BoyLeft = (CheckingCell[4][0] * RookVertex) 
            BoyTop = (CheckingCell[4][1] * RookVertex) 
            break
    
    DisplaySurface.blit(RookImage, (BoyLeft, BoyTop))
    
    for event in pygame.event.get():       
        
        if event.type == pygame.QUIT:
            #Shuts down the program
            CurrentlyRunning = False
        if event.type == pygame.KEYDOWN and KeyLock == 0:                                   
            #Based on the WASD press, several things happen.
            #Firstly, the legality of the move is tested by making sure the current cell connects to a cell in the given direction (CheckingCell[2][index of direction] cannot be 0)
            #Then, GridWalker is executed for the given direction, if GridWalker can be exectuted (returns True), then the Rook moving is animated using a for loop
            #Lastly, if the win condition (Rook made it to the last cell) isn't met, the while Gameplay Loop wraps around and the updated Rook position is drawn
            #Essentially, the whole animation works like this:
            #    Draw the Rook at the location indicated in the GridLayout
            #    Continuously overwrite the scene with a background, followed by a slightly updated Rook frame (updated by a pixel in either x or y direction)
            #    Overwrite the whole scene with a background, instantly redraw the Rook at the location indicated in the GridLayout
            #    Rinse, repeat
            
            if event.key in EventKeys:
                KeyPressDirectionProcesser(CheckingCell, EventKeys.index(event.key), BoyLeft, BoyTop, text)



    #Show amount of slides left
    DisplaySurface.blit(text, (textY, textX))
             
                
      
    #Initial setup of the scene and later refreshes
    pygame.display.flip()
    
    #Checks to see if the target cell is reached by considering the Rook value at the index of the cell, any other value than 0 indicates a Rook is in the cell
    if GridLayout[27][0] != 0:
        CurrentDir = os.getcwd()
        
        with open(CurrentDir + '\\I_Solved_It.txt', 'w') as Sequence:
            Sequence.write(MovesMade)
            Sequence.write("\nAfter inputting the above sequence, you manage to retrieve the key!")
            
        Sequence.close()
        
        CurrentlyRunning = False
        
        
    
    
pygame.quit()

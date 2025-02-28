"""
A Better Grid Solver that is based on A*
Based on a set Path max length, the script tries to propogate through the Grid, discarding dead ends each iteration
It can either run ALL paths to a win condition (including double takes) or cut off as soon as it finds a path
"""

#The function refers to these for positional checks
EDGE = [1,2,3,4]
NESW = ['n', 'e', 's', 'w']
RookConfigs = [1,2,3,4]


#    Cell_i, Rook, Path, LastCell_i            
StartCondition = [[2, 2, "", None]]           #Where and how the Rook is placed in the Grid, Path and LastCell_i will be empty (no path or last cell yet)
TargetCell = 27
MaxPathLength = 100
Fast = True                                  #If True, gets the fastest path and stops the script, if False, lists all paths (double takes included)



#Input Grid, no Rook is required
GridLayout = [
    [0,        [EDGE, [], EDGE, []],                          [0,2,0,7],        [-2, 3],                  [3,1],       [[3,3], 2, 180, 90, 1]         ],
    [0,        [EDGE, [], EDGE, []],                          [0,5,0,1],        [1, 1],                   [5,1],       [[5,3], 2, 90, 90, 0]          ],
    [0,        [EDGE, EDGE, [], EDGE],                        [0,0,6,0],        [0, None],                [9,1],       [None]                         ],
    
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
    ]



def GeneratePath(StartingCells):
    # A* ish search function
    
    ReturnCells = [] 
    
    for StartPoint in StartingCells:
        Cell = GridLayout[StartPoint[0]]   #This is the whole cell entry
        Cell_i = StartPoint[0]             #This is the index of the cell in the grid
        LastCell_i = StartPoint[3]         #The last cell_i to negate travelbacks
        
        for Direction in range(0,4): #try NESW directions
            Path = StartPoint[2]               #The path so far (str)
            Rook = StartPoint[1]               #The Rook config that is passed through and updated as needed
            if Rook not in Cell[1][Direction]:  #Targets inhibitor list
                
                if Cell[2][Direction] - 1 != LastCell_i or Cell[3][1] == Direction:
                    """This does allow rooks to pong back and forth across a rotation, but also allows rotations back to a previous cell (rook is now rotated)"""
                    GotoCell_i = Cell[2][Direction] - 1
                    Path += NESW[Direction]
                
                    if Cell[3][1] == Direction: #This means there is rotation, and rook needs to be updated
                        Rook = RookConfigs[(RookConfigs.index(Rook) + Cell[3][0]) % 4]

                    ReturnCells.append([GotoCell_i, Rook, Path, Cell_i])
                    
                    if GotoCell_i == TargetCell:
                        """
                        Depending on whether or not you want to print ALL paths (double takes/rotation ping pongs allowed)
                        Or just want a single, fastest solution printed
                        Enable/Disable the quit() call by setting Fast to True/False
                        """
                        print("PATH FOUND:", Path, " STEP LENGTH: ", len(Path), Rook)
                        if Fast:
                            quit()

    return ReturnCells




for Step in range(MaxPathLength):
    StartCondition = GeneratePath(StartCondition)
    

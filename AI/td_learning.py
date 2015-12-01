import math, heapq, sys, pickle
from Player import *
from Construction import Construction
from Ant import Ant
from AIPlayerUtils import *

##
# AIPlayer
#
# Description: The responsibility of this class is to interact with the game by
#   deciding a valid move based on a given game state. This class has methods that
#   will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#    playerId - The id of the player.
##
class AIPlayer(Player):

    ##
    # __init__
    #
    # Description: Creates a new AI Player that uses the Minimax algorithm
    #   and maintains a neural network.
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        # initialize the AI in the game
        super(AIPlayer,self).__init__(inputPlayerId, "Tadah, I'm Learning")

        # reference to AIPlayer's anthill structure
        self.playerAnthill = None

        # initialize our food location tracker to be empty
        self.foodList = []

        # neural network node values
        self.nodes = []

        # # initialize the neural network
        # if LOAD_WEIGHTS_FROM_FILE:
        #     # use weights previously saved to a file
        #     f = open("jorgense12_asuncion16_hw8.p", 'rb')
        #     weightsFromFile = pickle.load(f)
        #     self.firstWeights = weightsFromFile[0]
        #     self.secondWeights = weightsFromFile[1]
        #     f.close()
        # else:
        #     print "Finding best weights... (takes a long time)"
        #     # use random weights
        #     self.initNetworkWeights()

    ##
    # getSimpleState
    #
    # Description: Creates a simplified (consolidated) representation of a
    #   GameState object to be used for TD-Learning.
    #
    # Return: A list of integers representing the GameState
    ##
    def getSimpleState(self, state):
        # make some references to player inventories and the queens
        playerInv = state.inventories[state.whoseTurn]
        workerList = getAntList(state, state.whoseTurn, [WORKER])
        enemyInv = state.inventories[1 - state.whoseTurn]
        playerQueen = playerInv.getQueen()
        enemyQueen = enemyInv.getQueen()

        # INT 0: defeat state (true/false)
        if playerQueen is None or enemyInv.foodCount >= 11:
            int0 = 1
        else:
            int0 = 0

        # INT 1: victory state (true/false)
        if enemyQueen is None or playerInv.foodCount >= 11:
            int1 = 1
        else:
            int1 = 0

        # INT 2: player queen is on anthill (true/false)
        if playerQueen and playerQueen.coords == self.playerAnthill:
            int2 = 1
        else:
            int2 = 0

        # INT 3: player queen's Y-coordinate
        if playerQueen:
            int3 = playerQueen.coords[1]
        else:
            int3 = 0

        # INT 4: number of workers
        int4 = min([2, len(workerList)])

        # INT 5: worker 1 distance to enemy queen
        if enemyQueen and len(workerList) > 0:
            int5 = (abs(workerList[0].coords[0] - enemyQueen.coords[0]) +
                              abs(workerList[0].coords[1] - enemyQueen.coords[1]))
        else:
            int5 = 0

        # INT 6: worker 2 distance to enemy queen
        if enemyQueen and len(workerList) > 1:
            int6 = (abs(workerList[1].coords[0] - enemyQueen.coords[0]) +
                              abs(workerList[1].coords[1] - enemyQueen.coords[1]))
        else:
            int6 = 0

        # INT 7: enemy queen health
        if enemyQueen:
            int7 = enemyQueen.health
        else:
            int7 = 0

        return int0,int1,int2,int3,int4,int5,int6,int7

    ##
    # getReward
    #
    # Description: Finds the reward value for being in a particular simple state.
    #
    # Parameters:
    #   stateTup - A tuple representing a simple/consolidated GameState
    #
    # Return: The reward value for the state (float)
    ##
    def getReward(self, stateTup):
        if stateTup[0] == 1:
            return -1.
        elif stateTup[1] == 1:
            return 1.
        else:
            return -.01

    ##
    # getFutureState
    #
    # Description: Simulates and returns the new state that would exist after
    #   a move is applied to current state
    #
    # Parameters:
    #   currentState - The game's current state (GameState)
    #   move - The Move that is to be simulated
    #
    # Return: The simulated future state (GameState)
    ##
    def getFutureState(self, currentState, move):
        # create a bare-bones copy of the state to modify
        newState = currentState.fastclone()

        # get references to the player inventories
        playerInv = newState.inventories[newState.whoseTurn]
        enemyInv = newState.inventories[1 - newState.whoseTurn]

        if move.moveType == BUILD:
        # BUILD MOVE
            if move.buildType < 0:
                # building a construction
                playerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                playerInv.constrs.append(Construction(move.coordList[0], move.buildType))
            else:
                # building an ant
                playerInv.foodCount -= UNIT_STATS[move.buildType][COST]
                playerInv.ants.append(Ant(move.coordList[0], move.buildType, newState.whoseTurn))

        elif move.moveType == MOVE_ANT:
        # MOVE AN ANT
            # get a reference to the ant
            ant = getAntAt(newState, move.coordList[0])

            # update the ant's location after the move
            ant.coords = move.coordList[-1]
            ant.hasMoved = True

            # get a reference to a potential construction at the destination coords
            constr = getConstrAt(newState, move.coordList[-1])

            # check to see if a worker ant is on a food or tunnel or hill and act accordingly
            if constr and ant.type == WORKER:
                # if destination is food and ant can carry, pick up food
                if constr.type == FOOD:
                    if not ant.carrying:
                        ant.carrying = True
                # if destination is dropoff structure and and is carrying, drop off food
                elif constr.type == TUNNEL or constr.type == ANTHILL:
                    if ant.carrying:
                        ant.carrying = False
                        playerInv.foodCount += 1

            # get a list of the coordinates of the enemy's ants
            enemyAntCoords = [enemyAnt.coords for enemyAnt in enemyInv.ants]

            # contains the coordinates of ants that the 'moving' ant can attack
            validAttacks = []

            # go through the list of enemy ant locations and check if
            # we can attack that spot, and if so add it to a list of
            # valid attacks (one of which will be chosen at random)
            for coord in enemyAntCoords:
                if UNIT_STATS[ant.type][RANGE] ** 2 >= abs(ant.coords[0] - coord[0]) ** 2 + \
                                                       abs(ant.coords[1] - coord[1]) ** 2:
                    validAttacks.append(coord)

            # if we can attack, pick a random attack and do it
            if validAttacks:
                enemyAnt = getAntAt(newState, random.choice(validAttacks))
                attackStrength = UNIT_STATS[ant.type][ATTACK]

                if enemyAnt.health <= attackStrength:
                    # just to be safe, set the health to 0
                    enemyAnt.health = 0
                    # remove the enemy ant from their inventory
                    enemyInv.ants.remove(enemyAnt)
                else:
                    # lower the enemy ant's health because they were attacked
                    enemyAnt.health -= attackStrength

        # return the modified copy of the original state
        return newState

    ##
    # evaluateState
    #
    # Description: The evaluateState method looks at a state and
    #   assigns a value to the state based on how well the game is
    #   going for the current player
    #
    # Parameters:
    #   currentState - The State to evaluate
    #
    # Return: The score of the state on a scale of 0.0 to 1.0
    #   where 0.0 is a loss and 1.0 is a victory and 0.5 is neutral
    ##
    def evaluateState(self, state):
        # local constants for adjusting weights of evaluation
        QUEEN_EDGE_MAP_WEIGHT = 0.01
        BUILD_WORKER_WEIGHT = 0.1
        MOVE_TOWARDS_QUEEN_WEIGHT = 0.005
        QUEEN_HEALTH_WEIGHT = 0.025
        QUEEN_ON_HILL_WEIGHT = 0.1

        # get some references for use later
        playerInv = state.inventories[state.whoseTurn]
        enemyInv = state.inventories[1 - state.whoseTurn]
        enemyQueen = enemyInv.getQueen()

        # start the score at a semi-neutral value
        score = 0.4

        # check each of the player's ants
        for ant in playerInv.ants:
            if ant.type == QUEEN:
                # keep the queen off of the anthill
                if ant.coords == self.playerAnthill:
                    score -= QUEEN_ON_HILL_WEIGHT
                # keep the queen at the edge of the map
                score -= QUEEN_EDGE_MAP_WEIGHT * ant.coords[1]
            elif ant.type == WORKER:
                # encourage building more workers
                score += BUILD_WORKER_WEIGHT
                if enemyQueen:
                    # move workers towards queen
                    score -= MOVE_TOWARDS_QUEEN_WEIGHT * (abs(ant.coords[0] - enemyQueen.coords[0]) +
                                                          abs(ant.coords[1] - enemyQueen.coords[1]))

        if enemyQueen:
            # encourage damaging the enemy queen
            score += QUEEN_HEALTH_WEIGHT * (UNIT_STATS[QUEEN][HEALTH] - enemyQueen.health)
        else:
            score += QUEEN_HEALTH_WEIGHT * UNIT_STATS[QUEEN][HEALTH]

        # return the evaluation score of the state
        return score
           
    ##
    # getPlacement
    #
    # Description: called twice during setup phase to place objects that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #
    # Return: A list of coordinates of where the constructions are to be placed
    ##
    def getPlacement(self, currentState):
        self.foodList = []
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move is None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                        if i == 0:
                            self.playerAnthill = move
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move is None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    # getMove
    #
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):        
        # #fill the food locations list
        # if not self.foodList:
        #     for f in getConstrList(currentState, NEUTRAL, (FOOD,)):
        #         self.foodList.append(f)
        #
        # self.setNeuralInputs(currentState)

        # # create a root node to build our search tree from
        # rootNode = treeNode.copy()
        # rootNode["potential_state"] = currentState

        # return the best move, found by recursively searching potential moves
        #best = self.exploreTree(rootNode, 0)["move"]
        best = max([(self.evaluateState(self.getFutureState(currentState, m)), m) for m in listAllLegalMoves(currentState)])[1]
        if best.moveType == END:
            print "END TURN"
        else:
            print "SIMPLE: %s" % (self.getSimpleState(self.getFutureState(currentState, best)),)
        return best

    ##
    # getAttack
    #
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # attack a random enemy
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]
        
    ##
    # registerWin
    #
    # Description: Tells the player if they won or not
    #
    # Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):
        pass

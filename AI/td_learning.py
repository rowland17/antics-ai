import math, pickle
from Player import *
from Construction import Construction
from Ant import Ant
from AIPlayerUtils import *

MAX_RAND_MOVES = 1000000
GAMMA = .95

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

        # states the agent has seen so far (keys) with their utilities (values)
        self.stateUtils = {}

        # number of moves made so far by TD-Learning
        self.moveCount = 0

        # number of moves made this game
        self.moveCountThisGame = 0

        # load the state utilities from file if possible
        try:
            with open("utils.p", 'rb') as f:
                data = pickle.load(f)
                self.stateUtils = data[0]
                self.moveCount = data[1]
                print "Loading utils file..."
                print `len(self.stateUtils)` + " entries loaded."
        except IOError:
            print "No utils file, starting from scratch..."

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

        # INT 0: victory state (true/false)
        if enemyQueen is None or playerInv.foodCount >= 11:
            int0 = 1
        else:
            int0 = 0

        # INT 1: player food count
        int1 = playerInv.foodCount

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
            if len(workerList) > 1:
                int5 += (abs(workerList[1].coords[0] - enemyQueen.coords[0]) +
                                  abs(workerList[1].coords[1] - enemyQueen.coords[1]))
        else:
            int5 = 0

        # INT 6: enemy queen health
        if enemyQueen:
            int6 = enemyQueen.health
        else:
            int6 = 0

        return int0,int1,int2,int3,int4,int5,int6

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
            return 1.
        else:
            return -.01

    ##
    # ###################################################################################################################
    def chooseNextMove(self, currentState):
        randChance = self.randMoveChance()
        if random.random() < randChance:
            return random.choice(listAllLegalMoves(currentState))
        else:
            legals = listAllLegalMoves(currentState)
            i = 0
            nextMove = legals[i]
            while self.getSimpleState(self.getFutureState(currentState, nextMove)) not in self.stateUtils:
                i += 1
                if i >= len(legals):
                    return random.choice(listAllLegalMoves(currentState))
                nextMove = legals[i]
            for m in legals:
                mSimple = self.getSimpleState(self.getFutureState(currentState, m))
                nextMoveSimple = self.getSimpleState(self.getFutureState(currentState, nextMove))
                if mSimple in self.stateUtils and nextMoveSimple in self.stateUtils and self.stateUtils[mSimple] > self.stateUtils[nextMoveSimple]:
                    nextMove = m
            return nextMove

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
        nextMove = self.chooseNextMove(currentState)

        simpleState = self.getSimpleState(currentState)
        util = None
        if simpleState in self.stateUtils:
            utilTup = self.stateUtils[simpleState]
            util = utilTup[0]
            stateCount = utilTup[1]
        else:
            util = self.getReward(simpleState)
            self.stateUtils[simpleState] = (util, 1)
            stateCount = 1

        nextSimpleState = self.getSimpleState(self.getFutureState(currentState, nextMove))
        if nextSimpleState in self.stateUtils:
            nextUtil = self.stateUtils[nextSimpleState][0]
        else:
            nextUtil = self.getReward(nextSimpleState)
            self.stateUtils[nextSimpleState] = (nextUtil, 1)

        self.stateUtils[simpleState] = (util + self.alpha(stateCount) * (self.getReward(simpleState) + GAMMA * nextUtil - util), stateCount + 1)

        # if nextMove.moveType == END:
        #     print "END TURN"
        # else:
        #     print "SIMPLE: %s" % (self.getSimpleState(self.getFutureState(currentState, nextMove)),)

        self.moveCount += 1
        self.moveCountThisGame += 1

        return nextMove

    ##
    # alpha
    #
    # Description: Finds the learning rate for a state given how many times
    #   we've visited it.
    #
    # Parameters:
    #   visited - The number of times we've visited the state
    #
    # Return: The alpha value for that state
    ##
    def alpha(self, visited):
        return 1./math.sqrt(1. + (visited - 1)/10.)#######################################################################################

    ##
    # randMoveChance
    #
    # Description: #######################################################################################################
    ##
    def randMoveChance(self):
        return 1. - math.sqrt(self.moveCount)/1000. if self.moveCount < MAX_RAND_MOVES else 0.##############################

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
        # for k in self.stateUtils:
        #     print `k` + `self.stateUtils[k]`
        #     print self.alpha(self.stateUtils[k][1])
        print "Util table size: " + `len(self.stateUtils)`
        print "Final move count this game: " + `self.moveCountThisGame`
        print "Total agent move count: " + `self.moveCount`
        print "Random move chance: " + `self.randMoveChance()`
        self.moveCountThisGame = 0
        try:
            with open("AI/utils.p", 'w+b') as f:
                pickle.dump((self.stateUtils, self.moveCount), f, 0)
                print "Utils written to file."
        except IOError:
            print "ERROR: Failed writing utils to file."

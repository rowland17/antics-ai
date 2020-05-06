import math, pickle
from Player import *
from Construction import Construction
from Ant import Ant
from AIPlayerUtils import *

# TD-Learning constants
TDL_RAND_MOVE_FACTOR = 1000
TDL_MAX_RAND_MOVES = TDL_RAND_MOVE_FACTOR**2
TDL_GAMMA = .95

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
                # use pickling to deserialize the saved object
                data = pickle.load(f)
                self.stateUtils = data[0]
                self.moveCount = data[1]
        except IOError:
            pass

    ##
    # getSimpleState
    #
    # Description: Creates a simplified (consolidated) representation of a
    #   GameState object to be used for TD-Learning.
    #
    # Return: A tuple of 7 integers representing the GameState
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

        # INT 5: sum of first two workers' distance to enemy queen
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

        # return simple state as a tuple
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
            # victory, return 1.0
            return 1.
        else:
            # otherwise, return -0.01
            # (we will never see a defeat state)
            return -.01

    ##
    # chooseNextMove
    #
    # Description: Finds the next move to make based on random chance or
    #   utility.
    #
    # Parameters:
    #   currentState - the GameState we are choosing a move for
    #
    # Return: The appropriate Move to make
    ##
    def chooseNextMove(self, currentState):
        moves = listAllLegalMoves(currentState)

        # decide whether to move randomly
        randChance = self.randMoveChance()
        if random.random() < randChance:
            # return a random move
            return random.choice(moves)

        # otherwise, find the best move based on utility

        # pair each move with its resulting simple-state (state, move)
        simpleStates = zip([s for s in [self.getSimpleState(self.getFutureState(currentState, m))
                                 for m in moves]], moves)

        # find the subset of simpleStates that are already in our utility table
        # and pair their utilities with the corresponding moves (utility, move)
        seenStates = [(self.stateUtils[s],m) for s,m in simpleStates if
                    s in self.stateUtils]

        if len(seenStates) > 0:
            # find the max utility simple-state and return the corresponding move
            return max(seenStates)[1]
        else:
            # all legal moves lead to unseen states, so return a random move
            return random.choice(moves)

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
        moves = []

        if currentState.phase == SETUP_PHASE_1:
            # place player buildings

            for i in range(11):
                move = None
                while move is None:
                    # find a random space on player side
                    x = random.randint(0, 9)
                    y = random.randint(0, 3)

                    # check that the space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                        if i == 0:
                            # save anthill location for later
                            self.playerAnthill = move

                # add the space to our list
                moves.append(move)
            return moves

        elif currentState.phase == SETUP_PHASE_2:
            # place enemy food

            for _ in range(2):
                move = None
                while move is None:
                    # find a random space on enemy side
                    x = random.randint(0, 9)
                    y = random.randint(6, 9)

                    # check that the space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)

                # add the space to our list
                moves.append(move)
            return moves
    
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

        # lookup current state in utility table
        simpleState = self.getSimpleState(currentState)
        if simpleState in self.stateUtils:
            # state found
            utilTup = self.stateUtils[simpleState]
            util = utilTup[0]
            stateCount = utilTup[1]
        else:
            # state not found, so add it
            util = self.getReward(simpleState)
            self.stateUtils[simpleState] = (util, 1)
            stateCount = 1

        # lookup next state (from chosen move) in utility table
        nextSimpleState = self.getSimpleState(self.getFutureState(currentState, nextMove))
        if nextSimpleState in self.stateUtils:
            # state found
            nextUtil = self.stateUtils[nextSimpleState][0]
        else:
            # state not found, so add it
            nextUtil = self.getReward(nextSimpleState)
            self.stateUtils[nextSimpleState] = (nextUtil, 1)

        # set current state's utility with the utility function
        self.stateUtils[simpleState] = (util + self.alpha(stateCount) *
                    (self.getReward(simpleState) + TDL_GAMMA * nextUtil - util), stateCount + 1)

        # increment move counters for debugging
        self.moveCount += 1
        self.moveCountThisGame += 1

        return nextMove

    ##
    # alpha
    #
    # Description: Finds the learning rate for a state given how many times
    #   we've visited it. This rate decreases with more visits.
    #
    # Parameters:
    #   visited - The number of times we've visited the state
    #
    # Return: The alpha value for that state (float)
    ##
    def alpha(self, visited):
        return 1./math.sqrt(1. + (visited - 1)/10.)

    ##
    # randMoveChance
    #
    # Description: Finds the chance of making a random move given how many
    #   total moves the learning agent has made. This chance decreases
    #   with more moves.
    #
    # Return: The chance of making a random move (0.0 to 1.0)
    ##
    def randMoveChance(self):
        if self.moveCount < TDL_MAX_RAND_MOVES:
            return 1. - math.sqrt(self.moveCount)/TDL_RAND_MOVE_FACTOR
        else:
            return 0.

    ##
    # getAttack
    #
    # Description: Gets the attack to be made by the Player.
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The locations of the enemies that can be attacked (Location[])
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
        # reset move count for debugging
        self.moveCountThisGame = 0

        # write utility table to file
        try:
            with open("AI/utils.p", 'w+b') as f:
                pickle.dump((self.stateUtils, self.moveCount), f, 0)
        except IOError:
            print ("ERROR: Failed writing utils to file.")

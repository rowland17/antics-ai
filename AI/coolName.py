
import random
import copy
import math

from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from Ant import *
from AIPlayerUtils import *

# Depth limit for ai search
DEPTH_LIMIT = 1

# weight for having at least one worker
WORKER_WEIGHT = 100000

# weight for food
FOOD_WEIGHT = 500

# weight for worker ants carrying food
CARRY_WEIGHT = 100

# weight for worker ant's dist to their goals
DIST_WEIGHT = 5

# weight for queen being off of places the worker must go
QUEEN_LOCATION_WEIGHT = 20000

# weight for every ant having moved
MOVED_WEIGHT = 1


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):


    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "WE NEED A COOL NAME")

        self.buildingCoords = [(),()]
        self.hillCoords = None
        self.foodCoords = [()]

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]


    # scoreChildrenHelper - Helper to determine overall score of branch.
    # Returns max scoring child.
    def scoreChildrenHelper(self, nodeList):
        return max(n['score'] for n in nodeList)


    ##
    #expand
    #
    #Description: Called to expand a state. Recursively examines the game tree down to
    # DEPTH_LIMIT. Passes back up a dict with a move and associated score. The move is the
    # best move to take in this situation.
    #
    #Parameters:
    #   state - The state at this place in the game tree
    #           (to start it should be the current state)
    #   playerID - Ignored for now. Should always be the current player
    #   depth - The depth the tree has been examined to. (for recursive use only)
    #
    #Return: A dict with keys 'move' and 'score'
    # move is the ideal Move()
    # score is the associated score. 0.0 is a loss. 1.0 or more is a victory.
    ##
    def expand(self, state, playerID, depth=0):

        if depth == DEPTH_LIMIT:
            # Base case for depth limit
            return {'move': Move(END, None, None), 'score': self.evaluateState(state)}

        elif self.hasWon(state, playerID):
            # Base case for victory
            # Make the final score take into account how many moves it will take to reach this
            # victory state. Winning this turn is better than winning next turn.
            return {'move': Move(END, None, None), 'score': float(DEPTH_LIMIT + 1 - depth)}

        childrenList = []

        bestMove = None
        bestScore = -1

        # expand this node to find all child nodes
        for move in listAllLegalMoves(state):

            childState = self.hypotheticalMove(state, move)
            childState.whoseTurn = self.playerId

            for inventory in childState.inventories:
                for ant in inventory.ants:
                    ant.hasMoved = False

            # Recursive step
            score = self.expand(childState, playerID, depth + 1)['score']

            childrenList.append({'move': move, 'score': score})

            if score > bestScore:
                bestMove = move
                bestScore = score

        # return this node
        return {'move': bestMove, 'score': self.scoreChildrenHelper(childrenList)}


    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):

        # Cache the list of building locations for each player
        buildings = [
            getConstrList(currentState, 0, (ANTHILL, TUNNEL)),
            getConstrList(currentState, 1, (ANTHILL, TUNNEL))
        ]

        self.buildingCoords = [
            [tuple(b.coords) for b in buildings[0]],
            [tuple(b.coords) for b in buildings[1]]
        ]

        # Cache the hill coords for each player
        self.hillCoords = [
            tuple(getConstrList(currentState, 0, (ANTHILL,))[0].coords),
            tuple(getConstrList(currentState, 1, (ANTHILL,))[0].coords)
        ]

        self.buildingCoords[0] = [tuple(b.coords) for b in buildings[0]]
        self.buildingCoords[1] = [tuple(b.coords) for b in buildings[1]]

        # Cache the locations of foods
        foods = getConstrList(currentState, None, (FOOD,))
        self.foodCoords = [tuple(f.coords) for f in foods]

        return self.expand(currentState, self.playerId)['move']


    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]


    ##
    #hypotheticalMove
    #
    #Description: Determine what the agent's state would look like after a given move.
    #             We Will assume that all Move objects passed are valid.
    #
    #Parameters:
    #   state - A clone of the theoretical state given (GameState)
    #   move - a list of all move objects passed (Move)
    #
    #Returns:
    #   What the agent's state would be like after a given move.
    ##
    def hypotheticalMove(self, state, move):
        newState = state.fastclone()

        if move.moveType == END:
            newState.whoseTurn = 1 - state.whoseTurn
            return newState

        elif move.moveType == MOVE_ANT:
            ant = getAntAt(newState, move.coordList[0])
            ant.coords = move.coordList[-1]

            #check if ant is depositing food
            if ant.carrying:
                if tuple(ant.coords) in self.buildingCoords[self.playerId]:
                    ant.carrying = False
                    newState.inventories[self.playerId].foodCount += 1

            #check if ant is picking up food
            if not ant.carrying:
                if tuple(ant.coords) in self.foodCoords:
                    ant.carrying = True


            #check if ant can attack
            targets = [] #coordinates of attackable ants
            range = UNIT_STATS[ant.type][RANGE]

            for ant in newState.inventories[1 - self.playerId].ants:
                dist = math.sqrt((ant.coords[0] - ant.coords[0]) ** 2 +
                                 (ant.coords[1] - ant.coords[1]) ** 2)
                if dist <= range:
                    #target is in range and may be attacked
                    targets.append(ant.coords)

            if targets:
                #Attack the ant chosen by the AI
                target = self.getAttack(newState, ant, targets)
                targetAnt = getAntAt(newState, target)
                targetAnt.health -= UNIT_STATS[ant.type][ATTACK]

                if targetAnt.health <= 0:
                    #Remove the dead ant
                    newState.inventories[1 - self.playerId].ants.remove(targetAnt)

            ant.hasMoved = True

        else: #Move type BUILD
            if move.buildType in (WORKER, DRONE, SOLDIER, R_SOLDIER):
                #Build ant on hill
                ant = Ant(move.coordList[0], move.buildType, self.playerId)
                newState.inventories[self.playerId].ants.append(ant)

                newState.inventories[self.playerId].foodCount -= UNIT_STATS[move.buildType][COST]
            else:
                #build new building
                building = Building(move.coordList[0], move.buildType, self.playerId)
                newState.inventories[self.playerId].constrs.append(building)

                newState.inventories[self.playerId].foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

        return newState



    ##
    # getPlayerScore
    # Description: takes a state and player number and returns a number estimating that
    # player's score.
    #
    # Parameters:
    #    hypotheticalState - The state to score
    #    playerNo          - The player number to determine the score for
    #    debug             - If this is true then the score will be returned as a dict
    # Returns:
    #    If not debugging:
    #      A float representing that player's score
    #    If debugging
    #      A dict containing the components of the player's score along with the score
    ##
    def getPlayerScore(self, hypotheticalState, playerNo, debug=False):

        workers = getAntList(hypotheticalState, playerNo, (WORKER,))

        #################################################################################
        #Score having exactly one worker

        workerCountScore = 0
        if len(workers) == 1:
            workerCountScore = WORKER_WEIGHT

        #################################################################################
        #Score the food we have

        foodScore = hypotheticalState.inventories[playerNo].foodCount * FOOD_WEIGHT


        #################################################################################
        #Score queen being off of anthill and food

        queenScore = 0

        for ant in hypotheticalState.inventories[playerNo].ants:
            if ant.type == QUEEN:
                if tuple(ant.coords) in list(self.buildingCoords[playerNo]) + self.foodCoords:
                    queenScore = -QUEEN_LOCATION_WEIGHT
                else:
                    queenScore = QUEEN_LOCATION_WEIGHT
                break


        #################################################################################
        #Score the workers for getting to their goals and carrying food

        distScore = 0
        carryScore = 0

        for worker in workers:
            if worker.carrying:
                carryScore += CARRY_WEIGHT
                goals = self.buildingCoords[playerNo]
            else:
                goals = self.foodCoords

            wc = worker.coords
            dist = min(abs(wc[0]-gc[0]) + abs(wc[1]-gc[1]) for gc in goals)

            distScore -= DIST_WEIGHT * dist

        #################################################################################
        #Score every ant having moved

        movedScore = 0

        #It is to our advantage to have every ant move every turn
        for ant in hypotheticalState.inventories[playerNo].ants:
            if ant.hasMoved:
                movedScore += MOVED_WEIGHT

        score = foodScore + distScore + carryScore + queenScore + movedScore + workerCountScore

        if debug:
            return {'f': foodScore, 'd': distScore, 'c': carryScore, 'q': queenScore,
                    'm': movedScore, 'w': workerCountScore, 'S': score}
        else:
            return score

    ##
    # hasWon
    # Description: Takes a GameState and a player number and returns if that player has won
    # Parameters:
    #    hypotheticalState - The state to test for victory
    #    playerNo          - What player to test victory for
    # Returns:
    #    True if the player has won else False.
    ##
    def hasWon(self, hypotheticalState, playerNo):

        #Check if enemy anthill has been captured
        for constr in hypotheticalState.inventories[1 - playerNo].constrs:
            if constr.type == ANTHILL and constr.captureHealth == 1:
                #This anthill will be destroyed if there is an opposing ant sitting on it
                for ant in hypotheticalState.inventories[playerNo].ants:
                    if tuple(ant.coords) == tuple(constr.coords):
                        return True
                break

        #Check if enemy queen is dead
        for ant in hypotheticalState.inventories[1 - playerNo].ants:
            if ant.type == QUEEN and ant.health == 0:
                return True

        #Check if we have 11 food
        if hypotheticalState.inventories[playerNo].foodCount >= 11:
            return True

        return False


    ##
    #evaluateState
    #
    #Description: Examines a GameState and ranks how "good" that state is for the agent whose turn it is.
    #              A rating is given on the players state. 1.0 is if the agent has won; 0.0 if the enemy has won.
    #
    #Parameters:
    #   hypotheticalState - The state being considered by the AI for ranking.
    #
    #Return:
    #   The move rated as the "best"
    ##
    def evaluateState(self, hypotheticalState):

        #Check if the game is over
        if self.hasWon(hypotheticalState, self.playerId):
            return 1.0
        elif self.hasWon(hypotheticalState, 1 - self.playerId):
            return 0.0

        playerScore = self.getPlayerScore(hypotheticalState, self.playerId)

        #Normalize the score to be between 0.0 and 1.0
        return (math.atan(playerScore/10000.) + math.pi/2) / math.pi


    ##
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):
        pass

##
# unitTest1
# Description: Tests the AIPlayer.hypotheticalMove method
# Returns:
#    False if anything is wrong else True
##
def unitTest1():
    board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
    p1Inventory = Inventory(PLAYER_ONE, [], [], 10)
    p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
    neutralInventory = Inventory(NEUTRAL, [], [], 0)

    state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)

    #Add an ant to move
    ant = Ant((0,0), WORKER, 0)
    board[0][0].ant = ant
    p1Inventory.ants.append(ant)

    player = AIPlayer(0)
    newState = player.hypotheticalMove(state, Move(MOVE_ANT, ((0,0), (0,1), (0,2)), None))
    if tuple(newState.inventories[0].ants[0].coords) != (0, 2):
        print "didn't move ant"
        return False

    #test adding a building
    newState = player.hypotheticalMove(state, Move(BUILD, ((3,3),), TUNNEL))

    if len(newState.inventories[0].constrs) == 0:
        print "didn't create construction"
        return False

    if newState.inventories[0].constrs[0].type != TUNNEL:
        print "created wrong type of construction"
        return False

    if tuple(newState.inventories[0].constrs[0].coords) != (3, 3):
        print "created construction at wrong place"
        return False

    if newState.inventories[0].foodCount != 7:
        print "didn't subtract food cost"
        return False

    return True

if unitTest1():
    print "Unit Test 1 passed!"

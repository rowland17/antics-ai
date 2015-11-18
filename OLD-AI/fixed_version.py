import math, heapq
from Player import *
from Construction import Construction
from Ant import Ant
from AIPlayerUtils import *

# set constants

MAX_DEPTH = 3
INFINITY = 9999.9
WORKER_COUNT_WEIGHT = 10000
FOOD_WEIGHT = 1000
DISTANCE_WEIGHT = 250
CARRY_WEIGHT = 500
QUEEN_EDGE_WEIGHT = 200
SET_POOL = 4

# a representation of a 'node' in the search tree
treeNode = {
    # backreference to parent node
    "parent"            : None,
    # the Move that would be taken in the given state from the parent node
    "move"              : None,
    # the state that would be reached by taking the above move
    "potential_state"   : None,
    # an evaluation of the potential_state
    "state_value"       : 0.0,
    # alpha/beta values for minimax
    "alpha"             : -INFINITY,
    "beta"              : INFINITY,
}

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
    #
    # Parameters:
    #    inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        # initialize the AI in the game
        super(AIPlayer,self).__init__(inputPlayerId, "MiniMaximus")

        # initialize our food location tracker to be empty
        self.foodList = []
    
    ##
    # evaluateNodes
    #
    # Description: Takes a list of nodes and returns the min or
    # max node depending on whose turn it is
    #
    # Parameters:
    #   nodes - The list of nodes to evaluate
    #
    # Return: The appropriate min or max node
    ##
    def evaluateNodes(self, nodes):
        # look through the nodes and find the best min/max state value
        # based on the appropriate alpha/beta score and whose turn it is
        if self.playerId == nodes[0]['potential_state'].whoseTurn:
            maxScore = max(n['alpha'] for n in nodes)
            bestNodes = [n for n in nodes if n['alpha'] == maxScore]
            return random.choice(bestNodes)
        else:
            minScore = min(n['beta'] for n in nodes)
            bestNodes = [n for n in nodes if n['beta'] == minScore]
            return random.choice(bestNodes)
    
    ##
    # exploreTree
    #
    # Description: Explores the move search tree recursively and
    #   returns the node with the Move that leads to the best branch
    #   in the tree using alpha/beta pruning
    #
    # Parameters:
    #   currentNode - The State being 'searched' from
    #   currentDepth - The depth of the recursive tree search
    #
    # Return: A node containing the best predicted Move
    ##
    def exploreTree(self, currentNode, currentDepth):

        # create alias lookup/reference variables
        currentState = currentNode["potential_state"]
        whoseTurn = currentState.whoseTurn

        # determine whether this is a Min or a Max player
        isMax = whoseTurn == self.playerId

        # generate a list of Nodes from the possible Moves
        possibleNodes = []
        for m in listAllLegalMoves(currentState):

            #ignore moving the queen if she is not on structure
            if m.moveType == MOVE_ANT:
                if getAntAt(currentState, m.coordList[0]) == QUEEN:
                    if getConstrAt(currentState, m.coordList[0]) is None:
                        continue

            # initialize the node properties
            node = treeNode.copy()
            node["parent"] = currentNode
            node["move"] = m
            node["potential_state"] = self.processMove(currentState, m)
            node["state_value"] = self.evaluateState(node["potential_state"])
            possibleNodes.append(node)

        # intelligently select a subset of nodes to expand
        #nodesToIterate = heapq.nlargest(SET_POOL, possibleNodes, key=lambda x: x["state_value"])
        nodesToIterate = possibleNodes

        # expand and evaluate the subnodes for this node
        for newNode in nodesToIterate:

            # BASE STEP (leaf node)
            if currentDepth == MAX_DEPTH:
                # evaluate subnodes and set alpha/beta to the score
                if isMax:
                    newNode["alpha"] = self.evaluateState(newNode["potential_state"])
                else:
                    newNode["alpha"] = 0 - self.evaluateState(newNode["potential_state"])
                newNode["beta"] = newNode["alpha"]

                # flip whoseTurn if this an END move and reset the ants so that they can move
                # (this must be done after evaluateState so that evaluateState knows whose turn it is)
                if newNode["move"].moveType == END:
                    newNode["potential_state"].whoseTurn = 1 - newNode["potential_state"].whoseTurn
                    for ant in newNode["potential_state"].inventories[newNode["potential_state"].whoseTurn].ants:
                        ant.hasMoved = False

            # RECURSIVE STEP (branch node)
            else:
                # get a back-reference to the parent node
                parentNode = currentNode["parent"]

                # do alpha/beta pruning if we're not the root node
                if parentNode:
                    # parent is a MAX and current node is a MIN
                    if parentNode["potential_state"].whoseTurn == self.playerId:
                        if (not isMax) and parentNode["alpha"] > currentNode["beta"]:
                            break
                    # parent is a MIN and current node is a MAX
                    elif isMax and parentNode["beta"] < currentNode["alpha"]:
                            break

                # flip whoseTurn if this an END move and reset the ants so that they can move
                # (this must be done after evaluateState so that evaluateState knows whose turn it is)
                if newNode["move"].moveType == END:
                    newNode["potential_state"].whoseTurn = 1 - newNode["potential_state"].whoseTurn
                    for ant in newNode["potential_state"].inventories[newNode["potential_state"].whoseTurn].ants:
                        ant.hasMoved = False

                # recurse on the subnode
                self.exploreTree(newNode, currentDepth + 1)

            # update our alpha/beta values based on our expanded subnode's values
            if isMax:
                # current node is a MAX node
                if newNode["potential_state"].whoseTurn != self.playerId:
                    # subnode is a MIN node
                    if newNode["beta"] > currentNode["alpha"]:
                        currentNode["alpha"] = newNode["beta"]
                else:
                    # subnode is a MAX node
                    if newNode["alpha"] > currentNode["alpha"]:
                        currentNode["alpha"] = newNode["alpha"]
            else:
                # current node is a MIN node
                if newNode["potential_state"].whoseTurn == self.playerId:
                    # subnode is a MAX node
                    if newNode["alpha"] < currentNode["beta"]:
                        currentNode["beta"] = newNode["alpha"]
                else:
                    # subnode is a MIN node
                    if newNode["beta"] < currentNode["beta"]:
                        currentNode["beta"] = newNode["beta"]

        # return our best subnode
        return self.evaluateNodes(nodesToIterate)
    
    ##
    # processMove
    #
    # Description: The processMove method looks at the current state
    # of the game and returns a copy of the state that results from
    # making the given Move
    #
    # Parameters:
    #   currentState - The current State of the game
    #   move - The Move which alters the state
    #
    # Return: The resulting State after Move is applied
    ##
    def processMove(self, currentState, move):
        # create a bare-bones copy of the state to modify
        copyOfState = currentState.fastclone()
        
        # get references to the player inventories
        playerInv = copyOfState.inventories[copyOfState.whoseTurn]
        enemyInv = copyOfState.inventories[(copyOfState.whoseTurn+1) % 2]

        if move.moveType == BUILD:
        # BUILD MOVE
            if move.buildType < 0:
                # building a construction
                playerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]
                playerInv.constrs.append(Construction(move.coordList[0], move.buildType))
            else:
                # building an ant
                playerInv.foodCount -= UNIT_STATS[move.buildType][COST]
                playerInv.ants.append(Ant(move.coordList[0], move.buildType, copyOfState.whoseTurn))

        elif move.moveType == MOVE_ANT:
        # MOVE AN ANT
            # get a reference to the ant
            ant = getAntAt(copyOfState, move.coordList[0])

            # update the ant's location after the move
            ant.coords = move.coordList[-1]
            ant.hasMoved = True
            
            # get a reference to a potential construction at the destination coords
            constr = getConstrAt(copyOfState, move.coordList[-1])

            # check to see if the ant is on a food or tunnel or hill and act accordingly
            if constr:
                # we only care about workers
                if ant.type == WORKER:
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
                if UNIT_STATS[ant.type][RANGE] ** 2 >= abs(ant.coords[0] - coord[0]) ** 2 + abs(ant.coords[1] - coord[1]) ** 2:
                    validAttacks.append(coord)

            # if we can attack, pick a random attack and do it
            if validAttacks:
                enemyAnt = getAntAt(copyOfState, random.choice(validAttacks))
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
        return copyOfState

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
    def evaluateState(self, currentState):
        # make some references to player inventories and the queen
        playerInv = currentState.inventories[currentState.whoseTurn]
        enemyInv = currentState.inventories[1 - currentState.whoseTurn]
        playerQueen = playerInv.getQueen()
        enemyQueen = enemyInv.getQueen()

        # check for lost game (dead queen or enemy food victory)
        if playerInv.getQueen() is None or enemyInv.foodCount >= 11:
            return 0.0
        # check for victory (dead enemy queen or food victory)
        if enemyQueen is None or playerInv.foodCount >= 11:
            return 1.0

        # start our score at a neutral 0
        # (this will be normalized to a 0.0 - 1.0 range before being returned)
        stateScore = 0

        workerList = getAntList(currentState, currentState.whoseTurn, (WORKER,))

        # maintain 1 worker and 1 queen whenever possible
        if (len(workerList) == 1) and (len(playerInv.ants) == 2):
            stateScore += WORKER_COUNT_WEIGHT

        # encourage dropping off food
        stateScore += playerInv.foodCount * FOOD_WEIGHT

        # encourage workers to go towards food or dropoff locations appropriately
        for w in workerList:
            # pick a destination (goal) for the ant
            if w.carrying:
                # encourage picking up food
                stateScore += CARRY_WEIGHT
                goals = getConstrList(currentState, currentState.whoseTurn, (ANTHILL, TUNNEL))
            else:
                goals = self.foodList

            # encourage moving towards goal
            distanceToGoal = min(abs(w.coords[0] - g.coords[0]) + abs(w.coords[1] - g.coords[1]) for g in goals)
            stateScore += DISTANCE_WEIGHT / (distanceToGoal + 1.)

        # keep queen on edge of board
        stateScore -= (playerQueen.coords[1]) * QUEEN_EDGE_WEIGHT

        # normalization of evaluation score to 0.0 - 1.0 bounds
        return (math.atan(stateScore/10000.) + math.pi/2) / math.pi
           
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
        #fill the food locations list
        if not self.foodList:
            for f in getConstrList(currentState, NEUTRAL, (FOOD,)):
                self.foodList.append(f)

        # create a root node to build our search tree from
        rootNode = treeNode.copy()
        rootNode["potential_state"] = currentState

        # return the best move, found by recursively searching potential moves
        return self.exploreTree(rootNode, 0)["move"]

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
        #Attack a random enemy.
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

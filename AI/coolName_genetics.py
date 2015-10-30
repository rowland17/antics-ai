from Player import *
from Ant import *
from AIPlayerUtils import *
from Construction import *


# population size
POP_SIZE = 20

# chance of mutation when generating child genes
MUTATION_CHANCE = 0.1

# number of games to evaluate fitness of a gene
GAMES_PER_GENE = 20


##
# AIPlayer
#
# Description: The responsibility of this class is to interact with the game by
#   deciding a valid move based on a given game state. This class has methods that
#   will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    ##
    # __init__
    #
    # Description: Creates a new AI Player that uses a genetic algorithm
    #
    # Parameters:
    #    inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        # initialize the AI in the game
        super(AIPlayer,self).__init__(inputPlayerId, "Gene Genie")

        # reference to AIPlayer's anthill structure
        self.playerAnthill = None

        # GENETIC ALGORITHM VARS:

        # portion of population for phase one of placement
        self.constrPopulation = []
        # portion of population for phase two of placement
        self.foodPopulation = []
        # fitness of population
        self.fitness = [0] * POP_SIZE
        # index of current gene in population
        self.popIndex = 0
        # number of games played for current gene
        self.geneGamesPlayed = 0
        # var is true if current move is AI's first move of current game
        self.isFirstMove = True
        # number of AI's moves in current game
        self.numMoves = 0

        # build list of all possible friendly coords
        self.coordList = [(x,y) for y in range(4) for x in range(10)]

        # build list of all possible enemy coords
        self.enemyCoordList = [(x,y) for y in range(6,10) for x in range(10)]

        # initialize populations with new genes
        self.initializePopulations()

    ##
    # getPlacement
    #
    # Description: Called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   currentState - The GameState of the game at this point in time
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        # place the anthill, tunnel, and grass
        if currentState.phase == SETUP_PHASE_1:
            self.isFirstMove = True
            # generate placements using the gene currently being evaluated
            placementList = self.coordsFromGene(self.constrPopulation[self.popIndex], False)
            # get a reference to player's anthill
            self.playerAnthill = placementList[0]
            return placementList

        # place the enemy's food
        elif currentState.phase == SETUP_PHASE_2:
            moves = []
            # generate placements using the gene currently being evaluated
            foodCoords = self.coordsFromGene(self.foodPopulation[self.popIndex], True)

            # check to make sure placement coords are empty
            for coord in foodCoords:
                if currentState.board[coord[0]][coord[1]].constr is not None:
                    found = False
                    # space is occupied; find an empty space up to 2 steps away
                    for nextCoord in listReachableAdjacent(currentState, coord, 2):
                        if nextCoord[1] > 5 and currentState.board[nextCoord[0]][nextCoord[1]].constr is None:
                            coord = nextCoord
                            found = True
                            break
                    if not found:
                        # no space is empty nearby, so just pick a random spot
                        # in enemy territory
                        coord = None
                        while coord is None:
                            x = random.randint(0, 9)
                            y = random.randint(6, 9)
                            if currentState.board[x][y].constr is None and (x, y) not in moves:
                                # space is empty, so use it
                                coord = (x, y)

                # set space as occupied to prevent placing both food in same spot
                currentState.board[coord[0]][coord[1]].constr = True

                moves.append(coord)

            return moves

    ##
    # initializePopulation
    #
    # Description: Initialize the population of genes with random values
    ##
    def initializePopulations(self):
        # initialize fitness to a list of 0's
        self.fitness = [0] * POP_SIZE

        # initialize genes to lists of random numbers
        for _ in range(POP_SIZE):
            constrGene = [random.randint(0,1000) for _ in range(40)]
            foodGene = [random.randint(0,1000) for _ in range(40)]

            self.constrPopulation.append(constrGene)
            self.foodPopulation.append(foodGene)

    ##
    # generateChildren
    #
    # Description: Takes two parent genes and generates two child
    #   genes that result from the pairing
    #
    # Parameters:
    #   gene1 - The first parent gene
    #   gene2 - The second parent gene
    #   isFood - True if genes are from the food population (phase 2 placement)
    #
    # Return: A list of the two child genes
    ##
    def generateChildren(self, gene1, gene2, isFood):
        # pick a pivot point for joining the genes
        pivot = random.randint(1,len(gene1)-1)

        # splice the genes at the pivot point to make 2 children
        children = [gene1[:pivot] + gene2[pivot:], gene2[:pivot] + gene1[pivot:]]

        # randomly mutate children by chance, randomizing several cells to
        # approximate the chance of a single resulting coord being randomized
        for child in children:
            if random.random() < MUTATION_CHANCE:
                if isFood:
                    idxList = [x[1] for x in random.sample(sorted(zip(child,range(len(child)))),20)]
                else:
                    idxList = [x[1] for x in random.sample(sorted(zip(child,range(len(child)))),4)]

                for i in idxList: child[i] = random.randint(0,1000)

        return children

    ##
    # coordsFromGene
    #
    # Description: Takes a gene and generates the list of coords that represent
    #   its usage in the placement phase
    #
    # Parameters:
    #   gene - The gene to generate coords from
    #   isFood - True if gene is in the food population (phase 2 placement)
    #
    # Return: A list of coordinates representing the gene
    ##
    def coordsFromGene(self, gene, isFood):
        listSize = 2 if isFood else 11

        # pair the gene values with their respective indexes and sort by the values,
        # grabbing a slice of only the top 2 or top 11 values
        tuples = sorted(zip(gene,range(40)))[-listSize:]

        # get the indexes for these top gene values
        idxList = [x[1] for x in tuples]

        # return the coordinates representing these indexes
        if isFood:
            return [self.enemyCoordList[x] for x in idxList]
        else:
            return [self.coordList[x] for x in idxList]

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
        # keep track of how many moves the agent has made
        self.numMoves += 1

        # print the board at the beginning of each game
        if self.isFirstMove:
            asciiPrintState(currentState)
            self.isFirstMove = False

        # get an evaluation score for each legal move and return the best-scoring move
        moveList = listAllLegalMoves(currentState)
        return max([(score, move) for score,move in
                    zip([self.evaluateState(self.getFutureState(currentState, m)) for m in moveList],moveList)])[1]

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
        # return a random attackable enemy
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

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
                if UNIT_STATS[ant.type][RANGE] ** 2 >= abs(ant.coords[0] - coord[0]) ** 2 + abs(ant.coords[1] - coord[1]) ** 2:
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
    # Description: Evaluates how "good" a state is based on whose turn it is and
    #   what is on the board
    #
    # Parameters:
    #   state - The GameState to evaluate
    #
    # Return: A float between 0.0 (loss) and 1.0 (victory)
    ##
    def evaluateState(self, state):
        # local constants for adjusting weights of evaluation
        QUEEN_EDGE_MAP_WEIGHT = 0.01
        BUILD_WORKER_WEIGHT = 0.1
        MOVE_TOWARDS_QUEEN_WEIGHT = 0.005
        QUEEN_HEALTH_WEIGHT = 0.025

        # get some references for use later
        playerInv = state.inventories[state.whoseTurn]
        enemyInv = state.inventories[1 - state.whoseTurn]
        enemyQueen = enemyInv.getQueen()

        # check for defeat (dead queen or enemy food victory)
        if playerInv.getQueen() is None or enemyInv.foodCount >= 11:
            return 0.0
        # check for victory (dead enemy queen or food victory)
        if enemyQueen is None or playerInv.foodCount >= 11:
            return 1.0

        # start the score at a semi-neutral value
        score = 0.4

        # check each of the player's ants
        for ant in playerInv.ants:
            if ant.type == QUEEN:
                # keep the queen off of the anthill
                if ant.coords == self.playerAnthill:
                    return 0.01
                # keep the queen at the edge of the map
                score -= QUEEN_EDGE_MAP_WEIGHT * ant.coords[1]
            elif ant.type == WORKER:
                # encourage building more workers
                score += BUILD_WORKER_WEIGHT
                # move workers towards queen
                score -= MOVE_TOWARDS_QUEEN_WEIGHT * (abs(ant.coords[0] - enemyQueen.coords[0]) +
                                                      abs(ant.coords[1] - enemyQueen.coords[1]))

        # encourage damaging the enemy queen
        score += QUEEN_HEALTH_WEIGHT * (UNIT_STATS[QUEEN][HEALTH] - enemyQueen.health)

        # return the evaluation score of the state
        return score

    ##
    # registerWin
    #
    # Description: Tells the player if they won or not
    #
    # Parameters:
    #   hasWon - True if the player won the game, False if they lost (Boolean)
    ##
    def registerWin(self, hasWon):
        # if victory, increase gene fitness by a value inversely proportional
        # to the number of moves it took to win
        if hasWon:
            self.fitness[self.popIndex] += 1.0 / self.numMoves

        # reset move counter for next game
        self.numMoves = 0

        # track how many games have been played for this gene
        self.geneGamesPlayed += 1

        if self.geneGamesPlayed >= GAMES_PER_GENE:
            # switch to next gene
            self.geneGamesPlayed = 0
            self.popIndex += 1
            if self.popIndex >= POP_SIZE:
                # all genes have been evaluated
                self.popIndex = 0
                self.generateNewPopulation()

    ##
    # generateNewPopulation
    #
    # Description: generate a new population based on the fitness scores of the
    #   current population and then reset the fitness scores for the new generation
    ##
    def generateNewPopulation(self):
        # find the base (min) fitness score and adjust all other scores
        # down by it to magnify the differences in scores
        adj = min(self.fitness)
        adjFitness = [x - adj for x in self.fitness]

        # find the highest-scoring half of the population
        choiceList = sorted(zip(range(len(adjFitness)), adjFitness), key = lambda k: k[1])[POP_SIZE/2:]

        # we're going to construct new populations to replace the old ones
        newConstrPopulation = []
        newFoodPopulation = []

        for _ in range(POP_SIZE/2):
            # select a pair of genes randomly by fitness using a weighted choice algorithm
            idx = [weightedChoice(choiceList) for _ in [0,0]]

            # generate children from the chosen genes, two for each population
            constrChildren = self.generateChildren(self.constrPopulation[idx[0]],
                                                   self.constrPopulation[idx[1]], False)
            foodChildren = self.generateChildren(self.foodPopulation[idx[0]],
                                                 self.foodPopulation[idx[1]], True)

            newConstrPopulation.append(constrChildren[0])
            newConstrPopulation.append(constrChildren[1])
            newFoodPopulation.append(foodChildren[0])
            newFoodPopulation.append(foodChildren[1])

        self.constrPopulation = newConstrPopulation
        self.foodPopulation = newFoodPopulation

##
# weightedChoice
#
# Description: makes a weighted choice from a list of objects
#
# Parameters:
#   choices - a list of tuples of the form: (choice, weight)
#
# Return: the choice object from the selected tuple
##
def weightedChoice(choices):
    r = random.uniform(0, sum(weight for _, weight in choices))
    for choice, weight in choices:
        r -= weight
        if r < 0:
            return choice

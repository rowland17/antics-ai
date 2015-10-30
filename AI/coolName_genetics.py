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
#AIPlayer
#Description: The responsibility of this class is to interact with the game by
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
        super(AIPlayer,self).__init__(inputPlayerId, "Gene Genie")

        # reference to AIPlayer's anthill structure
        self.playerAnthill = None

        # GENETIC ALGORITHM VARS

        # portion of population for phase one of placement
        self.constrPopulation = []
        # portion of population for phase two of placement
        self.foodPopulation = []
        # fitness of population
        self.fitness = [0] * POP_SIZE
        # index of gene in population
        self.popIndex = 0
        # number of games played for current gene
        self.geneGamesPlayed = 0
        # true if current move is AI's first move of current game
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
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            self.isFirstMove = True
            placementList = self.coordsFromGene(self.constrPopulation[self.popIndex], False)
            self.playerAnthill = placementList[0]
            return placementList
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            moves = []
            foodCoords = self.coordsFromGene(self.foodPopulation[self.popIndex], True)
            for coord in foodCoords:
                if currentState.board[coord[0]][coord[1]].constr is not None:
                    found = False
                    for nextCoord in listReachableAdjacent(currentState, coord, 2):
                        if nextCoord[1] > 5 and currentState.board[nextCoord[0]][nextCoord[1]].constr is None:
                            coord = nextCoord
                            found = True
                            break
                    if not found:
                        coord = None
                        while coord == None:
                            #Choose any x location
                            x = random.randint(0, 9)
                            #Choose any y location on enemy side of the board
                            y = random.randint(6, 9)
                            #Set the move if this space is empty
                            if currentState.board[x][y].constr is None and (x, y) not in moves:
                                coord = (x, y)
                                #Just need to make the space non-empty. So I threw whatever I felt like in there.
                                currentState.board[x][y].constr = True
                currentState.board[coord[0]][coord[1]].constr = True
                moves.append(coord)
            return moves
        else:
            return [(0, 0)]

    ##
    # initializePopulation
    #
    # Description: initialize the population of genes with random values
    ##
    def initializePopulations(self):
        self.fitness = [0] * POP_SIZE

        for _ in range(POP_SIZE):
            constrGene = [random.randint(0,1000) for _ in range(40)]
            foodGene = [random.randint(0,1000) for _ in range(40)]

            self.constrPopulation.append(constrGene)
            self.foodPopulation.append(foodGene)

    ##
    # generateChildren
    #
    # Description: takes two parent genes and generates two child
    #   genes that result from the pairing
    #
    # Parameters:
    #   gene1 - the first parent gene
    #   gene2 - the second parent gene
    #
    # Return: a list of the two child genes
    ##
    def generateChildren(self, gene1, gene2, isFood):
        # pick a pivot point for joining the genes
        pivot = random.randint(1,len(gene1)-1)
        print "pivot = " + `pivot`
        # splice the genes at the pivot point to make 2 children
        children = [gene1[:pivot] + gene2[pivot:], gene2[:pivot] + gene1[pivot:]]

        # randomly mutate children by chance
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
    # Description: take a gene and generate the list of coords that represent
    #   its usage in the placement phase
    #
    # Parameters:
    #   gene - the gene to generate coords from
    #   isFood - true if gene is in the food population (phase 2 placement)
    #
    # Return: a list of coordinates representing the gene
    ##
    def coordsFromGene(self, gene, isFood):
        listSize = 2 if isFood else 11
        tuples = sorted(zip(gene,range(40)))[-listSize:]
        idxList = [x[1] for x in tuples]
        if isFood:
            return [self.enemyCoordList[x] for x in idxList]
        else:
            return [self.coordList[x] for x in idxList]

    ##
    # getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        self.numMoves += 1
#
        if self.isFirstMove:
            asciiPrintState(currentState)
            self.isFirstMove = False
#
        moveList = listAllLegalMoves(currentState)
        return max([(score, move) for score,move in
                    zip([self.evaluateState(self.getFutureState(currentState, m)) for m in moveList],moveList)])[1]

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
    def getFutureState(self, currentState, move):
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
    def evaluateState(self, currentState):
        # get a reference to the player's inventory
        playerInv = currentState.inventories[currentState.whoseTurn]
        # get a reference to the enemy player's inventory
        enemyInv = currentState.inventories[(currentState.whoseTurn+1) % 2]
        # get a reference to the enemy's queen
        enemyQueen = enemyInv.getQueen()

        # game over (lost) if player does not have a queen
        #               or if enemy player has 11 or more food
        if playerInv.getQueen() is None or enemyInv.foodCount >= 11:
            return 0.0
        # game over (win) if enemy player does not have a queen
        #              or if player has 11 or more food
        if enemyQueen is None or playerInv.foodCount >= 11:
            return 1.0

        # initial state value is neutral ( no player is winning or losing )
        valueOfState = 0.4

        # hurting the enemy queen is a very good state to be in
        valueOfState += 0.025 * (UNIT_STATS[QUEEN][HEALTH] - enemyQueen.health)

        # loop through the player's ants and handle rewards or punishments
        # based on whether they are workers or attackers
        for ant in playerInv.ants:
            if ant.type == QUEEN:
                # if the queen is on the hill, this is bad
                if ant.coords == self.playerAnthill:
                    return 0.001
                valueOfState -= .01 * ant.coords[1]
            elif ant.type == WORKER:
                # Reward the AI for having ants other than the queen
                valueOfState += 0.1
                # Punish the AI less and less as its ants approach the enemy's queen
                valueOfState -= 0.005 * (abs(ant.coords[0] - enemyQueen.coords[0]) +
                                         abs(ant.coords[1] - enemyQueen.coords[1]))

        # return the value of the currentState
        return valueOfState

    ##
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    ##
    def registerWin(self, hasWon):
        if hasWon:
            self.fitness[self.popIndex] += 1.0 / self.numMoves
        self.numMoves = 0
        self.geneGamesPlayed += 1
        if self.geneGamesPlayed >= GAMES_PER_GENE:
            self.geneGamesPlayed = 0
            self.popIndex += 1
            if self.popIndex >= POP_SIZE:
                self.popIndex = 0
                self.generateNewPopulation()

    ##
    # generateNewPopulation
    #
    # Description: generate a new population based on the fitness scores of the
    #   current population and then reset the fitness scores for the new generation
    ##
    def generateNewPopulation(self):
        adj = min(self.fitness)
        adjFitness = [x - adj for x in self.fitness]
        choiceList = sorted(zip(range(len(adjFitness)), adjFitness), key = lambda k: k[1])[POP_SIZE/2:]
        newConstrPopulation = []
        newFoodPopulation = []
        for _ in range(POP_SIZE/2):
            idx = [weightedChoice(choiceList) for _ in [0,0]]
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


def weightedChoice(choices):
    r = random.uniform(0, sum(weight for _, weight in choices))
    for choice, weight in choices:
        r -= weight
        if r < 0:
            return choice

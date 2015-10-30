
import random
import copy
import math
import collections

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

# population size
POP_SIZE = 10

# chance of mutation when generating child genes
MUTATION_CHANCE = 0.1

GAMES_PER_GENE = 10


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
        super(AIPlayer,self).__init__(inputPlayerId, "Gene Genie")

        self.buildingCoords = [(),()]
        self.hillCoords = None
        self.foodCoords = [()]

        # genetic algorithm vars
        self.constrPopulation = []
        self.foodPopulation = []
        self.fitness = [0] * POP_SIZE
        self.popIndex = 0
        self.geneGamesPlayed = 0
        self.firstMove = True
        self.numMoves = 0
        self.foodScore = 0

        # build list of all possible friendly coords
        self.coordList = [(x,y) for y in range(4) for x in range(10)]

        # build list of all possible enemy coords
        self.enemyCoordList = [(x,y) for y in range(6,10) for x in range(10)]

        # initialize populations with new genes
        self.initializePopulations()

        [printGene(x) for x in self.generateChildren([123,234,345,456,567,678],[333,444,555,666,777,888],False)]

        print "======TESTING COORDSFROMGENE======="
        printCoordList(self.coordsFromGene([0,0,0,0,1,1,1,1,1,123,234,345,456,567,0,0,0,678],False))

        self.f1=open('./out1.txt', 'w+')
        self.f1.truncate()


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
            self.firstMove = True
            return self.coordsFromGene(self.constrPopulation[self.popIndex], False)
        #     numToPlace = 11
        #     moves = []
        #     for i in range(0, numToPlace):
        #         move = None
        #         while move == None:
        #             #Choose any x location
        #             x = random.randint(0, 9)
        #             #Choose any y location on your side of the board
        #             y = random.randint(0, 3)
        #             #Set the move if this space is empty
        #             if currentState.board[x][y].constr == None and (x, y) not in moves:
        #                 move = (x, y)
        #                 #Just need to make the space non-empty. So I threw whatever I felt like in there.
        #                 currentState.board[x][y].constr == True
        #         moves.append(move)
        #     return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            # numToPlace = 2
            moves = []
            foodCoords = self.coordsFromGene(self.foodPopulation[self.popIndex], True)
            if len(foodCoords) != 2:
                print "foodCoords lenabob = " + `len(foodCoords)`
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
            # for i in range(0, numToPlace):
            #     move = None
            #     while move == None:
            #         #Choose any x location
            #         x = random.randint(0, 9)
            #         #Choose any y location on enemy side of the board
            #         y = random.randint(6, 9)
            #         #Set the move if this space is empty
            #         if currentState.board[x][y].constr is None and (x, y) not in moves:
            #             move = (x, y)
            #             #Just need to make the space non-empty. So I threw whatever I felt like in there.
            #             currentState.board[x][y].constr == True
            #     moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # initializePopulation
    #
    # Description: initialize the population of genes with random values
    ##
    def initializePopulations(self):
        print "============POP INIT============"
        self.fitness = [0] * POP_SIZE

        for x in range(POP_SIZE):
            # gene = []
            # for choiceIndex in random.sample(range(len(self.coordList)), 11):
            #     gene.append(self.coordList[choiceIndex])
            # for choiceIndex in random.sample(range(len(self.enemyCoordList)), 2):
            #     gene.append(self.enemyCoordList[choiceIndex])

            # gene = random.sample(self.coordList, 11) + random.sample(self.enemyCoordList, 2)

            constrGene = [random.randint(0,1000) for _ in range(40)]
            foodGene = [random.randint(0,1000) for _ in range(40)]

            self.constrPopulation.append(constrGene)
            self.foodPopulation.append(foodGene)

            print "NEW GENE " + `x` + ": fit " + `self.fitness[x]`
            printGene(constrGene)
            print "---"
            printGene(foodGene)

        print "=============INIT DONE=============="

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
                    # child[random.choice(sorted(zip(child,range(len(child))))[-2:])[1]] = random.randint(0,1000)

                else:
                    idxList = [x[1] for x in random.sample(sorted(zip(child,range(len(child)))),4)]
                    # child[random.choice(sorted(zip(child,range(len(child))))[-11:])[1]] = random.randint(0,1000)

                for i in idxList: child[i] = random.randint(0,1000)

                # child[random.randint(0,len(child)-1)] = random.randint(0,1000)

                # swapIdxs = random.sample(range(len(child)),2)
                # temp = child[swapIdxs[0]]
                # child[swapIdxs[0]] = child[swapIdxs[1]]
                # child[swapIdxs[1]] = temp

                # relevantCoordList = self.coordList if i < 11 else self.enemyCoordList
                # child[i] = random.choice(set(relevantCoordList)-set(child))

        # # check each of the children for duplicates
        # for child in [0,1]:
        #     # counterList = collections.Counter(child)
        #     # for i in [i for i in counterList if counterList[i]>1]:
        #
        #     seen = []
        #     # for i in children[child]:
        #     #     if children[child][i] in seen:
        #     #
        #     #     if i in set(self.coordList)-set(children[child]):
        #
        #     for i in range(13):
        #         relevantCoordList = self.coordList if i < 11 else self.enemyCoordList
        #         if children[child][i] in seen:
        #             children[child][i] = random.choice(set(relevantCoordList)-set(children[child]))
        #         seen.append(children[child][i])

        return children

    ##
    # coordsFromGene
    #
    # Description: take a gene and generate the list of coords that represent
    #   its usage in the placement phase
    #
    # Parameters:
    #   gene - the gene to get coords from
    #   isFood - true if gene is in the food population
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
        self.numMoves += 1
        self.foodScore = currentState.inventories[currentState.whoseTurn].foodCount

        if self.firstMove:
            asciiPrintState(currentState)
            self.asciiPrintStateToFile(currentState)
            self.firstMove = False

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
    ##
    def registerWin(self, hasWon):
        # if hasWon:
        #     print "won: increment fitness[" + `self.popIndex` + "]"
        #     self.fitness[self.popIndex] += 1
        if hasWon: self.foodScore = 11
        print "fitness = " + `self.foodScore` + " / " + `float(self.numMoves)` + " = " + `(self.foodScore / float(self.numMoves))`
        self.fitness[self.popIndex] += self.foodScore / float(self.numMoves)
        self.numMoves = 0
        self.geneGamesPlayed += 1
        if self.geneGamesPlayed >= GAMES_PER_GENE:
            print "switch to next gene"
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
        print "====GENERATING NEW POPULATION===="
        print "fitness: " + ' '.join([`x` for x in self.fitness])
        # masterList = sorted(zip(self.fitness, self.constrPopulation, self.foodPopulation))[-6:]#############################
        choiceList = zip(range(len(self.fitness)), self.fitness)
        newConstrPopulation = []
        newFoodPopulation = []
        for _ in range(POP_SIZE/2):
            print "======GENERATING CHILDREN====="
            idx = [weightedChoice(choiceList) for _ in [0,0]]
            print "IDX PARENTS: " + ' '.join([`x` for x in idx])
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
        print "CONSTR GENES: "
        [printGene(gene) for gene in newConstrPopulation]
        print "FOOD GENES: "
        [printGene(gene) for gene in newFoodPopulation]

    ##
    # asciiPrintState
    #
    # prints a text representation of a GameState to stdout.  This is useful for
    # debugging.
    #
    # Parameters:
    #    state - the state to print
    #
    def asciiPrintStateToFile(self, state):
        #select coordinate ranges such that board orientation will match the GUI
        #for either player
        coordRange = range(0,10)
        colIndexes = " 0123456789"
        if (state.whoseTurn == PLAYER_TWO):
            coordRange = range(9,-1,-1)
            colIndexes = " 9876543210"

        #print the board with a border of column/row indexes
        print >> self.f1, colIndexes
        index = 0              #row index
        for x in coordRange:
            row = str(x)
            for y in coordRange:
                ant = getAntAt(state, (y, x))
                if (ant != None):
                    row += charRepAnt(ant)
                else:
                    constr = getConstrAt(state, (y, x))
                    if (constr != None):
                        row += charRepConstr(constr)
                    else:
                        row += "."
            print >> self.f1, row + str(x)
            index += 1
        print >> self.f1, colIndexes

        #print food totals
        p1Food = state.inventories[0].foodCount
        p2Food = state.inventories[1].foodCount
        print >> self.f1, " food: " + str(p1Food) + "/" + str(p2Food)


def weightedChoice(choices):
    r = random.uniform(0, sum(weight for _, weight in choices))
    for choice, weight in choices:
        r -= weight
        if r < 0:
            return choice

##
# printGene
##
def printGene(gene):
    print "[" + ','.join([`x` for x in gene]) + "]"

##
# printCoordList
##
def printCoordList(coordList):
    print ' '.join(["(" + `x` + "," + `y` + ")" for x,y in coordList])



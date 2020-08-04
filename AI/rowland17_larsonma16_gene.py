import random
import sys
import time
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
#fix geneSplice to use all of board for food
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
        super(AIPlayer,self).__init__(inputPlayerId, "gene3")
        self.popSize = 30
        self.population = []
        self.nextGen = []
        self.fitnessList = []
        self.geneIndex = 0
        self.initPopulation()
        #self.generateSecondGen()
        self.t0 = 0
        self.gamesToEval = 1
        self.gamesPlayed = 0
        self.geneScore =0
        self.state = None
        self.stateList = []
        self.queenMinHealth = 8#DEFAULT QUEEN HEALTH
        self.maxFood = 0#DEFAULT FOOD AMOUNT

    ##
    #evalGene
    #
    #Description - evaluate the current gene for fitness.
    #       our goal is to get the anthill, tunnel as far from the bottom left
    #       corner as possible.
    #       also put the food as far from the opposing tunnel as we can
    #       also have the grass in row 1, not 0
    #
    #Parameters - state - currentState
    ##
    def evalGene(self,state):
        score = 0
        closeFood = None
        me = state.whoseTurn
        myQueen = getAntList(state,me,(QUEEN,))[0]
        myTunnel = getConstrList(state, (me), (TUNNEL,))[0]
        opponentTunnel = getConstrList(state, (me+1)%2, (TUNNEL,))[0]
        opponentFood = getConstrList(state, None,(FOOD,))
        grass = getConstrList(state, None,(GRASS,))
        #allMoves = [move for move in allMoves if currentNode.stateEval < self.gameStateEval(getNextStateAdversarial(currentState, move))]
        grassSum = 0
        grass = [x for x in grass if x.coords[1] <4]
        for g in grass:
            grassSum += abs((g.coords[1]-1)*10)
        opponentFood = [x for x in opponentFood if x.coords[1] >= 6]
        if(stepsToReach(state, opponentTunnel.coords, opponentFood[0].coords) >\
           stepsToReach(state, opponentTunnel.coords, opponentFood[1].coords)):
           closeFood = stepsToReach(state, opponentTunnel.coords, opponentFood[1].coords)
        else:
           closeFood = stepsToReach(state, opponentTunnel.coords, opponentFood[0].coords)
            
        distToCorner = approxDist(myQueen.coords, (9,0))
        distToCorner2 = approxDist(myTunnel.coords, (9,0))
        
        score = score + distToCorner * distToCorner
        score = score + closeFood * closeFood * closeFood*closeFood
        score = score + distToCorner2 * distToCorner2
        score -= grassSum*2
        if score < 5:#Set a minimum so genes have at least some chance of being picked when new generations are created
            score = 5
        self.geneScore = self.geneScore + score

        
        


    #initPopulation
    #Description: A method to initialize the population of genes with
    #random values and reset the fitness
    #list to default values.
    def initPopulation(self):
        width = 10
        height  = 4
        length = width*height
        
        for i in range(0, self.popSize):
            array = []
            for i in range(0,length):
                #print i
                array.append(random.randint(0,100))
            for i in range(0, 2):
                array.append(random.randint(0, 8))
                food = array[len(array) -1]
                if(food == 8):  #dont place the food on their grass. Hard coded for booger agent
                    array.append(6)
                elif(food ==7):
                    array.append(random.randint(6,7))
                elif(food == 6):
                    array.append(random.randint(6,8))
                else:
                    array.append(random.randint(6, 9))
            self.population.append(array)
    
        self.resetFitness()
    ##
    #resetFitness
    #reset the fitness scores to 0 for each population member
    #
    def resetFitness(self):
        for i in range(0, self.popSize):
            if(len(self.fitnessList) == i):
                self.fitnessList.append(0)
            self.fitnessList[i] = 0
        #self.fitnessList[0] = 2
        #self.fitnessList[3] = 3

    ##
    #geneSplice
    #Description: given two genes generate two children genes
    #parameters - gene1 - a gene
    #             gene2 - a gene
    ##       
    def geneSplice(self, gene1, gene2):
        split = random.randint(0,39)
        #print "split for gene " + str(split)
        
        temp = gene1[0:split] + gene2[split: len(gene2)]
        temp2 = gene2[0:split] + gene1[split: len(gene1)]

        if(random.randint(0,10) < 2):
            temp[random.randint(0, 39)] = random.randint(50,120) #for more mutations that change things
        elif(random.randint(0,10) < 2):
            temp2[random.randint(0, 39)] = random.randint(50,120) #for more mutations that change things
        elif(random.randint(0,5) == 2): #chance at mutation
            if(random.randint(0,1) == 0):
                if(random.randint(0,1) == 0):
                    temp[40] = random.randint(0,8)
                    food = temp[40]
                    if(food == 8):  #dont place the food on their grass. Hard coded for booger agent
                        temp[41] = 6
                    elif(food ==7):
                        temp[41] = random.randint(6,7)
                    elif(food == 6):
                        temp[41] = random.randint(6,8)
                    else:
                        temp[41] = random.randint(6,9)
            else:
                if(random.randint(0,1) == 0):#chance at mutaion
                    temp[42] = random.randint(0,6)
                    food = temp[42]
                    if(food == 8):  #dont place the food on their grass. Hard coded for booger agent
                        temp[43] = 6
                    elif(food ==7):
                        temp[43] = random.randint(6,7)
                    elif(food == 6):
                        temp[43] = random.randint(6,8)
                    else:
                        temp[43] = random.randint(6,9)
        elif(random.randint(0,5) == 3):#chance at mutation
            if(random.randint(0,1) == 0):
                if(random.randint(0,1) == 0):
                    temp2[40] = random.randint(0,6)
                    food = temp2[40]
                    if(food == 8):  #dont place the food on their grass. Hard coded for booger agent
                        temp2[41] = 6
                    elif(food ==7):
                        temp2[41] = random.randint(6,7)
                    elif(food == 6):
                        temp2[41] = random.randint(6,8)
                    else:
                        temp2[41] = random.randint(6,9)
            else:
                if(random.randint(0,1) == 0):#chance at mutation
                    temp2[42] = random.randint(0,6)
                    food = temp2[42]
                    if(food == 8):  #dont place the food on their grass. Hard coded for booger agent
                        temp[43] = 6
                    elif(food ==7):
                        temp[43] = random.randint(6,7)
                    elif(food == 6):
                        temp[43] = random.randint(6,8)
                    else:
                        temp[43] = random.randint(6,9)
                
                
        return temp, temp2

    ##
    #genNextGEnes
    #initializes the next set of genes to the to be full of children
    ##
    def genNextGenes(self):
        self.nextGen = []
        for i in range(0, self.popSize / 2):
            value = self.generateSecondGen()
            self.nextGen.append(value[0])
            self.nextGen.append(value[1])
            

    ##
    #generateSecondGen
    #chooses the two parents to mate for each child
    #the better the fitness, the more likely to mate.
    #
    def generateSecondGen(self):
        #print "hello"
        #print self.fitnessList.index(max(self.fitnessList))
        i = 0
        potentialMates = []
        for i in range(0, self.popSize):
            for j in range(0, self.fitnessList[i]):
                potentialMates.append(i)
        #print"length pop " + str(len(potentialMates))
        
        mate1 = self.population[potentialMates[random.randint(0, len(potentialMates)-1)]]
        mate2 = self.population[potentialMates[random.randint(0, len(potentialMates)-1)]]
        while mate1 == mate2:
            i = i+1;
            mate2 = self.population[potentialMates[random.randint(0, len(potentialMates))-1]]
            if i>=10 :
                mate2 = self.population[random.randint(0,len(self.population)-1)]

        return self.geneSplice(mate1, mate2)
            
                    
        
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
        
        tempGene = copy.copy(self.population[self.geneIndex])
        tempGeneFood =copy.copy(self.population[self.geneIndex])
        #print "scott" + str(len(tempGeneFood))
        #self.initPopulation()
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            self.t0 = time.clock()
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    index = tempGene.index(max(tempGene[0:40]))
                    col = int(index/10)
                    row = index %10
                    #print int(index/10)
                    #print index % 10
                    tempGene[index] = -1
                    move = (row,col) 
                moves.append(move)
            #print moves
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            needRand = False
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    
                    #Choose any x location
                    x = tempGeneFood[40]
                    #Choose any y location on enemy side of the board
                    y = tempGeneFood[41]
                    if(i == 1):
                        x= tempGeneFood[42]
                        y= tempGeneFood[43]
                    if(needRand):
                        x = random.randint(0,9)
                        y = random.randint(6,9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                    needRand = True
                moves.append(move)
                needRand = False
            #print moves
            return moves
        else:
            return [(0, 0)]


    ##
    #registerWin
    #
    def registerWin(self, hasWon):
        
        #print time.clock() - self.t0
        self.gamesPlayed = self.gamesPlayed + 1
        #self.geneScore = int((self.geneScore+ time.clock()- self.t0))+2
        
        #Add the queen health stat and maximum food stat to the gene score and then reset them
        self.geneScore += self.queenMinHealth*5 + self.maxFood*5
        self.queenMinHealth = 8
        self.maxFood = 0
        if(hasWon):
            self.geneScore = self.geneScore + 200#make a winning game give more score
        if(self.gamesPlayed == self.gamesToEval):
            
            #asciiPrintState(self.state)
            
            self.state = None
            #print str(self.geneScore) + "geneScore"
            self.fitnessList[self.geneIndex] = int(self.geneScore /self.gamesToEval)
            #print self.fitnessList
            self.geneIndex = self.geneIndex +1
            self.gamesPlayed = 0
            self.geneScore = 0
            
        if(self.geneIndex == len(self.population)):
            idx = self.fitnessList.index(max(self.fitnessList))
            print ""
            print ""
            asciiPrintState(self.stateList[idx])
            print ""
            print ""
            self.stateList = []
            self.geneIndex = 0
            self.genNextGenes()
            self.population = copy.copy(self.nextGen)
            for i in range(0,len(self.fitnessList)):
                self.fitnessList[i] = 0
        
        
            
            
    
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
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn
        #with each move check to see if we reached a new max food or a new queen health minimum
        self.maxFood = max(self.maxFood,myInv.foodCount)
        self.queenMinHealth = min(getAntList(currentState, me, (QUEEN,))[0].health,self.queenMinHealth)
        if(self.state is None):
            self.evalGene(currentState)
            self.state = copy.copy(currentState)
            self.stateList.append(copy.copy(currentState))
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];
            
        return selectedMove


    
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

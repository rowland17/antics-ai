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
        super(AIPlayer,self).__init__(inputPlayerId, "gene")
        self.popSize = 5
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
                array.append(random.randint(0, 9))
                array.append(random.randint(6, 9))
            self.population.append(array)
    
        self.resetFitness()

    def resetFitness(self):
        for i in range(0, self.popSize):
            if(len(self.fitnessList) == i):
                self.fitnessList.append(0)
            self.fitnessList[i] = 0
        #self.fitnessList[0] = 2
        #self.fitnessList[3] = 3

    def geneSplice(self, gene1, gene2):
        split = random.randint(0,39)
        
        temp = gene1[0:split] + gene2[split: len(gene2)]
        temp2 = gene2[0:split] + gene1[split: len(gene1)]

        if(random.randint(0,10) == 1):
            temp[random.randint(0, 39)] = random.randint(50,100) #for more mutations that change things
        elif(random.randint(0,10) == 2):
            temp2[random.randint(0, 39)] = random.randint(50,100) #for more mutations that change things
        return temp, temp2

    def genNextGenes(self):
        self.nextGen = []
        for i in range(0, self.popSize / 2):
            value = self.generateSecondGen()
            self.nextGen.append(value[0])
            self.nextGen.append(value[1])
            
            
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
                   # print int(index/10)
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
        print int(time.clock()- self.t0)
        self.geneScore = int((self.geneScore+ time.clock()- self.t0))+2
        if(hasWon):
            self.geneScore = self.geneScore + 1000
        if(self.gamesPlayed == self.gamesToEval):
            asciiPrintState(self.state) 
            self.state = None
            print str(self.geneScore) + "geneScore"
            self.fitnessList[self.geneIndex] = int(self.geneScore*10 /self.gamesToEval)
            print self.fitnessList
            self.geneIndex = self.geneIndex +1
            self.gamesPlayed = 0
            self.geneScore = 0
        if(self.geneIndex == len(self.population)):
            print self.fitnessList
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
        if(self.state is None):
            self.state = copy.copy(currentState)
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

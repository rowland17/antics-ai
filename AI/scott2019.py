import random
import sys
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
        super(AIPlayer,self).__init__(inputPlayerId, "SCOTT2019")
        self.myFood = None
        self.myFood2 = None
        self.myTunnel = None
        self.myHill = None
        self.number = 20

        self.geneScore = []
        self.geneIndex = 0
        self.fitnessList = []
        self.dist1 = 0
        self.dist2 = 0
        self.initPop()


    def initPop(self):
        for i in range(0,self.number):
            self.fitnessList.append(0)
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
        dist1 = 0
        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
            #print self.myTunnel.coords
        if (self.myHill == None):
            self.myHill = getConstrList(currentState, me, (ANTHILL,))[0]
            #print self.myHill.coords
        if (self.myFood == None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            
            #find the food closest to the tunnel
            bestDistSoFar = 1000 #i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood2 = self.myFood
                    self.myFood = food
                    bestDistSoFar = dist
            #print self.myFood.coords

        if getAntAt(currentState,self.myHill.coords) is None and myInv.foodCount >= 1 and len(myInv.ants)==2:
            print len(myInv.ants)
            #return Move(BUILD, [myInv.getAnthill().coords], WORKER)
        queen = getAntList(currentState, me, (QUEEN,))[0]
        if not queen.hasMoved:
            queenMove = self.getQueenMove(currentState, me, queen)
            if queenMove is not None:
                return queenMove
        workerList = getAntList(currentState, me, (WORKER,))
        for worker in workerList:
            print worker
            print worker.hasMoved
            return self.getFirstWorkerMove(currentState, me, workerList[0])





    def getQueenMove(self,currentState,me, queen):
        #print "queen"
        if not queen.coords ==self.myHill.coords and not queen.coords == self.myTunnel.coords and not queen.coords == self.myFood.coords and not queen.coords == self.myFood2.coords:
            return None
        moves = listAllLegalMoves(currentState)
        for move in moves:
            if not move.moveType == MOVE_ANT:
                self.geneScore.append(-30)
                continue
            if not move.coordList[0] == queen.coords:
                self.geneScore.append(-50)
                continue
            if move.coordList[len(move.coordList)-1] == self.myHill.coords or move.coordList[len(move.coordList)-1] == self.myTunnel.coords or move.coordList[len(move.coordList)-1] == self.myFood.coords or move.coordList[len(move.coordList)-1] == self.myFood2.coords:
                self.geneScore.append(-25)
            else:
                self.geneScore.append(0)
        selectedMove = moves[self.geneScore.index(max(self.geneScore))]
        #print self.geneScore
        self.geneScore = []
        #print "queenMov"
        return selectedMove

    
        
    def getFirstWorkerMove(self,currentState,me,worker):
        #if the worker has already moved, we're done
        print worker
        
            #myWorker = workerList[0]
        if (worker.hasMoved):
            print "moved"
            #self.dist2 = stepsToReach(currentState, myWorker.coords, self.myFood.coords)
            #self.geneScore = self.geneScore + (self.dist1 - self.dist2)
            #self.registerWin(True)
            return Move(END, None, None)
        else:
            self.dist1 = stepsToReach(currentState, worker.coords, self.myFood.coords)
            moves = listAllLegalMoves(currentState)
            selectedMove = moves[random.randint(0,len(moves) - 1)];

            #don't do a build move
            i = 0
            for move in moves:
                if move.moveType==MOVE_ANT and move.coordList[0]== move.coordList[len(move.coordList)-1]:
                    #print i+1
                    i = i+1
                    self.geneScore.append(-25)
                    continue
                if move.moveType == MOVE_ANT and worker.coords==move.coordList[0] and not worker.carrying:
                    self.dist2 = stepsToReach(currentState,move.coordList[len(move.coordList)-1],self.myFood.coords);
                    self.geneScore.append((self.dist1 - self.dist2))
                    #print i+1
                    i=i+1
                elif  move.moveType == MOVE_ANT and worker.coords==move.coordList[0] and worker.carrying:
                    self.dist2 = stepsToReach(currentState,move.coordList[len(move.coordList)-1],self.myTunnel.coords);
                    self.geneScore.append((self.dist1 - self.dist2))
                    #print i+1
                    i=i+1
                else:
                    self.geneScore.append( -10 )
                    #print i+1
                    i=i+1
                    continue
            #print "moves "+str(len(moves))
            
            #print self.geneScore.index(max(self.geneScore))
            selectedMove = moves[self.geneScore.index(max(self.geneScore))]
            print self.geneScore
            self.geneScore = []
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



    def registerWin(self, hasWon):
        if(hasWon):
            self.geneScore = self.geneScore
        if(1 == 1):
            #print "hello"
            self.state = None
            #print str(self.geneScore) + "geneScore"
            #self.fitnessList[self.geneIndex] = int(self.geneScore)
            #print self.geneScore
            self.geneIndex = self.geneIndex +1
            self.gamesPlayed = 0
            self.geneScore = []
            self.myFood=None
            self.myFood2=None
            self.myTunnel=None
            self.myHill=None

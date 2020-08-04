# -*- coding: cp1252 -*-
import time
import unittest
import random
import sys
import os
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
        super(AIPlayer,self).__init__(inputPlayerId, "searchFoodGatherer")
        self.depth = 2
        self.myTunnel = None
        self.myFood = None
        self.stateUtils = []
        self.first = False
        


    #def init_Utils(self):

    def outputStateUtils(self):
        if os.path.exists("rowland17.txt"):
            f = open("rowland17.txt", 'r')
            val = f.readline()
            val = float(val)
            print val
            print type(val)
            f.close()
        f = open("rowland17.txt", 'w')
        #for i in self.stateUtil
        f.write("42\n")
        f.write("42\n")
        f.close()

    
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
        if(not self.first):
            self.outputStateUtils()
        self.first  = True
        self.myFood = None
        self.myTunnel = None
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
        #set the current tunnel and food
        me = currentState.whoseTurn
        if (self.myTunnel is  None):
            #print "hello"
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood is None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            #find the food closest to the tunnel
            bestDistSoFar = 1000 #i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood = food
                    bestDistSoFar = dist
        #use the recursive method
        return self.pickMove(Node(None, currentState, 0.0, None),0)


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
    #gameStateEval
    #Description:A function that examines a GameState object and returns a double between 0.0 and 1.0
    #that indicates how “good” that state is for the agent whose turn it is. This function should
    #always return 1.0 if the agent has won. It should always return 0.0 if the enemy has won.
    #Any value greater than 0.5 means that the agent is winning. Any value less than 0.5
    #means it is losing.
    #
    #Parameters: currentState - copy of the current state (GameState)
    #
    #
    #Return: value to say who is winning(double)
    ##
    def gameStateEval(self, currentState):
        
        score = .5 # starting score nobody is winning
        #get the variables we will need
        me = currentState.whoseTurn
        myInv = getCurrPlayerInventory(currentState)
        oppInv = self.getOppInv(currentState)
        #if i won return 1 if opp won return 0
        if(self.hasWon(currentState,me)):
            return 1.0
        elif(self.hasWon(currentState,(me+1)/2)):
            return 0.0
        #calls to helper evaluators
        score+=self.numAntsEval(myInv,oppInv)
        score+=self.typeAntEval(currentState,myInv,oppInv)
        score+=self.foodCountEval(myInv,oppInv)
        score+=self.carryEval(currentState)
        return score

    
    ##
    #carryEval
    #Description: if more of my ants are carrying food then return a better score
    #
    #Parameters: current state of the game (GameState)
    #
    # Return - a score of the ants carrying (double)
    ###
    def carryEval(self, currentState):
        #variables we need
        myCount=0
        oppCount = 0
        me = currentState.whoseTurn
        myWorkers =getAntList(currentState, me, (WORKER,))
        oppWorkers=getAntList(currentState, (me+1)%2, (WORKER,))
        
        #count the number of workers for each team 
        for ant in myWorkers:
            if(ant.carrying):
                myCount+=1
        for ant in oppWorkers:
            if (ant.carrying):
                oppCount+=1
                
        #if my workers out number opponent workers then the score is better
        if(myCount > oppCount):
            score = .05
            if(myCount -oppCount >= 2):
                score+=.05
        elif(myCount < oppCount):
            score = -.05
            if(-myCount +oppCount >= 2):
                score-=.05
        else:
            score = 0
        #print "carry: " + str(time.clock() - t0)
        return score/50 #5 is arbitrary
    ##
    #foodCountEval
    #Description: if my food count is greater then I get more points i
    #
    #Parameters: myInv, oppInv inventories of both players (Inventory)
    #
    #Return -  a score of the ants carrying (double)
    ###
    def foodCountEval(self,myInv,oppInv):
        t0 = time.clock()
        # if our food is the same then no score for either team
        if(myInv.foodCount == oppInv.foodCount):
            score = 0
        elif(myInv.foodCount > oppInv.foodCount):#if i have more food then positive score
            score = .2
            if(myInv.foodCount - oppInv.foodCount ==1):
                score += .01*3
            elif(myInv.foodCount - oppInv.foodCount ==2):
                score += .02*3
            elif(myInv.foodCount - oppInv.foodCount ==3):
                score += .03*3
            elif(myInv.foodCount - oppInv.foodCount ==4):
                score += .04*3
            elif(myInv.foodCount - oppInv.foodCount ==5):
                score += .05*3
            elif(myInv.foodCount - oppInv.foodCount ==6):
                score += .06*3
            elif(myInv.foodCount - oppInv.foodCount ==7):
                score += .07*3
            elif(myInv.foodCount - oppInv.foodCount ==8):
                score += .08*3
            elif(myInv.foodCount - oppInv.foodCount ==9):
                score += .09*3
            elif(myInv.foodCount - oppInv.foodCount ==10):
                score += .1*3
        else:                                   #if opponent has more food then negative score
            score = -.2
            if(myInv.foodCount - oppInv.foodCount ==-1):
                score -= .01*3
            elif(myInv.foodCount - oppInv.foodCount ==-2):
                score -= .02*3
            elif(myInv.foodCount - oppInv.foodCount ==-3):
                score -= .03*3
            elif(myInv.foodCount - oppInv.foodCount ==-4):
                score -= .04*3
            elif(myInv.foodCount - oppInv.foodCount ==-5):
                score -= .05*3
            elif(myInv.foodCount - oppInv.foodCount ==-6):
                score -= .06*3
            elif(myInv.foodCount - oppInv.foodCount ==-7):
                score -= .07*3
            elif(myInv.foodCount - oppInv.foodCount ==-8):
                score -= .08*3
            elif(myInv.foodCount - oppInv.foodCount ==-9):
                score -= .09*3
            elif(myInv.foodCount - oppInv.foodCount ==-10):
                score -= .1*3
        
        return score/5 #divide by arbitrary to keep under 1.0

    ##
    #typeAntEval
    #Description: right now if we have more workers than the other person then positive score if less then negative
    #             don't worry about the other types of ants
    #
    #Parameters: current state of the game (GameState)
    #            myInv  inventories of both players (Inventory)
    #            oppInv inventories of both players (Inventory)
    #
    #Return - a score of the ants carrying (
    ###
    def typeAntEval(self,currentState,myInv,oppInv):
        t0 = time.clock()
        me = currentState.whoseTurn
        myWorkers =getAntList(currentState, me, (WORKER,)) #get my worker ants
        oppWorkers=getAntList(currentState, (me+1)%2, (WORKER,)) #get opponent worker ants
        score =0.00;
        if(len(myWorkers) > len(oppWorkers)):               #if my workers are more than the other players then thats a good thing
            
            score+=.3
        elif(len(myWorkers)==len(oppWorkers)):
            
            score+=0
        else:
            score -= .3
        
        return score/8


    ##
    #numAntsEval
    #Description: If my total ants are more than the opponent's then i get a better score
    #             Effectively compares the same thing as typeAntEval()
    #
    #Parameters: myInv, oppInv inventories of both players (Inventory)
    #
    #Return: a score of the ants carrying (double)
    ##
    def numAntsEval(self, myInv,oppInv):
        t0 = time.clock()
        if(len(myInv.ants) > len(oppInv.ants)):
            scoreToAdd =0.2
            divideBy =1.0
        elif(len(myInv.ants) == len(oppInv.ants)):
            scoreToAdd =0
            divideBy =1.0
        else:
            scoreToAdd = -0.2
            divideBy =1.0
        #print "numAnts: " + str(time.clock() - t0)
        return scoreToAdd/4

        
    ##
    #getOppInv
    #Description: get the opponent inventory
    #
    #Parameters: current state of game (Game State)
    #
    #Return: The opponent's inventory (Inventory)
    ##
    def getOppInv(self,currentState):
        resultInv = None
        for inv in currentState.inventories:
            if inv.player != currentState.whoseTurn:
                resultInv = inv
                break      
        return resultInv


    ##
    #hasWon
    #Description: tells us if somebody has won the game
    #
    #Parameters: current state of game (Game State)
    #            player id (int)
    #
    #Return: if the player with player id has won the game (boolean)
    ##
    def hasWon(self,currentState,playerId):
        opponentId = (playerId + 1) % 2
        
        if ((currentState.phase == PLAY_PHASE) and 
        ((currentState.inventories[opponentId].getQueen() == None) or
        (currentState.inventories[opponentId].getAnthill().captureHealth <= 0) or
        (currentState.inventories[playerId].foodCount >= FOOD_GOAL) or
        (currentState.inventories[opponentId].foodCount == 0 and 
            len(currentState.inventories[opponentId].ants) == 1))):
            return True
        else:
            return False


    ##
    #helperMethod
    #Description: a method to calculate the best of a list of nodes
    #parameter nodes - a list of nodes ([Node])
    #
    #Return: a double of the best score in the list of nodes (double)
    #    
    def helperMethod(self, nodes):
        bestScore =0
        bestNode = None
        for node in nodes:
            if node.stateEval > bestScore:
                bestScore = node.stateEval
        return bestScore




    ##
    #pickMove                          ####RECURSIVE####
    #
    #Description - Generate a list of all possible moves. Generate a list of the Node objects that will result from making each move.
    #               Recurse on the list of nodes. 
    #parameter nodes - a list of nodes ([Node])
    #                   depth a depth limit (int)
    #Return: either a value to replace the evaluation with (double)
    #        a move that should be chosen (Move)
    ##
    def pickMove(self, currentNode, depth):
        #variables we will  use
        currentState = currentNode.nextState
        foodLocs = getConstrList(currentState, None, (FOOD,))
        t0 = time.clock()
        sEval = 0.0
        bestEval = -1
        bestNode = None

        #step a
        #list all possible moves not end turn
        moves = listAllLegalMoves(currentNode.nextState)
        
        allMoves = [move for move in moves if move.moveType != END or move.moveType != BUILD]
        myAnts =getAntList(currentState, currentState.whoseTurn, (WORKER,QUEEN,SOLDIER,R_SOLDIER,DRONE))
        #make a list of nodes
        nodes = []
        for move in allMoves:
            if(move.moveType ==MOVE_ANT):
                if(getAntAt(currentState,move.coordList[0]).type == WORKER):
                    if(not getAntAt(currentState,move.coordList[0]).carrying): #if the ant has no food go to food
                        if(stepsToReach(currentState, move.coordList[0], self.myFood.coords) > \
                           stepsToReach(currentState, move.coordList[len(move.coordList)-1],self.myFood.coords)):
                            nodes.append(Node(move, getNextState(currentState,move), self.gameStateEval(getNextState(currentState,move)),currentState))
                    else:
                        if(stepsToReach(currentState, move.coordList[0], self.myTunnel.coords) > \
                           stepsToReach(currentState, move.coordList[len(move.coordList)-1],self.myTunnel.coords)): #if the ant has food go to tunnel
                            nodes.append(Node(move, getNextState(currentState,move), self.gameStateEval(getNextState(currentState,move)),currentState))
                elif(getAntAt(currentState,move.coordList[0]).type == QUEEN):
                    if(move.coordList[0] == self.myFood.coords):
                        nodes.append(Node(move, getNextState(currentState,move), self.gameStateEval(getNextState(currentState,move)),currentState))
                else:
                    nodes.append(Node(move, getNextState(currentState,move), self.gameStateEval(getNextState(currentState,move)),currentState))
        nodes = sorted(nodes, key=lambda n: n.stateEval, reverse = True) #sort the list borrowed from Stack Overflow
        #recursive case
        if(depth != self.depth):
           for i in range(0,10):
               if( i >= len(nodes)):
                   break
               #print nodes[i].stateEval 
               node = nodes[i]
               sEval= self.pickMove(node, depth+1)
               node.stateEval = sEval
        #like it says in the assignment step 5
        if(depth > 0):
            return self.helperMethod(nodes)
        else:
            for i in range(0,10):
                if( i >= len(nodes)):
                   break
                node = nodes[i]
                if node.stateEval >= bestEval:
                    bestEval = node.stateEval
                    bestNode = node
            #print "total: " + str(time.clock() - t0)
            if bestNode is not None:
                #print str(bestNode.move)
                return bestNode.move
            else:
                return Move(END, None,None)
        return Move(END, None,None)


                
                
#definition of the node      
class Node(object):
    #create a node object
    def __init__(self, move, nextState, stateEval, parent):
        self.move = move
        self.nextState = nextState
        self.stateEval = stateEval
        self.parent = parent
    #print a node string
    def __str__(self):
        return "Node: " + str(move) +" " + str(nextState)

class MyTest(unittest.TestCase):
    #unit test   
    myAnts = []
    oppAnts =[]
    myQueen = Ant((9,3),QUEEN,0)
    myWorker =Ant ((6,2),WORKER, 0)
    myWorker.carrying = True
    oppQ = Ant((5,7),QUEEN,0)
    oppW =Ant ((6,6),WORKER, 0)
    myAnts.append(myQueen)
    myAnts.append(myWorker)
    oppAnts.append(oppQ)
    oppAnts.append(oppW)
    #initialize all the constructions
    constrs = []
    constrs1 = []
    constrs2 = []
    constrs2.append(Building((9,3),ANTHILL, 0))
    constrs2.append(Building((7,1),TUNNEL, 0))
    constrs1.append(Building((5,7),ANTHILL, 1))
    constrs1.append(Building((6,6),TUNNEL, 1))
    constrs.append(Building((6,7),GRASS, None))
    constrs.append(Building((6,8),GRASS, None))
    constrs.append(Building((6,9),GRASS, None))
    constrs.append(Building((1,6),GRASS, None))
    constrs.append(Building((1,7),GRASS, None))
    constrs.append(Building((1,8),GRASS, None))
    constrs.append(Building((1,9),GRASS, None))
    constrs.append(Building((2,6),GRASS, None))
    constrs.append(Building((2,8),GRASS, None))
    constrs.append(Building((2,7),GRASS, None))
    constrs.append(Building((0,1),GRASS, None))
    constrs.append(Building((0,2),GRASS, None))
    constrs.append(Building((0,3),GRASS, None))
    constrs.append(Building((0,0),GRASS, None))
    constrs.append(Building((1,1),GRASS, None))
    constrs.append(Building((1,0),GRASS, None))
    constrs.append(Building((1,2),GRASS, None))
    constrs.append(Building((1,3),GRASS, None))
    constrs.append(Building((2,0),GRASS, None))
    constrs.append(Building((2,1),GRASS, None))
    constrs.append(Building((6,2),FOOD, None))
    constrs.append(Building((6,3),FOOD, None))
    constrs.append(Building((9,6),FOOD, None))
    constrs.append(Building((9,7),FOOD, None))
    #create a new board for the gamestates
    newBoard = []
    for i in range(0,10):
        newBoard.append([])
        for j in range(0,10):
            for c in constrs:
                if(c.coords == (i,j)):
                   newBoard[i].append(c)
                   continue
            for c in constrs1:
                if(c.coords == (i,j)):
                   newBoard[i].append(c)
                   continue 
            for c in constrs2:
                if(c.coords == (i,j)):
                   newBoard[i].append(c)
                   continue
            newBoard[i].append(None)
    #create inventories
    myInv = Inventory(0,myAnts, constrs2, 1)
    oppInv= Inventory(1,oppAnts, constrs1, 1)
    food = Inventory(NEUTRAL,[], constrs, 0)
    invs = (myInv,oppInv,food)
    #state is made
    state = GameState(newBoard, invs, 3, 0)
    player = AIPlayer(0)

    #Now that the state is created we can test the functions
    #first test that the returned value of the current state is .501
    assert abs(player.gameStateEval(state)- .501) < .00001
    #now test that the ants on each side are equal
    assert player.numAntsEval(myInv,oppInv) == 0
    #now test that neither side has more than the other of a type of ant
    assert player.typeAntEval(state,myInv,oppInv) == 0
    #now test that the food counts are equal
    assert player.foodCountEval(myInv,oppInv) == 0
    #check that only the one ant on my side is carrying food
    assert abs(player.carryEval(state) - .001) <.00001
    




    

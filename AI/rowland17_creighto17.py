import random
import sys
import math
import unittest
from collections import namedtuple, deque, defaultdict
# import pickle
import cPickle as pickle
from os import path
import numpy as np
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))  # nopep8
from Player import Player
import Constants as c
from Construction import CONSTR_STATS, Construction
from Ant import UNIT_STATS, Ant
from Move import Move
from GameState import addCoords, subtractCoords, GameState
import AIPlayerUtils as utils
from Location import Location
from Inventory import Inventory
from Building import Building

# ConState = namedtuple('ConState', ['id', 'utility'])


class AIPlayer(Player):
    """
    Description:
        The responsibility of this class is to interact with the game
        by deciding a valid move based on a given game state. This class has
        methods that will be implemented by students in Dr. Nuxoll's AI course.

    Variables:
        playerId - The id of the player.
    """

    def __init__(self, inputPlayerId):
        """
        Creates a new Player

        Parameters:
            inputPlayerId - The id to give the new player (int)
        """
        self.state_list_file = 'rowland17_creighto17'
        self.state_list = defaultdict(float)
        if path.isfile(path.join('..', self.state_list_file)):
            # print 'State list pickle found.'
            self.load_state_list()
        self.last_states = deque(maxlen=20)
        self.discount = 0.8
        self.alpha = 0.9  # * math.exp(-0.04 * len(self.state_list))
        super(AIPlayer, self).__init__(inputPlayerId, "TD Bot 3")

    

    def getPlacement(self, currentState):
        """
        getPlacement:
            The getPlacement method corresponds to the
            action taken on setup phase 1 and setup phase 2 of the game.
            In setup phase 1, the AI player will be passed a copy of the
            state as current_state which contains the board, accessed via
            current_state.board. The player will then return a list of 11 tuple
            coordinates (from their side of the board) that represent Locations
            to place the anthill and 9 grass pieces. In setup phase 2, the
            player will again be passed the state and needs to return a list
            of 2 tuple coordinates (on their opponent's side of the board)
            which represent locations to place the food sources.
            This is all that is necessary to complete the setup phases.

        Parameters:
          current_state - The current state of the game at the time the Game is
              requesting a placement from the player.(GameState)

        Return: If setup phase 1: list of eleven 2-tuples of ints ->
                    [(x1,y1), (x2,y2),...,(x10,y10)]
                If setup phase 2: list of two 2-tuples of ints ->
                    [(x1,y1), (x2,y2)]
        """
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == c.SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move is None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw
                        # whatever I felt like in there.
                        currentState.board[x][y].constr is True
                moves.append(move)
            return moves
        elif currentState.phase == c.SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move is None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw
                        # whatever I felt like in there.
                        currentState.board[x][y].constr is True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    def get_td_move(self, current_state):
        # Get possible moves:
        all_moves = [move for move in utils.listAllLegalMoves(
            current_state) if move.moveType != c.END]

        # If there are moves left, then end the turn.
        if len(all_moves) == 0:
            return Move(c.END, None, None)
            # return Node(Move(c.END, None, None), state, 0.5)

        # Get next states
        next_states = [self.getNextState(current_state, move)
                       for move in all_moves]

        # Match states with moves
        # state_moves = [(state, move) for move, state in zip(all_moves, next_states)]

        # Condense states
        cstates = [self.condense_state(state) for state in next_states]

        # Match each cstate with corresponding move
        cstate_moves = dict((cstate, move)
                            for cstate, move in zip(cstates, all_moves))

        # Get the utility of each cstate (use .get to not increase state count)
        possible_states = [(cstate, self.state_list.get(cstate, 0))
                           for cstate in cstates]

        # Shuffle possible states
        random.shuffle(possible_states)

        # Get the best state, utility-wise
        best_state, util = max(possible_states, key=(lambda elem: elem[1]))

        # Return move
        return cstate_moves[best_state]

    def getMove(self, currentState):
        """
        Description:
            Gets the next move from the Player.

        Parameters:
          current_state - The current state of the game at the time the Game is
              requesting a move from the player. (GameState)

        Return: Move(moveType [int],
                     coordList [list of 2-tuples of ints],
                     buildType [int])
        """

        
        move = self.get_td_move(currentState)

        self.update_state(currentState)

        return move

    def getAttack(self, currentState, attackingAnt, enemyLocations):
        """
        Description:
            Gets the attack to be made from the Player

        Parameters:
          current_state - The current state of the game at the time the
                Game is requesting a move from the player. (GameState)
          attackingAnt - A clone of the ant currently making the attack. (Ant)
          enemyLocation - A list of coordinate locations for valid attacks
            (i.e. enemies within range) ([list of 2-tuples of ints])

        Return: A coordinate that matches one of the entries of enemyLocations.
                ((int,int))
        """
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    def registerWin(self, hasWon):
        # Update the utility of the final state
        status = 'win' if hasWon else 'lose'
        self.update_state(self.last_states[-1], status)
        self.save_state_list()


    def condense_state(self, state):
        """Map a state to a series of neural net inputs."""
        # Various variables used in the function
        inputs = []
        enemy_id = abs(state.whoseTurn - 1)
        our_inv = utils.getCurrPlayerInventory(state)
        enemy_inv = [
            inv for inv in state.inventories if inv.player == enemy_id].pop()
        our_food = our_inv.foodCount
        enemy_food = enemy_inv.foodCount
        food_difference = abs(our_food - enemy_food)
        our_anthill = our_inv.getAnthill()
        enemy_anthill = enemy_inv.getAnthill()
        our_queen = our_inv.getQueen()
        enemy_queen = enemy_inv.getQueen()
        food_drop_offs = []
        try:
            our_tunnel = our_inv.getTunnels()[0]
            food_drop_offs.append(our_tunnel.coords)
        except:
            pass
        food_drop_offs.append(our_anthill.coords)

        # Food related mappings
        food_inputs = []
        # pattern (1 if true) [we have more food, food difference is 0, 1-2,
        # 3+]
        food_inputs = [int(our_food > enemy_food), int(our_food == enemy_food), int(2 >= abs(
    our_food - enemy_food) >= 1), int(abs(our_food - enemy_food) >= 3)]

        # [at least one worker is carrying food, at least one worker is
        # going to deposit food]
        our_workers = [
            ant for ant in our_inv.ants if ant.type == c.WORKER]
        dropping_off = [
            ant for ant in our_workers if ant.coords in food_drop_offs and ant.carrying]
        # Really gross way of doing this....
        food_inputs += [int(any([ant.carrying for an in our_workers])),
                        int(bool(len(dropping_off)))]

        inputs += food_inputs

        # Raw ant number inputs
        n_ants_inputs = []
        # [0 workers, 1 worker, 2 workers, 3+ workers]
        n_workers = len(our_workers)
        n_ants_inputs += map(int, [n_workers == 0, n_workers ==
                                   1, n_workers == 2, n_workers > 2])

        # Attacking ant numbers
        # [0 attack ants, 1 attacker, 2, 3+]
        offensive = [c.SOLDIER, c.R_SOLDIER, c.DRONE]
        our_offense = [ant for ant in our_inv.ants if ant.type in offensive]
        enemy_offense = [
            ant for ant in enemy_inv.ants if ant.type in offensive]
        n_offense = len(our_offense)
        n_e_offense = len(enemy_offense)
        n_ants_inputs += map(int, [n_offense == 0, n_offense ==
                                   1, n_offense == 2, n_offense > 2])
        # [0 enemy attack ants, 1 attacker, 2, 3+]
        n_ants_inputs += map(int, [n_e_offense == 0, n_e_offense ==
                                   1, n_e_offense == 2, n_e_offense > 2])

        # [>5 total friendly ants]
        n_ants_inputs.append(int(our_inv.ants > 5))

        inputs += n_ants_inputs

        # Ant movement/location stuff
        move_inputs = []
        # [if a worker is leaving home area]
        our_range = [(x, y) for x in xrange(10) for y in xrange(5)]
        move_inputs.append(
            int(any([ant for ant in our_workers if ant.coords not in our_range])))
        # [if on enemy anthill, if on our anthill]
        move_inputs += map(int, [any([ant.coords ==
                                      enemy_anthill.coords for ant in our_inv.ants]),
    any([ant.coords == our_anthill.coords for ant in enemy_inv.ants])])

        # [on our anthill and no food], aka get off my anthill reeeeeeee
        move_inputs.append(int(any(
            [ant.coords == our_anthill.coords and not ant.carrying for ant in our_inv.ants])))

        # Worker movement
        # [worker exists, enemy near, carrying, moving towards food drop-off] * 5
        worker_inputs = []
        for ant in our_workers:
            ant_inputs = [1, 0, 0, 0]
            ant_x = ant.coords[0]
            ant_y = ant.coords[1]
            for enemy in enemy_inv.ants:
                if ((abs(ant_x - enemy.coords[0]) > 3) and
                        (abs(ant_y - enemy.coords[1]) > 3)):
                    continue
                ant_inputs[1] = 1
                break
            if ant.carrying and ant not in dropping_off:
                # Good if carrying ants move toward a drop off.
                ant_inputs[2] = 1

                for dist in range(2, 4):
                    for dropoff in food_drop_offs:
                        if ((abs(ant_x - dropoff[0]) < dist) and
                                (abs(ant_y - dropoff[1]) < dist)):
                            ant_inputs[3] = 1
            worker_inputs += ant_inputs
            if len(worker_inputs) == 20:
                break

        # Expand worker_inputs if needed
        worker_inputs += [0] * (20 - len(worker_inputs))

        # Offensive ants
        offensive = [c.SOLDIER, c.R_SOLDIER, c.DRONE]
        our_offense = [ant for ant in our_inv.ants if ant.type in offensive]
        enemy_offense = [
            ant for ant in enemy_inv.ants if ant.type in offensive]

        move_inputs += worker_inputs

        # [exist, on anthill, in attack range, in close range] * 5
        offense_inputs = []
        for ant in our_offense:
            ant_inputs = [1, 0, 0, 0]
            ant_x = ant.coords[0]
            ant_y = ant.coords[1]
            # good if on enemy anthill
            if ant.coords == enemy_anthill.coords:
                ant_inputs[1] = 1
            for enemy_ant in enemy_inv.ants:
                enemy_x = enemy_ant.coords[0]
                enemy_y = enemy_ant.coords[1]
                x_dist = abs(ant_x - enemy_x)
                y_dist = abs(ant_y - enemy_y)

                # good if attacker ant attacks
                if x_dist + y_dist == 1:
                    ant_inputs[2] = 1

                # weighted more if closer to attacking
                for dist in xrange(1, 8):
                    if x_dist < dist and y_dist < dist:
                        ant_inputs[3] = 1

            offense_inputs += ant_inputs
            if len(offense_inputs) == 20:
                break

        # Expand offense_inputs if needed
        offense_inputs += [0] * (20 - len(offense_inputs))

        move_inputs += offense_inputs

        # TODO: Add a lot more here from the OG score_state function
        # Distance to enemy attackers
        # Anthill health?
        # Literally anything to do with attacks
        inputs += move_inputs

        # Queen stuff
        queen_inputs = []
        # our queen
        # [7-8 health, 6-5, 4-3, 2-1, 0]
        q_hp = our_queen.health
        queen_inputs += map(int, [q_hp >= 7, 6 >= q_hp >= 5, 4 >=
                                  q_hp >= 3, 2 >= q_hp >= 1, q_hp == 0])

        inputs += queen_inputs
        # convert the inputs into a single number using bitshifting
        # http://stackoverflow.com/questions/12461361/bits-list-to-integer-in-python
        out = 0
        for bit in inputs:
            out = (out << 1) | bit

        return out

    def save_state_list(self):
        """Save the state/utilities list to a file."""
        with open(self.state_list_file, 'wb+') as f:
            # print 'Saving state list.'
            pickle.dump(self.state_list, f, pickle.HIGHEST_PROTOCOL)

    def load_state_list(self):
        """Load the state/utilities list from a file.
        Sets self.state_list to the unpickled data in the file."""
        with open(path.join('..', self.state_list_file), 'rb+') as f:
            # print 'Loading state list.'
            self.state_list = pickle.load(f)

    def update_state(self, state, status='other'):
        """Add a state to the state_list if needed, and append it
        to the list of most recent states.
        """
        if type(state) is not int:
            cstate = self.condense_state(state)
        # if cstate not in self.state_list:
        #     self.state_list[cstate] = self.reward(status)

        if not len(self.last_states):
            self.last_states.append(state)
            self.state_list[cstate] = 0.0
            return

        last_state = self.last_states[-1]
        last_cstate = self.condense_state(last_state)

        # Generate the utility of the state
        util = self.reward(status) + self.alpha * \
            (0 + self.discount * self.state_list[cstate])
        # util = self.reward(status) + self.alpha * \
        #     (0 + self.discount * self.reward(status) - self.state_list[cstate])

        self.state_list[last_cstate] = util

        # Add state to most recently encountered states
        # if cstate in self.last_states:
        #     self.last_states.remove(cstate)

        self.last_states.append(state)

        # print "new util: {}".format(util)

        # Update the alpha
        self.alpha = 0.9 * math.exp(-0.01 * len(self.state_list))

    def reward(self, status='other'):
        """Returns the reward value for a win, loss, or other state."""
        if status == 'win':
            return 1
        elif status == 'lose':
            return -1

        return -0.07

    @staticmethod
    def getNextState(currentState, move):
        """
        Version of genNextState with food carrying bug fixed.
        """
        # variables I will need
        myGameState = currentState.fastclone()
        myInv = utils.getCurrPlayerInventory(myGameState)
        me = myGameState.whoseTurn
        myAnts = myInv.ants

        # If enemy ant is on my anthill or tunnel update capture health
        myTunnels = myInv.getTunnels()
        myAntHill = myInv.getAnthill()
        for myTunnel in myTunnels:
            ant = utils.getAntAt(myGameState, myTunnel.coords)
            if ant is not None:
                opponentsAnts = myGameState.inventories[not me].ants
                if ant in opponentsAnts:
                    myTunnel.captureHealth -= 1
        if utils.getAntAt(myGameState, myAntHill.coords) is not None:
            ant = utils.getAntAt(myGameState, myAntHill.coords)
            opponentsAnts = myGameState.inventories[not me].ants
            if ant in opponentsAnts:
                myAntHill.captureHealth -= 1

        # If an ant is built update list of ants
        antTypes = [c.WORKER, c.DRONE, c.SOLDIER, c.R_SOLDIER]
        if move.moveType == c.BUILD:
            if move.buildType in antTypes:
                ant = Ant(myInv.getAnthill().coords, move.buildType, me)
                myInv.ants.append(ant)
                # Update food count depending on ant built
                if move.buildType == c.WORKER:
                    myInv.foodCount -= 1
                elif move.buildType == c.DRONE or move.buildType == c.R_SOLDIER:
                    myInv.foodCount -= 2
                elif move.buildType == c.SOLDIER:
                    myInv.foodCount -= 3

        # If a building is built update list of buildings and the update food
        # count
        if move.moveType == c.BUILD:
            if move.buildType == c.TUNNEL:
                building = Construction(move.coordList[0], move.buildType)
                myInv.constrs.append(building)
                myInv.foodCount -= 3

        # If an ant is moved update their coordinates and has moved
        if move.moveType == c.MOVE_ANT:
            newCoord = move.coordList[len(move.coordList) - 1]
            startingCoord = move.coordList[0]
            for ant in myAnts:
                if ant.coords == startingCoord:
                    ant.coords = newCoord
                    ant.hasMoved = False
                    # If an ant is carrying food and ends on the anthill or tunnel
                    # drop the food
                    if ant.carrying and ant.coords == myInv.getAnthill().coords:
                        myInv.foodCount += 1
                        # ant.carrying = False
                    for tunnels in myTunnels:
                        if ant.carrying and (ant.coords == tunnels.coords):
                            myInv.foodCount += 1
                            # ant.carrying = False
                    # If an ant doesn't have food and ends on the food grab
                    # food
                    if not ant.carrying:
                        foods = utils.getConstrList(
                            myGameState, None, (c.FOOD,))
                        for food in foods:
                            if food.coords == ant.coords:
                                ant.carrying = True
                    # If my ant is close to an enemy ant attack it
                    adjacentTiles = utils.listAdjacent(ant.coords)
                    for adj in adjacentTiles:
                        # If ant is adjacent my ant
                        if utils.getAntAt(myGameState, adj) is not None:
                            closeAnt = utils.getAntAt(myGameState, adj)
                            if closeAnt.player != me:  # if the ant is not me
                                closeAnt.health = closeAnt.health - \
                                    UNIT_STATS[ant.type][c.ATTACK]  # attack
                                # If an enemy is attacked and looses all its health remove it from the other players
                                # inventory
                                if closeAnt.health <= 0:
                                    enemyAnts = myGameState.inventories[
                                        not me].ants
                                    for enemy in enemyAnts:
                                        if closeAnt.coords == enemy.coords:
                                            myGameState.inventories[
                                                not me].ants.remove(enemy)
                                # If attacked an ant already don't attack any
                                # more
                                break
        return myGameState




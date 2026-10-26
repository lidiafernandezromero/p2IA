#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""
import contextlib
import copy
import io
import math

import chess
import board
import numpy as np
import sys
import queue
from typing import List

RawStateType = List[List[List[int]]]

from itertools import permutations


class Aichess():
    """
    A class to represent the game of chess.

    ...

    Attributes:
    -----------
    chess : Chess
        represents the chess game
        
    listNextStates : list
        List of next possible states for the current player.

    listVisitedStates : list
        List of all visited states during A* and other search algorithms.

    listVisitedSituations : list
        List of visited game situations (state + color) for minimax/alpha-beta pruning.

    pathToTarget : list
        Sequence of states from the initial state to the target (used by A*).

    depthMax : int
        Maximum search depth for minimax/alpha-beta searches.

    dictPath : dict
        Dictionary used to reconstruct the path in A* search.

    Methods:
    --------
    copyState(state) -> list
        Returns a deep copy of the given state.

    isVisitedSituation(color, mystate) -> bool
        Checks whether a given state with a specific color has already been visited.

    getListNextStatesW(myState) -> list
        Returns a list of possible next states for the white pieces.

    getListNextStatesB(myState) -> list
        Returns a list of possible next states for the black pieces.

    isSameState(a, b) -> bool
        Checks whether two states represent the same board configuration.

    isVisited(mystate) -> bool
        Checks if a given state has been visited in search algorithms.

    getCurrentState() -> list
        Returns the combined state of both white and black pieces.

    getNextPositions(state) -> list
        Returns a list of possible next positions for a given state.

    heuristica(currentState, color) -> int
        Calculates a heuristic value for the current state from the perspective of the given color.

    movePieces(start, depthStart, to, depthTo) -> None
        Moves all pieces along the path between two states.

    changeState(start, to) -> None
        Moves a single piece from start state to to state.

    reconstructPath(state, depth) -> None
        Reconstructs the path from initial state to the target state for A*.

    isWatchedWk(currentState) / isWatchedBk(currentState) -> bool
        Checks if the white or black king is under threat.

    allWkMovementsWatched(currentState) / allBkMovementsWatched(currentState) -> bool
        Checks if all moves of the white or black king are under threat.

    isWhiteInCheckMate(currentState) / isBlackInCheckMate(currentState) -> bool
        Determines if the white or black king is in checkmate.

    minimaxGame(depthWhite: int, depthBlack: int) -> To be implemented by you
        Simulates a full game using the Minimax algorithm for both white and black.

    alphaBetaPoda(depthWhite: int, depthBlack: int) -> To be implemented by you
        Simulates a game where both players use Minimax with Alpha-Beta Pruning.

    expectimax(depthWhite: int, depthBlack: int) -> To be implemented by you
        Simulates a full game where both players use the Expectimax algorithm.

    mean(values: list[float]) -> float
        Returns the arithmetic mean (average) of a list of numerical values.

    standardDeviation(values: list[float], mean_value: float) -> float
        Computes the standard deviation of a list of numerical values based on the given mean.

    calculateValue(values: list[float]) -> float
        Computes the expected value from a set of scores using soft-probabilities 
        derived from normalized values (exponential weighting). Can be useful for Expectimax.

    """

    def __init__(self, TA, myinit=True):

        if myinit:
            self.chess = chess.Chess(TA, True)
        else:
            self.chess = chess.Chess([], False)

        self.listNextStates = []
        self.listVisitedStates = []
        self.listVisitedSituations = []
        # situations (state + turn) already played in the real game, to detect repetitions fast
        self.setVisitedSituations = set()
        self.pathToTarget = []
        self.depthMax = 8;
        # Dictionary to reconstruct the visited path
        self.dictPath = {}
        # Prepare a dictionary to control the visited state and at which
        # depth they were found for DepthFirstSearchOptimized
        self.dictVisitedStates = {}

    def copyState(self, state):
        
        copyState = []
        for piece in state:
            copyState.append(piece.copy())
        return copyState
        
    def isVisitedSituation(self, color, mystate):
        
        if (len(self.listVisitedSituations) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedSituations)):
                    if self.isSameState(list(perm_state[j]), self.listVisitedSituations.__getitem__(k)[1]) and color == \
                            self.listVisitedSituations.__getitem__(k)[0]:
                        isVisited = True

            return isVisited
        else:
            return False

    #key of a situation: the turn and the pieces (the order of the pieces does not matter)
    def situationKey(self, state, whitesTurn):
        return (whitesTurn, frozenset(tuple(piece) for piece in state))

    #saves a situation of the real game
    def addVisitedSituation(self, state, whitesTurn):
        self.setVisitedSituations.add(self.situationKey(state, whitesTurn))

    #True if the situation has already been played in the real game (repetition)
    def isRepeated(self, state, whitesTurn):
        return self.situationKey(state, whitesTurn) in self.setVisitedSituations

    def getListNextStatesW(self, myState):

        self.chess.boardSim.getListNextStatesW(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def getListNextStatesB(self, myState):
        self.chess.boardSim.getListNextStatesB(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def isSameState(self, a, b):

        isSameState1 = True
        # a and b are lists
        for k in range(len(a)):

            if a[k] not in b:
                isSameState1 = False

        isSameState2 = True
        # a and b are lists
        for k in range(len(b)):

            if b[k] not in a:
                isSameState2 = False

        isSameState = isSameState1 and isSameState2
        return isSameState

    def isVisited(self, mystate):

        if (len(self.listVisitedStates) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedStates)):

                    if self.isSameState(list(perm_state[j]), self.listVisitedStates[k]):
                        isVisited = True

            return isVisited
        else:
            return False 

    def newBoardSim(self, listStates):
        # We create a  new boardSim
        TA = np.zeros((8, 8))
        for state in listStates:
            TA[state[0]][state[1]] = state[2]

        self.chess.newBoardSim(TA)

    def getPieceState(self, state, piece):
        pieceState = None
        for i in state:
            if i[2] == piece:
                pieceState = i
                break
        return pieceState

    def getCurrentState(self):
        listStates = []
        for i in self.chess.board.currentStateW:
            listStates.append(i)
        for j in self.chess.board.currentStateB:
            listStates.append(j)
        return listStates

    def getNextPositions(self, state):
        # Given a state, we check the next possible states
        # From these, we return a list with position, i.e., [row, column]
        if state == None:
            return None
        if state[2] > 6:
            nextStates = self.getListNextStatesB([state])
        else:
            nextStates = self.getListNextStatesW([state])
        nextPositions = []
        for i in nextStates:
            nextPositions.append(i[0][0:2])
        return nextPositions

    def getWhiteState(self, currentState):
        whiteState = []
        wkState = self.getPieceState(currentState, 6)
        whiteState.append(wkState)
        wrState = self.getPieceState(currentState, 2)
        if wrState != None:
            whiteState.append(wrState)
        return whiteState

    def getBlackState(self, currentState):
        blackState = []
        bkState = self.getPieceState(currentState, 12)
        blackState.append(bkState)
        brState = self.getPieceState(currentState, 8)
        if brState != None:
            blackState.append(brState)
        return blackState

    def getMovement(self, state, nextState):
        # Given a state and a successor state, return the postiion of the piece that has been moved in both states
        pieceState = None
        pieceNextState = None
        for piece in state:
            if piece not in nextState:
                movedPiece = piece[2]
                pieceNext = self.getPieceState(nextState, movedPiece)
                if pieceNext != None:
                    pieceState = piece
                    pieceNextState = pieceNext
                    break

        return [pieceState, pieceNextState]

    def movePieces(self, start, depthStart, to, depthTo):
        
        # To move from one state to the next we will need to find
        # the state in common, and then move until the node 'to'
        moveList = []
        # We want that the depths are equal to find a common ancestor
        nodeTo = to
        nodeStart = start
        # if the depth of the node To is larger than that of start, 
        # we pick the ancesters of the node until being at the same
        # depth
        while(depthTo > depthStart):
            moveList.insert(0,to)
            nodeTo = self.dictPath[str(nodeTo)][0]
            depthTo-=1
        # Analogous to the previous case, but we trace back the ancestors
        #until the node 'start'
        while(depthStart > depthTo):
            ancestreStart = self.dictPath[str(nodeStart)][0]
            # We move the piece the the parerent state of nodeStart
            self.changeState(nodeStart, ancestreStart)
            nodeStart = ancestreStart
            depthStart -= 1

        moveList.insert(0,nodeTo)
        # We seek for common node
        while nodeStart != nodeTo:
            ancestreStart = self.dictPath[str(nodeStart)][0]
            # Move the piece the the parerent state of nodeStart
            self.changeState(nodeStart,ancestreStart)
            # pick the parent of nodeTo
            nodeTo = self.dictPath[str(nodeTo)][0]
            # store in the list
            moveList.insert(0,nodeTo)
            nodeStart = ancestreStart
        # Move the pieces from the node in common
        # until the node 'to'
        for i in range(len(moveList)):
            if i < len(moveList) - 1:
                self.changeState(moveList[i],moveList[i+1])

    def reconstructPath(self, state, depth):
        # Once the solution is found, reconstruct the path taken to reach it
        for i in range(depth):
            self.pathToTarget.insert(0, state)
            # For each node, retrieve its parent from dictPath
            state = self.dictPath[str(state)][0]

        # Insert the root node at the beginning
        self.pathToTarget.insert(0, state)


    def changeState(self, start, to):
        # Determine which piece has moved from the start state to the next state
        if start[0] == to[0]:
            movedPieceStart = 1
            movedPieceTo = 1
        elif start[0] == to[1]:
            movedPieceStart = 1
            movedPieceTo = 0
        elif start[1] == to[0]:
            movedPieceStart = 0
            movedPieceTo = 1
        else:
            movedPieceStart = 0
            movedPieceTo = 0

        # Move the piece that changed
        self.chess.moveSim(start[movedPieceStart], to[movedPieceTo])     

    def isWatchedBk(self, currentState):

        self.newBoardSim(currentState)

        bkPosition = self.getPieceState(currentState, 12)[0:2]
        wkState = self.getPieceState(currentState, 6)
        wrState = self.getPieceState(currentState, 2)

        # If the white king has been captured, this is not a valid configuration
        if wkState is None:
            return False

        # Check all possible moves of the white king to see if it can capture the black king
        for wkPosition in self.getNextPositions(wkState):
            if bkPosition == wkPosition:
                # Black king would be in check
                return True

        if wrState is not None:
            # Check all possible moves of the white rook to see if it can capture the black king
            for wrPosition in self.getNextPositions(wrState):
                if bkPosition == wrPosition:
                    return True

        return False

    def allBkMovementsWatched(self, currentState):
        # In this method, we check if the black king is threatened by the white pieces

        self.newBoardSim(currentState)
        # Get the current state of the black king
        bkState = self.getPieceState(currentState, 12)
        allWatched = False

        # If the black king is on the edge of the board, all its moves might be under threat
        if bkState[0] == 0 or bkState[0] == 7 or bkState[1] == 0 or bkState[1] == 7:
            wrState = self.getPieceState(currentState, 2)
            whiteState = self.getWhiteState(currentState)
            allWatched = True
            # Get the future states of the black pieces
            nextBStates = self.getListNextStatesB(self.getBlackState(currentState))

            for state in nextBStates:
                newWhiteState = whiteState.copy()
                # Check if the white rook has been captured; if so, remove it from the state
                if wrState is not None and wrState[0:2] == state[0][0:2]:
                    newWhiteState.remove(wrState)
                state = state + newWhiteState
                # Move the black pieces to the new state
                self.newBoardSim(state)

                # Check if in this position the black king is not threatened; 
                # if so, not all its moves are under threat
                if not self.isWatchedBk(state):
                    allWatched = False
                    break

        # Restore the original board state
        self.newBoardSim(currentState)
        return allWatched

    def isBlackInCheckMate(self, currentState):
        if self.isWatchedBk(currentState) and self.allBkMovementsWatched(currentState):
            return True

        return False


    def isWatchedWk(self, currentState):
        self.newBoardSim(currentState)

        wkPosition = self.getPieceState(currentState, 6)[0:2]
        bkState = self.getPieceState(currentState, 12)
        brState = self.getPieceState(currentState, 8)

        # If the black king has been captured, this is not a valid configuration
        if bkState is None:
            return False

        # Check all possible moves for the black king and see if it can capture the white king
        for bkPosition in self.getNextPositions(bkState):
            if wkPosition == bkPosition:
                # White king would be in check
                return True

        if brState is not None:
            # Check all possible moves for the black rook and see if it can capture the white king
            for brPosition in self.getNextPositions(brState):
                if wkPosition == brPosition:
                    return True

        return False

    def allWkMovementsWatched(self, currentState):

        self.newBoardSim(currentState)
        # In this method, we check if the white king is threatened by black pieces
        # Get the current state of the white king
        wkState = self.getPieceState(currentState, 6)
        allWatched = False

        # If the white king is on the edge of the board, it may be more vulnerable
        if wkState[0] == 0 or wkState[0] == 7 or wkState[1] == 0 or wkState[1] == 7:
            # Get the state of the black pieces
            brState = self.getPieceState(currentState, 8)
            blackState = self.getBlackState(currentState)
            allWatched = True

            # Get the possible future states for the white pieces
            nextWStates = self.getListNextStatesW(self.getWhiteState(currentState))
            for state in nextWStates:
                newBlackState = blackState.copy()
                # Check if the black rook has been captured. If so, remove it from the state
                if brState is not None and brState[0:2] == state[0][0:2]:
                    newBlackState.remove(brState)
                state = state + newBlackState
                # Move the white pieces to their new state
                self.newBoardSim(state)
                # Check if the white king is not threatened in this position,
                # which implies that not all of its possible moves are under threat
                if not self.isWatchedWk(state):
                    allWatched = False
                    break

        # Restore the original board state
        self.newBoardSim(currentState)
        return allWatched


    def isWhiteInCheckMate(self, currentState):
        if self.isWatchedWk(currentState) and self.allWkMovementsWatched(currentState):
            return True
        return False
    

    def heuristica(self, currentState, color):
        # This method calculates the heuristic value for the current state.
        # The value is initially computed from White's perspective.
        # If the 'color' parameter indicates Black, the final value is multiplied by -1.

        value = 0

        bkState = self.getPieceState(currentState, 12)  # Black King
        wkState = self.getPieceState(currentState, 6)   # White King
        wrState = self.getPieceState(currentState, 2)   # White Rook
        brState = self.getPieceState(currentState, 8)   # Black Rook

        filaBk, columnaBk = bkState[0], bkState[1]
        filaWk, columnaWk = wkState[0], wkState[1]

        if wrState is not None:
            filaWr, columnaWr = wrState[0], wrState[1]
        if brState is not None:
            filaBr, columnaBr = brState[0], brState[1]

        # If the black rook has been captured
        if brState is None:
            value += 50
            fila = abs(filaBk - filaWk)
            columna = abs(columnaWk - columnaBk)
            distReis = min(fila, columna) + abs(fila - columna)

            if distReis >= 3 and wrState is not None:
                filaR = abs(filaBk - filaWr)
                columnaR = abs(columnaWr - columnaBk)
                value += (min(filaR, columnaR) + abs(filaR - columnaR)) / 10

            # For White: the closer our king is to the opponent’s king, the better.
            # Subtract 7 from the king-to-king distance since 7 is the maximum distance possible on the board.
            value += (7 - distReis)

            # If the black king is against a wall, prioritize pushing him into a corner (ideal for checkmate).
            if bkState[0] in (0, 7) or bkState[1] in (0, 7):
                value += (abs(filaBk - 3.5) + abs(columnaBk - 3.5)) * 10
            # Otherwise, encourage moving the black king closer to the wall.
            else:
                value += (max(abs(filaBk - 3.5), abs(columnaBk - 3.5))) * 10

        # If the white rook has been captured.
        # The logic is similar to the previous section but with reversed (negative) values.
        if wrState is None:
            value -= 50
            fila = abs(filaBk - filaWk)
            columna = abs(columnaWk - columnaBk)
            distReis = min(fila, columna) + abs(fila - columna)

            if distReis >= 3 and brState is not None:
                filaR = abs(filaWk - filaBr)
                columnaR = abs(columnaBr - columnaWk)
                value -= (min(filaR, columnaR) + abs(filaR - columnaR)) / 10

            # For White: being closer to the opposing king is better.
            # Subtract 7 from the distance since that’s the maximum possible distance.
            value += (-7 + distReis)

            # If the white king is against a wall, penalize that position.
            if wkState[0] in (0, 7) or wkState[1] in (0, 7):
                value -= (abs(filaWk - 3.5) + abs(columnaWk - 3.5)) * 10
            # Otherwise, encourage the king to stay away from the wall.
            else:
                value -= (max(abs(filaWk - 3.5), abs(columnaWk - 3.5))) * 10

        # If the black king is in check, reward this state.
        if self.isWatchedBk(currentState):
            value += 20

        # If the white king is in check, penalize this state.
        if self.isWatchedWk(currentState):
            value -= 20        
        
        

        # If the current player is Black, invert the heuristic value.
        if not color:
            value *= -1

        return value
    
    def mean(self, values):
        # Calculate the arithmetic mean (average) of a list of numeric values.
        total = 0
        n = len(values)
        
        for i in range(n):
            total += values[i]

        return total / n


    def standard_deviation(self, values, mean_value):
        # Calculate the standard deviation of a list of values.
            total = 0
            n = len(values)

            for i in range(n):
                total += pow(values[i] - mean_value, 2)

            return pow(total / n, 1 / 2)


    def calculateValue(self, values):
        # Calculate a weighted expected value based on normalized probabilities. - useful for Expectimax.
        
        # Compute mean and standard deviation
        mean_value = self.mean(values)
        std_dev = self.standard_deviation(values, mean_value)

        # If all values are equal, the deviation is 0, equal probability
        if std_dev == 0:
            return values[0]

        expected_value = 0
        total_weight = 0
        n = len(values)

        for i in range(n):
            # Normalize value using z-score
            normalized_value = (values[i] - mean_value) / std_dev

            # Convert to a positive weight using e^(-x)
            positive_weight = pow(1 / math.e, normalized_value)

            # Weighted sum
            expected_value += positive_weight * values[i]
            total_weight += positive_weight

        # Final expected value (weighted average)
        return expected_value / total_weight


    #---OUR IMPLEMENTATION !---

    #auxiliar funcition of minimaxGame, it returns the best value for the current player

    # returns [value, best next state]
    #from the white's point of view: white maximizes the value, black minimizes it

    #IMPORTANT!!: here, depth is the number of moves TO reach the state,
    #not the moves that we have made until now (as in the first practical)
    def minimax(self, currentState, depth, whitesTurn):

        #if any player ate a king in the simulator (illegal but fair in the simulator), the game is over
        if self.getPieceState(currentState, 12) is None: #12:black king
            return [1000 + depth, None] # + depth because we want to win as fast as possible
        #being depth the lack of moves to reach this state
        
        if self.getPieceState(currentState, 6) is None: #6:white king
            return [-1000 - depth, None]

        #if only the two kings are left nobody can win (insufficient material): tie
        #the game loop already ends here, so the search must value it as a tie (0)
        if self.getPieceState(currentState, 2) is None and self.getPieceState(currentState, 8) is None:
            return [0, None]


        #if I have reached the maximum depth:
        if depth == 0:
            # check the checkmate
            if whitesTurn and self.isWhiteInCheckMate(currentState):
                return [-1000, None]
            if not whitesTurn and self.isBlackInCheckMate(currentState):
                return [1000, None]
            #analize the current state with the heuristic
            return [self.heuristica(currentState, True), None]

        # builds a new board simulator with the currentState 
        #bc the functions getListNextStatesX use the boardSim to get the next states
        self.newBoardSim(currentState)

        #next states for the current player
        if whitesTurn:
            #myState = self.getWhiteState(currentState)
            theirState = self.getBlackState(currentState)
            nextStates = self.getListNextStatesW(self.getWhiteState(currentState))
            bestValue = -math.inf

        else:
            #myState = self.getBlackState(currentState)
            theirState = self.getWhiteState(currentState)
            nextStates = self.getListNextStatesB(self.getBlackState(currentState))
            bestValue = math.inf    

        #Best state: to keep the best value of the best movement found so far
        # white ones maximizes the value, black minimizes it
        bestState = None

        #for each possible next state, we call minimax recursively to get the value of that state
        for nextState in nextStates:
            # if the moved piece lands on an opponent's piece, it is captured (killed).
            # we need to remove that piece from the state before passing it to the next minimax call.
            fullState = nextState.copy()

            # Add the opponent's pieces that have not been captured
            for piece in theirState:
                if piece[0:2] != nextState[0][0:2]:
                    fullState.append(piece)

            #don't permit to eat the rival king (illegal move) 
            # LEGALLITY FILTER: descart moves that leave my king on scac
            if whitesTurn and self.isWatchedWk(fullState):
                continue
            if not whitesTurn and self.isWatchedBk(fullState):
                continue

            # call minimax recursively to get the value of the next state
            # a situation already played in the real game is a repetition: tie
            if self.isRepeated(fullState, not whitesTurn):
                value = 0
            else:
                value = self.minimax(fullState, depth - 1, not whitesTurn)[0]

            #update the best value and best state if the current value is better than the best value found so far
            if whitesTurn and value > bestValue:
                bestValue = value
                bestState = fullState
            if not whitesTurn and value < bestValue:
                bestValue = value
                bestState = fullState

        # no legal move left: checkmate or ties 
        if bestState is None:
            if whitesTurn:
                inCheck = self.isWatchedWk(currentState)
                return [-1000 - depth, None] if inCheck else [0, None]
            else:
                inCheck = self.isWatchedBk(currentState)
                return [1000 + depth, None] if inCheck else [0, None]

        return [bestValue, bestState]    



    #returns 'W' if the white pieces win, 'B' the other way around, 
    #'none' if there's a tie
    def minimaxGame(self, depthWhite, depthBlack):

        #getCurrentState returns references to the lists of the real board
        currentState = self.getCurrentState()
        whitesTurn = True
        maxMoves = 100 #so we don't get stuck in an infinite loop, it would be a tie

        for i in range (maxMoves):

            # if any king has disappeared in the simulator, the game has ended
            if self.getPieceState(currentState, 6) is None:
                print("Black wins!")
                return 'B'
            if self.getPieceState(currentState, 12) is None:
                print("White wins!")
                return 'W'

            # if we only have the two kings left: no checkmate possible
            if self.getPieceState(currentState, 2) is None and self.getPieceState(currentState, 8) is None:
                print("Insufficient material (2kings): ties")
                return None

            #Check for checkmate BEFORE the move, so the king is never captured in the real game
            if whitesTurn and self.isWhiteInCheckMate(currentState):
                print("Black wins!")
                return 'B'
            elif not whitesTurn and self.isBlackInCheckMate(currentState):
                print("White wins!")
                return 'W'

            #we get the depth of the current player for the minimax call
            if whitesTurn:
                depth = depthWhite
            else:
                depth = depthBlack


            # 1) decision on the board SIMULATION
            result = self.minimax(currentState, depth, whitesTurn)
            bestState = result[1]

            if bestState is None:
                if whitesTurn and self.isWhiteInCheckMate(currentState):
                    print("Black wins!")
                    return 'B'

                if not whitesTurn and self.isBlackInCheckMate(currentState):
                    print("White wins!")
                    return 'W'

                print("No moves, ties")
                return None

            # 2) move the REAL board with the decision
            orig, dest = self.getMovement(currentState, bestState)
            # [0:2] keeps the position of the pieces (row, column), not the piece type
            self.chess.move(orig[0:2], dest[0:2])
             
            # 3) actualize the state and change the turn
            currentState = self.copyState(bestState)
            whitesTurn = not whitesTurn
            self.addVisitedSituation(currentState, whitesTurn)

        print("Limit of plays: ties")
        return None

    



    #auxiliar function of alphaBetaPoda, it is the same as minimax but it cuts the branches
    #that can't change the final decision

    # returns [value, best next state]
    #from the white's point of view: white maximizes the value, black minimizes it

    #alpha: best value that white (max) can guarantee so far
    #beta: best value that black (min) can guarantee so far
    def alphaBeta(self, currentState, depth, whitesTurn, alpha, beta):

        #if any player ate a king in the simulator (illegal but fair in the simulator), the game is over
        if self.getPieceState(currentState, 12) is None: #12:black king
            return [1000 + depth, None] # + depth because we want to win as fast as possible

        if self.getPieceState(currentState, 6) is None: #6:white king
            return [-1000 - depth, None]

        #if only the two kings are left nobody can win (insufficient material): tie
        #the game loop already ends here, so the search must value it as a tie (0)
        if self.getPieceState(currentState, 2) is None and self.getPieceState(currentState, 8) is None:
            return [0, None]

        #if I have reached the maximum depth:
        if depth == 0:
            # check the checkmate
            if whitesTurn and self.isWhiteInCheckMate(currentState):
                return [-1000, None]
            if not whitesTurn and self.isBlackInCheckMate(currentState):
                return [1000, None]
            #analize the current state with the heuristic
            return [self.heuristica(currentState, True), None]

        # builds a new board simulator with the currentState
        #bc the functions getListNextStatesX use the boardSim to get the next states
        self.newBoardSim(currentState)

        #next states for the current player
        if whitesTurn:
            theirState = self.getBlackState(currentState)
            nextStates = self.getListNextStatesW(self.getWhiteState(currentState))
            bestValue = -math.inf

        else:
            theirState = self.getWhiteState(currentState)
            nextStates = self.getListNextStatesB(self.getBlackState(currentState))
            bestValue = math.inf

        #Best state: to keep the best movement found so far
        bestState = None

        for nextState in nextStates:
            # if the moved piece lands on an opponent's piece, it is captured (killed).
            fullState = nextState.copy()

            # Add the opponent's pieces that have not been captured
            for piece in theirState:
                if piece[0:2] != nextState[0][0:2]:
                    fullState.append(piece)

            # LEGALLITY FILTER: descart moves that leave my king on scac
            if whitesTurn and self.isWatchedWk(fullState):
                continue
            if not whitesTurn and self.isWatchedBk(fullState):
                continue

            # call alphaBeta recursively to get the value of the next state
            # a situation already played in the real game is a repetition: tie
            if self.isRepeated(fullState, not whitesTurn):
                value = 0
            else:
                value = self.alphaBeta(fullState, depth - 1, not whitesTurn, alpha, beta)[0]

            #update the best value, the best state and the alpha/beta of the current player
            if whitesTurn:
                if value > bestValue:
                    bestValue = value
                    bestState = fullState
                alpha = max(alpha, bestValue)
            else:
                if value < bestValue:
                    bestValue = value
                    bestState = fullState
                beta = min(beta, bestValue)

            #pruning: the other player already has a better option in another branch,
            #so he will never let us arrive here and we don't need to see the rest of moves
            if alpha >= beta:
                break

        # no legal move left: checkmate or ties
        if bestState is None:
            if whitesTurn:
                inCheck = self.isWatchedWk(currentState)
                return [-1000 - depth, None] if inCheck else [0, None]
            else:
                inCheck = self.isWatchedBk(currentState)
                return [1000 + depth, None] if inCheck else [0, None]

        return [bestValue, bestState]



    #returns 'W' if the white pieces win, 'B' the other way around,
    #'none' if there's a tie
    #whitesAlphaBeta: True if both players use alpha-beta (exercise 4),
    #False if white plays with minimax and only black uses alpha-beta (exercise 3)
    def alphaBetaPoda(self, depthWhite, depthBlack, whitesAlphaBeta=True):

        #getCurrentState returns references to the lists of the real board
        currentState = self.getCurrentState()
        whitesTurn = True
        maxMoves = 100 #so we don't get stuck in an infinite loop, it would be a tie

        for i in range (maxMoves):

            # if any king has disappeared in the simulator, the game has ended
            if self.getPieceState(currentState, 6) is None:
                print("Black wins!")
                return 'B'
            if self.getPieceState(currentState, 12) is None:
                print("White wins!")
                return 'W'

            # if we only have the two kings left: no checkmate possible
            if self.getPieceState(currentState, 2) is None and self.getPieceState(currentState, 8) is None:
                print("Insufficient material (2kings): ties")
                return None

            #Check for checkmate BEFORE the move, so the king is never captured in the real game
            if whitesTurn and self.isWhiteInCheckMate(currentState):
                print("Black wins!")
                return 'B'
            elif not whitesTurn and self.isBlackInCheckMate(currentState):
                print("White wins!")
                return 'W'

            #we get the depth of the current player for the alphaBeta call
            if whitesTurn:
                depth = depthWhite
            else:
                depth = depthBlack

            # 1) decision on the board SIMULATION
            if whitesTurn and not whitesAlphaBeta:
                result = self.minimax(currentState, depth, whitesTurn)
            else:
                # initialize alpha and beta with the worst possible values for each player
                result = self.alphaBeta(currentState, depth, whitesTurn, -math.inf, math.inf)
            bestState = result[1]

            if bestState is None:
                if whitesTurn and self.isWhiteInCheckMate(currentState):
                    print("Black wins!")
                    return 'B'

                if not whitesTurn and self.isBlackInCheckMate(currentState):
                    print("White wins!")
                    return 'W'

                print("No moves, ties")
                return None

            # 2) move the REAL board with the decision
            orig, dest = self.getMovement(currentState, bestState)
            # [0:2] keeps the position of the pieces (row, column), not the piece type
            self.chess.move(orig[0:2], dest[0:2])

            # 3) actualize the state and change the turn
            currentState = self.copyState(bestState)
            whitesTurn = not whitesTurn
            self.addVisitedSituation(currentState, whitesTurn)

        print("Limit of plays: ties")
        return None


    #auxiliar function of expectimax, it is the same as minimax but the black nodes
    #are chance nodes: instead of taking the minimum, we take the expected value
    #of the children (calculateValue)

    # returns [value, best next state]
    #from the white's point of view: white maximizes the value, black is an expected value
    def expectimaxValue(self, currentState, depth, whitesTurn):

        #if any player ate a king in the simulator (illegal but fair in the simulator), the game is over
        if self.getPieceState(currentState, 12) is None: #12:black king
            return [1000 + depth, None] # + depth because we want to win as fast as possible

        if self.getPieceState(currentState, 6) is None: #6:white king
            return [-1000 - depth, None]

        #if only the two kings are left nobody can win (insufficient material): tie
        #the game loop already ends here, so the search must value it as a tie (0)
        if self.getPieceState(currentState, 2) is None and self.getPieceState(currentState, 8) is None:
            return [0, None]

        #if I have reached the maximum depth:
        if depth == 0:
            # check the checkmate
            if whitesTurn and self.isWhiteInCheckMate(currentState):
                return [-1000, None]
            if not whitesTurn and self.isBlackInCheckMate(currentState):
                return [1000, None]
            #analize the current state with the heuristic
            return [self.heuristica(currentState, True), None]

        # builds a new board simulator with the currentState
        #bc the functions getListNextStatesX use the boardSim to get the next states
        self.newBoardSim(currentState)

        #next states for the current player
        if whitesTurn:
            theirState = self.getBlackState(currentState)
            nextStates = self.getListNextStatesW(self.getWhiteState(currentState))
            bestValue = -math.inf
        else:
            theirState = self.getWhiteState(currentState)
            nextStates = self.getListNextStatesB(self.getBlackState(currentState))

        bestState = None
        #values of all the legal children, used for the expected value in black nodes
        values = []

        for nextState in nextStates:
            # if the moved piece lands on an opponent's piece, it is captured (killed).
            fullState = nextState.copy()

            # Add the opponent's pieces that have not been captured
            for piece in theirState:
                if piece[0:2] != nextState[0][0:2]:
                    fullState.append(piece)

            # LEGALLITY FILTER: descart moves that leave my king on scac
            if whitesTurn and self.isWatchedWk(fullState):
                continue
            if not whitesTurn and self.isWatchedBk(fullState):
                continue

            # call expectimaxValue recursively to get the value of the next state
            # a situation already played in the real game is a repetition: tie
            if self.isRepeated(fullState, not whitesTurn):
                value = 0
            else:
                value = self.expectimaxValue(fullState, depth - 1, not whitesTurn)[0]
            values.append(value)

            #white (max node): keeps the best value and its state
            if whitesTurn and value > bestValue:
                bestValue = value
                bestState = fullState
            #black (chance node): we only need a state to return, the value is the expected one
            if not whitesTurn and bestState is None:
                bestState = fullState

        # no legal move left: checkmate or ties
        if bestState is None:
            if whitesTurn:
                inCheck = self.isWatchedWk(currentState)
                return [-1000 - depth, None] if inCheck else [0, None]
            else:
                inCheck = self.isWatchedBk(currentState)
                return [1000 + depth, None] if inCheck else [0, None]

        if not whitesTurn:
            bestValue = self.calculateValue(values)

        return [bestValue, bestState]



    #returns 'W' if the white pieces win, 'B' the other way around,
    #'none' if there's a tie
    #white plays expectimax and black plays alpha-beta
    def expectimax(self, depthWhite, depthBlack):

        #getCurrentState returns references to the lists of the real board
        currentState = self.getCurrentState()
        whitesTurn = True
        maxMoves = 100 #so we don't get stuck in an infinite loop, it would be a tie

        for i in range (maxMoves):

            # if any king has disappeared in the simulator, the game has ended
            if self.getPieceState(currentState, 6) is None:
                print("Black wins!")
                return 'B'
            if self.getPieceState(currentState, 12) is None:
                print("White wins!")
                return 'W'

            # if we only have the two kings left: no checkmate possible
            if self.getPieceState(currentState, 2) is None and self.getPieceState(currentState, 8) is None:
                print("Insufficient material (2kings): ties")
                return None

            #Check for checkmate BEFORE the move, so the king is never captured in the real game
            if whitesTurn and self.isWhiteInCheckMate(currentState):
                print("Black wins!")
                return 'B'
            elif not whitesTurn and self.isBlackInCheckMate(currentState):
                print("White wins!")
                return 'W'

            # 1) decision on the board SIMULATION
            if whitesTurn:
                result = self.expectimaxValue(currentState, depthWhite, whitesTurn)
            else:
                result = self.alphaBeta(currentState, depthBlack, whitesTurn, -math.inf, math.inf)
            bestState = result[1]

            if bestState is None:
                if whitesTurn and self.isWhiteInCheckMate(currentState):
                    print("Black wins!")
                    return 'B'

                if not whitesTurn and self.isBlackInCheckMate(currentState):
                    print("White wins!")
                    return 'W'

                print("No moves, ties")
                return None

            # 2) move the REAL board with the decision
            orig, dest = self.getMovement(currentState, bestState)
            # [0:2] keeps the position of the pieces (row, column), not the piece type
            self.chess.move(orig[0:2], dest[0:2])

            # 3) actualize the state and change the turn
            currentState = self.copyState(bestState)
            whitesTurn = not whitesTurn
            self.addVisitedSituation(currentState, whitesTurn)

        print("Limit of plays: ties")
        return None


#---SIMULATIONS OF THE PRACTICAL---

#creates a new game with the initial position of the practical
#we need a new Aichess for each game, bc the real board is modified when we play
def newGame():
    TA = np.zeros((8, 8))
    TA[7][0] = 2   # white rook
    TA[7][5] = 6   # white king
    TA[0][7] = 8   # black rook
    TA[0][5] = 12  # black king
    return Aichess(TA, True)


# (Idea given by AI, as explained in the inform)
# plays one game and returns 'W' if the white pieces win, 'B' the other way around,
#None if there's a tie
#game: function that receives the Aichess and returns the result of the game
#the prints of the simulator are hidden so the terminal is readable
def playGame(game):
    ai = newGame()
    with contextlib.redirect_stdout(io.StringIO()):
        result = game(ai)
    return result


#plays n games and returns [whiteWins, blackWins, ties]
def playGames(game, n):
    whiteWins = 0
    blackWins = 0
    ties = 0

    for i in range(n):
        result = playGame(game)
        if result == 'W':
            whiteWins += 1
        elif result == 'B':
            blackWins += 1
        else:
            ties += 1
        print("  game", i + 1, "/", n, "->", result)

    return [whiteWins, blackWins, ties]


#---EXERCISE 2: minimax vs minimax, depth 3 and 4 for both players---

def exercise2(n=3, depths=(3, 4)):
    import matplotlib.pyplot as plt

    labels = []
    whitePerc = []
    blackPerc = []
    tiesPerc = []

    for depthWhite in depths:
        for depthBlack in depths:
            print("W:", depthWhite, "B:", depthBlack)
            wins = playGames(lambda ai: ai.minimaxGame(depthWhite, depthBlack), n)
            print("  [white wins, black wins, ties] =", wins)

            labels.append("W" + str(depthWhite) + " - B" + str(depthBlack))
            whitePerc.append(100 * wins[0] / n)
            blackPerc.append(100 * wins[1] / n)
            tiesPerc.append(100 * wins[2] / n)

    # plot the percentage of white wins, black wins and ties for each combination of depths
    # (stacked bars: the three percentages add up to 100)
    plt.figure()
    plt.bar(labels, whitePerc, label="White wins")
    plt.bar(labels, blackPerc, bottom=whitePerc, label="Black wins")
    plt.bar(labels, tiesPerc, bottom=[w + b for w, b in zip(whitePerc, blackPerc)], label="Ties")
    plt.ylim(0, 100)
    plt.xlabel("Depth (white - black)")
    plt.ylabel("Games (%)")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
    plt.title("Exercise 2: minimax vs minimax")
    plt.savefig("exercise2.png", bbox_inches="tight")
    plt.show()


#---EXERCISE 3: white minimax vs black alpha-beta, depth 4---

def exercise3(n=3, depth=4):
    print("W: minimax", depth, "B: alpha-beta", depth)
    wins = playGames(lambda ai: ai.alphaBetaPoda(depth, depth, False), n)
    print("  [white wins, black wins, ties] =", wins)


#---EXERCISE 4: alpha-beta vs alpha-beta, depth 1 to 5 for both players---

def exercise4(n=3, depths=(1, 2, 3, 4, 5)):
    import matplotlib.pyplot as plt

    # proportion of wins for each combination of depths (rows: white, columns: black)
    whiteProp = np.zeros((len(depths), len(depths)))
    blackProp = np.zeros((len(depths), len(depths)))

    for i, depthWhite in enumerate(depths):
        for j, depthBlack in enumerate(depths):
            print("W:", depthWhite, "B:", depthBlack)
            wins = playGames(lambda ai: ai.alphaBetaPoda(depthWhite, depthBlack), n)
            print("  [white wins, black wins, ties] =", wins)

            whiteProp[i][j] = wins[0] / n
            blackProp[i][j] = wins[1] / n

    # plot the proportion of wins for whites and blacks
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, prop, title in zip(axes, [whiteProp, blackProp], ["White wins", "Black wins"]):
        image = ax.imshow(prop, vmin=0, vmax=1, cmap="Blues")
        ax.set_xticks(range(len(depths)))
        ax.set_xticklabels(depths)
        ax.set_yticks(range(len(depths)))
        ax.set_yticklabels(depths)
        ax.set_xlabel("Black depth")
        ax.set_ylabel("White depth")
        ax.set_title(title + " (proportion)")
        for i in range(len(depths)):
            for j in range(len(depths)):
                ax.text(j, i, round(prop[i][j], 2), ha="center", va="center")
        fig.colorbar(image, ax=ax)
    plt.tight_layout()
    plt.savefig("exercise4.png")
    plt.show()


#---EXERCISE 5: white expectimax vs black alpha-beta---

def exercise5(n=3, depth=3):
    import matplotlib.pyplot as plt

    print("W: expectimax", depth, "B: alpha-beta", depth)
    wins = playGames(lambda ai: ai.expectimax(depth, depth), n)
    print("  [white wins, black wins, ties] =", wins)

    # plot the proportion of wins for whites, blacks and ties
    plt.figure()
    plt.bar(["White", "Black", "Tie"], [w / n for w in wins])
    plt.ylim(0, 1)
    plt.ylabel("Proportion of games")
    plt.title("Exercise 5: expectimax (W) vs alpha-beta (B)")
    plt.savefig("exercise5.png")
    plt.show()


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     sys.exit(usage())

    # Initialize an empty 8x8 chess board
    TA = np.zeros((8, 8))


    # Load initial positions of the pieces
    TA = np.zeros((8, 8))
    TA[7][0] = 2   
    TA[7][5] = 6   
    TA[0][7] = 8   
    TA[0][5] = 12  

    # Initialise board and print
    print("stating AI chess... ")
    aichess = Aichess(TA, True)
    print("printing board")
    aichess.chess.boardSim.print_board()
    
    # Run exercise 1
    #aichess.minimaxGame(4,4)

    # exercise 2
    #aichess.minimaxGame(3, 3)
    #aichess.minimaxGame(3, 4)
    #aichess.minimaxGame(4, 3)
    #aichess.minimaxGame(4, 4)

    # simulations of exercises 2 to 5 (n = games per combination)
    #exercise2(3)
    #exercise3(3)
    #exercise4(3)
    #exercise5(3)

    aichess.minimaxGame(4,4)



# AI REPORT P2

Lidia Fernández Romero, Maria Farelo Iglesias

## Introduction

The objective of this practical is to study adversarial games using search algorithms. We work on a reduced chess endgame in which each player has a king and a rook (white king [7,5] and rook [7,0]; black king [0,5] and rook [0,7]), and White moves first. The players move in alternation, and each one searches the game tree for the moves that lead to checkmate.

We implemented and compared three algorithms:

- **Minimax**, in which White maximizes the value of a state and Black minimizes it.
- **Alpha-beta pruning**, which returns the same decision as minimax but discards the branches that cannot change it.
- **Expectimax**, in which the opponent's moves are treated as chance nodes: instead of taking the minimum, we take an expected value of the children.

In all of them the leaves are evaluated with the heuristic provided in the base code, which we have not modified, so that the results of the different algorithms and depths can be compared.

## Functions

- `minimax(currentState, depth, whitesTurn)` and `minimaxGame(depthWhite, depthBlack)`
- `alphaBeta(currentState, depth, whitesTurn, alpha, beta)` and `alphaBetaPoda(depthWhite, depthBlack, whitesAlphaBeta)`
- `expectimaxValue(currentState, depth, whitesTurn)` and `expectimax(depthWhite, depthBlack)`
- `simulations.py`: runs the games of each exercise, counts the wins and draws, and plots the results.

## Question 6

**a. Is it really the case? Justify your answer.**

Not completely. With perfect play from both sides, king and rook against king and rook is a theoretical draw, so in that sense the situation is even: the material is identical and neither player can force a checkmate against correct defence. In practice, however, the situation is not symmetric:

- **White moves first.** It has the tempo, so it can be the first one to attack the opposing rook or to give a check that forces a reply.
- **The material is not equally safe.** If a rook is exchanged, only the two kings remain and the game is a draw. If a rook is lost without compensation, the other side has king and rook against a lone king, which is a won endgame. A single tactical mistake therefore decides the game.
- **The evaluation is not symmetric.** The heuristic is computed from White's perspective, and the capture of the black rook is rewarded and the capture of the white one penalized with different terms. This is why in our simulations White wins when Black searches with less depth, but never the other way round.

**b. What makes this situation of particular interest for the study of adversarial games?**

- It is a zero-sum game with perfect information and a small branching factor, so it can be searched at a reasonable depth, and the results are easy to interpret.
- A material balance does not make a position balanced: who moves first, and how far each player sees, decide the result. It shows well the effect of the search depth and of the heuristic.
- Many games end in a draw by repetition. With a limited depth and a deterministic algorithm, both players can enter a loop of moves that the evaluation does not distinguish (horizon effect), because no checkmate falls inside the depth they explore.
- Tactical motifs such as forks or skewers on the king and the rook appear even with so few pieces, and a depth-limited search can only see them if it looks far enough ahead.

## AI Use Statement

> To be completed by the authors: the percentages and tools below are placeholders and must reflect what was really used.

We used an AI tool (Claude Code, by Anthropic) in this practical, as follows:

| Part of the work | AI contribution (estimate) | Purpose |
|---|---|---|
| `minimax` and `minimaxGame` | [__ %] | [e.g. our own implementation / review] |
| `alphaBeta` and `alphaBetaPoda` | [__ %] | Implementation following the structure of our minimax |
| `expectimaxValue` and `expectimax` | [__ %] | Implementation following the structure of our minimax |
| `simulations.py` (games, statistics and plots) | [__ %] | Implementation of the simulation script |
| Report | [__ %] | Reading of the assignment, draft of the introduction and of exercise 6 |

We reviewed and tested the code produced with the AI tool, and we are able to explain it.

## Conclusions

> To be written once the simulation results are available.

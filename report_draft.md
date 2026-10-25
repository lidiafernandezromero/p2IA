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
- `playGame`, `playGames`, `exercise2`, `exercise3`, `exercise4` and `exercise5` (also in `aichess.py`): run the games of each exercise, count the wins and draws, and plot the results.

## Implementation decisions

- **Value of a state.** The heuristic is always computed from White's point of view. White maximizes it and Black minimizes it. A checkmate is worth ±1000 (plus the remaining depth, so the faster checkmate is preferred), and a state in which a king has been captured in the simulator is worth the same.
- **Capturing the king in the simulator.** In `boardSim` the king can be captured, so the search detects that a branch has been won. The real board is only moved in the game loop, right after the decision, so the real game never captures a king.
- **Legality filter.** The moves that leave one's own king under attack are discarded. Without this filter a player in check could ignore it.
- **Depth.** `depth` is the number of moves that are still missing to reach the depth we want, not the moves already made (as in the first practical).
- **Ties.** The game ends in a tie when only the two kings are left (insufficient material), when the player to move has no legal moves and is not in check, or after 100 moves. The search values the state with only the two kings as 0, so the search and the game loop agree.
- **Repetitions.** A situation (pieces and turn) that has already been played in the real game is valued as a tie (0) inside the search, as in real chess. Without this, the players repeat the same moves until the limit of 100 moves.
- **Alpha-beta.** `alphaBeta` follows the structure of `minimax`, with `alpha = -inf` and `beta = +inf` at the root, and it stops exploring a state when `alpha >= beta`.
- **Expectimax.** White's nodes maximize, and Black's nodes are chance nodes whose value is `calculateValue` of the values of the children. In the game, White plays expectimax and Black plays alpha-beta.
- **Determinism.** None of the algorithms uses random numbers, and the initial position is always the same, so the games of the same combination of depths are identical. We still ran the three games that the assignment asks for.

## Question 1 (minimax vs minimax, depth 4)

**a. How often do whites win?** [RESULT: white wins / black wins / ties over the games run]

**b. Justification.** [Fill in with the result. Points that we have verified:]

- Both players use the same deterministic algorithm, the same heuristic and the same depth, so every game is the same.
- With a depth of 4 moves both players see the same, so neither of them can force a checkmate: the best defence of Black to the first check (1.Ra8+) is to move the king to [1,6] (g7), protecting its rook. Capturing the rook would be answered by recapturing, and only the two kings would be left, which is a tie.
- The positions that the heuristic evaluates do not distinguish well those that lead to a checkmate, so the players move the king and the rook around without making progress until the limit of moves is reached.

## Question 2 (minimax vs minimax, depth 3 and 4)

[TABLE: for each pair (white depth, black depth) in {3,4}²: white wins / black wins / ties over 3 games. Figure: `exercise2.png`]

**a.** [Percentage of white wins for each combination.]

**b. Is the result symmetric? Why?** [Fill in with the table. Points: the game is not symmetric because White moves first and because the heuristic is written from White's point of view, but with these depths the four combinations are expected to give the same result: Black sees enough to defend.]

## Question 3 (white minimax, black alpha-beta, depth 4)

[RESULT of the 3 games]

**a. Who is the best in each simulation?** [Fill in with the result.]

**b. Why?** Alpha-beta returns the same decision as minimax at the same depth, because the pruning only discards branches that cannot change the result (we checked that `minimax` and `alphaBeta` return the same value in 12 consecutive positions of a real game, for depths 1 to 3). The difference is only the time: a game with minimax at depth 4 for White took about 45 to 60 minutes on our machines, and alpha-beta takes a fraction of that. [Add the measured times of each algorithm.]

## Question 4 (alpha-beta vs alpha-beta, depths 1 to 5)

[TABLE 5x5 of results and figure `exercise4.png`]

**a.** [Proportion of wins of White and Black.]

**b. Comment on the result.** [Fill in with the table. Expected points: White only wins when Black searches a single move; with depth 2 or more, Black finds the defence (protecting the rook) and the game is a tie; Black does not win with any combination.]

## Question 5 (white expectimax, black alpha-beta)

[RESULT of the 3 games and figure `exercise5.png`]

**a.** [Proportion of wins of White and Black.]

**b. Who wins the most? Why?** [Fill in with the result.] Points that we have verified: expectimax does not assume that Black plays its best move, but a weighted average of all its replies (`calculateValue`). After 1.Ra8+ Kg7, White captures the black rook on h8. Expectimax averages over all the replies of Black, and the replies other than the recapture do not recover the rook, so the average looks good for White [check this with the values of the search before submitting]. But the best reply, recapturing, leaves only the two kings and the game is a tie. Alpha-beta in Black's side does find that reply.

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

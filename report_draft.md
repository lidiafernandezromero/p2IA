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

**a. How often do whites win?** Never. In the 3 games that we ran, with White and Black playing minimax at depth 4, the result was a tie each time (white wins / black wins / ties = 0 / 0 / 3). The three games are identical, because the algorithm is deterministic.

**b. Justification.**

- Both players use the same deterministic algorithm, the same heuristic and the same depth, so every game is the same.
- With a depth of 4 moves both players see the same, so neither of them can force a checkmate: the best defence of Black to the first check (1.Ra8+) is to move the king to [1,6] (g7), protecting its rook. Capturing the rook would be answered by recapturing, and only the two kings would be left, which is a tie.
- We played one of the games move by move: no piece is captured, and from some point on White moves the rook between [1,0] and [0,0] and Black moves the king between [0,5] and [1,6]. The game ends on the limit of 100 moves, so it is a tie. The heuristic does not distinguish well the positions that lead to a checkmate, so the players do not make progress.

## Question 2 (minimax vs minimax, depth 3 and 4)

Results over 3 games per combination (white wins / black wins / ties). Figure: `exercise2.png`.

| White depth \ Black depth | 3 | 4 |
|---|---|---|
| 3 | 0 / 0 / 3 | 0 / 0 / 3 |
| 4 | 0 / 0 / 3 | 0 / 0 / 3 |

**a.** The percentage of white wins is 0 % in the four combinations: all the games (100 %) are ties, and Black does not win either (the figure shows white wins, black wins and ties).

**b. Is the result symmetric? Why?** The result is the same in the four combinations: all the games are ties. The game is not symmetric in itself (White moves first, and the heuristic is written from White's point of view), but with depth 3 or 4 Black sees enough to find the defence (protecting the rook), so that asymmetry does not show up in the result. It only shows when the two depths are very different (see question 4).

## Question 3 (white minimax, black alpha-beta, depth 4)

Result of the 3 games: white wins / black wins / ties = 0 / 0 / 3.

**a. Who is the best in each simulation?** Nobody: the three games are ties.

**b. Why?** Alpha-beta returns the same decision as minimax at the same depth, because the pruning only discards branches that cannot change the result (we checked that `minimax` and `alphaBeta` return the same value in 12 consecutive positions of a real game, for depths 1 to 3). Since both players see the same, none of them gets an advantage. The difference is only the time. We measured the first decision of White from the initial position (machine with other simulations running at the same time):

| Depth | Minimax | Alpha-beta | Ratio |
|---|---|---|---|
| 2 | 0.2 s | 0.1 s | 1.7 |
| 3 | 2.8 s | 1.2 s | 2.3 |
| 4 | 40.8 s | 14.8 s | 2.7 |

Both return the same value at every depth (0, 76.1 and 0), and the advantage of alpha-beta grows with the depth. A full game of 100 moves with minimax at depth 4 for White took about 45 to 60 minutes.

## Question 4 (alpha-beta vs alpha-beta, depths 1 to 5)

Result over 3 games per combination (W = White wins the 3 games, B = Black wins the 3 games, t = the 3 games are ties). Figure: `exercise4.png`.

| White depth \ Black depth | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | t | t | t | t | t |
| 2 | W | t | t | t | t |
| 3 | W | B | t | t | B |
| 4 | W | t | t | t | B |
| 5 | W | W | W | t | W |

**a.** White wins in 7 of the 25 combinations, Black wins in 3 (W3-B2, W3-B5 and W4-B5) and the rest are ties. In every combination the three games have the same result.

**b. Comment on the result.**

- When Black searches a single move (depth 1), White wins with any depth from 2 to 5: Black does not see the defence (protecting the rook).
- White with depth 1 does not win and does not lose against any depth.
- When both players search at least 2 moves, most of the games are ties, which is consistent with the position being even (question 6).
- **How Black wins.** We played the three games where Black wins at depth 3-2, 3-5 and 4-5. In all of them Black captures the white rook (on move 22, 22 and 28) and then checkmates with king and rook against a lone king (the game ends on move 36, 34 and 58). White with depth 5 never loses, so the depth that White needs to avoid that loss is greater than 4.
- **How White wins.** For example, in W5-B1 the white king captures the black rook on move 13 (Black, with depth 1, leaves its rook capturable) and White checkmates on move 33 with king and rook against a lone king.
- **No progress games.** In the ties with equal depths (for example W4-B4) no piece is captured and the players move the king and the rook between two squares until the limit of 100 moves.
- The result is not monotonic: a larger depth does not always give a better result. W5-B4 is a tie (no capture in 100 moves), but W5-B5 is a win for White: the white king captures the black rook on move 23 and White checkmates on move 55. Also, White with depth 3 loses against Black with depth 2. In this game a small difference in what each player sees decides whether a rook is lost, and the heuristic does not guide the players towards the checkmate when no piece is captured.
- Black can win, so White's advantage is not absolute; it depends on the depth of both players.

## Question 5 (white expectimax, black alpha-beta)

Result of the 3 games (depth 3 for both): white wins / black wins / ties = 0 / 0 / 3. Figure: `exercise5.png`.

**a.** The proportion of wins is 0 for White, 0 for Black and 1 for ties.

**b. Who wins the most? Why?** Nobody wins: the three games are ties, and they end on move 4, with only the two kings left. Expectimax does not assume that Black plays its best move, but a weighted average of all its replies (`calculateValue`). After 1.Ra8+ Kg7, White can capture the black rook (Rxh8). We computed the values of the search:

| | Minimax | Expectimax |
|---|---|---|
| Value of Rxh8 | 0 | 21.6 |
| Best alternative for White | 20 | 20 |

Black has four replies after Rxh8. Recapturing leaves only the two kings (value 0), and the other three leave White with an extra rook (values from 87 to 97). The average is 21.6, a little higher than the 20 of the best alternative, so expectimax chooses to capture. Minimax assumes the best reply of Black, sees 0 and does not capture. Alpha-beta on Black's side does find the recapture, so White's optimism does not pay off and the game is a tie.

## Question 6

**a. Is it really the case? Justify your answer.**

Not completely. With perfect play from both sides, king and rook against king and rook is a theoretical draw, so in that sense the situation is even: the material is identical and neither player can force a checkmate against correct defence. In practice, however, the situation is not symmetric:

- **White moves first.** It has the tempo, so it can be the first one to attack the opposing rook or to give a check that forces a reply.
- **The material is not equally safe.** If a rook is exchanged, only the two kings remain and the game is a draw. If a rook is lost without compensation, the other side has king and rook against a lone king, which is a won endgame. A single tactical mistake therefore decides the game.
- **The evaluation is not symmetric.** The heuristic is computed from White's perspective, and the capture of the black rook is rewarded and the capture of the white one penalized with different terms. This is why in our simulations White wins when Black searches only one move. Black also wins in some combinations of depth (question 4), so the advantage depends on the depths and is not exclusive to White.

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
| Simulation functions in `aichess.py` (`playGames`, `exercise2` to `exercise5`) and the plots | [__ %] | Implementation of the simulations and the plots |
| Debugging: ties for insufficient material and repetitions in the search | [__ %] | Analysis of games move by move |
| Report | [__ %] | Reading of the assignment, draft of the introduction and of exercise 6 |

We reviewed and tested the code produced with the AI tool, and we are able to explain it.

## Conclusions

- We implemented minimax, alpha-beta pruning and expectimax for a game of king and rook against king and rook. Alpha-beta returns the same decisions as minimax and is faster (2.7 times at depth 4 for one decision), and the advantage grows with the depth.
- Most of the games are ties. When both players see enough, the defence of the rook (keeping it protected by the king) makes a checkmate impossible, which agrees with the position being a theoretical draw.
- White wins when Black searches only one move, and also in some combinations with more depth (for example, White with depth 5). Black wins when it captures the white rook with a tactic that White does not see at depth 3 or 4. The result depends on the depth of both players and is not monotonic.
- The simulation and the game loop have to use the same rules. Valuing the position with only the two kings as a tie, and the repetitions of positions as ties, changed the results, because without them the players exchanged the rooks or repeated moves until the limit of 100 moves.
- Expectimax is not better than alpha-beta in this game: it assumes that the opponent can make mistakes, and the opponent here plays well, so the optimism of White does not pay off.
- All the algorithms are deterministic, so the three games of every combination are identical. To observe a variation between games, some randomness would be needed (for example, choosing at random among the moves with the same value).
- The heuristic of the base code, written from White's point of view, does not evaluate well the positions that lead to a checkmate. We did not modify it. A better heuristic is the main improvement that we would make.

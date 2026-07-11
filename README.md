# Micropython Experiments

A small repo for small Micropython experiments. Initially started 2026-07-11 while working on OpenSauce project (Keep Yapping or We're Cooked).

Keep Yapping or We're Cooked is a game meant to bring the well-known co-op game "Keep Talking and Nobody Explodes" to real life! The game involves defusing modules on a larger bomb under time pressure, requiring communication between the defuser (with access to the bomb) and an "expert" who has access to a manual with the instructions for how to actually defuse modules.

# Modules

## Maze Module

The maze module requires the defuser to navigate a maze where the walls are invisible (they are only visible to the expert). The module has a joystick and an LED matrix.

On the LED matrix there will be a goal (yellow), a player (purple), and a marker (blue).

The LED matrix is an 8x8 LED array (WS2812B-64). Each LED represents a position.

The Joystick should be edge-triggered. Moving up once requires pushing the joystick up once.

There are walls that aren't visible to the player (not indicated on the LED matrix). Walls exist between adjacent positions. Two positions are adjacent if their coordinates have a manhattan distance of 1. i.e.: A pixel is adjacent to the pixels to its north, west, south, and east.

At startup, a wall configuration should be randomly chosen from a pre-drawn set of mazes. The way the module is solved is that the defuser must communicate with the expert where the marker is, as the marker uniquely identifies which wall configuration is in place. From there the expert must communicate directions to the defuser to guide their "player" in the maze to the goal square.

When the user hits a wall, the LED matrix should flash red twice (during this period no user input should be accepted).

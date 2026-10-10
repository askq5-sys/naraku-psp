NARAKU PSP 1.6.2 - Dealer cutscene route fix

Requires version 1.6.1. No assets or saves are changed.

Fixes the Map094 encounter leading to END 5/7. While the first NPC walked away, the second NPC still collided with its old visual cell. Skippable approach steps were lost, leaving the second NPC in the wrong position; the later non-skippable escape route then blocked forever while the scene waited.

Moving NPC collision in Map094 now uses the logical destination committed at step start, matching RPG Maker. Replacing a forced route also retains an already-running step until arrival. Original event commands, paths, map collision masks and story switches remain unchanged. Other map chase behavior is unchanged.

Validation: replay of all original NPC forced routes through the actual C movement/contact code and the original Map094 pass masks. The previous code reproduces the command-215 NPC-12 deadlock; the fixed code completes the scene routes with 30, 60 and 120-frame dialog intervals. Existing five-pursuer route and giant-spider checks pass, as do host C syntax and shell syntax. This is host simulation, not an emulator or hardware playthrough.

Install and restart the game. Load an in-game save before entering the dealer encounter. An emulator save state captured inside the stalled scene retains its already-broken actor positions and is not suitable for retesting.

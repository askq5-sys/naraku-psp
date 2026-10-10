NARAKU PSP 1.4.2 - Lever final state and continuous first ending approach

Requires the complete game with patch 1.4.1 installed.
Extract into the project and run tools/build_deploy_v142.sh.
Restart and load an in-game save to test the scene again.

Map055: the lever's original intermediate positions and the Enri swing
animation are preserved. Once the completed-scene switch 632 is enabled,
the lever stays in its disabled/down position (original tile 449), instead
of returning to the initial up position. This uses the original artwork;
it does not introduce a newly drawn damaged lever texture.

Map062: the four first-ending touch triggers start one tile earlier, on
the original self-transfer destination row. The black tint/self-transfer
was removed. Enri walks horizontally to the central lane when necessary,
then follows the original three-tile approach without being moved back.
The complete branch-specific ending after the approach is unchanged.

The small key display uses artwork from the original tileset, including
its tiny lettering. Source pixels are retained before PSP downsampling.

Validation: all four approach paths reach the original destination without
crossing blocked cells; ending tails and intermediate lever scripts match
the original. 420 stage pages, 623 native actor frames, 1408 script pages,
puzzle timer, Rope and host C syntax checks passed. No PSP/PPSSPP runtime
testing was available. Saves/config and their formats remain unchanged.

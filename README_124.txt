NARAKU PSP 1.2.4 — cumulative patch over 1.2.3

Return ladder (Map025):
- Opaque black ceiling autotiles 5888..5935 now render above actors, including
  the boundary border, so Enri's head cannot protrude into the dark ceiling.
- Tile slots, collision masks, original map/event coordinates and routes preserved.

Killer contact (Maps024/025):
- One logical destination tile is reserved while the killer moves. Negative
  movement no longer uses truncated interpolation to identify the contact tile.
- Walking into the killer invokes the original contact scene before solid-event
  blocking. Contact checks also run while the player moves, including the target tile.
- Inactive story pages retain their original behaviour; the original capture
  command sequence and subsequent transfer to Map027 are unchanged.

Torture room (Map027):
- Killer uses all three patterns in all four directions during its scripted walk.
- Filtered 54x108 source frames render at the original PSP 36x72 size.
- Hanging figures remain filtered 36x144 -> 24x96; key retains original 48x48
  frames and renders at 24x24. All resources fit one 512x512 event atlas.

Validation: host C tests for actual contact/block routines, forced-route animation,
source pixel/resampling checks, map upper-layer flags, atlas bounds, previous text,
flashback, worm, laser and press regressions; converter and shell syntax checked.
No PSP SDK or PPSSPP available here: PSP compilation, visuals and gameplay require
user runtime verification.

Install with PPSSPP closed from ~/projects/naraku-psp:
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.4_ladder_contact_torture_patch.zip
chmod +x tools/build_deploy_v124.sh
./tools/build_deploy_v124.sh

Fully restart the game after deploying. Use an in-game save/new run for verification:
old emulator save states can restore the code/resources of the old build.

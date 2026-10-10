NARAKU PSP 1.3.9 - Native actor sprites and factory scene polish

Install over the complete game with patches 1.3.7 and 1.3.8 already applied.
Unzip into the project and run tools/build_deploy_v139.sh. Restart the game
and load an in-game save instead of an older emulator save state.

Changes:
- Preserve original source texels for all Enri poses, killer character sheets,
  and hanging-body sheets in the 29 affected maps within the implemented
  Map001-064 range, including the special escape poses in Map035.
- Use hardware linear filtering at the existing PSP display sizes. No AI
  redrawing, source replacement, altered hitboxes or runtime compression.
- Repack native sheets into at most two 512x512 texture pages per map.
  The loader now detects detail pages from sprite references on any map.
- Load the correct compact walking-sheet layout from its sprite flags.
- Reduce the first Map036 event17 delay by two frames (120 to 118). Its
  other waits, forced route, music and story switches remain unchanged.
- Reveal the Map034 event51 ambush sprite over six frame intervals, rather
  than showing it at full opacity immediately. Collision and AI stay active;
  explicit original opacity is still respected. Reveal resets on map transfer.
- Draw Map038's stair ceiling over actors, matching the prior Map025 ceiling
  correction. Tile identities and passage masks remain unchanged.
- Keep the 1.3.8 Rope reconciliation and every earlier runtime fix.

Validation:
623 native actor frames compared byte-for-byte to original source pixels;
1407 event command pages checked against their original compilation, with
the existing Plant1 Worm adaptation retained; atlas bounds, stair passage
masks, actual C reveal/timing behavior, renderer sampling, chase/contact,
flashback routes, puzzle timers, save/note UI and Rope correction checked.
Whole main.c passes host syntax checking with PSP API stubs.
No PSP SDK/device/emulator runtime testing was available in this environment.

This patch does not add the remaining story stages beyond Map064.

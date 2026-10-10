NARAKU PSP 1.3.2 — sheet interaction, corridor sampling, dialogue portraits
Cumulative over 1.3.1. Previous progress/resources/scripts retained.

Metal sheet interaction (Map037):
- Event4 below the player has an empty page (only END). The earlier runtime
  treated it as a successful action, never checking Event3 immediately ahead.
- Empty compiled pages no longer start an interaction. Action selection follows
  MZ priority: below/above-character pages on the current tile, normal-priority
  pages on the front tile. Collider/page ownership remains authoritative, so
  skipping an empty action does not reopen old one-shot transfers.
- Actual C event selection tested with the delivered Map037 VM bytes: the empty
  floor page is ignored, intact sheets start, damaged blank pages do not start,
  and normal-priority sheets retain their original collision.

Corridor shimmering (Maps033/034):
- Dense body details and background tiles are prefiltered with LANCZOS once
  onto the native PSP pixel grid, rather than relying on changing render-scale
  sampling of high-frequency source details. Keep existing atlas dimensions
  and sprite display sizes. The corpse sheets use nearest sampling of this
  fixed grid, and the camera position remains integer-aligned for these objects.
- 82 background tile frames and corridor corpse frames verified; VM command
  streams, map tile flags and passage bytes remain identical to 1.3.1.
- This targets the sampling shimmer visible during movement. The resulting
  appearance in PPSSPP and on real hardware still needs a gameplay check.

Dialogue character pictures:
- Rebuilt all 66 canonical portrait/expression/cut-in assets from original PNGs.
  Crop only the transparent canvas, retaining its original offsets and origin.
  Spend the existing 512x512 texture budget on the actual character, preserving
  native source pixels where they fit and smoothly resizing larger crops.
- New NPR1 picture header stores source-region dimensions, original logical
  canvas and crop geometry. GPU linear filtering handles display scaling.
- Original picture coordinates, origin, zoom, opacity/blend, layering and
  on-screen character size preserved. Existing NP50/NGO1 pictures remain valid;
  original game-over filling and control-board layout are unchanged.
- Still RGBA4444 and 512 KiB per loaded picture, with the same five-picture cap.
  No runtime compression or extra portrait texture RAM.
- Full world asset regeneration also invokes the portrait preparation step.

Validation: actual C current/front event selection; 66 source crop/texture
comparisons; actual new and legacy picture loader/drawing tests for crop offset,
origin, zoom, linear filtering and game-over fitting; fixed 2x2 corridor texel
sampling grids; all earlier regression scripts passed; Python/shell syntax.
No PSP SDK or PPSSPP here: device compilation and final visuals require testing.
Completed stage scope remains Maps001–045 as documented by previous patches;
later Maps046 onward are not newly implemented by this graphics/input patch.

Close PPSSPP and install:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.3.2_interaction_portraits_patch.zip
chmod +x tools/build_deploy_v132.sh
./tools/build_deploy_v132.sh

Fully restart the game and use an in-game save/new run, not an older emulator
save state that restores the previous executable. Existing saves/XMB retained.

NARAKU PSP 0.8.3 — floor movement and font patch
Includes 0.8.1 menu + 0.8.2 player animation fixes; requires full existing assets.

Fixes:
- Instant touch events no longer discard tile-arrival rendering.
- Floor touch events no longer reset the animation phase every tile.
- Non-repeating player routes containing only speed/facing/flag changes execute
  immediately instead of holding manual input for an extra render frame.
- Timed/movement routes retain their queued execution.
- Runtime font rebuilt from original mplus-1m-regular for supported glyphs.
  Existing unsupported CJK glyphs retained, NF30 coverage/slots unchanged.
  Descenders retain full ink and padding. Font assets included in deploy.

Observed Map006 gate/sound scene (Event13 page3):
Original commands wait 30 frames after water sound, face down, wait60,
move down four tiles, face right, then show Enri '......?' dialogue.
Manual input is intentionally disabled until the scene/dialogue completes.
No original waits or scripted movements have been removed.
The screenshot alone does not demonstrate a permanent freeze after dismissal.

Controls artwork:
User will supply PNG 480x272 (native PSP), ratio30:17; safe margin8px.
Readable text around18-20px. D-pad movement, R run, X confirm/investigate,
Circle cancel/menu in default configuration; Japanese confirm setting can swap X/O.
No new controls artwork included in this patch.

Validation:
Host animation/reference and actual route-tick tests passed, including immediate
speed/turn routes and retained timed waits. C syntax verified with PSP stubs.
Font format/coverage checked; g/j/p/q/y tails and bottom padding checked.
23.55s supplied video inspected with sampled frames; no input trace is available.
Real PSP compilation and runtime visual verification require your setup.

Install (close PPSSPP):
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_0.8.3_movement_font_patch.zip
chmod +x tools/build_deploy_v083.sh
./tools/build_deploy_v083.sh

Host tests: bash tests/run_host_checks.sh
Font regeneration optional: requires Python Pillow + fontTools, original game
fonts and existing assets; see tools/prepare_font_v083.py --help.
Font preview: font_preview.png.

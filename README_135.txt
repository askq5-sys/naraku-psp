NARAKU PSP 1.3.5 - Next factory stage and item fixes

This delta patch applies over a complete 1.3.3 or 1.3.4 project/installation.
It includes the 1.3.4 fixes. It is not a complete game download.

Changes
- Choices use red Cleaver and metallic gray Axe, with capital initials.
- The Axe broke message uses the same gray color and capitalization.
- Correct the English green-key pickup messages on Maps023/024. The
  original Japanese text, item ID 50, and green sprite agree; English
  incorrectly called the item an Iron Key. Actual Iron Keys are unchanged.
- Refilter corpse barricades from the original pixels at the PSP display
  resolution, using Lanczos filtering and smooth reconstruction. Keep the
  original display dimensions, collision pages and ambush logic.
- Add Maps048-055: timed switch puzzles, chase rooms, shutter/door sequences,
  elevator and the arrival at the next junction. Preserve original event
  conditions, dialogue, failure sequences and transfers.
- Add a nonblocking trigger-4 interpreter for this stage. Switch loops,
  countdowns, sound cues, route waits and screen shakes run without blocking
  player input. Each event cancels/restarts when its active page changes.
- Preserve original killer custom routes, walking animation and one-cell
  contact in Maps049-053. Add native event graphics and the moving chain
  background, including its scripted stop in the elevator.
- Include required sound variants and the missing A6 game-over picture.
- Retain 1.3.4 dialogue font-control removal and elevator-flashback fix.

Installation (WSL)
Close PPSSPP first, then:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.3.5_next_factory_stage_patch.zip
chmod +x tools/build_deploy_v135.sh
./tools/build_deploy_v135.sh

Do not load an emulator savestate made with an older executable. Test the
new stage from an in-game save. Saves, config and existing XMB assets are
preserved. Runtime asset formats remain uncompressed.

Validation
- 304 original event pages and six autonomous routes checked against MZ.
- Collision grids, sprite atlas bounds and picture/audio references checked.
- Actual C scheduler tested with real compiled resources: parallel loops,
  page changes, 70/200-frame puzzle timers, one-shot timers, route waits,
  840-frame door timeline, asynchronous shakes and elevator background stop.
- Actual C chase startup, animation, pause, cancellation and one-cell contact
  checked for all five new chase rooms.
- Earlier factory, dialogue, interaction, rendering and flashback checks pass.
- Full-source host C syntax checked using PSP surface stubs.

Limits
No PSP SDK build or full PPSSPP/physical PSP playthrough was performed here.
Visual quality, device performance and complete scene playback still need
in-game testing. Support added in this patch ends at Map055; later branches
are not represented as completed or verified. Six screenshots were requested,
but only five images were attached to this report.

Resource rebuild (developers, original data required)
python3 tools/prepare_stage_v135.py --game /path/to/original --assets assets
Requires the complete existing asset manifests, Pillow and ffmpeg.

NARAKU PSP 1.3.1 — factory extension, Maps036–045
Cumulative over 1.3.0; all previous fixes retained.

Requested objects:
- Map037 metal sheets: preserve the native 144x48 source frames and draw with
  linear filtering at the original 72x24 PSP size. All damaged sheet states,
  Enri's bare-hand/axe poses, interaction choices, sounds, waits and branches
  rebuilt from the original. The axe branch consumes the original item.
- Map040 crank/lift: all seven switch-controlled visual states and the original
  interaction event at its left-hand cell are included. Crank source frames
  use filtered 3/4-size images (108x324), displayed at 72x216 PSP pixels.
  Direction choices, neutral reset, lift/shutter switches and sounds retained.
- Map043 key: three native animation frames, correct colour/direction, original
  pickup sound/item/notification and switch345-controlled empty collected page.
  State is governed by the pickup switch; possession of the same key item in
  earlier rooms does not incorrectly remove this room's key.

Entire connected block refreshed, not just these three objects:
- All 239 event pages on Maps036–045 compiled from the original command lists;
  all 75 visual pages reference their corresponding graphics.
- Doors, save points, inventory gates, laser-room switches, capture/death events,
  classroom memory sequence, lift/crank puzzle and both password terminals.
- Map043 sensors use their exact autonomous turn routes. A turn consumes one
  frame for these sensors, avoiding four turns collapsing into one update.
- Added VM commands for 24-frame fade out/in, retaining darkness over waits and
  map transfers, and original number input. PSP number input: left/right choose
  digit, up/down change digit (with repeat), X confirms; O is disabled as in MZ.
  Both password branches and incorrect-code responses remain original.
- Classroom actors retain all directional walking frames and standing stepping
  where the original enables it. Exact audio variants and portraits included;
  previous resource IDs verified unchanged.
- Crowded Maps039/040 use a second event atlas, only resident while that map is
  loaded and freed on transfer. +1 MiB event texture RAM on those maps.
  No runtime asset compression.

Checks passed: original command/page/condition comparison; all tile passage
masks in this block; 159 exact/filtered source-frame comparisons; stable audio
and portrait references; sheet/crank/key/fade/password bytecode branch tests;
actual C digit input, fade cadence, sensor routes/page cancellation, classroom
stepping, atlas-coordinate decoding, crank display scale and key animation;
115 English dialogue messages wrapped losslessly; all 24 earlier regression
scripts and Python/shell syntax checks.
No PSP SDK or PPSSPP here: PSP compilation and gameplay/visuals need device tests.
Later Maps046 onward remain outside this patch's completed scope.

Close PPSSPP, then:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.3.1_factory_extension_patch.zip
chmod +x tools/build_deploy_v131.sh
./tools/build_deploy_v131.sh

Fully restart and load an in-game save/new run. Do not restore an emulator save
state from an older executable. Existing saves/assets/XMB settings retained.

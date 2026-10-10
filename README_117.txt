NARAKU PSP 1.1.7 cumulative patch.
- Flashback English source typos repaired (these materials, to wait, Mrs. Peliah),
  original size, whole-word reflow and 3-row pagination retained.
- Only 'Obtained an Axe.' notification shows lowercase axe in grey palette8.
- Actual Pressing Room is Map026, not neighbouring S-003 Map024. Sensor4 uses
  an autonomous down/left/right/up turn route at frequency5 (threshold0),
  including the route-end update; directional atlas restored. Inactive page
  keeps its original fixed image. Parallel event3 waits500 frames and plays
  Electrocardiogram50/80/0 then enables switches134/135/136/137. The sensor and
  both hazard cells become inactive. The flags persist in saves as in original.
- Map026 VM and sprites rebuilt with exact audio IDs; Explosion4 100/120/0
  restored when press lands. No fabricated Laser1/Laser2 sound added.
- Game-over pictures fill480x272, eliminating side bars (aspect is adapted).
- Dedicated keys use the same Y-depth order as character events and render
  before world tint/fades/fog/pictures, preventing head overlap and fade leaks.
All previous patches, controls board and saves preserved.
Close PPSSPP, extract over complete project, run tools/build_deploy_v117.sh.
Host tests passed for dialogue layout, corrected source, original laser directions,
500-frame disable and beep, Map026 hit sound/PCM, key ordering and previous
scene/sprite/camera/press checks. PSP SDK build/runtime unavailable here.

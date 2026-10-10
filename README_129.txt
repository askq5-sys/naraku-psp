NARAKU PSP 1.2.9 — factory source-resolution graphics and depth ordering
Cumulative over 1.2.8. Earlier fixes and progression retained.

Scope: factory Maps032-035 shown in the supplied recordings.
- Press machine now uses the full original 336x384 frame, rendered at 168x192.
- Conveyor/corpse-box/barrier frames use full original 144x96 pixels, rendered
  at 72x48; all conveyor direction and switch-selected frames retained.
- Falling/moving corpse tile and hatch/event tiles retain native 48x48 pixels
  and render at 24x24. Corpse motion preserves fractional position.
- Selected map hatch/grate tiles (135/143/151/161/162) use isolated linear
  filtering, immediately restoring nearest sampling for surrounding tiles.
- Factory events now sort by foot Y, as in the original: the killer no longer
  draws above every corpse barricade solely because of its larger event ID.
  Player/event depth partitions and original event priorities are preserved.
- All 326 source page collider priorities, through flags, switch/self-switch
  gates, coordinates and all 2418 tile passage masks verified against original.
  Did not expand original three-cell barriers or seal scripted openings.

The crowded machine room uses two 512x512 event texture pages. Sprite X upper
bits encode the texture page; older one-page assets remain compatible. The
second texture costs 1 MiB RAM only while Map032 is loaded and is freed on
transfer/failure. No runtime asset compression introduced.

Validation: 69 native-frame comparisons; 326 collider-page and 2418 passage-cell
checks; 24 selectively filtered map tiles; actual C renderer texture selection,
coordinate decoding, filtering and display dimensions; actual factory depth
sorting around the player; all previous regression checks passed.
No PSP SDK / PPSSPP available here: compilation, visual appearance, performance
and collision behavior during real play still need runtime verification.
Later gameplay beyond the previously implemented factory block remains outside
this patch's scope.

Install with PPSSPP closed:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.9_factory_graphics_patch.zip
chmod +x tools/build_deploy_v129.sh
./tools/build_deploy_v129.sh

Fully restart the game. Use an in-game save rather than an old emulator savestate.

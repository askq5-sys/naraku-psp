NARAKU PSP 1.2.7 — classroom motion, room centering, door touch and factory block
Cumulative over 1.2.6. Keep the complete installed game; no runtime compression.

Requested fixes:
- Rooms 021/023/027 share a passage at x7 with asymmetric empty margins.
  Centre this visible geometry by +24 PSP pixels, without changing event,
  collision or tile coordinates; vertical scrolling remains unchanged.
- Emma in the second classroom flashback now uses standing step animation,
  rather than resetting to the idle pattern while she is stationary.
- Lucas's original two jumps, 10-frame waits and timing are retained and tested.
- Implement MZ front-touch behavior for same-priority Player Touch events:
  blocked door cells can start their script when walked into. This includes
  Map031 event2, the door into the new factory block. Floor events continue
  to require entering their cell; inactive/unsupported pages cannot start.

New block: Maps032-035 (first factory area, both chase corridors and escape scene).
- 326 event pages accounted for: 325 compiled command-for-command from the
  original plus Map032 event20's parallel machine sequence implemented separately.
- Original autonomous sensor/conveyor/killer routes, speeds and switch gates.
- Map032 corpse transport and the 430-frame machine cycle run without taking
  player input away. Restore the corpse position with the original event-location
  command at the end of the cycle.
- Walking killer frames in all four directions, original capture scenes and
  one-cell contact. Crowded sheets use the established 3/4 source resolution
  and filtered downsampling, rendered at the original PSP display size.
- Rectangle atlas packing for these maps preserves all required frames.
- Required portraits, exact volume/pitch/pan sounds and music included; earlier
  resource IDs verified unchanged.

Scope limit: later Maps036 onward, including later memory scenes and branches,
are not completed by this patch. Existing base resources for those maps remain.
The second screenshot was not attached; the door correction is grounded in
Map031's original event and the missing front-touch behavior.

Validation: earlier regression checks passed; added actual C tests for door
front-touch filtering, room centering, Emma step animation, factory route startup
and cancellation, corpse transport and the machine cycle. Source command/route
comparison, visible-page references, atlas bounds, audio/portrait presence and
seven factory dialogue messages checked. Lucas jump/wait/repeat tests passed.
No PSP SDK / PPSSPP here: device compilation, gameplay and visuals require testing.

Install with PPSSPP closed:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.7_factory_patch.zip
chmod +x tools/build_deploy_v127.sh
./tools/build_deploy_v127.sh

Fully restart the game. Use an in-game save/new run, not an old emulator save
state, which can restore old code/resources. Saves and XMB configuration retained.

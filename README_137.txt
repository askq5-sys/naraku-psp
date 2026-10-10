NARAKU PSP 1.3.7 — factory sequence and Purgatory entrance

Cumulative patch over a complete 1.3.3–1.3.6 installation.
Includes the earlier font, flashback, factory-stage and save-book fixes.

Changes:
- Remaining corpse barricades were baked into corridor map tiles, rather
  than event sprites. Six corpse/cage tile types now retain native source
  pixels with linear sampling. Floor/wall sampling and collision masks stay
  unchanged.
- The map 049 timeout now clears checkpoint 5 and pending door progress as
  well as the earlier checkpoints. The original reset list omitted these
  switches, allowing a failed sequence to resume late in the puzzle.
- Interpreter wait frames use live player coordinates. A nonwaiting forced
  route no longer snaps Enri back to its old start after completing.
- Restored the full original lowered lever tile and original switch-driven
  attack poses. Removed the 1.3.6 half-frame crop after lever destruction.
- Extended original event depth sorting to the entrance-stage rooms. Closed
  lift doors cover Enri when her position is behind the door sprite.
- Added original map 059–064 resources, door states, transfers, panorama,
  sounds, pictures, entrance events and the END 1/7 scene/credits branch.
- Parallel lift events now support inventory conditions, item removal and
  queued dialogue. A dialogue pauses its own event while other lift timers
  continue, without recursively rendering an unfinished frame.
- Ending and credit boards use the existing full-screen fitting mechanism.

Demonic Axe:
Original item 55 is obtained from map 045 event 1 (at tile 8,4). The supported
pickup page, sprite reference and item-gain command were verified.
It is consumed when used to cut the web in map 056. If retained, the original
map 059 lift event breaks it and displays the corresponding message.
This patch does not grant skipped items or rewrite your inventory.

Install in WSL:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.3.7_entrance_stage_patch.zip
chmod +x tools/build_deploy_v137.sh
./tools/build_deploy_v137.sh

Fully restart the executable and test from an in-game save. A PPSSPP save
state made with an older executable can restore old program state/code.
Saves, configuration, XMB resources and existing game assets are preserved.

Validation:
- 419 original event pages across maps 048–064 checked for byte-exact
  compiled commands, conditions, collision masks, atlas bounds and audio /
  picture dependencies.
- Actual C route/frame test checks the two-step lever approach through and
  after route completion; frames remain at the destination.
- Actual C scheduler tests cover puzzle timeouts and tail reset, lift stop,
  held dialogue continuation, and axe-present / axe-absent branches.
- Real C depth, sprite, save-book and note-renderer regression checks pass,
  alongside earlier factory, chase and elevator-flashback checks.
- Whole-source C syntax checked using host PSP declaration stubs. This is
  not a PSP SDK build or an emulator/hardware visual runtime verification.

Scope:
The entrance and END 1 branch are included. Other later branches, beginning
with maps 065 onward, are not certified complete by this patch.

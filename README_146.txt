NARAKU PSP 1.4.6 - Spider performance and tentacle arena stage

Requires 1.4.5. Extract into the project and run tools/build_deploy_v146.sh.
The script rebuilds EBOOT and deploys only the listed new/updated assets.
Save files, configuration, prior story progress and save format are unchanged.
Runtime textures/audio remain uncompressed.

Spider fix (Maps067/068): blocked non-skippable routes no longer open/write a
trace file on every rendered frame. This previously alternated the last-event
log marker between blocked spiders, repeatedly writing to storage. Optional
NARAKU_ROUTE_TRACE builds use separate deduplication for each event.
Original drop triggers, movement speeds, routes, through flags and collision
behavior are retained. The source pages initially enable Through and their
routes temporarily change it, so spiders can overlap as in the source game.

New playable stage: Map069 tentacle arena with its introduction, camera pans,
original nine-plate puzzle, visual switch pages, animated opening, moving
hazard boundaries, progressive timed constriction, sounds/music, original
death sequences and successful escape. Maps071-073 add the next dialogue,
giant-spider chase, original collision event and the post-chase save room.
Boss and giant-spider poses retain original source pixels and GPU filtering;
the moving giant spider has all three gait frames in a compact atlas layout.
Transparent death text is preserved. The arena timeout is dispatched even
when the player is idle. Timelines cancel when their original switch turns off.

Current endpoint: the original save room Map073 after the giant-spider chase.
Its save/load/options menu is implemented. Its onward exit displays a build
boundary message rather than attempting to load missing Map074 resources.
Later chapters and remaining endings are not included in this patch.
Ending 1 and all previously implemented stages remain intact.

Validation: host C syntax check; resource/VM/collision/audio/picture audit;
actual C route scheduler exercised through 40,000 blocked-spider updates
with zero trace writes and subsequent movement recovery; all 2,304 valid
plate transitions and completion conditions; original native boss/spider
pixels; actual C arena timer stages, route dispatch and cancellation;
existing puzzle resets, killer retention, spider hold timers, save/menu,
rope consumption and ending transparency regressions.
No PSP hardware or PPSSPP runtime was available for verification; frame-rate
improvement still needs confirmation in the reported room on the target.

Restart the game and load an in-game save. Avoid resuming emulator save states
created with an older executable. Test the same rightward spider escape,
then the arena introduction, puzzle, timeout/death, success, giant-spider
chase and save menu in the next save room.

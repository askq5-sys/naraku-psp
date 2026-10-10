NARAKU PSP 1.4.4 - Spider area, up to the pre-boss save point

Requires the complete game with 1.4.3 installed.
Extract into the project and run tools/build_deploy_v144.sh.
The script copies only the resources listed in assets_patch_144.txt.
Restart and load an in-game save. Saves/config are not deleted or migrated.

Implemented original Maps065,066,067,068 and070: connecting rooms, both save
rooms, spider ambushes, touch collisions, chase routes, escape/death branches,
180-frame hold timers, original switch resets on exit, pictures and exact
sound variants. Native actor and spider source pixels use linear reduction.
Spider walking directions and three gait frames are retained. Moving spiders
can catch an idle player; recovery does not pause the killer route subsystem.
The original transparent attack/death messages are preserved.

Continue through the web passage from Map056 into Map064, then Map065.
Use an in-game save before that branch; finishing END1 returns to the title.
The branch requires the original Demonic Axe web interaction in Map056.

Current implementation boundary: the save room before the boss (Map070).
The boss encounter in Map069 and the subsequent story are the next stage;
this patch does not implement or certify those scenes. Stop testing this
stage at the pre-boss save point rather than entering the boss room.

Suggested checks:
- Enter/leave both side rooms and save/load using their original menus.
- Trigger each ambush, confirm promptly to escape, and confirm after the
  hold timeout to exercise the original death branch.
- Leave/re-enter the spider rooms and verify their original switch resets.
- Reach Map070, save there and return to the spider area.

Validation: all 50 new pages compile as supported and five autonomous
routes match the original. Combined checks cover 470 stage pages, 723 native
actor/spider frames, 1445 script pages, all picture/audio dependencies,
timer expiration/cancellation, actual moving contact cells, original
collisions and rendering. Previous ending, Rope, save/input/fade and host C
syntax checks passed. No PSP SDK/emulator/hardware was available here;
actual gameplay, performance and visual output still need runtime testing.

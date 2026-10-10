NARAKU PSP 1.5.2 - Will chapter opening

Requires 1.5.1. Extract into the project and run tools/build_deploy_v152.sh.

The original post-Ending-2 continuation is restored. After the caption and
credits, the game changes the leader to Will, enters the Eber house upstairs,
shows the original introduction and removes Enri's original inventory items.
It no longer returns to the title at this milestone.

Playable new section: Maps080-086, including the house upstairs/downstairs,
the connecting route, Royal Capital streets, the general store, restaurant
and alley. Includes the original conversations, wallet pickup, event pages,
self switches, NPC routes, pictures, sounds and save book. New dialogue art
uses cropped native source images with the existing PSP portrait renderer.
Will's 12 source animation frames are retained at native texture resolution.

The next districts (Maps087/088/100/111) are not part of this patch. Their exit
pages display a milestone message instead of loading unfinished areas. Save
at the book in Will's house before testing the next stage.

Character membership persists in unused PG60 header bits without resizing
save files. Earlier Enri saves remain compatible. Previous ending approach,
white Finish-A1 side fields and giant-spider fixes are preserved. Configuration
and save slots are not deleted or overwritten by deployment.

Restart and load an in-game save before the second ending to reach the new
chapter. Older emulator states retain the previous event resource data.

Validation: 143 packed pages, original continuation/inventory commands, page
conditions, tile passability, atlas bounds, picture/audio dependencies, native
Will pixels, NPC walking sheets, actor save-bit compatibility and actual C
blocked-front city door dispatch. Ending-2 approach and spider contact tests
pass. Whole main.c host syntax, Python preparation and deployment shell checks
pass. No PSP SDK build, PPSSPP playthrough or physical PSP test was available.

NARAKU PSP 1.4.1 - Second puzzle timeout and passage ceiling

Requires the complete game with patch 1.4.0 installed.
Extract into the project and run tools/build_deploy_v141.sh.
The script builds the EBOOT and copies the updated Map041 resource.
Restart the game and load an in-game save when testing.

Map048 event15's original timeout reset now runs on the next frame after
the timer, without touching another switch. The exact original reset page
clears the lever progress. The separate door-opening autorun is unchanged.
Map049's previous timeout fix is retained.

Map041's black ceiling tiles now draw in front of actors, hiding the head
above the narrow passage. Only ceiling depth bits changed in map041.bin;
tile identities, passage masks, event scripts and textures are unchanged.

Validation: actual packed resources and actual C scheduler passed idle
timeouts, retry timers, cancellation and unrelated switch/item retention.
419 original stage pages, 623 native actor frames, 1407 original script pages,
both passage ceiling resources and Rope checks passed. Whole main.c passed
host syntax checks with PSP API stubs. PSP/PPSSPP runtime testing was not
available here. Save/config files and the save format are unchanged.

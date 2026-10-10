NARAKU PSP 1.4.9 - Giant-spider contact correction

Requires 1.4.8. Extract into the project and run tools/build_deploy_v149.sh.
Only EBOOT is rebuilt; assets and save format are unchanged.

During a normal movement step, RPG Maker MZ immediately commits the player's
logical destination. Map072 now tests event contact against that destination,
instead of also testing the cell Enri is leaving. This removes premature
captures on the straight corridor and the downward turn into the exit.
Idle contact and moving into the spider remain lethal. Other maps retain
their existing contact handling. Spider speeds and route data are unchanged.

Hold R to run with Always Dash OFF; with Always Dash ON, release R.
Restart the game and load an in-game save, rather than an old emulator state.

Validation: compiled actual main-loop contact calls cover horizontal escape,
the downward exit turn, incoming/idle contact, and unchanged other-map checks.
The existing actual C route timing regression also passes. Build script syntax
checked. This patch has not been tested in PPSSPP or on PSP hardware.

NARAKU PSP 1.5.1 - Ending 2 presentation fixes

Requires 1.5.0. Extract into the project and run tools/build_deploy_v151.sh.

Finish A1's fitted image now has white side fields instead of black. Only
this picture is affected; the fields use the picture's current fade opacity.
The artwork is unchanged and retains its aspect ratio.

Map078's four confrontation triggers move from row10 to row9, the original
script's approach destination. Enri walks horizontally to the centre if
needed, then follows the existing approach. The same-map transfer and the
preceding instant tint reset are removed, preventing the backward snap.
The scene after alignment, final confrontation, Ending 2 and credits remain.

Deploys EBOOT and Map078's event/VM data. No texture replacement, configuration
reset or save deletion. Restart and load an in-game save before this scene;
an older emulator state contains the earlier event resources.

Checks: all four entrances, packed VM, unchanged scene tails, actual C white
margin calls across all fade levels, full new-stage resource/scheduler/form
regression, whole-main host syntax and shell syntax. Not emulator/hardware tested.

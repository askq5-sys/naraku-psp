NARAKU PSP 1.4.7 - Original arena exit-door collision

Requires 1.4.6. Extract into the project and run tools/build_deploy_v147.sh.
Only EBOOT and assets/map069_vm.bin are deployed. Saves, configuration,
textures, audio, arena timer and all existing story commands are retained.

Cause: the original closed exit door is a below-character tile event. MZ
checks its tileset passage flags before the map layers; the port previously
checked ordinary actor-priority colliders and static map passage only.
This allowed walking through the closed door.

Fix: opt-in packed VM metadata stores original passage flags for the active
non-star tile pages. Movement now observes that active tile state. Closed
door tile738 blocks all directions; opening tiles730/722 have the original
star flag and defer to underlying corridor passage. Blank opened pages have
no tile collider. Old resources without this metadata retain their behavior.
Only Map069 is rebuilt with the new metadata in this patch.

Original interaction: solving the nine-plate puzzle lights the green panel.
Face the panel to the left of the door and press the action button to open
it. Puzzle completion does not automatically open the door in the original.
The panel event sets switches715/716/717 with three-frame waits, plays the
opening sound/shake and sets738 to retain its completed state. These original
commands and all visual-page references are unchanged.

Validation: actual C passage/page-selection code tested with packed Map069;
closed passage both before and after puzzle completion; all three visual
opening states at original timings; open/restored states; all original
passage metadata; legacy compatibility. Stage timer, spider performance,
plate puzzle, original contact/action and direct book-save regressions pass.
Whole main.c passes host syntax checking. No PSP/PPSSPP runtime verification
was available. Restart and load an in-game save to test.

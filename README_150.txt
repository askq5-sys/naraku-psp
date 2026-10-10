NARAKU PSP 1.5.0 - Elevator, surface and Ending 2

Requires 1.4.9. Extract this patch into the existing project, then run:
  chmod +x tools/build_deploy_v150.sh
  ./tools/build_deploy_v150.sh

Continue from the original save room after the giant-spider escape (Map073).
The previously guarded exit now leads into the next original story section.

Added:
- Maps074-079, including the elevator lever, door stages, ride and exit.
- Original elevator background, timing, shake, sounds and save-access changes.
- Surface conversations, heartbeat scenes and Enri's changing character forms.
- The original final confrontation, transformation, pictures and sound cues.
- Ending 2, its separate transparent caption and the original credits.
- Native source pixels for new event graphics and all alternate leader frames,
  sampled with the port's existing linear filtering at PSP scale.

This milestone returns to the title after Ending 2 and its credits. The
original additional-content transition into Map083 is intentionally deferred
until that next chapter is implemented. The existing first ending remains.

The 1.4.9 giant-spider contact correction and preceding fixes are preserved.
Your configurations and save slots are not deleted or overwritten. PG60 keeps
its existing size; spare header bits store the current leader form. Older saves
load as normal Enri. Restart the game and load an in-game save after installing,
rather than resuming an emulator state captured with an earlier executable.

Testing completed on the host:
- All 100 event pages match the original compiled commands and page conditions,
  except the documented post-credits boundary into the deferred chapter.
- Tile passability, atlas bounds, exact native elevator/leader pixels and all
  picture/audio dependencies checked.
- Actual C parallel scheduler tested for the 640-frame ride, staged door opening,
  terminal page cancellation and restored switch state.
- Actual VM party handler and compatible save-bit round trips checked.
- Giant-spider timing/contact and arena-door regressions pass.
- Whole main.c syntax checked with PSP API declarations; deployment shell and
  Python preparation scripts checked.
No PSP SDK build, PPSSPP playthrough or physical PSP test was available here.

For testing, first save in Map073. Check the lever, entering the lift from all
three entrance tiles, waiting for arrival, exiting to the surface, the heartbeat
scenes, the confrontation, Ending 2 caption, credits and return to title.

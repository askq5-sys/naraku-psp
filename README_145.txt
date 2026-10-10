NARAKU PSP 1.4.5 - Preserve the killer during puzzle timeout

Requires 1.4.4. Extract into the project, then run tools/build_deploy_v145.sh.
Rebuild only; no asset replacement, save deletion or save format change.

The additional Map049 timeout reset previously cleared switches 561-570,
including the killer spawn flags 561/562, entrance flag 565 and pose flag567.
The original reset did not clear those flags. The extra reset now clears
checkpoint five (541-552) and only door progress flags566/568/569/570.
Actor/entrance state is retained, so the timer no longer hides the killer.

Validation: actual packed VM pages and actual C scheduler tested for timeout
with fourth checkpoint active, checkpoint/door reset, active killer sprite
page retention and preservation of all actor/entrance flags. Existing timer
retry/cancellation and new spider timers pass. Whole main.c passes host syntax
checking. No PSP/PPSSPP runtime verification was available.

Restart and load an in-game save made before the failed timeout to verify.
This fix prevents future disappearance; it cannot reliably reconstruct an
already-cleared killer state from an older save or emulator save state.

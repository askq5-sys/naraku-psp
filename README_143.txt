NARAKU PSP 1.4.3 - Transparent first ending messages

Requires 1.4.2. Extract into the project and run tools/build_deploy_v143.sh.

Map062 now preserves the original transparent message background, including
END 1/7 No Salvation. The frame and tinted window fill are omitted; bottom
placement, left alignment, smooth font rendering and confirmation stay intact.
The VM adds opcode40 with the existing text payload. Other installed map
resources remain compatible; normal dialogue retains its frame.

Validation: actual renderer tested for cached/fallback transparent text and
normal dialogue/name frames. Stage, native sprite, continuous ending approach
and host C syntax checks passed. No PSP/PPSSPP runtime test was available.
Saves/config and save format are unchanged. Restart and load an in-game save.

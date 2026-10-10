NARAKU PSP 1.5.8 - Pre-Will maintenance
Requires 1.5.7. Runtime and development checks only; no new story locations.

Changes
- Replace linear trail shifting with a fixed-capacity circular buffer. O(1) insertion instead of copying 510 coordinates after filling the history. Capacity and chase decisions are unchanged.
- Extract secret ladder clipping into runtime/render_boundaries.h. Actor-only scissor, original walk/transfer and camera behavior are preserved.
- Update obsolete host checks for original capitalization, full-screen white Finish A1 underlay, message helper boundaries, new chase helper, and restored Will continuation.

Validation
- 100 original lift/Ending2 pages and 143 post-credits/Will pages: packed script parity, passage masks, native artwork, dependencies.
- Actual C lift scheduler, player form/save flags and blocked city doors.
- Giant spider timing/contact, arena door, killer contact, laser and press cycles.
- Dialogue capitalization/colors, notification closure, all 16 classroom messages and rasterizer glyph retention.
- 20000 differential trail operations against the previous implementation, including turns, overflow and resets. Ladder clipping scope/camera checks.
- Whole-main host syntax and deployment shell syntax.
No PSP SDK link, emulator or hardware gameplay verification was available. This is a targeted regression audit, not an assertion that every route and ending has been tested.

Installation
Unzip into the project, chmod +x tools/build_deploy_v158.sh, run it.
Restart and use an in-game save. Config/save files and assets are untouched.
Host Python resource tests require original/data beside the project and the previously generated development assets; they are not part of the player installation.

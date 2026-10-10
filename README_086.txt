NARAKU PSP 0.8.6 — inventory and camera patch

Install over the existing full game, then run tools/build_deploy_v086.sh.
Requires the same PSP SDK and complete assets as previous patches.

Inventory opens on categories. Left/right selects Items or Key Items.
X enters the list; arrow keys select in the two-column grid.
Cancel returns to categories, then closes the inventory.
Descriptions and item highlight appear only in list mode.
Red translucent windows overlay a blurred snapshot of the world.
Compact labels preserve color escapes and complete glyph cells.

Player follows the continuous camera while tiles retain integer rasterization,
removing the fractional-motion screen-position oscillation when camera follows.
Includes previous font, fall-animation and lowercase cleaver assets.
Shutdown unchanged. Saves and XMB artwork preserved.

Validation: host animation/route regression checks and C syntax check.
No PSP SDK, PPSSPP or real PSP execution was available for this patch.

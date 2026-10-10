NARAKU PSP 1.5.9 - Will: city streets and Krois shop
Requires 1.5.8. Existing Enri/Will save format and gameplay progress are preserved.

Saved actor previews
Each occupied slot now displays its saved party leader, including Will. PG40/PG30 saves retain the Enri fallback. The menu does not change the current party while reading previews. Standing frames are cached once per actor and freed when the menu closes (up to 160 KiB).

New playable area
Maps087-092: residential alley2, main street, alley3, alley4, gate, Krois shop. City hub exits to these streets are restored. Original conversations, item purchases (57/58/59), choices, conditions and self-switches are compiled. RPG Maker Break Loop (113) now exits the nearest loop, allowing the original shop conversation menu to execute.
Outward pages leading beyond Maps080-092 remain explicit stage boundaries. Chases, further interiors and later endings beyond this section are not included yet. The earlier guarded entrances to the underground and special backstreet remain guarded.
Native NPC frames/portraits, exact audio variants, map textures and passage masks are prepared from the original files. No runtime asset compression.

Validation
551 pages across post-credits and the available Will section: compiled commands, conditions, passage masks, textures, dependencies, actor/save bits and blocked-front city doors. Saved-slot actor selection and preview caching executed in host C. Simple/nested loop jump targets checked. Lift/Enri finale, giant chase/contact, key colors and smooth ending approach regressions pass. Whole-main host syntax and deployment shell syntax pass.
PSP SDK link, real hardware and PPSSPP playthrough were not available.

Install
Unzip into the project, chmod +x tools/build_deploy_v159.sh, run it, restart the game and load an in-game save. Save files are not replaced. Re-saving an existing Will slot is unnecessary: its actor flags are already present.
To continue, explore the city exits toward the new streets and Krois shop. Save at an available book before choosing a purchase branch.

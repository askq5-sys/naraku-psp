NARAKU PSP 1.1.5 cumulative patch.
Flashback English dialogue is reflowed by actual glyph advances. Long messages paginate across 3-row pages without reducing font size or dropping content. Old PC line breaks are removed in flashback prose only. CPU word measurement matches its rounded glyph advances.
Map012/013 VM rebuilt with exact audio IDs. Cleaver pickup restores original sheathing SE (volume90/pitch80/pan0), wait60 frames and notification SE. Partial asset converter now loads existing exact audio manifest automatically.
Previous 1.1.4 changes, user controls and saves preserved.
Close PPSSPP, extract over complete project and run tools/build_deploy_v115.sh.
Host tests: all 16 original flashback messages fit, no lost text, NPC sprites/camera/transfer tests pass. PSP build/runtime unavailable here.

NARAKU PSP 1.7.1 - Spider entrances and cinematic exits

Install over your existing 1.7.x project and game assets.
Run tools/build_deploy_v171.sh after extracting this archive.
Restart the game and use an in-game save, not an old emulator save state.
Save slots, settings and progress files are preserved.

Changes:
- Spider-room entrance sensors span the interior width at the original
  activation depth (Map067 row 6; Map068 row 5). The original descent,
  chase, contact and one-shot page conditions are unchanged.
- Will fades out across the last tile of the first suspicious-men escape
  scene (Map094). Party visibility and save metadata are unchanged.
- Includes the complete 1.7.0 remaining-city asset set again: bonus room,
  gallery, sewer side route, Blue Envelope and secret finale resources.

Secret-route audit:
- Map032 Secret Key pickup enables persistent switch 984.
- Map095 Amalia wakeup enables switch 933.
- Map120 envelope page requires both switches 933 and 984.
- Map124 envelope delivery enables switch 992.
- Map139 sewer event enables switch 1027.
- Map082 home finale checks delivery and the sewer event for the extra scene.
Continue from Enri's ending into Will's story in the same run; a new game
clears the route flags. Older saves cannot recover events never completed.
No missing story flags are enabled automatically by this patch.

Validation: host C syntax; actual touch dispatch and fade fixture; original
944 post-credits/city event pages and resource dependencies; cinematic routes,
actor frames and save-preview compatibility. PSP/emulator playthrough of
all secret branches has not been performed in this environment.

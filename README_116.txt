NARAKU PSP 1.1.6 cumulative patch.
Pressing Room (Map024): event12 parallel cycle restored as a nonblocking
frame timer. Wait60 -> switch183 ON/184 OFF -> Wait60 -> flash red for5,
switch183 OFF/184 ON, original bonecrush5 90/100/0 -> Wait100 -> both OFF.
Switch191 disables the cycle as in the original; timer resets on map load/exit.
Timer updates during scene waits and ordinary world rendering.
Map024 S-003 active collision page (switch91, event touch) and Map025 collision
retain original command lists, conditions, sprite references and transfer to
Map027. Exact audio IDs rebuilt for Maps024/025/027. Missing later-room sound
assets generated from original files with original volume/pitch/pan. Map027
crushing sounds: bonecrush4, bonecrush5 twice, hit_axe3 (all90/100/0).
No new Laser1/Laser2 sounds: original scripts do not reference those files.
All previous patches and controls image included. Saves preserved.
Close PPSSPP, unzip over the complete project and run tools/build_deploy_v116.sh.
Host tests passed: press phases/repetition/disable/map exit; original death sound
references and PCM availability; existing flashback/text/camera/sprite checks.
PSP SDK build and runtime collision/audio synchronisation not tested here.

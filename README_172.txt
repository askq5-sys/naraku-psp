NARAKU PSP 1.7.2 - Gallery entrance interaction

Front action input now matches MZ checkEventTriggerThere([0,1,2]):
normal-priority Player Touch and Event Touch doors accept the action button.
Current-cell action remains restricted to Action Button pages. Autorun,
parallel, inactive and empty pages cannot be started by this input.

Map112 gallery entrance is at tile (8,2). Approach along the narrow alley,
stand immediately left of the grate and face right; press action or attempt
walking into it. Map113 leads onward to the Map114 CG gallery.

Includes the 1.7.1 fixes and the complete 1.7.0 extra-city asset set.
Install over the existing project, run tools/build_deploy_v172.sh, restart
and load an in-game save. Saves and configuration are not deleted.

Validated with actual runtime touch/action dispatch, 944 original city
pages and resources, host C syntax and shell syntax. No PSP playtest here.

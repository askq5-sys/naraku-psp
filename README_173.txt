NARAKU PSP 1.7.3 - Ending captions and gallery exit

- The gallery north exit hides Will's upper body beneath the dark ceiling.
- English END captions preserve original line breaks: I see something...
  remains on a separate line. Prose still uses PSP word wrapping.
- Avoid redundant GU alpha/color changes for fully opaque player sprites.
- Correct outdated diagnostic version labels.

Original-event audit: all 3,543 pages across 139 maps examined. 3,542 are
accepted by the command compiler. Map032 event20 page1 is implemented by
its dedicated nonblocking factory scheduler, including Set Event Location.
The existing 944-page city bytecode/resource audit still passes.
This is a static/host audit, not a complete PSP replay of every branch.

Install over the current project; run tools/build_deploy_v173.sh. This patch
includes 1.7.2 changes and extra-city resources. Saves/config are preserved.
Restart and load an in-game save rather than an old emulator save state.

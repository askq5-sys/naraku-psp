#ifndef NARAKU_PRESSING_ROOM_H
#define NARAKU_PRESSING_ROOM_H
/* Map024 event12: Wait60, phase1, Wait60, crush, Wait100, reset, repeat.
 * Returns transitions only; disabling the event does not rewrite its switches. */
static int pressing_room_tick(int *frame, int enabled)
{
    if (!enabled) { *frame = 0; return 0; }
    ++*frame;
    if (*frame == 60) return 1;
    if (*frame == 120) return 2;
    if (*frame == 220) { *frame = 0; return 3; }
    return 0;
}
#endif

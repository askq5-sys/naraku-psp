#ifndef NARAKU_PLAYER_ANIMATION_H
#define NARAKU_PLAYER_ANIMATION_H
/* MZ animation count in half units: avoids floating point and keeps phase
 * when speed changes or control passes between input and event routes. */
typedef struct {
    int count_half;
    int pattern;
} PlayerAnimation;

static void player_animation_reset(PlayerAnimation *state)
{
    state->count_half = 0;
    state->pattern = 1;
}

static int player_animation_tick(PlayerAnimation *state, int moving,
                                 int jumping, int speed, int walk, int step)
{
    int visual = state->pattern < 3 ? state->pattern : 1;
    if (speed < 1) speed = 1;
    if (speed > 7) speed = 7;
    if (moving && walk) state->count_half += 3;
    else if (step || visual != 1) state->count_half += 2;
    if (state->count_half >= (9 - speed) * 6) {
        state->pattern = (!step && !moving && !jumping)
            ? 1 : (state->pattern + 1) % 4;
        state->count_half = 0;
    }
    return state->pattern < 3 ? state->pattern : 1;
}

/* RPG Maker route 12 = forward, 13 = backward. Backward keeps facing. */
static int player_route_delta(int code, int row, int *dx, int *dy)
{
    static const int row_dx[4] = {0, -1, 1, 0};
    static const int row_dy[4] = {1, 0, 0, -1};
    int sign = 1;
    if (row < 0 || row > 3) row = 0;
    if (code >= 1 && code <= 4) row = code - 1;
    else if (code == 13) sign = -1;
    else if (code != 12) return 0;
    *dx = row_dx[row] * sign;
    *dy = row_dy[row] * sign;
    return 1;
}
#endif

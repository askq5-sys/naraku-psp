#include <assert.h>
#include <stdio.h>
#include "../runtime/player_animation.h"
/* Independent transcription of original rmmz_objects.js using double count. */
typedef struct { double count; int pattern; } Reference;
static int reference_tick(Reference *r,int moving,int jumping,int speed,int walk,int step)
{
    int visual = r->pattern < 3 ? r->pattern : 1;
    if (moving && walk) r->count += 1.5;
    else if (step || visual != 1) r->count++;
    if (r->count >= (9-speed)*3) {
        if (!step && !moving && !jumping) r->pattern=1;
        else r->pattern=(r->pattern+1)%4;
        r->count=0;
    }
    return r->pattern<3?r->pattern:1;
}
int main(void)
{
    int speed,walk,step,f,row,dx,dy;
    unsigned int rng=17;
    PlayerAnimation a={0,1}; Reference r={0,1};
    for(speed=1;speed<=7;speed++) for(walk=0;walk<2;walk++) for(step=0;step<2;step++) {
        player_animation_reset(&a);r.count=0;r.pattern=1;
        for(f=0;f<600;f++) {
            int moving=f<300;
            assert(player_animation_tick(&a,moving,0,speed,walk,step)==
                   reference_tick(&r,moving,0,speed,walk,step));
        }
    }
    /* Speed changes, starts/stops, walking disabled, stepping, jump phases. */
    for(f=0;f<100000;f++) {
        int moving,jumping;
        rng=rng*1664525u+1013904223u;
        speed=1+(rng%7);moving=(rng>>4)&1;jumping=(rng>>5)&1;
        walk=(rng>>6)&1;step=(rng>>7)&1;
        assert(player_animation_tick(&a,moving,jumping,speed,walk,step)==
               reference_tick(&r,moving,jumping,speed,walk,step));
        assert(a.pattern==r.pattern && a.count_half==r.count*2);
    }
    for(row=0;row<4;row++) {
        int bx,by;
        assert(player_route_delta(12,row,&dx,&dy));
        assert(player_route_delta(13,row,&bx,&by));
        assert(bx==-dx && by==-dy);
        assert(player_route_delta(row+1,3,&bx,&by));
        assert(bx==dx && by==dy);
    }
    player_animation_reset(&a);
    for(f=0;f<100;f++)assert(player_animation_tick(&a,1,0,4,0,0)==1);
    puts("PASS: animation reference traces and four-direction routes");
    return 0;
}

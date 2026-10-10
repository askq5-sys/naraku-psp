/* Map032 / killer23 only: ordered player cells, never shortcut a corner.
 * Fixed original route commands remain authoritative. No save-file changes. */
static struct { short x[256], y[256]; int count, next, head; } laser_chase_trail;
static void laser_chase_reset(void)
{
    memset(&laser_chase_trail,0,sizeof(laser_chase_trail));
    laser_chase_trail.next=-1;
}
static void laser_chase_record(int x,int y)
{
    int n=laser_chase_trail.count;
    if(n && laser_chase_trail.x[(laser_chase_trail.head+n-1)&255]==x && laser_chase_trail.y[(laser_chase_trail.head+n-1)&255]==y)return;
    if(n && abs(x-laser_chase_trail.x[(laser_chase_trail.head+n-1)&255])+abs(y-laser_chase_trail.y[(laser_chase_trail.head+n-1)&255])!=1) {
        laser_chase_reset();n=0;
    }
    if(n==256) {
        laser_chase_trail.head=(laser_chase_trail.head+1)&255;
        n=255;
        if(laser_chase_trail.next>0)--laser_chase_trail.next;
    }
    laser_chase_trail.x[(laser_chase_trail.head+n)&255]=x;
    laser_chase_trail.y[(laser_chase_trail.head+n)&255]=y;
    laser_chase_trail.count=n+1;
}
/* -1 means the original route has not reached the recorded trail yet. */
static int laser_chase_step(int x,int y)
{
    int i,dx,dy;
    if(laser_chase_trail.next<0) {
        for(i=0;i<laser_chase_trail.count;++i)
            if(laser_chase_trail.x[(laser_chase_trail.head+i)&255]==x && laser_chase_trail.y[(laser_chase_trail.head+i)&255]==y) {
                laser_chase_trail.next=i;break;
            }
        if(laser_chase_trail.next<0)return -1;
    }
    i=laser_chase_trail.next;
    while(i<laser_chase_trail.count && laser_chase_trail.x[(laser_chase_trail.head+i)&255]==x && laser_chase_trail.y[(laser_chase_trail.head+i)&255]==y)++i;
    laser_chase_trail.next=i;
    if(i==laser_chase_trail.count)return 0;
    dx=laser_chase_trail.x[(laser_chase_trail.head+i)&255]-x;dy=laser_chase_trail.y[(laser_chase_trail.head+i)&255]-y;
    /* A scripted displacement may detach the enemy: rejoin on a later move,
     * rather than walking diagonally or through an obstacle. */
    if(abs(dx)+abs(dy)!=1) {laser_chase_trail.next=-1;return -1;}
    return dx<0?2:(dx>0?3:(dy<0?4:1));
}

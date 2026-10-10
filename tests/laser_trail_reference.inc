/* Map032 / killer23 only: ordered player cells, never shortcut a corner.
 * Fixed original route commands remain authoritative. No save-file changes. */
static struct { short x[256], y[256]; int count, next; } reference_chase_trail;
static void reference_chase_reset(void)
{
    memset(&reference_chase_trail,0,sizeof(reference_chase_trail));
    reference_chase_trail.next=-1;
}
static void reference_chase_record(int x,int y)
{
    int n=reference_chase_trail.count;
    if(n && reference_chase_trail.x[n-1]==x && reference_chase_trail.y[n-1]==y)return;
    if(n && abs(x-reference_chase_trail.x[n-1])+abs(y-reference_chase_trail.y[n-1])!=1) {
        reference_chase_reset();n=0;
    }
    if(n==256) {
        memmove(reference_chase_trail.x,reference_chase_trail.x+1,255*sizeof(short));
        memmove(reference_chase_trail.y,reference_chase_trail.y+1,255*sizeof(short));
        n=255;
        if(reference_chase_trail.next>0)--reference_chase_trail.next;
    }
    reference_chase_trail.x[n]=x;reference_chase_trail.y[n]=y;
    reference_chase_trail.count=n+1;
}
/* -1 means the original route has not reached the recorded trail yet. */
static int reference_chase_step(int x,int y)
{
    int i,dx,dy;
    if(reference_chase_trail.next<0) {
        for(i=0;i<reference_chase_trail.count;++i)
            if(reference_chase_trail.x[i]==x && reference_chase_trail.y[i]==y) {
                reference_chase_trail.next=i;break;
            }
        if(reference_chase_trail.next<0)return -1;
    }
    i=reference_chase_trail.next;
    while(i<reference_chase_trail.count && reference_chase_trail.x[i]==x && reference_chase_trail.y[i]==y)++i;
    reference_chase_trail.next=i;
    if(i==reference_chase_trail.count)return 0;
    dx=reference_chase_trail.x[i]-x;dy=reference_chase_trail.y[i]-y;
    /* A scripted displacement may detach the enemy: rejoin on a later move,
     * rather than walking diagonally or through an obstacle. */
    if(abs(dx)+abs(dy)!=1) {reference_chase_trail.next=-1;return -1;}
    return dx<0?2:(dx>0?3:(dy<0?4:1));
}

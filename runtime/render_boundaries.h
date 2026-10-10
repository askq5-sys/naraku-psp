#ifndef NARAKU_RENDER_BOUNDARIES_H
#define NARAKU_RENDER_BOUNDARIES_H
#include <math.h>
/* Upper ladder lip hides the actor only; world rendering and transfers stay
 * independent. -1 leaves the full screen visible on every other location. */
static int secret_ladder_clip_top(int map_id,float world_x,float world_y,
                                  int tile_px,float origin_y,float camera_y,int height)
{
    int top;
    /* Gallery's north exit: the upper body passes beneath the dark ceiling. */
    if(map_id==114 && world_x>=14.0f*tile_px && world_x<=15.0f*tile_px &&
       world_y<=3.0f*tile_px) {
        top=(int)floorf(origin_y+tile_px-camera_y);
        return top<0?0:(top>height?height:top);
    }
    if(map_id!=105 || world_x<1.5f*tile_px || world_x>3.5f*tile_px ||
       world_y>20.0f*tile_px)return -1;
    top=(int)floorf(origin_y+16.0f*tile_px-camera_y);
    return top<0?0:(top>height?height:top);
}
/* A horizontal entrance sensor cannot be bypassed along the room wall.
 * Keep the original event, depth, page conditions and descent commands. */
static int spider_entrance_contact(int map_id,int event_id,int x,int y,int width)
{
    if(x<=0 || x>=width-1)return 0;
    return (map_id==67 && event_id==5 && y==6) ||
           (map_id==68 && event_id==3 && y==5);
}
/* Cosmetic cinematic exit only. Never changes the saved visibility flag. */
static int cinematic_player_opacity(int map_id,float world_x,int tile_px)
{
    float alpha;
    if(map_id!=94)return 255;
    alpha=(19.5f-world_x/tile_px)*255.0f;
    return alpha<=0?0:alpha>=255?255:(int)alpha;
}
#endif

from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static void draw_event_sprite_record(');b=s.index('static int is_dedicated_story_key_event(',a)
pre='''#include <assert.h>
#include <stdint.h>
#include <string.h>
#define MAX_EVENT_ID 160
#define TILE_PX 24
#define EVENT_ATLAS_W 512
#define EVENT_ATLAS_H 512
#define GU_LINEAR 1
#define GU_NEAREST 0
#define GU_TFX_MODULATE 1
#define GU_TCC_RGBA 1
typedef struct{int x,y,sx,sy,sw,sh,flags,event_id;}EventSpriteRecord;
typedef struct{void *records;int remaining,dx,dy;}EventRoute;
static EventRoute g_routes[160];static float g_event_shift_x[160],g_event_shift_y[160],g_event_jump_height[160],g_actor_camera_x,g_actor_camera_y;
static int g_event_direction[160],g_event_opacity[160];static struct{int pattern;}g_event_animation[160];static unsigned int g_world_render_frames;
static void *g_event_texture_base=(void*)1,*g_event_texture_detail=(void*)2,*g_event_texture_bound;
static void *bound;static float srcx,dstw,dsth;static int filter;
static int is_chase_enemy(int m,int id){return (m==32&&id==23);}
static float render_floor_pixel(float x){return (int)x;}
static void bind_texture_8888(void*p,int w,int h){bound=p;}
static void sceGuTexFilter(int a,int b){filter=a;}
static void sceGuTexFunc(int a,int b){}
static void sceGuColor(unsigned int a){}
static void set_pixel_art_texture_state(void){}
static void draw_bound_rect(float x,float y,float w,float h,float dx,float dy,float dw,float dh){srcx=x;dstw=dw;dsth=dh;assert(filter==GU_LINEAR);}
'''
post='''int main(void){for(int i=0;i<160;i++)g_event_opacity[i]=255;
g_event_direction[7]=3;g_event_animation[7].pattern=1;g_routes[7].records=(void*)1;g_routes[7].dy=-1;
EventSpriteRecord sp={4,12,1,1,54,108,236,7};int expected[]={1,2,1,0,1,2,1};
for(int step=0;step<7;step++){g_event_shift_y[7]=-step-.5f;draw_event_sprite_record(&sp,35,0,0,0,0);assert(srcx==1+162+54*expected[step]);}
g_routes[7].dy=0;g_event_shift_y[7]=-7;draw_event_sprite_record(&sp,35,0,0,0,0);assert(srcx==217);
g_routes[7].dx=1;g_event_direction[7]=2;
for(int step=0;step<13;step++){static const int gait[]={1,2,1,0};g_event_shift_x[7]=step+.5f;draw_event_sprite_record(&sp,35,0,0,0,0);assert(srcx==1+54*gait[(step+7)&3]);}
g_routes[7].records=0;draw_event_sprite_record(&sp,35,0,0,0,0);assert(srcx==55);return 0;}'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: actual renderer selects walking poses for all seven up and thirteen right steps; pauses and route end use idle')

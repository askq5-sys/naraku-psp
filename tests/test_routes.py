"""Exercise the actual asynchronous player-route tick from main.c on host."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'main.c').read_text()
a=s.index('static void tick_player_route(');b=s.index('static float picture_ease(',a)
pre=r'''
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "runtime/player_animation.h"
#define TILE_PX 24
typedef struct {int w,h;} MapState;
typedef struct {uint8_t *records;int count,index,flags,remaining,total,dx,dy,base_x,base_y;float start_x,start_y;} EventRoute;
static EventRoute g_player_route;
static int *g_route_player_x,*g_route_player_y,*g_route_player_direction;
static float g_route_real_x,g_route_real_y;
static int g_player_move_speed_code=6,g_player_direction_fix,g_player_walk_anime=1,g_player_step_anime,g_player_through,g_player_visible=1;
static int blocked;
static int read_u16_le(const uint8_t*p){return p[0]|p[1]<<8;}
static int clamp_move_speed_code(int n){return n<1?1:n>6?6:n;}
static int pass_mask_at(const MapState*m,int x,int y){(void)m;(void)x;(void)y;return blocked?0:15;}
static int vm_event_blocks_at(const MapState*m,int x,int y){(void)m;(void)x;(void)y;return 0;}
static void play_vm_se_params(int a,int b,int c,int d){(void)a;(void)b;(void)c;(void)d;}
static void begin(int code,int *x,int*y,int*row){
 free(g_player_route.records);memset(&g_player_route,0,sizeof(g_player_route));
 g_player_route.records=calloc(5,1);g_player_route.records[0]=code;
 g_player_route.count=1;g_route_player_x=x;g_route_player_y=y;g_route_player_direction=row;
}
'''
post=r'''
int main(void){MapState m={10,10};int x=5,y=5,row=0,i;
 begin(13,&x,&y,&row);tick_player_route(&m);assert(x==5&&y==4&&row==0);
 for(i=0;i<3;i++)tick_player_route(&m);
 assert(g_player_route.remaining==0&&g_route_real_y==120);
 tick_player_route(&m);assert(!g_player_route.records);
 blocked=1;begin(3,&x,&y,&row);tick_player_route(&m);
 assert(x==5&&row==2&&g_player_route.index==0);
 g_player_direction_fix=1;begin(1,&x,&y,&row);tick_player_route(&m);assert(row==2);
 blocked=0;g_player_through=1;x=9;begin(3,&x,&y,&row);tick_player_route(&m);assert(x==9);
 free(g_player_route.records);g_player_route.records=NULL;
 { uint8_t config[5]={29,4,0,0,0};
   assert(start_player_route(config,1,0,&x,&y,&row));
   assert(!g_player_route.records && g_player_move_speed_code==4);
 }
 { uint8_t turn[5]={16,0,0,0,0};
   g_player_direction_fix=0;
   assert(start_player_route(turn,1,0,&x,&y,&row));assert(!g_player_route.records && row==0);
 }
 { uint8_t wait[5]={15,5,0,0,0};
   assert(start_player_route(wait,1,0,&x,&y,&row));assert(g_player_route.records);
   free(g_player_route.records);g_player_route.records=NULL;
 }
 return 0;}
'''
with tempfile.TemporaryDirectory() as t:
 c=Path(t)/'routes.c';exe=Path(t)/'routes';c.write_text(pre+s[a:b]+post)
 subprocess.run(['cc','-std=c99','-I',str(root),str(c),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
print('PASS: actual route tick, backward facing, arrival, blocking, direction fix, bounds')

"""Run actual frame/route code past the two-step nonwaiting lever approach."""
from pathlib import Path
import re,subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static void tick_player_route(');b=s.index('static float picture_ease(',a);engine=s[a:b];a=s.index('static void vm_render_frame(\n');b=s.index('static void vm_wait_frames(',a);frame=s[a:b]
pre=r'''#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define TILE_PX 24
typedef struct{int w,h,id;}MapState;
typedef struct{uint8_t*records;int count,index,flags,remaining,total,start_x,start_y,dx,dy;}EventRoute;
static EventRoute g_player_route;
static int *g_route_player_x,*g_route_player_y,*g_route_player_direction;
static float g_route_real_x,g_route_real_y,last_x,last_y;
static int g_player_move_speed_code=4,g_player_direction_fix,g_player_walk_anime=1,g_player_step_anime,g_player_through,g_player_visible=1,g_player_animation_speed;
static const MapState *g_vm_position_owner;static int *g_vm_tile_x,*g_vm_tile_y,*g_vm_direction;
static uint16_t read_u16_le(const uint8_t*p){return p[0]|p[1]<<8;}
static int clamp_move_speed_code(int x){return x<1?1:x>6?6:x;}
static void player_route_delta(int code,int d,int *dx,int *dy){*dx=code==2?-1:code==3?1:0;*dy=code==1?1:code==4?-1:0;}
static int pass_mask_at(const MapState*m,int x,int y){return 15;}
static int vm_event_blocks_at(const MapState*m,int x,int y){return 0;}
static void play_vm_se_params(int a,int b,int c,int d){}
static void tick_player_route(const MapState*m);
static void render_world(const MapState*m,void*a,void*b,void*c,int v,float x,float y,int p,int d,int f,float k,void*t,void*q,int r,int z,int n){int had=!!g_player_route.records;tick_player_route(m);if(had){x=g_route_real_x;y=g_route_real_y;}last_x=x;last_y=y;}
static void vm_pump_stage_message(const MapState*m,void*a,int x,int y,int d){}
'''
post=r'''int main(void){MapState m={17,13,55};int x=2,y=8,d=0;g_vm_position_owner=&m;g_vm_tile_x=&x;g_vm_tile_y=&y;g_vm_direction=&d;
uint8_t route[]={29,5,0,0,0,3,0,0,0,0,3,0,0,0,0,19,0,0,0,0};assert(start_player_route(route,4,0,&x,&y,&d));
float previous=60;for(int i=0;i<30;i++){vm_render_frame(&m,NULL,2,8,0,0,0);assert(last_x>=previous&&last_x<=108);previous=last_x;}assert(!g_player_route.records&&x==4&&y==8&&d==3&&last_x==108&&last_y==216);
g_vm_position_owner=NULL;vm_render_frame(&m,NULL,1,1,0,0,0);assert(last_x==36&&last_y==48);return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'position.c';e=Path(tmp)/'position';p.write_text(pre+engine+frame+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: actual nonwaiting two-tile route stays at the lever after completion; wait frames do not snap to stale coordinates; ownerless rendering remains unchanged')

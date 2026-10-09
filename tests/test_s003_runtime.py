from pathlib import Path
import struct,subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
a=s.index('static int event_route_can_step(');b=s.index('static void tick_player_route(',a)
globals_=s[s.index('static float g_event_shift_x'):s.index('static EventRoute g_player_route;')]
pre=r'''#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include "runtime/player_animation.h"
#define MAX_EVENT_ID 160
#define TILE_PX 24
static const char*g_scene_trace_path="/dev/null";
typedef struct {int id,vm_event_count;} MapState;
typedef struct {int event_id,x,y,first_page;} VmEventRecord;
typedef struct {int flags;} VmPageRecord;
static int first,active,blocked_axis;
static int vm_read_event(const MapState*m,int i,VmEventRecord*e){*e=(VmEventRecord){3,6,8,first};return 1;}
static int vm_active_page_index(const MapState*m,const VmEventRecord*e,VmPageRecord*p,int*i){p->flags=12;*i=active;return 1;}
static uint16_t read_u16_le(const uint8_t*p){return p[0]|p[1]<<8;}
static int pass_mask_at(const MapState*m,int x,int y){return blocked_axis && x==6 && y==8 ? 7 : 15;}
static int vm_event_blocks_except(const MapState*m,int x,int y,int id){return 0;}
static void play_vm_se_params(int a,int b,int c,int d){}
'''
post='int main(void){'
for mid,local in [(24,5),(25,1)]:
 raw=(r/'assets'/f'map{mid:03d}_vm.bin').read_bytes();ne=struct.unpack_from('<H',raw,4)[0]
 first=next(struct.unpack_from('<H',raw,20+i*10+6)[0]for i in range(ne)if struct.unpack_from('<H',raw,20+i*10)[0]==3)
 post+=f'''{{MapState m={{{mid},1}};first={first};active=first+{local};g_s003_paused=0;
 memset(g_routes,0,sizeof(g_routes));memset(g_event_shift_x,0,sizeof(g_event_shift_x));memset(g_event_shift_y,0,sizeof(g_event_shift_y));player_animation_reset(&g_event_animation[3]);
 tick_s003_autonomous(&m,9.5f*24,3.f*24);assert(g_routes[3].records);
 uint8_t*p=g_routes[3].records;tick_s003_autonomous(&m,9.5f*24,3.f*24);assert(g_routes[3].records==p);
 tick_event_routes(&m);assert(g_event_shift_y[3]<0);assert(g_event_direction[3]==3);
 int animated=0;for(int i=0;i<40;++i){{tick_event_routes(&m);if(g_event_animation[3].pattern!=1)animated=1;}}assert(animated);
 free(g_routes[3].records);memset(&g_routes[3],0,sizeof(g_routes[3]));g_event_shift_x[3]=g_event_shift_y[3]=0;blocked_axis=1;
 tick_s003_autonomous(&m,9.5f*24,3.f*24);tick_event_routes(&m);assert(g_event_shift_x[3]>0&&g_event_shift_y[3]==0);blocked_axis=0;
 free(g_routes[3].records);memset(&g_routes[3],0,sizeof(g_routes[3]));active=first;tick_s003_autonomous(&m,0,0);assert(!g_routes[3].records);
 active=first+{local};g_s003_paused=1;tick_s003_autonomous(&m,0,0);assert(!g_routes[3].records);}}
'''
post+='''{MapState m={27,1};first=0;active=0;g_s003_paused=0;
memset(g_routes,0,sizeof(g_routes));memset(g_event_shift_x,0,sizeof(g_event_shift_x));memset(g_event_shift_y,0,sizeof(g_event_shift_y));player_animation_reset(&g_event_animation[1]);
/* The torture autorun forces nine up steps, independent of the chase AI. */
uint8_t route[45]={0};for(int i=0;i<9;++i)route[i*5]=4;
assert(start_event_route(&m,1,route,9,0));g_event_move_speed[1]=3;
int animated=0;for(int i=0;i<80;++i){tick_event_routes(&m);if(g_event_animation[1].pattern!=1)animated=1;}
assert(animated && g_event_shift_y[1]<-1);free(g_routes[1].records);memset(&g_routes[1],0,sizeof(g_routes[1]));}
return 0;}'''

with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+globals_+s[a:b]+post);subprocess.run(['cc','-std=c99','-Wall','-Wno-unused-function','-Wno-unused-variable','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: actual S-003 route startup on global VM page indexes, movement toward player, walking animation, inactive and paused pages, forced-route preservation')

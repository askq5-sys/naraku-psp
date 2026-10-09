from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static int is_chase_enemy(');b=s.index('/* A supported active VM page',a)
pre='''#include <stdint.h>
#include <assert.h>
#define MAX_EVENT_ID 160
typedef struct {int id,vm_event_count;void*vm_bin;} MapState;
typedef struct {int event_id,x,y;} VmEventRecord;
typedef struct {int trigger,supported,priority,flags,cmd_size;} VmPageRecord;
typedef struct {void*records;int remaining,dx,dy;float start_x,start_y;} EventRoute;
static EventRoute g_routes[MAX_EVENT_ID];
static float g_event_shift_x[MAX_EVENT_ID],g_event_shift_y[MAX_EVENT_ID];
static int g_event_through[MAX_EVENT_ID],armed=1,test_trigger=2,test_priority=1,test_supported=1;
static int vm_read_event(const MapState*m,int i,VmEventRecord*e){*e=(VmEventRecord){3,6,8};return 1;}
static int vm_active_page(const MapState*m,const VmEventRecord*e,VmPageRecord*p){*p=(VmPageRecord){armed?test_trigger:0,test_supported,test_priority,0,2};return 1;}
static int event_block_at(const MapState*m,int x,int y){return 0;}
'''
post='''int main(void){MapState m={24,1,(void*)1};VmEventRecord e;VmPageRecord p;
assert(vm_event_blocks_at(&m,6,8));assert(!vm_event_blocks_at(&m,5,8));
assert(vm_find_event_at(&m,6,8,2,&e,&p)&&e.event_id==3);
/* Left/up movement reserves one destination cell, never the truncated origin. */
g_routes[3]=(EventRoute){(void*)1,31,-1,0,0,0};g_event_shift_x[3]=-.03125f;
assert(vm_event_blocks_at(&m,5,8));assert(!vm_event_blocks_at(&m,6,8));
assert(vm_find_event_at(&m,5,8,2,&e,&p));assert(!vm_find_event_at(&m,5,7,2,&e,&p));
g_routes[3]=(EventRoute){(void*)1,31,0,-1,-1,0};g_event_shift_x[3]=-1;g_event_shift_y[3]=-.03125f;
assert(vm_find_event_at(&m,5,7,2,&e,&p));assert(!vm_find_event_at(&m,5,8,2,&e,&p));
armed=0;assert(!vm_find_event_at(&m,5,7,2,&e,&p));armed=1;
g_event_through[3]=1;assert(!vm_event_blocks_at(&m,5,7));g_event_through[3]=0;
/* The other chase map uses exactly the same single-cell contact. */
m.id=25;assert(vm_find_event_at(&m,5,7,2,&e,&p));
/* Same-priority door starts on a blocked front cell; floor events still
 * require entering their cell and unsupported pages cannot start. */
test_trigger=1;assert(vm_find_event_at(&m,5,7,-1,&e,&p));
test_priority=0;assert(!vm_find_event_at(&m,5,7,-1,&e,&p));
test_priority=1;test_supported=0;assert(!vm_find_event_at(&m,5,7,-1,&e,&p));
test_supported=1;test_trigger=2;assert(!vm_find_event_at(&m,5,7,-1,&e,&p));
return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
assert 'vm_run_event_at(&map,nx,ny,2' in s
assert 'vm_run_event_at(&map,nx,ny,-1' in s
assert 'if (is_chase_map(map.id) && !g_s003_paused)'in s
print('PASS: actual contact/block routines reserve one cell in both movement directions; inactive pages do not capture; player-front and moving-player checks retained')

"""Actual event selection with Map037 bytes, including its empty floor page."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static int vm_read_event(');b=s.index('/* A supported active VM page',a)
pre='''#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#define MAX_EVENT_ID 160
#define MAX_SWITCHES 1601
#define MAX_MAP_ID 139
#define VM_EVENT_BYTES 10
#define VM_PAGE_BYTES 20
typedef struct{int id,vm_event_count,vm_page_count;uint8_t*vm_bin;const uint8_t*vm_events,*vm_pages;}MapState;
typedef struct{int event_id,x,y,first_page,page_count;}VmEventRecord;
typedef struct{int cond_flags,trigger,priority,flags,switch1,switch2,self_index,supported,sprite_ref;uint32_t cmd_offset,cmd_size;}VmPageRecord;
typedef struct{void*records;int remaining,dx,dy;float start_x,start_y;}EventRoute;
static EventRoute g_routes[160];static float g_event_shift_x[160],g_event_shift_y[160];
static unsigned char g_switches[1601],g_self_switches[140][160],g_event_erased[160],g_event_through[160];
static uint16_t read_u16_le(const uint8_t*p){return p[0]|p[1]<<8;}
static uint32_t read_u32_le(const uint8_t*p){return read_u16_le(p)|read_u16_le(p+2)<<16;}
static int event_block_at(const MapState*m,int x,int y){return 0;}
'''
post='''int main(int argc,char**argv){uint8_t data[65536];FILE*f=fopen(argv[1],"rb");assert(f);size_t n=fread(data,1,sizeof(data),f);fclose(f);assert(n>20);
MapState m={37,read_u16_le(data+4),read_u16_le(data+6),data,data+20,data+20+read_u16_le(data+4)*10};VmEventRecord e;VmPageRecord p;
/* Standing on event4's empty floor page must not consume X. */
assert(!vm_find_event_at(&m,5,4,-2,&e,&p));
assert(vm_find_event_at(&m,5,3,-3,&e,&p)&&e.event_id==3&&p.cmd_size>1);
assert(!vm_find_event_at(&m,5,3,-2,&e,&p));
assert(!vm_find_event_at(&m,4,4,-2,&e,&p));
/* The normal-priority sheets still block, even when damaged page has no script. */
assert(vm_event_blocks_at(&m,5,3));g_switches[288]=1;
assert(vm_event_blocks_at(&m,5,3));assert(!vm_find_event_at(&m,5,3,-3,&e,&p));
g_switches[288]=0;assert(vm_find_event_at(&m,5,3,-3,&e,&p));return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e),str(r/'assets/map037_vm.bin')],check=True)
# Ensure the player action dispatcher applies the filters tested above.
a=s.index('/* RPG Maker checks the current cell for below-character action');b=s.index('lang = g_language;',a);dispatch=s[a:b]
assert '&map, fx, fy, -2, char_atlas' in dispatch and '&map, fx, fy, -3, char_atlas' in dispatch
print('PASS: actual Map037 current/front event selection, empty page rejection, intact interaction and unchanged collider')

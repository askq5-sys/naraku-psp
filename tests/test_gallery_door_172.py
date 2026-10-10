"""Execute runtime touch dispatch and cinematic alpha, including spent pages."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static int vm_find_event_at(');b=s.index('static int vm_event_blocks_except',a)
pre='''#include <assert.h>
#include "runtime/render_boundaries.h"
typedef struct{int id,w,vm_event_count;void*vm_bin;}MapState;
typedef struct{int event_id;}VmEventRecord;
typedef struct{int supported,cmd_size,trigger,priority;}VmPageRecord;
static int spent,door;
static int vm_read_event(const MapState*m,int i,VmEventRecord*e){e->event_id=door?2:m->id==67?5:3;return 1;}
static void vm_event_contact_cell(const MapState*m,const VmEventRecord*e,int*x,int*y){*x=door?8:m->id==67?4:6;*y=door?2:m->id==67?6:5;}
static int vm_active_page(const MapState*m,const VmEventRecord*e,VmPageRecord*p){*p=(VmPageRecord){1,spent?1:20,door?2:spent?0:1,door?1:0};return 1;}
'''
post='''int main(void){VmEventRecord e;VmPageRecord p;MapState m={67,17,1,(void*)1};
for(int x=1;x<16;x++)assert(vm_find_event_at(&m,x,6,1,&e,&p)&&e.event_id==5);
assert(!vm_find_event_at(&m,12,5,1,&e,&p));assert(!vm_find_event_at(&m,12,7,1,&e,&p));
assert(!vm_find_event_at(&m,12,6,0,&e,&p));assert(!vm_find_event_at(&m,0,6,1,&e,&p));
spent=1;assert(!vm_find_event_at(&m,12,6,1,&e,&p));spent=0;
m.id=68;assert(vm_find_event_at(&m,12,5,1,&e,&p));m.id=69;assert(!vm_find_event_at(&m,12,5,1,&e,&p));
assert(cinematic_player_opacity(94,18.5f*24,24)==255);
int previous=255;for(int i=0;i<=24;i++){int alpha=cinematic_player_opacity(94,18.5f*24+i,24);assert(alpha<=previous);previous=alpha;}assert(previous==0);
assert(cinematic_player_opacity(95,19.5f*24,24)==255);assert(cinematic_player_opacity(94,17.5f*24,24)==255);
door=1;spent=0;m.id=112;
assert(vm_find_event_at(&m,8,2,-3,&e,&p)&&e.event_id==2);
assert(vm_find_event_at(&m,8,2,-1,&e,&p));
assert(!vm_find_event_at(&m,8,2,-2,&e,&p));
assert(!vm_find_event_at(&m,7,2,-3,&e,&p));
return 0;}''' 
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+s[a:b]+post)
 subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-lm','-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: gallery Touch door responds to front action and blocked movement; current-cell action excludes it; spider and fade regression checks')

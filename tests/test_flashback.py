from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[1]
s=(root/'main.c').read_text();a=s.index('static int vm_cell_owns_transfer(');b=s.index('static int vm_touch_transfer_at',a)
pre='''#include <assert.h>
#include "runtime/player_animation.h"
typedef struct {int vm_bin,vm_event_count;} MapState;
typedef struct {int x,y;} VmEventRecord;
typedef struct {int supported;} VmPageRecord;
static int active=1,supported=1;
static int vm_read_event(const MapState*m,int i,VmEventRecord*e){e->x=7;e->y=5;return 1;}
static int vm_active_page(const MapState*m,const VmEventRecord*e,VmPageRecord*p){p->supported=supported;return active;}
'''
post='''int main(void){MapState m={1,1};PlayerAnimation a,b;int dx,dy;
assert(vm_cell_owns_transfer(&m,7,5)); /* empty page still suppresses old transfer */
assert(!vm_cell_owns_transfer(&m,8,5));supported=0;assert(!vm_cell_owns_transfer(&m,7,5));supported=1;active=0;assert(!vm_cell_owns_transfer(&m,7,5));m.vm_bin=0;assert(!vm_cell_owns_transfer(&m,7,5));
player_animation_reset(&a);player_animation_reset(&b);
for(int i=0;i<11;i++)player_animation_tick(&a,1,0,3,1,0);
assert(a.pattern==1);player_animation_tick(&a,1,0,3,1,0);assert(a.pattern==2);assert(b.pattern==1);
assert(player_route_delta(13,1,&dx,&dy)&&dx==1&&dy==0);
return 0;}'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'test.c';exe=Path(tmp)/'test';p.write_text(pre+s[a:b]+post)
 subprocess.run(['cc','-std=c99','-I',str(root),str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
print('PASS: empty-page transfer suppression, legacy fallback and independent NPC animation')

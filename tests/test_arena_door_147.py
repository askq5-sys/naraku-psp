"""Exercise native event-tile passage and the original panel opening timeline."""
from pathlib import Path
import re,struct,subprocess,tempfile,sys
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
mp=w.read_json(r.parent/'original/data/Map069.json');ts=w.read_json(r.parent/'original/data/Tilesets.json')[mp['tilesetId']]
vb=(r/'assets/map069_vm.bin').read_bytes();ne=struct.unpack_from('<H',vb,4)[0];pb=20+ne*10
assert struct.unpack_from('<I',vb,16)[0]&2
for i in range(ne):
 eid,_,_,first,np,_=struct.unpack_from('<HHHHBB',vb,20+i*10)
 for j,page in enumerate(mp['events'][eid]['pages']):
  meta=vb[pb+(first+j)*20]&248;tid=page['image']['tileId'];flag=ts['flags'][tid] if tid else 16
  expected=(8|((flag&15)<<4)) if tid and page['priorityType']==0 and not flag&16 else 0
  assert meta==expected,(eid,j,meta,expected)
# The control panel is an Action event; puzzle completion alone is not the
# door-opening command in the original. Its three Wait commands are 3 frames.
panel=mp['events'][12]['pages'][1];assert panel['trigger']==0
assert [c['parameters'][0] for c in panel['list'] if c['code']==230]==[3,3,3,5]
a=s.index('static int vm_read_event(');b=s.index('static int is_chase_enemy(',a);vm=s[a:b]
helper=(r/'runtime/event_tile_passage.h').read_text()
a=s.index('static uint8_t pass_mask_at(');b=s.index('static uint16_t action_event_at(',a);pass_fn=s[a:b]
a=s.index('        } else if (op == VM_OP_SWITCH) {');b=s.index('        } else if (op == VM_OP_SELF_SWITCH)',a);switch=s[a:b].split('{',1)[1]
defines='\n'.join(re.findall(r'^#define VM_OP_\w+ \d+',s,re.M))
pre=r'''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define MAX_EVENT_ID 160
#define MAX_MAP_ID 139
#define MAX_SWITCHES 1601
#define VM_EVENT_BYTES 10
#define VM_PAGE_BYTES 20
#define MAP_HEADER_BYTES 20
typedef struct{int id,w,h,vm_event_count,vm_page_count,vm_flags;uint8_t*vm_bin,*map_bin;const uint8_t*vm_events,*vm_pages,*vm_commands;size_t vm_command_size;}MapState;
typedef struct{int event_id,x,y,first_page,page_count;}VmEventRecord;
typedef struct{int cond_flags,trigger,priority,flags,switch1,switch2,self_index,supported,sprite_ref;uint32_t cmd_offset,cmd_size;}VmPageRecord;
static uint8_t g_switches[MAX_SWITCHES],g_self_switches[MAX_MAP_ID+1][MAX_EVENT_ID],g_event_erased[MAX_EVENT_ID],g_event_through[MAX_EVENT_ID];
static int g_event_active_page[MAX_EVENT_ID];
static uint16_t read_u16_le(const uint8_t*p){return p[0]|p[1]<<8;}
static uint32_t read_u32_le(const uint8_t*p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void reconcile_consumed_items(void){}
static void vm_event_contact_cell(const MapState*m,const VmEventRecord*ev,int*x,int*y){*x=ev->x;*y=ev->y;}
'''
post=r'''
static MapState m;static int frame,visual[3];
static VmPageRecord page(int id,int*local){VmEventRecord ev;VmPageRecord pg;int active;for(int i=0;i<m.vm_event_count;i++)if(vm_read_event(&m,i,&ev)&&ev.event_id==id){assert(vm_active_page_index(&m,&ev,&pg,&active));*local=active-ev.first_page;return pg;}assert(0);return (VmPageRecord){0};}
static void render_frame(void){int local;VmPageRecord pg=page(72,&local);assert(pg.sprite_ref==visual[local]);assert(pass_mask_at(&m,18,18)==9);if(frame<3)assert(local==1);else if(frame<6)assert(local==2);else assert(local==3);frame++;}
static void open_panel(void){int local;VmPageRecord record=page(12,&local);assert(local==1&&record.trigger==0);VmPageRecord*pg=&record;const uint8_t*base=m.vm_commands+pg->cmd_offset,*p=base,*end=base+pg->cmd_size;while(p<end){int op=*p++;if(op==VM_OP_END)break;if(op==VM_OP_SE){p+=5;}
'''
code=pre+defines+'\n'+vm+helper+pass_fn+post+'else if(op==VM_OP_SWITCH){'+switch+'''}else if(op==VM_OP_WAIT){int frames=read_u16_le(p);p+=2;while(frames--)render_frame();}else if(op==VM_OP_SHAKE){int frames=read_u16_le(p+2);int waiting=p[4];p+=5;if(waiting)while(frames--)render_frame();}else assert(0);}}
'''
code+=r'''
static uint8_t*read_file(const char*path){FILE*f=fopen(path,"rb");assert(f);fseek(f,0,SEEK_END);long size=ftell(f);rewind(f);uint8_t*b=malloc(size);assert(fread(b,1,size,f)==size);fclose(f);return b;}
int main(int argc,char**argv){assert(argc==3);m.vm_bin=read_file(argv[1]);m.map_bin=read_file(argv[2]);m.id=69;m.w=40;m.h=40;m.vm_flags=read_u32_le(m.vm_bin+16);m.vm_event_count=read_u16_le(m.vm_bin+4);m.vm_page_count=read_u16_le(m.vm_bin+6);m.vm_events=m.vm_bin+20;m.vm_pages=m.vm_events+m.vm_event_count*10;m.vm_commands=m.vm_bin+read_u32_le(m.vm_bin+8);
for(int i=0;i<MAX_EVENT_ID;i++)g_event_active_page[i]=-1;
int local;VmPageRecord pg=page(72,&local);assert(local==0&&pg.sprite_ref&&pass_mask_at(&m,18,18)==0);
for(int i=0;i<9;i++)assert(pass_mask_at(&m,17+i%3,20+i/3)==15);
/* Retain baseline behavior for old resources without metadata. */
m.vm_flags&=~2;assert(pass_mask_at(&m,18,18)==9);m.vm_flags|=2;
g_switches[720]=1;pg=page(12,&local);assert(local==1&&pass_mask_at(&m,18,18)==0&&!g_switches[717]);
/* Capture the three distinct opening sprite refs, then run the real switches. */
g_switches[715]=1;pg=page(72,&local);assert(local==1);visual[1]=pg.sprite_ref;
g_switches[716]=1;pg=page(72,&local);assert(local==2);visual[2]=pg.sprite_ref;
g_switches[717]=1;pg=page(72,&local);assert(local==3);visual[3]=pg.sprite_ref;assert(!visual[3]&&visual[1]&&visual[2]&&visual[1]!=visual[2]);
g_switches[715]=g_switches[716]=g_switches[717]=0;
open_panel();assert(frame==20&&g_switches[738]&&g_switches[717]);pg=page(12,&local);assert(local==2&&pg.cmd_size==1);assert(pass_mask_at(&m,18,18)==9);
/* A restored save immediately reflects its stored door state. */
g_switches[715]=g_switches[716]=g_switches[717]=0;assert(pass_mask_at(&m,18,18)==0);g_switches[717]=1;assert(pass_mask_at(&m,18,18)==9);
free(m.vm_bin);free(m.map_bin);return 0;}
'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(code)
 subprocess.run(['cc','-std=c99','-Wall','-Wno-unused-function',str(p),'-o',str(e)],check=True)
 subprocess.run([str(e),str(r/'assets/map069_vm.bin'),str(r/'assets/map069.bin')],check=True)
print('PASS: original tile passage metadata, closed door before/after puzzle, all three opening stages at original timings, permanent opening, restored state and legacy-resource compatibility')

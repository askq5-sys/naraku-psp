from pathlib import Path
import json, struct, sys, re, subprocess, tempfile
from PIL import Image

r=Path(__file__).resolve().parents[1];G=r.parent/'original';O=r/'assets'
sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
texts=w.read_json(G/'data/I18NTexts.json');key=bytes.fromhex(w.read_json(G/'data/System.json')['encryptionKey'])
w.PICTURE_IDS=w.read_json(O/'picture_v050_manifest.json');audio=w.read_json(O/'audio_exact_v079.json')
w.EXACT_SE_IDS={w.audio_key(x):x['id'] for x in audio if x['kind']=='se'}
w.EXACT_BGM_IDS={w.audio_key(x):x['id'] for x in audio if x['kind']=='bgm'}
pages=0;parallel_codes=set();route_count=0
route_header=(r/'runtime/factory_routes.h').read_text()
for mid in range(48,74):
    data=w.adapt_stage_142(w.read_json(G/'data'/f'Map{mid:03}.json'),mid);b=(O/f'map{mid:03}_vm.bin').read_bytes()
    _,ne,np,blob,_,flags=struct.unpack_from('<4sHHIII',b);base=20+ne*10
    mb=(O/f'map{mid:03}.bin').read_bytes();mw,mh=data['width'],data['height'];tileset=w.read_json(G/'data/Tilesets.json')[data['tilesetId']]
    for y in range(mh):
        for x in range(mw):assert mb[20+mw*mh*8+y*mw+x]==w.build_pass_mask(data,tileset['flags'],x,y)
    eb=(O/f'map{mid:03}_events.bin').read_bytes();_,_,_,nt,ns,_=struct.unpack_from('<4s5H',eb);sb=14+mw*mh*5+nt*20
    for i in range(ne):
        eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10);event=data['events'][eid]
        assert (x,y,n)==(event['x'],event['y'],len(event['pages']))
        for j,page in enumerate(event['pages']):
            pg=struct.unpack_from('<BBBBHHBBHII',b,base+(first+j)*20);ref,off,length=pg[8:]
            assert pg[7] and w.page_vm_supported(page)
            assert b[blob+off:blob+off+length]==w.compile_vm_commands(page,texts,preserve_message_background=mid in (62,67,68,69,72))
            assert (pg[0]&7,pg[4],pg[5],pg[6])==w.vm_page_conditions(page)
            assert (pg[1],pg[2],bool(pg[3]&1))==(page['trigger'],page['priorityType'],page['through'])
            if ref:
                rec=struct.unpack_from('<6H2BH',eb,sb+(ref-1)*16);sx,sy,sw,sh=rec[2:6];bits=rec[7]
                assert rec[-1]==eid
                assert (O/f'map{mid:03}_event_atlas{1 if sx>>12 else ""}.rgba8888').stat().st_size==1048576
                width=sw*(2 if mid==72 and eid==2 and bits&128 else 6 if bits&128 and bits&64 else 2 if bits&64 else 3 if bits&2 else 1)
                height=sh*(2 if bits&64 or (mid==72 and eid==2 and bits&128) else 1)
                assert (sx&4095)+width<=512 and sy+height<=512
            if page['trigger']==4:parallel_codes.update(c['code'] for c in page['list'])
            if page['moveType']==3:
                route=page['moveRoute'];cmds=[c for c in route['list'] if c['code']]
                raw=b''.join(struct.pack('<Bhh',c['code'],*(list(c.get('parameters')or[])+[0,0])[:2]) for c in cmds)
                name=f'factory_route_{mid}_{eid}_{j}'
                found=re.search(name+r'\[\] = \{([^}]+)\}',route_header);assert found
                assert bytes(map(int,found[1].split(',')))==raw;route_count+=1
            for c in page['list']:
                if c['code']==231 and c['parameters'][1]!='A1':assert (O/f"pic_{w.PICTURE_IDS[c['parameters'][1]]:03}.p44").is_file()
                if c['code']in(241,250) and c['parameters'][0]['name']:
                    kind='bgm' if c['code']==241 else 'se';ids=w.EXACT_BGM_IDS if kind=='bgm' else w.EXACT_SE_IDS
                    assert (O/f"{kind}_exact_{ids[w.audio_key(c['parameters'][0])]}.pcm").stat().st_size>0
            pages+=1
assert parallel_codes<={118,0,112,413,121,123,230,250,205,505,225,135,284,101,401,111,411,412,126}
assert (O/'parallax_chain.rgba8888').stat().st_size==1048576
assert w.localized_string(r'\I18N[1308]',texts,'en_US')=='Obtained a Green Key.'
assert w.localized_string('Destroy with axe',texts,'en_US')==r'Destroy with \c[8]Axe\c[0]'
assert w.localized_string('Destroy with cleaver',texts,'en_US')==r'Destroy with \c[18]Cleaver\c[0]'
assert w.localized_string('The axe broke.',texts,'en_US')==r'The \c[8]Axe\c[0] broke.'
print(f'PASS: {pages} original stage pages, {route_count} autonomous routes, collisions, atlas bounds, all picture/audio dependencies')

# Run the real nonblocking scheduler against the actual packed event resources.
s=(r/'main.c').read_text();a=s.index('static int vm_read_event(');b=s.index('static int vm_active_page(',a)
defines='\n'.join(re.findall(r'^#define VM_OP_\w+ \d+',s,re.M))
pre=r'''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define MAX_EVENT_ID 160
#define MAX_MAP_ID 139
#define MAX_SWITCHES 1601
#define MAX_ITEMS 256
#define VM_EVENT_BYTES 10
#define VM_PAGE_BYTES 20
typedef struct{int id,vm_event_count,vm_page_count;uint8_t*vm_bin;const uint8_t*vm_events,*vm_pages,*vm_commands;size_t vm_command_size;}MapState;
typedef struct{int event_id,x,y,first_page,page_count;}VmEventRecord;
typedef struct{int cond_flags,trigger,priority,flags,switch1,switch2,self_index,supported,sprite_ref;uint32_t cmd_offset,cmd_size;}VmPageRecord;
static uint8_t g_switches[MAX_SWITCHES],g_self_switches[MAX_MAP_ID+1][MAX_EVENT_ID],g_event_erased[MAX_EVENT_ID];
static struct{void*records;}g_routes[MAX_EVENT_ID];
static int16_t g_items[MAX_ITEMS];
static float g_screen_shake_x,g_stage_parallax_y;static int g_stage_parallax_scrolling,g_save_enabled,g_language,g_runtime_message_transparent,frame,beep_frame=-1;
static uint16_t read_u16_le(const uint8_t*p){return p[0]|p[1]<<8;}
static uint32_t read_u32_le(const uint8_t*p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void play_vm_se_params(int id,int v,int pitch,int pan){beep_frame=frame;}
static int start_event_route(const MapState*m,int id,const uint8_t*p,int n,int flags){g_routes[id].records=(void*)1;return 1;}
'''
a_shake=s.index('        } else if (op == VM_OP_SHAKE) {');b_shake=s.index('        } else if (op == VM_OP_BGM) {',a_shake)
shake_body=s[a_shake:b_shake].split('{',1)[1]
shake_code=r'''
static void vm_render_frame(const MapState*m,void*a,int x,int y,int d,int b,int f){tick_stage_parallel(m);frame++;}
static void primary_shake(MapState*m,int waiting){uint8_t bytes[]={2,9,5,0,0};bytes[4]=waiting;const uint8_t*p=bytes,*end=bytes+5;int x=0,y=0,d=0,*tile_x=&x,*tile_y=&y,*direction_row=&d;void*char_atlas=NULL;while(1){
'''+shake_body+'break;}}\n'
pump_start=s.index('static void vm_pump_stage_message(const MapState *m, void *char_atlas, int x, int y, int direction)\n{');pump_end=s.index('static int vm_wait_choices(',pump_start)
pump_code='static int messages;\nstatic void vm_wait_text(const MapState*m,void*a,int x,int y,int d,const char*s,size_t sl,const char*t,size_t tl,int c){assert(tl>0&&g_stage_parallel[9].text_blocked);messages++;for(int i=0;i<3;i++)tick_stage_parallel(m);assert(g_stage_parallel[9].text_blocked&&!g_switches[792]);}\n'+s[pump_start:pump_end]
post=r'''
static MapState m;
static void load(const char*dir,int mid){char path[1024];free(m.vm_bin);memset(&m,0,sizeof(m));memset(g_switches,0,sizeof(g_switches));memset(g_self_switches,0,sizeof(g_self_switches));memset(g_routes,0,sizeof(g_routes));clear_stage_parallel();frame=0;snprintf(path,sizeof(path),"%s/map%03d_vm.bin",dir,mid);FILE*f=fopen(path,"rb");assert(f);fseek(f,0,SEEK_END);long size=ftell(f);rewind(f);m.vm_bin=malloc(size);assert(fread(m.vm_bin,1,size,f)==(size_t)size);fclose(f);m.id=mid;m.vm_event_count=read_u16_le(m.vm_bin+4);m.vm_page_count=read_u16_le(m.vm_bin+6);m.vm_events=m.vm_bin+20;m.vm_pages=m.vm_events+m.vm_event_count*10;m.vm_commands=m.vm_bin+read_u32_le(m.vm_bin+8);m.vm_command_size=size-(m.vm_commands-m.vm_bin);}
static void step(void){tick_stage_parallel(&m);frame++;}
int main(int argc,char**argv){assert(argc==2);
load(argv[1],48);step();assert(g_switches[421]);step();assert(g_switches[421]);step();assert(!g_switches[421]);step();step();assert(g_switches[421]);g_switches[432]=1;step();assert(!g_switches[421]&&g_switches[423]);g_switches[433]=1;step();assert(!g_switches[423]&&!g_switches[424]&&g_switches[425]);
load(argv[1],48);g_switches[441]=1;while(frame<70)step();assert(!g_switches[442]);step();assert(!g_switches[441]&&g_switches[442]&&beep_frame==70);
// Map048 timeout must clear all original reset switches without another action.
g_switches[408]=g_switches[416]=g_switches[424]=g_switches[432]=1;
g_switches[390]=g_switches[444]=1;g_items[55]=1;
step();assert(!g_switches[442]&&!g_switches[441]);
for(int i=401;i<=442;i++){if(i==409||i==415||i==422||i==431)continue;assert(!g_switches[i]);}
assert(g_switches[390]&&g_switches[444]&&g_items[55]);
g_switches[441]=1;int retry48=frame;while(frame-retry48<70)step();assert(!g_switches[442]);step();assert(g_switches[442]);step();assert(!g_switches[442]);
load(argv[1],48);beep_frame=-1;g_switches[441]=1;step();g_switches[441]=0;g_switches[416]=1;while(frame<100)step();assert(g_switches[416]&&!g_switches[442]&&beep_frame==-1);
load(argv[1],49);g_switches[459]=1;while(frame<200)step();assert(!g_switches[460]);step();assert(g_switches[460]&&beep_frame==200);
g_switches[472]=g_switches[492]=g_switches[512]=g_switches[532]=g_switches[541]=g_switches[552]=g_switches[561]=g_switches[568]=g_switches[570]=1;g_items[55]=1;reset_factory_checkpoint_tail(48,16,3);assert(g_switches[541]);step();assert(!g_switches[459]&&!g_switches[460]);for(int i=461;i<=472;i++)assert(!g_switches[i]);for(int i=481;i<=492;i++)assert(!g_switches[i]);for(int i=501;i<=512;i++)assert(!g_switches[i]);for(int i=521;i<=532;i++)assert(!g_switches[i]);for(int i=541;i<=552;i++)assert(!g_switches[i]);assert(g_switches[561]);assert(!g_switches[566]&&!g_switches[568]&&!g_switches[569]&&!g_switches[570]);assert(g_items[55]==1);VmEventRecord checkpoint;VmPageRecord cp;int active;assert(vm_read_event(&m,23,&checkpoint)&&checkpoint.event_id==24);assert(vm_active_page_index(&m,&checkpoint,&cp,&active)&&active==checkpoint.first_page);
// A fresh attempt starts a fresh timer; completed attempts must not reset.
load(argv[1],49);g_switches[459]=g_switches[532]=g_switches[562]=g_switches[565]=1;
g_switches[541]=g_switches[552]=g_switches[566]=g_switches[568]=g_switches[569]=g_switches[570]=1;
while(frame<200){step();}
step();assert(g_switches[460]);step();
assert(g_switches[562]&&g_switches[565]&&!g_switches[561]&&!g_switches[567]);
assert(!g_switches[532]&&!g_switches[541]&&!g_switches[552]&&!g_switches[566]&&!g_switches[568]&&!g_switches[569]&&!g_switches[570]);
VmEventRecord killer;VmPageRecord kp;int ka;assert(vm_read_event(&m,27,&killer)&&killer.event_id==28);
assert(vm_active_page_index(&m,&killer,&kp,&ka)&&ka==killer.first_page+1&&kp.sprite_ref);
g_switches[561]=g_switches[563]=g_switches[564]=g_switches[567]=g_switches[460]=1;
reset_factory_checkpoint_tail(49,16,3);assert(g_switches[561]&&g_switches[562]&&g_switches[563]&&g_switches[564]&&g_switches[565]&&g_switches[567]);
load(argv[1],49);g_switches[459]=g_switches[492]=1;while(frame<200)step();assert(g_switches[492]);step();assert(g_switches[460]);step();assert(!g_switches[492]&&!g_switches[459]&&!g_switches[460]);g_switches[459]=1;int retry=frame;while(frame-retry<200)step();assert(!g_switches[460]);step();assert(g_switches[460]);step();assert(!g_switches[460]);
load(argv[1],49);beep_frame=-1;g_switches[459]=1;step();g_switches[459]=0;g_switches[492]=1;while(frame<250)step();assert(!g_switches[460]&&g_switches[492]&&beep_frame==-1);
load(argv[1],50);while(frame<100)step();assert(!g_switches[572]);step();assert(g_switches[572]&&(g_self_switches[50][11]&1));
load(argv[1],51);while(frame<50)step();assert(!g_switches[573]);step();assert(g_switches[573]&&(g_self_switches[51][5]&1));
load(argv[1],52);g_switches[581]=1;while(frame<31)step();assert(g_routes[5].records);int pc=g_stage_parallel[7].pc;for(int i=0;i<60;i++)step();assert(g_stage_parallel[7].pc==(uint32_t)pc);g_routes[5].records=NULL;step();assert(g_stage_parallel[7].pc!=(uint32_t)pc);
load(argv[1],53);g_switches[593]=1;while(frame<120)step();assert(!g_switches[586]);step();assert(g_switches[586]);while(frame<840)step();assert(!g_switches[592]);step();assert(g_switches[592]);
load(argv[1],54);g_stage_parallax_scrolling=1;while(frame<640)step();assert(g_stage_parallax_scrolling&&!g_switches[609]);step();assert(!g_stage_parallax_scrolling&&g_switches[609]&&!g_save_enabled);
clear_stage_parallel();for(int i=0;i<MAX_EVENT_ID;i++)assert(!g_stage_parallel[i].page&&!g_stage_parallel[i].wait);
load(argv[1],55);primary_shake(&m,0);assert(frame==0&&g_stage_shake_frames==5);step();assert(g_stage_shake_frames==4&&g_screen_shake_x!=0);while(frame<5)step();assert(!g_stage_shake_frames&&g_screen_shake_x==0);primary_shake(&m,1);assert(frame==10&&g_screen_shake_x==0);
load(argv[1],67);g_switches[832]=1;while(frame<180)step();assert(!g_switches[831]);step();assert(g_switches[831]&&!g_switches[832]);
load(argv[1],68);g_switches[832]=1;step();g_switches[832]=0;while(frame<200)step();assert(!g_switches[831]);
load(argv[1],69);g_switches[733]=1;
while(frame<1200){step();}assert(!g_switches[727]);step();assert(g_switches[727]&&g_routes[54].records&&g_routes[62].records);
while(frame<2400){step();}step();assert(g_switches[728]&&!g_switches[729]);
while(frame<3600){step();}step();assert(g_switches[729]);
while(frame<3650){step();}step();assert(g_switches[730]);
while(frame<3750){step();}step();assert(g_switches[731]&&g_switches[736]&&!g_switches[733]);
load(argv[1],69);g_switches[733]=1;for(int i=0;i<200;i++)step();g_switches[733]=0;for(int i=0;i<4000;i++)step();assert(!g_switches[727]&&!g_switches[736]&&!g_stage_parallel[68].page);
load(argv[1],72);g_switches[975]=1;for(int i=0;i<50;i++)step();assert(beep_frame>=32);g_switches[975]=0;int old_beep=beep_frame;for(int i=0;i<50;i++)step();assert(beep_frame==old_beep);
load(argv[1],59);g_items[55]=1;while(frame<300)step();assert(g_items[55]==1);step();assert(g_items[55]==1&&beep_frame==300);while(frame<360)step();step();assert(g_items[55]==0&&beep_frame==360);while(frame<420)step();assert(!g_stage_message_event);step();assert(g_stage_message_event==9&&g_stage_parallel[9].text_blocked);int held=g_stage_parallel[9].pc;for(int i=0;i<10;i++)step();assert(g_stage_parallel[9].pc==(uint32_t)held&&!g_switches[792]);vm_pump_stage_message(&m,NULL,8,7,0);assert(messages==1&&!g_stage_message_event&&!g_stage_parallel[9].text_blocked);step();assert(g_switches[792]);g_stage_parallax_scrolling=1;while(frame<640)step();step();assert(g_switches[662]&&!g_stage_parallax_scrolling&&!g_save_enabled);
load(argv[1],59);g_items[55]=0;while(frame<301)step();assert(g_switches[792]&&!g_stage_message_event&&messages==1);
free(m.vm_bin);return 0;}
'''
with tempfile.TemporaryDirectory()as td:
    p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+defines+'\n'+s[a:b]+'\n#include "runtime/factory_puzzle.h"\n#include "runtime/stage_parallel.h"\n'+shake_code+pump_code+post)
    subprocess.run(['cc','-std=c99','-Wall','-Wno-unused-function','-I',str(r),str(p),'-o',str(e)],check=True)
    subprocess.run([str(e),str(O)],check=True)
print('PASS: actual C parallel loops, page cancellation, 70/200-frame puzzle timeouts, one-shot self-switch timers, route waits, 840-frame door timeline and lift stop')

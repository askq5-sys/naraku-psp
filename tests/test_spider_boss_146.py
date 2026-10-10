from pathlib import Path
import runpy,subprocess,tempfile,struct,json,sys
from PIL import Image,ImageChops
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
n=runpy.run_path(str(r/'tests/test_s003_runtime.py'))
a=s.index('static int event_route_can_step(');b=s.index('static void tick_player_route(',a)
pre=n['pre']+"\nstatic int trace_calls;\nstatic FILE*trace_open(const char*a,const char*b){trace_calls++;return NULL;}\n#define fopen trace_open\n"
post=r'''int main(void){MapState m={67,1};blocked_axis=1;
for(int id=1;id<=4;id++) {EventRoute*r=&g_routes[id];r->records=calloc(1,5);r->records[0]=4;r->count=1;r->base_x=6;r->base_y=8;g_event_move_speed[id]=2;}
for(int f=0;f<10000;f++)tick_event_routes(&m);
assert(!trace_calls);for(int id=1;id<=4;id++) {assert(g_routes[id].records&&g_routes[id].index==0&&g_event_shift_y[id]==0);g_event_through[id]=1;}
for(int f=0;f<140;f++)tick_event_routes(&m);
for(int id=1;id<=4;id++)assert(!g_routes[id].records&&g_event_shift_y[id]==-1);
return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+n['globals_']+s[a:b]+post)
 subprocess.run(['cc','-std=c99','-Wno-unused-function','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
# Native giant-spider gait and both boss sides exactly match the source pixels.
sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
G=r.parent/'original';O=r/'assets';key=bytes.fromhex(w.read_json(G/'data/System.json')['encryptionKey'])
for mid,name in [(69,'!お肉ラスボス'),(72,'!デカ蜘蛛キャラチップ')]:
 mp=w.read_json(G/'data'/f'Map{mid:03}.json');eb=(O/f'map{mid:03}_events.bin').read_bytes();vb=(O/f'map{mid:03}_vm.bin').read_bytes()
 ne,_,_=struct.unpack_from('<HHI',vb,4);mw,mh=mp['width'],mp['height'];nt=struct.unpack_from('<H',eb,8)[0];sb=14+mw*mh*5+nt*20;pb=20+ne*10
 source=w.load_encrypted_png(w.resolve_named_file(G/'img/characters',name),key);seen=set()
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',vb,20+i*10)
  for j,pg in enumerate(mp['events'][eid]['pages']):
   if pg['image']['characterName']!=name:continue
   ref=struct.unpack_from('<H',vb,pb+(first+j)*20+10)[0];rec=struct.unpack_from('<6H2BH',eb,sb+(ref-1)*16);sx,sy,sw,sh=rec[2:6];flags=rec[7]
   assert flags&4;atlas=Image.frombytes('RGBA',(512,512),(O/f'map{mid:03}_event_atlas{1 if sx>>12 else ""}.rgba8888').read_bytes());sx&=4095
   img=pg['image'];patterns=range(3)if mid==72 and flags&128 else [img['pattern']]
   for pat in patterns:
    target=w.extract_character_frame(source,name,img['characterIndex'],img['direction'],pat)
    xx=sx+(pat%2)*sw if mid==72 and flags&128 else sx;yy=sy+(pat//2)*sh if mid==72 and flags&128 else sy
    expected=Image.new("RGBA",target.size);expected.alpha_composite(target)
    assert target.size==(sw,sh) and atlas.crop((xx,yy,xx+sw,yy+sh)).tobytes()==expected.tobytes()
    seen.add((img['direction'],pat))
 assert len(seen)==(4 if mid==72 else 2),seen
# Exhaustively execute the packed plate pages using the actual C switch/branch bodies.
ops={}
for op in ('VM_OP_SWITCH','VM_OP_COND_SWITCH','VM_OP_JUMP'):
 import re
 match=re.search(r'        } else if \(op == '+op+r'\) \{',s)
 a=match.end();b=s.index('        } else if ',a);ops[op]=s[a:b]
pre=r'''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#define MAX_SWITCHES 1601
static uint8_t g_switches[MAX_SWITCHES];
static void reconcile_consumed_items(void){}
static uint16_t read_u16_le(const uint8_t*p){return p[0]|p[1]<<8;}
static uint32_t read_u32_le(const uint8_t*p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
typedef struct{uint32_t cmd_size;}Page;
static void execute(const uint8_t*base,Page*pg){const uint8_t*p=base,*end=base+pg->cmd_size;int budget=1000;while(p<end&&budget--){int op=*p++;
if(op==0)break;
if(op==6){assert(end-p>=5);p+=5;}
'''
code=pre
for op,num in [('VM_OP_SWITCH',2),('VM_OP_COND_SWITCH',16),('VM_OP_JUMP',20)]:
 code+='else if(op=='+str(num)+'){'+ops[op]+'}'
code+='else {assert(0);}}assert(budget>0);}'
post=r'''int main(int argc,char**argv){FILE*f=fopen(argv[1],"rb");assert(f);fseek(f,0,SEEK_END);long size=ftell(f);rewind(f);uint8_t*raw=malloc(size);assert(fread(raw,1,size,f)==size);fclose(f);int ne=read_u16_le(raw+4);uint8_t*pages=raw+20+ne*10;uint8_t*blob=raw+read_u32_le(raw+8);
for(int mask=0;mask<512;mask++)for(int id=3;id<=11;id++) {memset(g_switches,0,sizeof(g_switches));int k=id-3;for(int j=0;j<9;j++)g_switches[701+j]=(mask>>j)&1;if(g_switches[701+k])continue;
int expected=mask|(1<<k);int x=k%3,y=k/3;if(x>0)expected^=1<<(k-1);if(x<2)expected^=1<<(k+1);if(y>0)expected^=1<<(k-3);if(y<2)expected^=1<<(k+3);
uint8_t*ev=NULL;for(int e=0;e<ne;e++)if(read_u16_le(raw+20+e*10)==id)ev=raw+20+e*10;assert(ev);uint8_t*page=pages+20*read_u16_le(ev+6);Page pg={read_u32_le(page+16)};execute(blob+read_u32_le(page+12),&pg);
int actual=0;for(int j=0;j<9;j++)actual|=!!g_switches[701+j]<<j;assert(actual==expected);assert(!!g_switches[720]==(expected==511));}
free(raw);return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(code+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e),str(O/'map069_vm.bin')],check=True)
print('PASS: 40,000 blocked-spider updates with zero storage writes, movement recovery; exact native boss/spider poses; all 2,304 valid plate transitions and unlock conditions')

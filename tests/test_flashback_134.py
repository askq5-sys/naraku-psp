from pathlib import Path
import json,re,subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'main.c').read_text()
a=s.index('static char *strip_message_font_controls(');b=s.index('static void vm_pump_stage_message(const MapState *m, void *char_atlas, int x, int y, int direction)\n{',a)
pre=r'''#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#define MESSAGE_BOX_W 260
typedef struct {int id;} MapState;
static int g_language=0,pages,total;
static unsigned char font[65536];static size_t font_size;
static const uint8_t *font_find_glyph(uint32_t cp){for(size_t j=12;j+8<=font_size;j+=8){uint32_t c=font[j]|font[j+1]<<8|font[j+2]<<16|font[j+3]<<24;if(c==cp)return font+j;}return NULL;}
static uint32_t utf8_next_cp(const char **p,const char *end){unsigned char c=*(*p)++;if(c<128)return c;int n=c<224?1:c<240?2:3;uint32_t v=c&((1<<(6-n))-1);while(n--&&*p<end)v=(v<<6)|(*(*p)++&63);return v;}
static void vm_wait_text_page(const MapState*m,void*a,int x,int y,int d,const char*sp,size_t sl,const char*t,size_t len,int next){
int lines=1,width=0;const char*p=t,*end=t+len;pages++;
while(p<end){if(end-p>=3&&p[0]=='\\'&&(p[1]=='c'||p[1]=='C')&&p[2]=='['){const char*q=p+3;while(q<end&&*q!=']')q++;if(q<end){p=q+1;continue;}}uint32_t c=utf8_next_cp(&p,end);if(c=='\n'){if(width>242){fprintf(stderr,"overflow %d: %.*s\n",width,(int)len,t);}assert(width<=242);width=0;lines++;continue;}const uint8_t*r=font_find_glyph(c);width+=r?(int)(r[7]*.55f):5;if(c!=' '&&c!='\r'&&c!='\t')total++;}if(width>242){fprintf(stderr,"overflow %d: %.*s\n",width,(int)len,t);}assert(width<=242&&lines<=3);}
'''.replace("c=='\\n'","c=='\n'").replace("c!='\\r'","c!='\r'").replace("c!='\\t'","c!='\t'")
# Correct the C escape literals without converting them to actual line breaks.
pre=pre.replace("c=='\n'", "c=='\\n'").replace("c!='\r'", "c!='\\r'").replace("c!='\t'", "c!='\\t'")
texts=json.load(open(root.parent/'original/data/I18NTexts.json'));m=json.load(open(root.parent/'original/data/Map039.json'));cases=[]
for ev in m['events']:
 if not ev:continue
 for pg in ev['pages']:
  buf=[]
  for cmd in pg['list']:
   if cmd['code']==401:
    val=cmd['parameters'][0];val=re.sub(r'\\I18N\[(\d+)\]',lambda match:texts[int(match[1])]['en_US'],val);buf.append(val)
   elif buf:cases.append('\n'.join(buf));buf=[]
post='int main(int argc,char**argv){FILE*f=fopen(argv[1],"rb");assert(f);font_size=fread(font,1,sizeof(font),f);fclose(f);MapState m={12};'
for t in cases:
 visible=re.sub(r'\\(?:[cC]|[fF][sS])\[\d+\]', '', t);expected=sum(not c.isspace()for c in visible)
 post+='pages=0;total=0;vm_wait_text(&m,NULL,0,0,0,"Emma",4,'+json.dumps(t,ensure_ascii=False)+','+str(len(t.encode()))+',0);assert(total=='+str(expected)+');assert(pages==1);'
post+='return 0;}'
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc',str(p),'-o',str(e)],check=True);subprocess.run([str(e),str(root/'assets/font_map.bin')],check=True)
print(f'PASS: {len(cases)} factory flashback messages fit one 3-row window without font controls or text loss')

# Scene 47's original autorun must compile in full, including direction lock.
import struct
sys=__import__('sys');sys.path.insert(0,str(root/'tools'));import prepare_world_v060 as w
O=root/'assets';G=root.parent/'original';w.PICTURE_IDS=w.read_json(O/'picture_v050_manifest.json');audio=w.read_json(O/'audio_exact_v079.json');w.EXACT_SE_IDS={w.audio_key(x):x['id'] for x in audio if x['kind']=='se'};w.EXACT_BGM_IDS={w.audio_key(x):x['id'] for x in audio if x['kind']=='bgm'}
for mid in (46,47):
 data=w.read_json(G/'data'/f'Map{mid:03}.json');b=(O/f'map{mid:03}_vm.bin').read_bytes();_,ne,np,blob,_,flags=struct.unpack_from('<4sHHIII',b);base=20+ne*10
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10)
  for j,page in enumerate(data['events'][eid]['pages']):
   pg=struct.unpack_from('<BBBBHHBBHII',b,base+(first+j)*20);assert pg[7] and w.page_vm_supported(page)
   ref,off,length=pg[8:];assert b[blob+off:blob+off+length]==w.compile_vm_commands(page,texts)
   for cmd in page['list']:
    if cmd['code']==231 and cmd['parameters'][1]!='A1':assert(O/f"pic_{w.PICTURE_IDS[cmd['parameters'][1]]:03}.p44").is_file()
    if cmd['code']in(241,250):
     kind='bgm' if cmd['code']==241 else 'se';ids=w.EXACT_BGM_IDS if kind=='bgm' else w.EXACT_SE_IDS;assert(O/f"{kind}_exact_{ids[w.audio_key(cmd['parameters'][0])]}.pcm").stat().st_size>0
assert (O/'map047_event_atlas1.rgba8888').stat().st_size==1048576
assert w.localized_string('Also... I brought a \\c[18]cleaver\\c[0] for',texts,'en_US')=='Also... I brought a \\c[18]Cleaver\\c[0] for'
assert all(line in (root/'runtime/factory_routes.h').read_text() for line in (root.parent/'github_latest/menu133/runtime/factory_routes.h').read_text().splitlines() if line.startswith('static const uint8_t') or line.startswith('{'))
print('PASS: complete original elevator flashback pages, portraits/audio, Cleaver color/case; barricade AI unchanged')

# Exercise direction lock/unlock and walking in the actual C scheduler.
import runpy
n=runpy.run_path(str(root/'tests/test_s003_runtime.py'));pre=n['pre'];glob=n['globals_']
a=(root/'main.c').read_text().index('static int event_route_can_step(');b=(root/'main.c').read_text().index('static void tick_player_route(',a)
post=r'''int main(void){MapState m={47,1};uint8_t route[]={35,0,0,0,0,3,0,0,0,0,36,0,0,0,0,16,0,0,0,0};first=0;active=0;assert(start_event_route(&m,3,route,4,0));int initial=g_event_direction[3];tick_event_routes(&m);assert(g_event_direction_fix[3]&&g_event_direction[3]==initial);int moving=0;for(int i=0;i<100;++i){tick_event_routes(&m);if(g_event_animation[3].pattern!=1)moving=1;}assert(!g_routes[3].records&&!g_event_direction_fix[3]&&g_event_direction[3]==0&&moving);return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+glob+(root/'main.c').read_text()[a:b]+post);subprocess.run(['cc','-std=c99','-I',str(root),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: actual C elevator actor direction lock, animated walking and unlock')

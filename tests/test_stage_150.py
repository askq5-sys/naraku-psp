"""Audit original elevator/surface/Ending 2 resources and execute lift scheduler."""
from pathlib import Path
import ast,json,re,struct,subprocess,sys,tempfile
from PIL import Image
r=Path(__file__).resolve().parents[1];G=r.parent/'original';O=r/'assets'
sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
texts=w.read_json(G/'data/I18NTexts.json');key=bytes.fromhex(w.read_json(G/'data/System.json')['encryptionKey'])
w.PICTURE_IDS=w.read_json(O/'picture_v050_manifest.json');audio=w.read_json(O/'audio_exact_v079.json')
w.EXACT_SE_IDS={w.audio_key(x):x['id']for x in audio if x['kind']=='se'}
w.EXACT_BGM_IDS={w.audio_key(x):x['id']for x in audio if x['kind']=='bgm'}
page_count=0
for mid in range(74,80):
 data=w.adapt_stage_151(w.adapt_stage_150(w.read_json(G/'data'/f'Map{mid:03}.json'),mid),mid)
 b=(O/f'map{mid:03}_vm.bin').read_bytes();_,ne,np,blob,bs,vflags=struct.unpack_from('<4sHHIII',b);base=20+ne*10
 assert blob+bs==len(b)
 eb=(O/f'map{mid:03}_events.bin').read_bytes();mw,mh=data['width'],data['height'];nt,ns=struct.unpack_from('<HH',eb,8);sb=14+mw*mh*5+nt*20
 mb=(O/f'map{mid:03}.bin').read_bytes();flags=w.read_json(G/'data/Tilesets.json')[data['tilesetId']]['flags']
 for y in range(mh):
  for x in range(mw):assert mb[20+mw*mh*8+y*mw+x]==w.build_pass_mask(data,flags,x,y)
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10);ev=data['events'][eid]
  assert (x,y,n)==(ev['x'],ev['y'],len(ev['pages']))
  for j,pg in enumerate(ev['pages']):
   rec=struct.unpack_from('<BBBBHHBBHII',b,base+(first+j)*20);ref,off,size=rec[8:]
   assert rec[7] and w.page_vm_supported(pg)
   assert b[blob+off:blob+off+size]==w.compile_vm_commands(pg,texts,preserve_message_background=mid in(78,79))
   assert (rec[0]&7,rec[4],rec[5],rec[6])==w.vm_page_conditions(pg)
   assert (rec[1],rec[2],bool(rec[3]&1))==(pg['trigger'],pg['priorityType'],pg['through'])
   if ref:
    sp=struct.unpack_from('<6H2BH',eb,sb+(ref-1)*16);sx,sy,sw,sh=sp[2:6];bits=sp[7]
    assert (bits&4 or pg['image']['characterName']=="お邪魔ブロック！！") and sp[-1]==eid
    atlas=Image.frombytes('RGBA',(512,512),(O/f'map{mid:03}_event_atlas{1 if sx>>12 else ""}.rgba8888').read_bytes());sx&=4095
    width=sw*(6 if bits&128 and bits&64 else 2 if bits&64 else 3 if bits&2 else 1);height=sh*(2 if bits&64 else 1)
    assert sx+width<=512 and sy+height<=512
    # Static elevator pages preserve the exact source pose and native pixels.
    img=pg['image']
    if img['characterName']=='!エレベーター':
     source=w.load_encrypted_png(w.resolve_named_file(G/'img/characters',img['characterName']),key)
     frame=w.extract_character_frame(source,img['characterName'],img['characterIndex'],img['direction'],img['pattern'])
     expected=Image.new('RGBA',frame.size);expected.alpha_composite(frame)
     assert frame.size==(sw,sh) and atlas.crop((sx,sy,sx+sw,sy+sh)).tobytes()==expected.tobytes()
   for c in pg['list']:
    if c['code']==201:assert c['parameters'][1] in range(73,80) or (mid==79 and c['parameters'][1]==83)
    if c['code']==231 and c['parameters'][1]!='A1':assert (O/f"pic_{w.PICTURE_IDS[c['parameters'][1]]:03}.p44").is_file()
    if c['code']in(241,250) and c['parameters'][0]['name']:
     kind='bgm'if c['code']==241 else'se';ids=w.EXACT_BGM_IDS if kind=='bgm'else w.EXACT_SE_IDS
     assert (O/f"{kind}_exact_{ids[w.audio_key(c['parameters'][0])]}.pcm").stat().st_size>0
   page_count+=1
# Every actor form uses the same untouched source pixels as the original leader.
actors=w.read_json(G/'data/Actors.json')
for aid in(4,5,6):
 a=actors[aid];source=w.load_encrypted_png(w.resolve_named_file(G/'img/characters',a['characterName']),key)
 atlas=Image.frombytes('RGBA',(256,512),(O/f'actor{aid:02}_atlas.rgba8888').read_bytes())
 for row in range(4):
  for pat in range(3):
   frame=w.extract_character_frame(source,a['characterName'],a['characterIndex'],2+row*2,pat)
   expected=Image.new('RGBA',frame.size);expected.alpha_composite(frame)
   x,y=pat*50+1,row*80+1;assert atlas.crop((x,y,x+48,y+78)).tobytes()==expected.tobytes()
# Preserve the original finale and restored continuation into Will.
original=w.read_json(G/'data/Map079.json')['events'][1]['pages'][0]['list']
boundary=next(i for i,c in enumerate(original)if c['code']==118 and c['parameters']==['追加コンテンツ'])
adapted=w.adapt_stage_150(w.read_json(G/'data/Map079.json'),79)['events'][1]['pages'][0]['list']
assert adapted==original  # 1.5.2 restores the original Will continuation
assert any(c['code']==129 and c['parameters'][:2]==[7,0] for c in adapted)
assert any(c['code']==201 and c['parameters'][1:4]==[83,14,3] for c in adapted)
print(f'PASS: {page_count} original pages, passability, native lift poses, 36 actor frames, all picture/audio dependencies and Ending 2 boundary')

# Reuse only fixture declarations, not the older test's resource execution.
s=(r/'main.c').read_text();tree=ast.parse((r/'tests/test_stage_135.py').read_text())
pre=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='pre'for t in n.targets))
defines='\n'.join(re.findall(r'^#define VM_OP_\w+ \d+',s,re.M))
a=s.index('static int vm_read_event(');b=s.index('static int vm_active_page(',a)
post=r'''
static MapState m;
static void load(const char*dir,int mid){char path[1024];memset(&m,0,sizeof(m));snprintf(path,sizeof(path),"%s/map%03d_vm.bin",dir,mid);FILE*f=fopen(path,"rb");assert(f);fseek(f,0,SEEK_END);long size=ftell(f);rewind(f);m.vm_bin=malloc(size);assert(fread(m.vm_bin,1,size,f)==(size_t)size);fclose(f);m.id=mid;m.vm_event_count=read_u16_le(m.vm_bin+4);m.vm_page_count=read_u16_le(m.vm_bin+6);m.vm_events=m.vm_bin+20;m.vm_pages=m.vm_events+m.vm_event_count*10;m.vm_commands=m.vm_bin+read_u32_le(m.vm_bin+8);m.vm_command_size=size-(m.vm_commands-m.vm_bin);}
static void step(void){tick_stage_parallel(&m);frame++;}
int main(int argc,char**argv){load(argv[1],75);g_stage_parallax_scrolling=1;g_save_enabled=1;
while(frame<640)step();assert(g_stage_parallax_scrolling&&!g_switches[763]&&g_save_enabled);
step();assert(!g_stage_parallax_scrolling&&g_switches[763]&&!g_save_enabled&&!g_switches[775]);
while(frame<690)step();assert(!g_switches[766]);step();assert(g_switches[766]);
VmEventRecord ev;VmPageRecord pg;int page;assert(vm_read_event(&m,0,&ev));assert(vm_active_page_index(&m,&ev,&pg,&page));int last=page;
for(int i=0;i<7;i++){for(int k=0;k<5;k++)step();assert(vm_active_page_index(&m,&ev,&pg,&page)&&page==last+1);last=page;}
assert(g_switches[773]&&g_switches[775]&&g_switches[764]&&pg.trigger==1&&pg.priority==0&&(pg.flags&1));
int stop=frame;for(int k=0;k<100;k++)step();assert(g_switches[775]&&g_switches[764]&&frame==stop+100);
/* A load after opening must preserve the final page without replaying the lift. */
clear_stage_parallel();for(int k=0;k<100;k++)step();assert(g_switches[773]&&g_switches[775]&&g_stage_parallel[7].page==0&&g_stage_parallel[8].page==0);
free(m.vm_bin);puts("PASS: actual C lift parallel scheduler: 640-frame travel, staged opening, save lock, terminal-state/load preservation");return 0;}
'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+defines+'\n'+s[a:b]+'\n#include "runtime/factory_puzzle.h"\n#include "runtime/stage_parallel.h"\n'+post)
 subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e),str(O)],check=True)
assert '(map_id==75 && !g_switches[763])' in s
# Exercise the actual VM party handler and save encoding, including old saves.
a=s.index('        } else if (op == VM_OP_PARTY) {');a=s.index('\n',a)+1;b=s.index('        } else if ',a)
code='#include <stdint.h>\n#include <assert.h>\n#include "runtime/player_forms.h"\nstatic void execute(uint8_t actor,uint8_t remove_actor){uint8_t data[]={actor,remove_actor};const uint8_t*p=data,*end=data+2;while(1){'+s[a:b]+'break;}}\n'
code+=r'''int main(void){player_form_restore_bits(1);assert(player_form_actor()==1);execute(1,1);execute(5,0);assert(player_form_actor()==5);execute(5,1);execute(6,0);assert(player_form_actor()==6);uint8_t flags=3|player_form_save_bits();g_player_party_mask=1;player_form_restore_bits(flags);assert(player_form_actor()==6&&(flags&3)==3);execute(6,1);execute(5,0);execute(5,1);execute(4,0);assert(player_form_actor()==4);flags=1|player_form_save_bits();g_player_party_mask=1;player_form_restore_bits(flags);assert(player_form_actor()==4);for(int i=0;i<4;i++){player_form_restore_bits(i);assert(player_form_actor()==1);}return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'p.c';e=Path(td)/'p';p.write_text(code);subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: actual VM party changes, intermediate and demon forms, PG60 spare-bit round trip and legacy flags')

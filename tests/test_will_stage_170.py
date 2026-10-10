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
for mid in (*range(79,105),*range(111,140)):
 data=w.adapt_stage_152(w.read_json(G/'data'/f'Map{mid:03}.json'),mid)
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
   assert b[blob+off:blob+off+size]==w.compile_vm_commands(pg,texts,preserve_message_background=True)
   assert (rec[0]&7,rec[4],rec[5],rec[6])==w.vm_page_conditions(pg)
   assert (rec[1],rec[2],bool(rec[3]&1))==(pg['trigger'],pg['priorityType'],pg['through'])
   if ref:
    sp=struct.unpack_from('<6H2BH',eb,sb+(ref-1)*16);sx,sy,sw,sh=sp[2:6];bits=sp[7]
    assert (bits&4 or pg['image']['characterName']=="お邪魔ブロック！！") and sp[-1]==eid
    atlas=Image.frombytes('RGBA',(512,512),(O/f'map{mid:03}_event_atlas{1 if sx>>12 else ""}.rgba8888').read_bytes());sx&=4095
    width=sw*(6 if bits&128 and bits&64 and mid!=94 else 3 if bits&128 and bits&64 else 2 if bits&64 else 3 if bits&2 else 1);height=sh*(4 if bits&64 and bits&128 and mid==94 else 2 if bits&64 else 1)
    assert sx+width<=512 and sy+height<=512,(mid,eid,j,sx,sy,sw,sh,bits,width,height)
    # Static elevator pages preserve the exact source pose and native pixels.
    img=pg['image']
    if img['characterName']=='!エレベーター':
     source=w.load_encrypted_png(w.resolve_named_file(G/'img/characters',img['characterName']),key)
     frame=w.extract_character_frame(source,img['characterName'],img['characterIndex'],img['direction'],img['pattern'])
     expected=Image.new('RGBA',frame.size);expected.alpha_composite(frame)
     assert frame.size==(sw,sh) and atlas.crop((sx,sy,sx+sw,sy+sh)).tobytes()==expected.tobytes()
   for c in pg['list']:
    if c['code']==201:assert c['parameters'][1] in (*range(79,105),*range(111,140))
    if c['code']==231 and c['parameters'][1]!='A1':assert (O/f"pic_{w.PICTURE_IDS[c['parameters'][1]]:03}.p44").is_file()
    if c['code']in(241,250) and c['parameters'][0]['name']:
     kind='bgm'if c['code']==241 else'se';ids=w.EXACT_BGM_IDS if kind=='bgm'else w.EXACT_SE_IDS
     assert (O/f"{kind}_exact_{ids[w.audio_key(c['parameters'][0])]}.pcm").stat().st_size>0
   page_count+=1
# Post-credits commands, inventory cleanup and house entry are fully original.
original=w.read_json(G/'data/Map079.json');raw=(O/'map079_vm.bin').read_bytes();blob=struct.unpack_from('<I',raw,8)[0]
pg=original['events'][1]['pages'][0];assert raw[blob:]==w.compile_vm_commands(pg,texts,True)
assert any(c['code']==129 and c['parameters']==[7,0,False]for c in pg['list'])
assert any(c['code']==201 and c['parameters']==[0,83,14,3,0,0]for c in pg['list'])
# NPC walking sheets and actor7 keep native dimensions and pixels.
a=w.read_json(G/'data/Actors.json')[7];source=w.load_encrypted_png(w.resolve_named_file(G/'img/characters',a['characterName']),key)
atlas=Image.frombytes('RGBA',(256,512),(O/'actor07_atlas.rgba8888').read_bytes())
for row in range(4):
 for pat in range(3):
  frame=w.extract_character_frame(source,a['characterName'],a['characterIndex'],2+row*2,pat)
  expected=Image.new('RGBA',frame.size);expected.alpha_composite(frame)
  x,y=pat*50+1,row*80+1;assert frame.size==(48,78)and atlas.crop((x,y,x+48,y+78)).tobytes()==expected.tobytes()
for mid,eid in [(82,11),(82,28),(85,1)]:
 b=(O/f'map{mid:03}_events.bin').read_bytes();mw,mh,nt,ns=struct.unpack_from('<4H',b,4);sb=14+mw*mh*5+nt*20
 assert any(struct.unpack_from('<6H2BH',b,sb+i*16)[-1]==eid and struct.unpack_from('<6H2BH',b,sb+i*16)[7]&0xC4==0xC4 for i in range(ns))
# Compatible character save bits and actual blocked-front event dispatch.
s=(r/'main.c').read_text();a=s.index('static int vm_find_event_at(');b=s.index('static int vm_event_blocks_except(',a)
pre=r'''#include <stdint.h>
#include <assert.h>
#include "runtime/player_forms.h"
#include "runtime/render_boundaries.h"
typedef struct{int id,vm_event_count,w;void*vm_bin;}MapState;
typedef struct{int event_id;}VmEventRecord;
typedef struct{int trigger,priority,supported,cmd_size;}VmPageRecord;
static int vm_read_event(const MapState*m,int i,VmEventRecord*e){e->event_id=1;return 1;}
static void vm_event_contact_cell(const MapState*m,const VmEventRecord*e,int*x,int*y){*x=3;*y=4;}
static int vm_active_page(const MapState*m,const VmEventRecord*e,VmPageRecord*p){*p=(VmPageRecord){2,1,1,2};return 1;}
'''
post=r'''int main(void){player_change_party(1,1);player_change_party(4,0);player_change_party(4,1);player_change_party(7,0);assert(player_form_actor()==7);uint8_t flags=3|player_form_save_bits();g_player_party_mask=1;player_form_restore_bits(flags);assert(player_form_actor()==7&&(flags&3)==3);player_change_party(7,1);player_change_party(8,0);flags=3|player_form_save_bits();player_form_restore_bits(flags);assert(player_form_actor()==8&&(flags&3)==3);for(int old=0;old<4;old++){player_form_restore_bits(old);assert(player_form_actor()==1);}player_form_restore_bits(3|(8<<2));assert(player_form_actor()==6);MapState m={82,1,30,(void*)1};VmEventRecord e;VmPageRecord p;assert(vm_find_event_at(&m,3,4,-1,&e,&p));m.id=68;assert(!vm_find_event_at(&m,3,4,-1,&e,&p));return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-lm','-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print(f'PASS: {page_count} post-credits/Will pages, original continuation and items, city boundaries, dependencies, native Will/NPC frames, save bits and blocked-front doors')

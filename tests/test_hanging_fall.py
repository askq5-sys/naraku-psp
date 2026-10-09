from pathlib import Path
import struct,json,sys
from PIL import Image
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
key=bytes.fromhex(json.load(open(r.parent/'original/data/System.json'))['encryptionKey'])
src=w.load_encrypted_png(w.resolve_named_file(r.parent/'original/img/characters','!吊るしエンリ'),key)
for mid in (21,23,27):
 raw=(r/'assets'/f'map{mid:03d}_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',raw);off=14+mw*mh*5+nt*20
 records=[struct.unpack_from('<6H2BH',raw,off+i*16)for i in range(ns)]
 data=json.load(open(r.parent/f'original/data/Map{mid:03d}.json'));atlas=Image.frombytes('RGBA',(512,512),(r/'assets'/f'map{mid:03d}_event_atlas.rgba8888').read_bytes());idx=0
 for ev in data['events']:
  if not ev:continue
  for page in ev['pages']:
   im=page['image'];cn=im['characterName']
   if not cn and not im['tileId']:continue
   rec=records[idx];idx+=1
   if cn!='!吊るしエンリ':continue
   x,y,sx,sy,sw,sh,priority,flags,eid=rec
   assert (sw,sh)==(36,144) and flags&4
   assert sx+sw*(3 if flags&2 else 1)<=512 and sy+sh<=512
   assert abs(sw*2/3-24)<1e-5 and abs(sh*2/3-96)<1e-5
   for slot,pat in enumerate(range(3) if flags&2 else [im["pattern"]]):
    expected=w.extract_character_frame(src,cn,im['characterIndex'],im['direction'],pat).resize((sw,sh),Image.Resampling.LANCZOS)
    actual=atlas.crop((sx+slot*sw,sy,sx+(slot+1)*sw,sy+sh)).tobytes();expected=expected.tobytes()
    for i in range(0,len(actual),4):
     assert actual[i+3]==expected[i+3]
     if expected[i+3]:assert actual[i:i+4]==expected[i:i+4]
s=(r/'main.c').read_text();assert 'camera_y = g_actor_camera_y' in s and 'g_routes[5].remaining > 0' in s
print('PASS: hanging source resampling, unchanged display size, all patterns and atlas bounds; continuous falling actor camera')

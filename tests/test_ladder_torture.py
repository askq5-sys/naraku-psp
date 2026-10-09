from pathlib import Path
import struct,json,sys
from PIL import Image
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
m=json.load(open(r.parent/'original/data/Map025.json'));raw=(r/'assets/map025.bin').read_bytes();mw,mh=struct.unpack_from('<HH',raw,4);assert(mw,mh)==(m['width'],m['height'])
flags=json.load(open(r.parent/'original/data/Tilesets.json'))[m['tilesetId']]['flags']
unique=sorted({tid for tid in m['data'][:mw*mh*4] if tid>0});slots={tid:i+1 for i,tid in enumerate(unique)}
for i,tid in enumerate(m['data'][:mw*mh*4]):
 word=struct.unpack_from('<H',raw,20+i*2)[0]
 if tid==0:assert word==0;continue
 assert word&32767==slots[tid]
 assert bool(word&32768)==bool(flags[tid]&16 or 5888<=tid<5936)
# Ceiling above the return ladder, including its bottom border, occludes sprites.
for y in range(6,10):assert struct.unpack_from('<H',raw,20+(y*mw+6)*2)[0]&32768
key=bytes.fromhex(json.load(open(r.parent/'original/data/System.json'))['encryptionKey']);src=w.load_encrypted_png(w.resolve_named_file(r.parent/'original/img/characters','!S-003'),key)
b=(r/'assets/map027_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',b);off=14+mw*mh*5+nt*20
records=[struct.unpack_from('<6H2BH',b,off+i*16)for i in range(ns)];rec=next(x for x in records if x[-1]==1);x,y,sx,sy,sw,sh,priority,flags,eid=rec
assert(sw,sh)==(54,108)and(flags&0xC4)==0xC4
assert sx+6*sw<=512 and sy+2*sh<=512
atlas=Image.frombytes('RGBA',(512,512),(r/'assets/map027_event_atlas.rgba8888').read_bytes())
for ri,d in enumerate([2,4,6,8]):
 for pat in range(3):
  im=w.extract_character_frame(src,'!S-003',0,d,pat).resize((sw,sh),Image.Resampling.LANCZOS).tobytes();ox=sx+(ri%2*3+pat)*sw;oy=sy+(ri//2)*sh
  actual=atlas.crop((ox,oy,ox+sw,oy+sh)).tobytes()
  for j in range(0,len(im),4):
   assert actual[j+3]==im[j+3]
   if im[j+3]:assert actual[j:j+4]==im[j:j+4]
assert abs(sw*2/3-36)<1e-5 and abs(sh*2/3-72)<1e-5
assert next(x for x in records if x[-1]==3)[-2]&4
print('PASS: ladder ceiling/border occlusion, all other tile slots/order preserved; twelve torture-room killer frames at unchanged display size, high-resolution key')

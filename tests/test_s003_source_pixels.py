from pathlib import Path
import struct,json,sys
from PIL import Image
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
key=bytes.fromhex(json.load(open(r.parent/'original/data/System.json'))['encryptionKey'])
src=w.load_encrypted_png(w.resolve_named_file(r.parent/'original/img/characters','!S-003'),key)
for mid in (24,25):
 raw=(r/'assets'/f'map{mid:03d}_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',raw);off=14+mw*mh*5+nt*20
 atlas=Image.frombytes('RGBA',(512,512),(r/'assets'/f'map{mid:03d}_event_atlas.rgba8888').read_bytes())
 for i in range(ns):
  x,y,sx,sy,sw,sh,p,flags,eid=struct.unpack_from('<HHHHHHBBH',raw,off+i*16)
  if eid!=3 or not(flags&128):continue
  assert (sw,sh)==(72,144)and flags&4
  for ri,d in enumerate([2,4,6,8]):
   for pat in range(3):
    frame=w.extract_character_frame(src,'!S-003',0,d,pat);ox=sx+(ri%2*3+pat)*sw;oy=sy+(ri//2)*sh
    a=atlas.crop((ox,oy,ox+sw,oy+sh)).tobytes();b=frame.tobytes()
    for j in range(0,len(a),4):
     assert a[j+3]==b[j+3]
     if b[j+3]:assert a[j:j+4]==b[j:j+4]
  break
 else:raise AssertionError('walking sheet missing')
print('PASS: all 12 S-003 walking frames retain original visible RGBA pixels on both maps')

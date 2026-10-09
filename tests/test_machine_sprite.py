from pathlib import Path
import json,struct,sys
from PIL import Image
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
b=(r/'assets/map032_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',b);off=14+mw*mh*5+nt*20
rec=next(struct.unpack_from('<6H2BH',b,off+i*16)for i in range(ns)if struct.unpack_from('<6H2BH',b,off+i*16)[-1]==2)
sx,sy,sw,sh=rec[2:6];page_index=sx>>12;sx&=0xFFF;assert(sw,sh)==(336,384)and rec[7]&4
key=bytes.fromhex(json.load(open(r.parent/'original/data/System.json'))['encryptionKey']);src=w.load_encrypted_png(w.resolve_named_file(r.parent/'original/img/characters','!プレス機'),key);frame=w.extract_character_frame(src,'!プレス機',0,2,1)
normalized=Image.new('RGBA',frame.size);normalized.alpha_composite(frame);frame=normalized
atlas=Image.frombytes('RGBA',(512,512),(r/'assets'/('map032_event_atlas1.rgba8888'if page_index else'map032_event_atlas.rgba8888')).read_bytes());assert atlas.crop((sx,sy,sx+sw,sy+sh)).tobytes()==frame.tobytes()
assert sw/2==168 and sh/2==192
s=(r/'main.c').read_text();assert 'float src_x = (float)(sp->sx & 0x0FFF)'in s
print('PASS: machine source pixels retain full native resolution, atlas bounds and unchanged 168x192 display size')

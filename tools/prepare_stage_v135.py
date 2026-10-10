"""Rebuild 1.3.5 resources from original MZ data without renumbering assets."""
import argparse, json, struct
from pathlib import Path
from PIL import Image
import prepare_world_v060 as w
import prepare_exact_audio_v079 as audio
from prepare_ui_v060 import rgba4444_bytes

def prepare(game, out):
    w.PICTURE_IDS=w.read_json(out/'picture_v050_manifest.json')
    previous=w.read_json(out/'audio_exact_v079.json')
    audio.prepare(game,out,w)
    current=w.read_json(out/'audio_exact_v079.json')
    merged=previous+[row for row in current if row not in previous]
    (out/'audio_exact_v079.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2),encoding='utf-8')
    key=bytes.fromhex(w.read_json(game/'data/System.json')['encryptionKey'])
    texts=w.read_json(game/'data/I18NTexts.json');tilesets=w.read_json(game/'data/Tilesets.json')
    for mid in range(1,48):
        path=out/f'map{mid:03}_vm.bin'
        if not path.exists():continue
        b=path.read_bytes();_,ne,np,blob,_,flags=struct.unpack_from('<4sHHIII',b);refs={};base=20+ne*10
        for i in range(ne):
            eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10)
            for j in range(n):refs[eid,j]=struct.unpack_from('<H',b,base+(first+j)*20+10)[0]
        w.compile_map_vm(w.read_json(game/'data'/f'Map{mid:03}.json'),texts,path,refs if flags&1 else None)
    for mid in (23,24,33,34):w.prepare_dynamic_event_assets(game,out,key,texts,mid)
    for mid in range(48,56):
        # The legacy signature retains a font argument; map packing does not use it.
        w.prepare_map(game,out,key,tilesets,texts,Path('unused.ttf'),mid)
        print(w.prepare_dynamic_event_assets(game,out,key,texts,mid))
    chain=w.load_encrypted_png(w.resolve_named_file(game/'img/parallaxes','鎖の背景'),key)
    chain=chain.resize((408,312),Image.Resampling.LANCZOS)
    tex=Image.new('RGBA',(512,512));tex.alpha_composite(chain)
    (out/'parallax_chain.rgba8888').write_bytes(tex.tobytes())
    ending=w.load_encrypted_png(w.resolve_named_file(game/'img/pictures','ゲームオーバーA6'),key)
    ending=ending.resize((480,272),Image.Resampling.LANCZOS)
    tex=Image.new('RGBA',(512,512));tex.alpha_composite(ending)
    rid=w.PICTURE_IDS['ゲームオーバーA6']
    (out/f'pic_{rid:03}.p44').write_bytes(struct.pack('<4sHH',b'NGO1',480,272)+rgba4444_bytes(tex))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',required=True,type=Path);p.add_argument('--assets',required=True,type=Path)
    a=p.parse_args();prepare(a.game,a.assets)

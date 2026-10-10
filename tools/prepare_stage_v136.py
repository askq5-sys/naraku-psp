"""Rebuild the 1.3.6 elevator rooms and native corpse barriers."""
import argparse,json
from pathlib import Path
import prepare_world_v060 as w
import prepare_exact_audio_v079 as audio
def prepare(game,out):
    w.PICTURE_IDS=w.read_json(out/'picture_v050_manifest.json')
    previous=w.read_json(out/'audio_exact_v079.json');audio.prepare(game,out,w)
    current=w.read_json(out/'audio_exact_v079.json')
    (out/'audio_exact_v079.json').write_text(json.dumps(previous+[r for r in current if r not in previous],ensure_ascii=False,indent=2))
    key=bytes.fromhex(w.read_json(game/'data/System.json')['encryptionKey'])
    texts=w.read_json(game/'data/I18NTexts.json');tilesets=w.read_json(game/'data/Tilesets.json')
    for mid in (32,33,34,56,57,58):
        if mid>=56:w.prepare_map(game,out,key,tilesets,texts,Path('unused.ttf'),mid)
        print(w.prepare_dynamic_event_assets(game,out,key,texts,mid))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--assets',type=Path,required=True)
    a=p.parse_args();prepare(a.game,a.assets)

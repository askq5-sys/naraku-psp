"""Rebuild Map069 with original event-tile passage metadata."""
import argparse
from pathlib import Path
import prepare_world_v060 as w
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--assets',type=Path,required=True);a=p.parse_args()
 key=bytes.fromhex(w.read_json(a.game/'data/System.json')['encryptionKey'])
 w.PICTURE_IDS=w.read_json(a.assets/'picture_v050_manifest.json')
 print(w.prepare_dynamic_event_assets(a.game,a.assets,key,w.read_json(a.game/'data/I18NTexts.json'),69))

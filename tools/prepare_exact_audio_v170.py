"""Build exact volume/pitch/pan variants referenced by maps 001-079 and common events.
IDs are assigned across all maps, so adding later assets cannot renumber early sounds.
"""
import json, subprocess, tempfile
from pathlib import Path

def prepare(game, out, world):
    from prepare_ui_v060 import resolve_audio_file, decrypt_mz
    system=world.read_json(game/'data/System.json')
    key=bytes.fromhex(system['encryptionKey'])
    all_keys={'se':set(),'bgm':set()}; early={'se':set(),'bgm':set()}
    def visit(commands, wanted):
        for cmd in commands:
            code=cmd.get('code',0);p=cmd.get('parameters',[])
            if code in (241,250) and p and isinstance(p[0],dict):
                kind='bgm' if code==241 else 'se';k=world.audio_key(p[0])
                if k[0]:
                    all_keys[kind].add(k)
                    if wanted:early[kind].add(k)
            if code==205 and len(p)>1:visit(p[1].get('list',[]),wanted)
            if code==44 and p and isinstance(p[0],dict):
                k=world.audio_key(p[0]);all_keys['se'].add(k)
                if wanted:early['se'].add(k)
    for path in sorted((game/'data').glob('Map[0-9][0-9][0-9].json')):
        mid=int(path.stem[3:]);mp=world.read_json(path)
        for ev in mp.get('events',[]):
            if ev:
                for pg in ev.get('pages',[]):visit(pg.get('list',[]),(mid<=104 or 111<=mid<=139))
    for ev in world.read_json(game/'data/CommonEvents.json'):
        if ev:visit(ev.get('list',[]),True)
    manifest=[]
    for kind in ('se','bgm'):
        ids={k:1000+i for i,k in enumerate(sorted(all_keys[kind]))}
        if kind=='se':world.EXACT_SE_IDS=ids
        else:world.EXACT_BGM_IDS=ids
        for k in sorted(early[kind]):
            name,volume,pitch,pan=k;rid=ids[k];dst=out/f'{kind}_exact_{rid:04d}.pcm'
            manifest.append({'kind':kind,'id':rid,'name':name,'volume':volume,'pitch':pitch,'pan':pan})
            if dst.is_file() and dst.stat().st_size:continue
            src=resolve_audio_file(game/'audio'/kind,name)
            raw=decrypt_mz(src,key) if src.suffix.endswith('_') else src.read_bytes()
            with tempfile.TemporaryDirectory() as td:
                inp=Path(td)/'in.ogg';inp.write_bytes(raw)
                rate=int(round(44100*pitch/100))
                left=1.0-max(0,pan)/100;right=1.0+min(0,pan)/100
                filt=f'asetrate={rate},aresample=44100,volume={volume/100},aformat=channel_layouts=stereo,pan=stereo|c0={left}*c0|c1={right}*c1'
                subprocess.run(['ffmpeg','-v','error','-y','-i',str(inp),'-af',filt,'-f','s16le','-ar','44100','-ac','2',str(dst)],check=True)
    (out/'audio_exact_v079.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Exact early/common audio variants: {len(manifest)}')

"""Build the original elevator, surface transformation and second ending."""
import argparse,json
from pathlib import Path
import prepare_world_v060 as w
import prepare_exact_audio_v161 as audio
def prepare(game,out):
    w.PICTURE_IDS=w.read_json(out/'picture_v050_manifest.json')
    previous=w.read_json(out/'audio_exact_v079.json');audio.prepare(game,out,w)
    current=w.read_json(out/'audio_exact_v079.json')
    (out/'audio_exact_v079.json').write_text(json.dumps(previous+[r for r in current if r not in previous],ensure_ascii=False,indent=2))
    key=bytes.fromhex(w.read_json(game/'data/System.json')['encryptionKey'])
    texts=w.read_json(game/'data/I18NTexts.json');tilesets=w.read_json(game/'data/Tilesets.json')
    for mid in (*range(80,100),115):
        if True:w.prepare_map(game,out,key,tilesets,texts,Path('unused.ttf'),mid)
    for mid in (*range(80,100),115):
        print(w.prepare_dynamic_event_assets(game,out,key,texts,mid))
    # Add only missing picture dependencies; retain optimized installed portraits.
    import struct
    from PIL import Image
    from prepare_ui_v060 import rgba4444_bytes
    for mid in (*range(80,100),115):
        mp=w.adapt_stage_152(w.read_json(game/'data'/f'Map{mid:03}.json'),mid)
        for ev in mp['events']:
            if not ev:continue
            for page in ev['pages']:
                for cmd in page['list']:
                    if cmd['code']!=231 or cmd['parameters'][1]=='A1':continue
                    name=cmd['parameters'][1];rid=w.PICTURE_IDS[name];dst=out/f'pic_{rid:03}.p44'
                    if dst.exists():
                        if name in ('END','背景黒','フィニッシュA1','フィニッシュB2') or name.startswith('エンドクレジット'):
                            b=dst.read_bytes();dst.write_bytes(b'NGO1'+b[4:])
                        continue
                    im=w.load_encrypted_png(w.resolve_named_file(game/'img/pictures',name),key)
                    if name.startswith('ゲームオーバー'):
                        im=im.resize((480,272),Image.Resampling.LANCZOS);tag=b'NGO1'
                    else:
                        im=im.resize((im.width//2,im.height//2),Image.Resampling.LANCZOS);tag=b'NP50'
                        if im.width>512 or im.height>512:im.thumbnail((512,512),Image.Resampling.LANCZOS)
                        if name in ('END','背景黒','フィニッシュA1','フィニッシュB2') or name.startswith('エンドクレジット'):tag=b'NGO1'
                    tex=Image.new('RGBA',(512,512));tex.alpha_composite(im)
                    dst.write_bytes(struct.pack('<4sHH',tag,*im.size)+rgba4444_bytes(tex))
    from prepare_portraits_v132 import prepare as portraits
    names={c['parameters'][1] for mid in (*range(80,100),115)
           for e in w.adapt_stage_152(w.read_json(game/'data'/f'Map{mid:03}.json'),mid)['events'] if e
           for pg in e['pages'] for c in pg['list'] if c['code']==231}
    portraits(game,out,names)
    # Alternate leaders retain all 12 native 48x78 source frames.
    actors=w.read_json(game/'data/Actors.json')
    for aid in (7,8):
        actor=actors[aid];name=actor['characterName']
        source=w.load_encrypted_png(w.resolve_named_file(game/'img/characters',name),key)
        atlas=Image.new('RGBA',(256,512))
        for row in range(4):
            for pat in range(3):
                frame=w.extract_character_frame(source,name,actor['characterIndex'],2+2*row,pat)
                assert frame.size==(48,78)
                w.paste_with_gutter(atlas,frame,pat*50,row*80)
        (out/f'actor{aid:02}_atlas.rgba8888').write_bytes(w.rgba8888_bytes(atlas))
    source=w.load_encrypted_png(w.resolve_named_file(game/'img/system','Balloon'),key)
    balloon=Image.new('RGBA',(512,512))
    for row in range(10):
        for frame in range(8):
            w.paste_with_gutter(balloon,source.crop((frame*48,row*48,frame*48+48,row*48+48)),frame*50,row*50)
    (out/'balloon_atlas.rgba8888').write_bytes(w.rgba8888_bytes(balloon))
    source=w.load_encrypted_png(w.resolve_named_file(game/'img/parallaxes','鎖の背景'),key)
    source=source.resize((408,312),Image.Resampling.LANCZOS)
    atlas=Image.new('RGBA',(512,512));atlas.alpha_composite(source)
    (out/'parallax_chain.rgba8888').write_bytes(w.rgba8888_bytes(atlas))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--assets',type=Path,required=True)
    a=p.parse_args();prepare(a.game,a.assets)

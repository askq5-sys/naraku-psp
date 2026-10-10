"""Crop dialogue art, use the 512px texture budget, retain original picture geometry."""
from pathlib import Path
import json,struct
from PIL import Image
import prepare_world_v060 as w

def is_portrait(name):
    return name.startswith(('D-001','アマリア','エマ','エンリ立ち絵','エーベル兄','オリバー','ルーカス','吊るしエンリ'))

def prepare(game,out,names=None):
    key=bytes.fromhex(w.read_json(game/'data/System.json')['encryptionKey'])
    manifest=w.read_json(out/'picture_v050_manifest.json');report=[]
    for name,rid in manifest.items():
        if not is_portrait(name) or (names is not None and name not in names):continue
        src=w.resolve_named_file(game/'img/pictures',name,('.png_','.png'))
        image=w.load_encrypted_png(src,key)if src.name.endswith('.png_')else Image.open(src).convert('RGBA')
        bbox=image.getchannel('A').getbbox()
        if bbox is None:continue
        crop=image.crop(bbox);bw,bh=crop.size
        scale=min(1,510/bw,510/bh);tw,th=max(1,round(bw*scale)),max(1,round(bh*scale))
        crop=crop.resize((tw,th),Image.Resampling.LANCZOS)
        sheet=Image.new('RGBA',(512,512));sheet.paste(crop,(1,1));rgba=sheet.tobytes();packed=bytearray(512*512*2)
        for i in range(0,len(rgba),4):
            c=(rgba[i]>>4)|((rgba[i+1]>>4)<<4)|((rgba[i+2]>>4)<<8)|((rgba[i+3]>>4)<<12)
            struct.pack_into('<H',packed,i//2,c)
        logical=(max(1,round(image.width*.5)),max(1,round(image.height*.5)))
        (out/f'pic_{rid:03}.p44').write_bytes(struct.pack('<4s8H',b'NPR1',tw,th,*logical,bbox[0],bbox[1],bw,bh)+packed)
        report.append({'id':rid,'name':name,'canvas':image.size,'logical':logical,'bounds':bbox,'texture_region':[tw,th],'display_region':[bw*.5,bh*.5]})
    (out/'portraits_v132.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return report
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('game',type=Path);ap.add_argument('--out',type=Path,default=Path('assets'));args=ap.parse_args()
    print('Portraits rebuilt:',len(prepare(args.game,args.out)))

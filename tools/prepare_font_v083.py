#!/usr/bin/env python3
"""Rebuild existing NF30 coverage, using the original Latin font and CJK fallback."""
import argparse,io,math,struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont

def prepare(game,assets,out):
    original=TTFont(game/'fonts/mplus-1m-regular.woff');original.flavor=None
    stream=io.BytesIO();original.save(stream);stream.seek(0)
    latin=ImageFont.truetype(stream,20)
    cmap=original.getBestCmap()
    data=(assets/'font_map.bin').read_bytes()
    magic,count,pages,cw,ch,cols,rows=struct.unpack_from('<4sHBBBBH',data)
    assert (magic,cw,ch,cols,rows)==(b'NF30',24,28,21,18)
    images=[Image.frombytes('L',(512,512),(assets/f'font_page{i}.t8').read_bytes()) for i in range(pages)]
    records=[]
    out.mkdir(parents=True,exist_ok=True)
    for i in range(count):
        cp,page,slot,old_adv=struct.unpack_from('<IBHB',data,12+i*8)
        char=chr(cp)
        if cp not in cmap:
            records.append(struct.pack('<IBHB',cp,page,slot,old_adv))
            continue
        font=latin
        # Draw unclipped first; preserve full ascenders/descenders and bearings.
        full=Image.new('L',(96,96));draw=ImageDraw.Draw(full)
        draw.text((32,48),char,font=font,fill=255,anchor='ls')
        box=full.getbbox()
        cell=Image.new('L',(24,28))
        advance=max(4,min(23,math.ceil(font.getlength(char))+2))
        if box:
            ink=full.crop(box)
            if ink.width>22 or ink.height>26:
                scale=min(22/ink.width,26/ink.height,1)
                ink=ink.resize((max(1,round(ink.width*scale)),max(1,round(ink.height*scale))),Image.Resampling.LANCZOS)
            x=max(1,box[0]-32+1)
            x=min(x,23-ink.width)
            y=max(1,min(21+box[1]-48,27-ink.height))
            cell.paste(ink,(x,y))
            advance=max(advance,x+ink.width)
            assert cell.getbbox()[3]<=27
        images[page].paste(cell,(slot%cols*cw,slot//cols*ch))
        records.append(struct.pack('<IBHB',cp,page,slot,advance))
    (out/'font_map.bin').write_bytes(data[:12]+b''.join(records))
    for i,img in enumerate(images):(out/f'font_page{i}.t8').write_bytes(img.tobytes())
    # Readable native-size preview; g/j/p/q/y must retain their tails.
    sample='Processing Plant No. 1  g j p q y'
    preview=Image.new('RGB',(480,56),(18,0,0));x=8
    mapping={struct.unpack('<IBHB',r)[0]:struct.unpack('<IBHB',r)[1:] for r in records}
    for c in sample:
        page,slot,adv=mapping[ord(c)];mask=images[page].crop((slot%cols*cw,slot//cols*ch,slot%cols*cw+adv,slot//cols*ch+ch))
        preview.paste((255,255,255),(x,12),mask);x+=adv
    preview.save(out.parent/'font_preview.png')
    print(f'PASS: {count} glyphs rebuilt, {pages} pages, protected descenders')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--assets',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();prepare(a.game,a.assets,a.out)

#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('game')
    a=ap.parse_args(); game=Path(a.game)
    maps=[]; disabled=[]; p6=[]; water_touch=0
    for mid in range(1,140):
        mp=read_json(game/'data'/f'Map{mid:03d}.json'); maps.append(mp)
        if mp.get('disableDashing'): disabled.append(mid)
        for ev in mp.get('events') or []:
            if not ev: continue
            for page in ev.get('pages',[]):
                for c in page.get('list',[]):
                    code=c.get('code'); par=c.get('parameters',[]) or []
                    if code in (231,232,235) and par and int(par[0])==6:
                        p6.append((mid,ev['id'],code,par))
                    if mid==1 and page.get('trigger')==1 and code==250 and par and isinstance(par[0],dict):
                        se=par[0]
                        if se.get('name')=='【効果音ラボ】水をバシャッとかける1' and int(se.get('volume',0))==5:
                            water_touch += 1
    print(f'Maps checked: {len(maps)}')
    print(f'Disable Dashing = true: {disabled if disabled else "none (dash enabled on all 139 maps)"}')
    print(f'Map001 Player Touch splash commands (volume 5): {water_touch}')
    print('Picture #6 commands:')
    for mid,eid,code,par in p6:
        kind={231:'Show',232:'Move',235:'Erase'}[code]
        print(f'  Map{mid:03d} event {eid}: {kind} {par}')
    if disabled:
        raise SystemExit('Unexpected dashing flags for the supplied game build')
    if not any(mid==1 and code==231 for mid,_,code,_ in p6):
        raise SystemExit('Expected Map001 Show Picture #6 not found')
    if not any(mid==10 and code==235 for mid,_,code,_ in p6):
        raise SystemExit('Expected Map010 Erase Picture #6 not found')
    if water_touch < 1:
        raise SystemExit('Expected original Map001 water-touch SE events not found')
    print('Parity anchors: OK')

if __name__=='__main__': main()

#!/usr/bin/env python3
import argparse, json
from collections import Counter
from pathlib import Path

def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('game')
    a=ap.parse_args(); game=Path(a.game)
    maps=[]; disabled=[]; p6=[]; water_touch=0
    player_speed_changes=[]
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
                    if code==205 and len(par)>=2 and int(par[0])==-1 and isinstance(par[1],dict):
                        for rc in par[1].get('list',[]) or []:
                            if int(rc.get('code',0))==29:
                                rp=rc.get('parameters',[]) or []
                                if rp:
                                    player_speed_changes.append((mid, ev['id'], ev.get('name',''), ev.get('x',0), ev.get('y',0), int(rp[0]), page.get('trigger')))
    counts=Counter(x[5] for x in player_speed_changes)
    print(f'Maps checked: {len(maps)}')
    print(f'Disable Dashing = true: {disabled if disabled else "none (dash enabled on all 139 maps)"}')
    print(f'Map001 Player Touch splash commands (volume 5): {water_touch}')
    print(f'Player Change Speed commands: {len(player_speed_changes)} total; by speed = {dict(sorted(counts.items()))}')
    print('Early movement-speed boundary events:')
    for row in player_speed_changes:
        mid,eid,name,x,y,speed,trig=row
        if mid in (2,5,6,7) and name=='移動速度設定':
            print(f'  Map{mid:03d} event {eid} @ ({x},{y}) trigger={trig}: speed {speed}')
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
    map2={(x,y,speed) for mid,_,name,x,y,speed,trig in player_speed_changes if mid==2 and name=='移動速度設定' and trig==1}
    expected={(4,7,4),(4,8,4),(4,9,4),(5,7,3),(5,8,3),(5,9,3)}
    if not expected.issubset(map2):
        raise SystemExit('Expected Map002 speed-3/speed-4 Player Touch boundary events not found')
    print('Movement-speed parity anchor: OK (Map002 explicitly switches base speed 3 <-> 4).')
    print('Parity anchors: OK')

if __name__=='__main__': main()

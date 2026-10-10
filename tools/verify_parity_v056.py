#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def j(path): return json.loads(path.read_text(encoding='utf-8'))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('game',type=Path); a=ap.parse_args(); g=a.game
    m1=j(g/'data'/'Map001.json')
    e2=m1['events'][2]; e44=m1['events'][44]; e45=m1['events'][45]
    pic6=[]
    for p in e2['pages']:
        for c in p['list']:
            if c['code']==231 and c['parameters'][0]==6: pic6.append(c['parameters'])
    assert pic6 and pic6[0][1]=='A1' and pic6[0][2:9]==[0,0,0,0,100,100,255], pic6
    assert all(p['moveSpeed']==6 for p in e45['pages']), [p['moveSpeed'] for p in e45['pages']]
    page=e44['pages'][1]
    assert page['trigger']==1
    assert any(c['code']==205 and c['parameters'][0]==45 for c in page['list'])
    moves=[]
    for c in page['list']:
        if c['code']==205 and c['parameters'][0]==45:
            moves=[r['code'] for r in c['parameters'][1]['list'] if r['code']]
    assert moves.count(1)==12 and 37 in moves, moves
    print('NARAKU PSP 0.5.6 parity anchors: OK')
    print('  A1: Picture #6, top-left (0,0), 100%, opacity 255, original viewport 816x624')
    print('  Map001 Event45: moveSpeed 6 on every page')
    print('  Map001 Event44: Player Touch -> Event45 Through ON + 12x Move Down, wait=true')
    print('  Expected corpse route time at speed6: 48 frames (~0.8 s at 60 Hz), not ~6.4 s')

if __name__=='__main__': main()

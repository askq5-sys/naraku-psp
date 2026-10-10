#!/usr/bin/env python3
import json, sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
if not (root/'data'/'System.json').is_file():
    raise SystemExit(f'ERROR: game data not found under {root}')

maps = []
transfer_with_tail = 0
visibility_transfer_sequences = 0
change_speed = {}
for mp in sorted((root/'data').glob('Map[0-9][0-9][0-9].json')):
    data=json.loads(mp.read_text(encoding='utf-8'))
    maps.append(mp)
    for ev in data.get('events') or []:
        if not ev: continue
        for pg in ev.get('pages') or []:
            lst=pg.get('list') or []
            for i,c in enumerate(lst):
                if c.get('code') == 201 and any(x.get('code') not in (0,) for x in lst[i+1:]):
                    transfer_with_tail += 1
                    before = any(x.get('code') == 211 for x in lst[:i])
                    after = any(x.get('code') in (211,121,123,205,230,223,231,232,235,241,250) for x in lst[i+1:])
                    if before and after: visibility_transfer_sequences += 1
                if c.get('code') == 205:
                    pars=c.get('parameters') or []
                    if len(pars)>=2 and pars[0] == -1 and isinstance(pars[1],dict):
                        for rc in pars[1].get('list') or []:
                            if rc.get('code') == 29:
                                ps=rc.get('parameters') or []
                                if ps:
                                    v=int(ps[0]); change_speed[v]=change_speed.get(v,0)+1
print(f'Maps checked: {len(maps)}')
print(f'Event pages with commands after Transfer Player: {transfer_with_tail}')
print(f'Transparency/state-sensitive transfer sequences: {visibility_transfer_sequences}')
print('Player Change Speed commands:', sum(change_speed.values()), 'total; by speed =', dict(sorted(change_speed.items())))
if len(maps) != 139: raise SystemExit('ERROR: expected 139 maps')
if transfer_with_tail <= 0: raise SystemExit('ERROR: expected events that continue after transfer')
if visibility_transfer_sequences <= 0: raise SystemExit('ERROR: expected state-sensitive transfer sequences')
print('Transfer-interpreter parity anchor: OK')

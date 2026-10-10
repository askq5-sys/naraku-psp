from pathlib import Path
import sys, copy, struct
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r/'tools'))
import prepare_world_v060 as w
g=r.parent/'original'
d=w.read_json(g/'data/Map055.json')
a=w.adapt_stage_142(d,55)
assert a['events'][1]['pages'][:3]==d['events'][1]['pages']
assert a['events'][1]['pages'][3]['image']['tileId']==449
assert a['events'][1]['pages'][3]['conditions']['switch1Id']==632
# Intermediate switch changes, swing poses and timings are untouched.
assert a['events'][3]==d['events'][3]
assert w.adapt_stage_142(a,55)==a
d=w.read_json(g/'data/Map062.json');a=w.adapt_stage_142(d,62)
flags=w.read_json(g/'data/Tilesets.json')[d['tilesetId']]['flags']
for eid in (4,5,6,7):
    old=d['events'][eid];e=a['events'][eid]
    assert (e['x'],e['y'])==(old['x'],9)
    assert e['pages'][1:]==old['pages'][1:]
    cmds=e['pages'][0]['list'];original=old['pages'][0]['list']
    align=cmds[:1] if e['x']!=7 else []
    assert cmds[len(align):]==original[2:]
    assert cmds[len(align)]['code']==223
    x,y=e['x'],e['y']
    for route in align+[original[3]]:
        for c in route['parameters'][1]['list']:
            code=c['code']
            if code not in (1,2,3,4):continue
            dx,dy={1:(0,1),2:(-1,0),3:(1,0),4:(0,-1)}[code]
            bit,reverse={1:(1,8),2:(2,4),3:(4,2),4:(8,1)}[code]
            assert w.build_pass_mask(d,flags,x,y)&bit
            assert w.build_pass_mask(d,flags,x+dx,y+dy)&reverse
            x+=dx;y+=dy
    assert (x,y)==(7,12)
assert w.adapt_stage_142(a,62)==a
assert d['events'][4]['y']==10
print('PASS: persistent lever position, untouched swing timeline, four continuous ending approaches, passage masks and identical ending tails')

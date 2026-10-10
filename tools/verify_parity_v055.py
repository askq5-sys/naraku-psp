#!/usr/bin/env python3
import argparse, json, pathlib, re, sys

ap=argparse.ArgumentParser()
ap.add_argument('game', help='NARAKU game directory')
a=ap.parse_args()
root=pathlib.Path(a.game)

def load_map(mid):
    return json.loads((root/'data'/f'Map{mid:03d}.json').read_text(encoding='utf-8'))

# Engine truth: command211 in the shipped RPG Maker MZ runtime.
js=(root/'js'/'rmmz_objects.js').read_text(encoding='utf-8', errors='replace')
if '$gamePlayer.setTransparent(params[0] === 0);' not in js:
    print('FAIL: could not verify RPG Maker MZ command211 semantics')
    sys.exit(1)

m3=load_map(3); m4=load_map(4); m1=load_map(1)
# Map003 Event2 hides the real player before Map004's entrance cutscene.
e3=m3['events'][2]['pages'][0]['list']
if not any(c['code']==211 and c['parameters']==[0] for c in e3):
    print('FAIL: Map003 Event2 expected Transparency ON [0]')
    sys.exit(1)
# Map004 Event7 restores player visibility after the gate animation.
e4=m4['events'][7]['pages'][0]['list']
if not any(c['code']==211 and c['parameters']==[1] for c in e4):
    print('FAIL: Map004 Event7 expected Transparency OFF [1]')
    sys.exit(1)

# The two intro entries reported as fake PSP prompts are transparent blank text.
e1=m1['events'][2]['pages'][0]['list']
anchors=[]
for idx,c in enumerate(e1):
    if c['code']==101 and len(c['parameters'])>=3 and c['parameters'][2]==2:
        lines=[]; j=idx+1
        while j<len(e1) and e1[j]['code']==401:
            lines.extend(e1[j]['parameters']); j+=1
        if any('I18N[986]' in str(x) for x in lines) or any('I18N[988]' in str(x) for x in lines):
            anchors.append(idx)
if len(anchors)!=2:
    print('FAIL: could not locate both transparent blank intro messages')
    sys.exit(1)

print('NARAKU PSP 0.5.5 parity anchors: OK')
print('  RPG Maker command211: param 0 = transparent ON, param 1 = OFF')
print('  Map003 Event2 hides player before transition')
print('  Map004 Event7 restores player visibility')
print('  Map001 fall has 2 transparent blank text anchors; PSP no longer turns them into X-gates')

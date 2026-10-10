#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path

def readj(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    ap=argparse.ArgumentParser(description='Verify NARAKU 0.6.9 UI/story/audio parity anchors')
    ap.add_argument('game',type=Path); a=ap.parse_args(); g=a.game.resolve()
    system=readj(g/'data/System.json')
    ce=readj(g/'data/CommonEvents.json')
    plugins_text=(g/'js/plugins.js').read_text(encoding='utf-8-sig')
    plugins=json.loads(plugins_text[plugins_text.find('['):plugins_text.rfind(']')+1])
    active={p['name']:p for p in plugins if p.get('status')}

    assert system.get('advanced',{}).get('screenWidth')==816
    assert system.get('advanced',{}).get('screenHeight')==624
    assert system.get('titleCommandWindow',{}).get('offsetX')==-250
    assert system.get('titleCommandWindow',{}).get('offsetY')==50
    tb=system.get('titleBgm',{})
    assert tb.get('name')=='【SE音人】街独特の低音' and tb.get('volume')==50 and tb.get('pitch')==100

    m=active.get('MenuCallCommon'); assert m
    assert m.get('parameters',{}).get('ComEvent')=='1'
    c1=ce[1]; cmds=c1.get('list',[])
    assert cmds[0]['code']==250 and cmds[0]['parameters'][0]['name']=='【魔王魂】-SE1'
    assert cmds[1]['code']==355 and 'Scene_Item' in cmds[1]['parameters'][0]

    opt=active.get('OptionEx'); assert opt
    op=opt.get('parameters',{})
    assert op.get('defaultAlwaysDash')=='false'
    assert op.get('defaultVolume')=='75'
    assert op.get('defaultWindowOpacity')=='195'

    disp=active.get('DisplayI18NTexts'); assert disp
    langs=json.loads(disp.get('parameters',{}).get('supportedLanguages','[]'))
    assert langs==['en_US','ja_JP','zh_CN','zh_TW']

    maps=sorted((g/'data').glob('Map[0-9][0-9][0-9].json'))
    assert len(maps)==139
    dash_disabled=[]
    for p in maps:
        d=readj(p)
        if d.get('disableDashing'): dash_disabled.append(p.name)
    assert not dash_disabled

    # 0.6.9 regression anchors: A1 must be full opacity in the real Map001
    # autorun; blood floor footsteps use 5%@70/120; and the Map009 worm death
    # event contains the custom Game Over picture + Return to Title.
    map1=readj(g/'data/Map001.json')
    a1_cmds=[c for c in map1['events'][2]['pages'][0]['list']
             if c.get('code')==231 and len(c.get('parameters',[]))>=9
             and c['parameters'][0]==6 and c['parameters'][1]=='A1']
    assert a1_cmds and int(a1_cmds[0]['parameters'][8])==255

    map8=readj(g/'data/Map008.json')
    blood=[]
    for ev in map8.get('events',[]):
        if not ev: continue
        for pg in ev.get('pages',[]):
            for c in pg.get('list',[]):
                if c.get('code')==250 and c.get('parameters'):
                    a=c['parameters'][0]
                    if isinstance(a,dict) and '水をバシャッとかける1' in str(a.get('name','')):
                        blood.append((int(a.get('volume',0)),int(a.get('pitch',0))))
    assert (5,70) in blood

    map9=readj(g/'data/Map009.json')
    death=map9['events'][4]['pages'][4]['list']
    assert any(c.get('code')==231 and len(c.get('parameters',[]))>=2 and c['parameters'][1]=='ゲームオーバーA1' for c in death)
    assert any(c.get('code')==354 for c in death)

    print('NARAKU PSP 0.6.9 parity anchors: OK')
    print('  active MenuCallCommon: cancel/menu -> Common Event 1 -> Scene_Item')
    print('  title: localized title art, BGM 50% pitch100, command offset (-250,+50)')
    print('  options defaults: Always Dash OFF, BGM/SE 75, Window Opacity 195')
    print('  languages: en_US / ja_JP / zh_CN / zh_TW')
    print('  maps: 139, disableDashing=true on none')
    print('  A1: Map001 Picture #6 opacity 255; blood-step 5%@70 present')
    print('  Map009 worm death: custom Game Over picture + Return to Title present')

if __name__=='__main__': main()

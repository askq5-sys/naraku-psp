#!/usr/bin/env python3
"""Regression checks against the user's original data and executable C picture math."""
import argparse,json,struct,subprocess,tempfile
from pathlib import Path
import prepare_world_v060 as w

def main():
    ap=argparse.ArgumentParser();ap.add_argument('game',type=Path);a=ap.parse_args()
    pages=0;errors=[]
    for i in range(1,21):
        for ev in w.read_json(a.game/'data'/f'Map{i:03d}.json')['events']:
            if not ev:continue
            for n,pg in enumerate(ev['pages']):
                pages+=1
                if not w.page_vm_supported(pg):errors.append((i,ev['id'],n+1))
    assert not errors,errors
    raw=w.compile_vm_commands({'list':[{'code':232,'parameters':[52,1,0,0,81,62,300,275,150,1,60,False,3]}]},[])
    assert raw[0]==w.VM_OP_MOVE_PICTURE_EX
    assert struct.unpack('<HBiiHHBBHBBB',raw[1:-1])==(52,1,81,62,300,275,150,1,60,0,3,0)
    assert w.compile_vm_commands({'list':[{'code':251,'parameters':[]}]},[])==bytes([w.VM_OP_STOP_SE,0])
    raw=w.compile_vm_commands({'list':[{'code':205,'parameters':[7,{'list':[{'code':3}], 'wait':False,'repeat':True,'skippable':True}]}]},[])
    assert raw[:6]==struct.pack('<BhHB',w.VM_OP_MOVE_ROUTE_EX,7,1,3)
    root=Path(__file__).resolve().parent.parent
    src=(root/'main.c').read_text()
    start=src.index('static float picture_ease(');end=src.index('static void draw_vm_pictures',start)
    structure=src[src.index('typedef struct {\n    int number, resource_id'):src.index('static PictureSlot g_pictures')]
    code='#include <assert.h>\n#include <math.h>\n#define MAX_ACTIVE_PICTURES 5\n'+structure+'static PictureSlot g_pictures[5];\n'+src[start:end]+'''
int main(void) {
    PictureSlot *p=&g_pictures[0];p->number=52;p->scale_x=p->scale_y=100;
    move_picture_start(p,1,100,80,300,200,255,1,4,1);
    tick_pictures();
    assert(fabsf(p->x-6.25f)<0.0001f);assert(fabsf(p->scale_x-112.5f)<0.0001f);
    assert(p->origin==1 && p->blend==1 && p->duration==3);
    tick_pictures();tick_pictures();tick_pictures();
    assert(p->x==100 && p->scale_x==300 && p->opacity==255 && !p->duration);
    move_picture_start(p,0,-100,0,100,100,0,0,2,2);
    tick_pictures();assert(fabsf(p->x-(-50))<0.0001f);
    tick_pictures();assert(p->x==-100 && p->opacity==0);
    assert(picture_ease(0.25f,3)==0.125f);
    return 0;
}
'''
    with tempfile.TemporaryDirectory() as td:
        cp=Path(td)/'test.c';exe=Path(td)/'test';cp.write_text(code)
        subprocess.run(['cc','-std=c99','-O2',str(cp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
    print(f'PASS: {pages} early-map pages accepted; bytecode layouts and real C picture interpolation tested.')
if __name__=='__main__':main()

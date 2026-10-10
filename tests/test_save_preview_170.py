from pathlib import Path
import subprocess,tempfile,struct,sys
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
a=s.index('static int save_slot_metadata(');b=s.index('/* ------------------------------------------------------------------------- */',a)
pre=r"""#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define ASSET_ROOT ""
#define CHAR_ATLAS_W 256
#define CHAR_ATLAS_BYTES (256*512*4)
#define CHAR_SLOT_W 50
#define CHAR_SRC_W 48
#define CHAR_SRC_H 78
static unsigned char g_switches[1601],g_variables[100],g_items[100],g_self_switches[100];
static const char *path;
static void save_slot_path(int n,char*p,size_t size){snprintf(p,size,"%s",path);}
static int read_u16_le(const unsigned char*p){return p[0]|p[1]<<8;}
static unsigned read_u32_le(const unsigned char*p){return p[0]|p[1]<<8|p[2]<<16|p[3]<<24;}
#include "runtime/player_forms.h"
static void *g_ui_char_atlas;
static int loads;
static void *load_exact_file(const char *p,size_t n){int aid=0;assert(sscanf(p,"actor%d_atlas.rgba8888",&aid)==1);loads++;void*b=malloc(n);memset(b,aid,n);return b;}
static void sceKernelDcacheWritebackInvalidateAll(void){}
#include "runtime/save_previews.h"
"""
post=r"""int main(int argc,char**argv){path=argv[1];
 unsigned char h[16]={0};memcpy(h,"PG60",4);h[4]=83;
 for(int aid=1;aid<=10;++aid){int bit=player_form_bit(aid);if(!bit)continue;
 h[15]=1|(bit<<2);h[14]=4|(bit&192);FILE*f=fopen(path,"wb");assert(fwrite(h,1,16,f)==16);fclose(f);
 int actor=0,map=0;g_player_party_mask=16;
 assert(save_slot_metadata(1,&map,NULL,NULL,NULL,&actor)&&actor==aid&&map==83);
 assert(g_player_party_mask==16);}
 memcpy(h,"PG40",4);h[15]=255;FILE*f=fopen(path,"wb");fwrite(h,1,16,f);fclose(f);
 int actor=0;assert(save_slot_metadata(1,NULL,NULL,NULL,NULL,&actor)&&actor==1);
 g_ui_char_atlas=malloc(CHAR_ATLAS_BYTES);memset(g_ui_char_atlas,1,CHAR_ATLAS_BYTES);
 for(int aid=1;aid<=10;++aid){if(!player_form_bit(aid))continue;
 unsigned char*p=save_preview_texture(aid);assert(p&&p[(1*64+1)*4]==aid);
 assert(p[(78*64+48)*4+3]==aid&&p[0]==0);
 int before=loads;assert(save_preview_texture(aid)==p&&loads==before);}
 assert(loads==7);clear_save_previews();for(int i=0;i<8;++i)assert(!g_save_preview[i]);
 free(g_ui_char_atlas);puts("PASS: actual slot metadata selects saved actor, legacy saves retain Enri; standing-frame cache loads once and frees on close");}
"""
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+s[a:b]+post)
 subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(e)],check=True)
 subprocess.run([str(e),str(Path(td)/'save.bin')],check=True)

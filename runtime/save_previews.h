/* Keep only a standing frame per actor while the slot menu is open.
 * Reading a slot never changes the current player's party membership. */
static void *g_save_preview[8];
static unsigned char g_save_preview_attempted[8];
static void clear_save_previews(void)
{
    int i;
    for(i=0;i<8;++i){free(g_save_preview[i]);g_save_preview[i]=NULL;}
    memset(g_save_preview_attempted,0,sizeof(g_save_preview_attempted));
}
static void *save_preview_texture(int actor)
{
    int index=actor==1?0:actor-3,y;
    void *source=NULL;unsigned char *texture;char path[128];
    if(index<0 || index>=8)index=0;
    if(g_save_preview_attempted[index])return g_save_preview[index];
    g_save_preview_attempted[index]=1;
    if(index==0)source=g_ui_char_atlas;
    else {
        snprintf(path,sizeof(path),ASSET_ROOT "actor%02d_atlas.rgba8888",actor);
        source=load_exact_file(path,CHAR_ATLAS_BYTES);
    }
    if(!source)return NULL;
    texture=calloc(64*128,4);
    if(texture)for(y=0;y<CHAR_SRC_H;++y)
        memcpy(texture+((y+1)*64+1)*4,
               (unsigned char*)source+((y+1)*CHAR_ATLAS_W+CHAR_SLOT_W+1)*4,
               CHAR_SRC_W*4);
    if(index!=0)free(source);
    if(texture)sceKernelDcacheWritebackInvalidateAll();
    g_save_preview[index]=texture;return texture;
}

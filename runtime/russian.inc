/* Additive fifth language. The four original bytecode/UI variants stay intact.
 * Dictionary pointers remain valid for the lifetime of the game. */
static uint8_t *g_russian;
static size_t g_russian_size;
static uint32_t g_russian_count;

static int init_russian(void)
{
    uint32_t i;
    g_russian=(uint8_t *)load_whole_file(ASSET_ROOT "russian177.bin",&g_russian_size);
    if(!g_russian || g_russian_size<8 || memcmp(g_russian,"NR77",4))return 0;
    g_russian_count=read_u32_le(g_russian+4);
    if(g_russian_count>10000 || 8u+(size_t)g_russian_count*12u>g_russian_size)return 0;
    for(i=0;i<g_russian_count;++i) {
        const uint8_t *r=g_russian+8+i*12;
        uint32_t k=read_u32_le(r),v=read_u32_le(r+4),n=read_u32_le(r+8);
        if(k>=g_russian_size || v>=g_russian_size || n>=g_russian_size-v ||
           !memchr(g_russian+k,0,g_russian_size-k) || g_russian[v+n])return 0;
        if(i && strcmp((char *)g_russian+read_u32_le(r-12),(char *)g_russian+k)>=0)return 0;
    }
    return 1;
}

static int russian_lookup(const char **text,size_t *length)
{
    size_t i=0,n=0,len=*length;
    char *key;
    int lo=0,hi=(int)g_russian_count-1;
    if(g_language!=4 || !g_russian || !text || !*text || !len)return 0;
    key=(char *)malloc(len+1);
    if(!key)return 0;
    while(i<len) {
        unsigned char c=(unsigned char)(*text)[i];
        if(c=='\\' && i+1<len) {
            size_t j=i+1;
            while(j<len && (((*text)[j]>='a'&&(*text)[j]<='z')||((*text)[j]>='A'&&(*text)[j]<='Z')))++j;
            if(j>i+1 && j<len && (*text)[j]=='[') {
                while(j<len && (*text)[j]!=']')++j;
                if(j<len){i=j+1;continue;}
            } else if(j==i+1){i+=2;continue;}
        }
        if(c==' '||c=='\t'||c=='\r'||c=='\n'){++i;continue;}
        if(i+2<len && c==0xe3 && (unsigned char)(*text)[i+1]==0x80 && (unsigned char)(*text)[i+2]==0x80){i+=3;continue;}
        key[n++]=(char)(c>='A'&&c<='Z'?c+32:c);++i;
    }
    key[n]=0;
    while(lo<=hi) {
        int mid=(lo+hi)/2;
        const uint8_t *r=g_russian+8+mid*12;
        int cmp=strcmp(key,(char *)g_russian+read_u32_le(r));
        if(cmp<0)hi=mid-1;
        else if(cmp>0)lo=mid+1;
        else {
            *text=(char *)g_russian+read_u32_le(r+4);*length=read_u32_le(r+8);
            free(key);return 1;
        }
    }
    free(key);return 0;
}

static int vm_text_language(int lang){return lang==4?0:lang;}

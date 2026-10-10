/* Original trigger-4 timelines for Maps048-079. Commands advance once per
 * rendered game frame; waits never poll input or recursively render a frame.
 * Map048 event15 and Map049 event16 also run switch-only timeout resets. */
typedef struct {
    int page, wait, route_target, text_blocked;
    uint32_t text_offset;
    uint32_t pc;
} StageParallel;
static StageParallel g_stage_parallel[MAX_EVENT_ID];
static int g_stage_message_event;
static int g_stage_shake_frames, g_stage_shake_total, g_stage_shake_power, g_stage_shake_speed;

static void clear_stage_parallel(void)
{
    memset(g_stage_parallel, 0, sizeof(g_stage_parallel));
    g_stage_shake_frames = 0;
    g_stage_message_event = 0;
}

static void tick_stage_parallel(const MapState *m)
{
    int i;
    if (m->id < 48 || m->id > 79 || !m->vm_commands) return;
    if (g_stage_shake_frames > 0) {
        int period = 18 - g_stage_shake_speed;
        float phase;
        if (period < 2) period = 2;
        phase = (float)((g_stage_shake_total-g_stage_shake_frames)%period)/period;
        g_screen_shake_x = (phase<.5f ? phase*4-1 : 3-phase*4)*g_stage_shake_power*.5f;
        if (!--g_stage_shake_frames) g_screen_shake_x=0;
    }
    for (i=0; i<m->vm_event_count; ++i) {
        VmEventRecord ev; VmPageRecord pg; int page_index, budget=128;
        StageParallel *r;
        const uint8_t *base, *end, *p;
        if (!vm_read_event(m,i,&ev) || ev.event_id<1 || ev.event_id>=MAX_EVENT_ID) continue;
        r=&g_stage_parallel[ev.event_id];
        if (!vm_active_page_index(m,&ev,&pg,&page_index) ||
            (pg.trigger!=4 && !(pg.trigger==3 &&
                ((m->id==48 && ev.event_id==15 && g_switches[442]) ||
                 (m->id==49 && ev.event_id==16 && g_switches[460])))) || !pg.supported ||
            (size_t)pg.cmd_offset+pg.cmd_size>m->vm_command_size) {
            memset(r,0,sizeof(*r));continue;
        }
        if (r->page!=page_index+1) {
            memset(r,0,sizeof(*r));r->page=page_index+1;
        }
        /* These two timeout pages contain only switches and one sound.
         * Run this original reset here even when the player stays idle, rather
         * than waiting for the action/transfer autorun dispatcher. */
        if (m->id==49 && ev.event_id==16 && pg.trigger==3)
            reset_factory_checkpoint_tail(m->id,ev.event_id,pg.trigger);
        if (r->text_blocked) continue;
        if (r->wait>0 && --r->wait>0) continue;
        if (r->route_target) {
            if (g_routes[r->route_target].records) continue;
            r->route_target=0;
        }
        base=m->vm_commands+pg.cmd_offset;end=base+pg.cmd_size;
        if (r->pc>=pg.cmd_size) r->pc=0;
        p=base+r->pc;
        while (p<end && budget-->0) {
            int op=*p++;
            if (op==VM_OP_END) {r->pc=0;break;}
            if (op==VM_OP_SWITCH) {
                int a,z,v;
                if (end-p<5) break;
                a=read_u16_le(p);z=read_u16_le(p+2);v=p[4];p+=5;
                for (;a<=z && a<MAX_SWITCHES;++a) g_switches[a]=(uint8_t)v;
            } else if (op==VM_OP_SELF_SWITCH) {
                int bit;
                if (end-p<2) break;
                bit=p[0];
                if (bit<4) {
                    if (p[1]) g_self_switches[m->id][ev.event_id]|=(uint8_t)(1u<<bit);
                    else g_self_switches[m->id][ev.event_id]&=(uint8_t)~(1u<<bit);
                }
                p+=2;
            } else if (op==VM_OP_WAIT) {
                if (end-p<2) break;
                r->wait=read_u16_le(p);p+=2;r->pc=(uint32_t)(p-base);
                if (r->wait>0) break;
            } else if (op==VM_OP_JUMP) {
                uint32_t to;
                if (end-p<4) break;
                to=read_u32_le(p);
                if (to>=pg.cmd_size) break;
                p=base+to;
            } else if (op==VM_OP_SE) {
                if (end-p<5) break;
                play_vm_se_params(read_u16_le(p),p[2],p[3],(int)p[4]-100);p+=5;
            } else if (op==VM_OP_COND_ITEM) {
                int id;uint32_t to;
                if (end-p<6) break;
                id=read_u16_le(p);to=read_u32_le(p+2);p+=6;
                if (id>=MAX_ITEMS || g_items[id]<=0) {
                    if(to>=pg.cmd_size)break;
                    p=base+to;
                }
            } else if (op==VM_OP_ITEM) {
                int id,v;
                if (end-p<4) break;
                id=read_u16_le(p);v=(int16_t)read_u16_le(p+2);p+=4;
                if(id<MAX_ITEMS) {
                    v+=g_items[id];g_items[id]=(int16_t)(v<0?0:v>999?999:v);
                }
            } else if (op==VM_OP_TEXT || op==VM_OP_TEXT_TRANSPARENT || op==VM_OP_TEXT_STYLE) {
                const uint8_t *q,*text_start=p-1;int k;
                if(op==VM_OP_TEXT_STYLE){if(end-p<2)break;p+=2;}
                if (g_stage_message_event) break;
                if (end-p<16) break;
                q=p+16;
                for(k=0;k<4;++k) {
                    size_t n=read_u16_le(p+k*4)+read_u16_le(p+k*4+2);
                    if((size_t)(end-q)<n)break;
                    q+=n;
                }
                if(k!=4)break;
                r->text_offset=(uint32_t)(text_start-base);r->pc=(uint32_t)(q-base);
                r->text_blocked=1;g_stage_message_event=ev.event_id;break;
            } else if (op==VM_OP_SAVE_ACCESS) {
                if (p==end) break;
                g_save_enabled=!!*p++;
            } else if (op==VM_OP_PARALLAX) {
                if (p==end) break;
                g_stage_parallax_scrolling=!!*p++;g_stage_parallax_y=0;
            } else if (op==VM_OP_SHAKE) {
                int wait;
                if (end-p<5) break;
                g_stage_shake_power=p[0];g_stage_shake_speed=p[1];
                g_stage_shake_total=g_stage_shake_frames=read_u16_le(p+2);
                wait=p[4];p+=5;
                if (wait && g_stage_shake_frames>0) {
                    r->wait=g_stage_shake_frames;r->pc=(uint32_t)(p-base);break;
                }
            } else if (op==VM_OP_MOVE_ROUTE_EX) {
                int target,count,flags;
                if (end-p<5) break;
                target=(int16_t)read_u16_le(p);count=read_u16_le(p+2);flags=p[4];p+=5;
                if (end-p<count*5) break;
                if (!target) target=ev.event_id;
                if (target>0 && target<MAX_EVENT_ID && start_event_route(m,target,p,count,flags) && (flags&4))
                    r->route_target=target;
                p+=count*5;
                if (r->route_target) {r->pc=(uint32_t)(p-base);break;}
            } else {
                /* The resource audit rejects other commands in these parallel
                 * pages; malformed data must never spin on the game thread. */
                r->pc=pg.cmd_size;break;
            }
            r->pc=(uint32_t)(p-base);
        }
    }
}

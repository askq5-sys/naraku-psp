#include <pspkernel.h>
#include <pspdisplay.h>
#include <pspctrl.h>
#include <pspgu.h>
#include <pspge.h>
#include <pspdebug.h>
#include <pspaudio.h>

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

PSP_MODULE_INFO("NARAKU PSP", PSP_MODULE_USER, 1, 33);
#include "runtime/player_animation.h"
#include "runtime/pressing_room.h"
PSP_MAIN_THREAD_ATTR(PSP_THREAD_ATTR_USER);

#define SCREEN_W 480
#define SCREEN_H 272
#define BUF_W 512
#define TILE_PX 24

#define TILE_ATLAS_W 512
#define TILE_ATLAS_H 512
#define TILE_ATLAS_BYTES (TILE_ATLAS_W * TILE_ATLAS_H * 4)
#define TILE_SLOT 50
#define TILE_SOURCE 48
#define TILE_ATLAS_COLS 10

#define CHAR_ATLAS_W 256
#define CHAR_ATLAS_H 512
#define CHAR_ATLAS_BYTES (CHAR_ATLAS_W * CHAR_ATLAS_H * 4)
#define CHAR_SLOT_W 50
#define CHAR_SLOT_H 80
#define CHAR_SRC_W 48
#define CHAR_SRC_H 78
#define CHAR_DST_W 24
#define CHAR_DST_H 39

#define EVENT_ATLAS_W 512
#define EVENT_ATLAS_H 512
#define EVENT_ATLAS_BYTES (EVENT_ATLAS_W * EVENT_ATLAS_H * 4)

#define FALL_ATLAS_W 512
#define FALL_ATLAS_H 128
#define FALL_ATLAS_BYTES (FALL_ATLAS_W * FALL_ATLAS_H * 4)
#define FALL_SLOT_W 82
#define FALL_SRC_W 80
#define FALL_SRC_H 80
#define FALL_DST_W 40
#define FALL_DST_H 40
#define FALL_EVENT_X 12

/* Map001 second-visit Lucas corpse fall.  This is a real event sprite in the
 * original project (Event 45), not a player animation.  Earlier PSP builds
 * moved its logical event position but had no dynamic page graphic, making
 * the player appear frozen while an invisible event crawled downward. */
#define LUCAS_FALL_ATLAS_W 256
#define LUCAS_FALL_ATLAS_H 64
#define LUCAS_FALL_ATLAS_BYTES (LUCAS_FALL_ATLAS_W * LUCAS_FALL_ATLAS_H * 4)
#define LUCAS_FALL_SLOT_W 32
#define LUCAS_FALL_SRC_W 24
#define LUCAS_FALL_SRC_H 39
#define LUCAS_FALL_EVENT_X 4
#define LUCAS_FALL_EVENT_Y 0

#define LUCAS_CORPSE_TEX_W 64
#define LUCAS_CORPSE_TEX_H 64
#define LUCAS_CORPSE_TEX_BYTES (LUCAS_CORPSE_TEX_W * LUCAS_CORPSE_TEX_H * 4)
#define LUCAS_CORPSE_SRC_W 24
#define LUCAS_CORPSE_SRC_H 39
#define LUCAS_CORPSE_EVENT_X 4
#define LUCAS_CORPSE_EVENT_Y 12

#define PIC_TEX_W 512
#define PIC_TEX_H 512
#define PIC_TEX_BYTES (PIC_TEX_W * PIC_TEX_H * 4)

#define DIALOG_TEX_W 512
#define DIALOG_TEX_H 128
#define DIALOG_TEX_BYTES (DIALOG_TEX_W * DIALOG_TEX_H * 4)
#define DIALOG_VISIBLE_H 96

#define MAP_HEADER_BYTES 20
#define EVENT_HEADER_BYTES 14
#define TRANSFER_RECORD_BYTES 20
#define SPRITE_RECORD_BYTES 16
#define MAX_MAP_ID 139
#define MAX_TILE_ATLASES 3
#define MAX_SWITCHES 1601
#define MAX_VARIABLES 64
#define MAX_ITEMS 128
#define MAX_EVENT_ID 160

#define VM_HEADER_BYTES 20
#define VM_EVENT_BYTES 10
#define VM_PAGE_BYTES 20

#define FONT_TEX_W 512
#define FONT_TEX_H 512
#define FONT_PAGE_BYTES (FONT_TEX_W * FONT_TEX_H)
#define FONT_MAX_PAGES 8
#define FONT_CELL_W 24
#define FONT_CELL_H 28
#define FONT_COLS 21
#define FONT_MAP_HEADER_BYTES 12
#define FONT_GLYPH_BYTES 8

#define VM_OP_END 0
#define VM_OP_TEXT 1
#define VM_OP_SWITCH 2
#define VM_OP_SELF_SWITCH 3
#define VM_OP_WAIT 4
#define VM_OP_TRANSFER 5
#define VM_OP_SE 6
#define VM_OP_ITEM 7
#define VM_OP_TRANSPARENCY 8
#define VM_OP_TINT 9
#define VM_OP_FLASH 10
#define VM_OP_BGM 11
#define VM_OP_FADE_BGM 12
#define VM_OP_EXIT 13
#define VM_OP_PICTURE6 14
#define VM_OP_VARIABLE 15
#define VM_OP_COND_SWITCH 16
#define VM_OP_COND_VAR 17
#define VM_OP_COND_ITEM 18
#define VM_OP_COND_LANG 19
#define VM_OP_JUMP 20
#define VM_OP_MOVE_ROUTE 21
#define VM_OP_CHOICES 22
#define VM_OP_COND_CHOICE 23
#define VM_OP_COMMON_EVENT 24
#define VM_OP_SHOW_PICTURE 25
#define VM_OP_MOVE_PICTURE 26
#define VM_OP_ERASE_PICTURE 27
#define VM_OP_SCENE 28
#define VM_OP_SCROLL_MAP 29
#define VM_OP_SHAKE 30
#define VM_OP_STOP_SE 31
#define VM_OP_SHOW_PICTURE_EX 32
#define VM_OP_MOVE_PICTURE_EX 33
#define VM_OP_MOVE_ROUTE_EX 34
#define VM_OP_ERASE_EVENT 35
#define VM_OP_SAVE_ACCESS 36
#define VM_OP_FADE_SCREEN 37
#define VM_OP_NUMBER_INPUT 38

#define SCENE_ITEM 1
#define SCENE_STATUS 2
#define SCENE_SAVE 3
#define SCENE_LOAD 4
#define SCENE_OPTIONS 5
#define SCENE_TITLE 6

#define ROOT "ms0:/PSP/GAME/NARAKU/"
#define ASSET_ROOT ROOT "assets/"
#define CONFIG_PATH ROOT "config.bin"
#define PROGRESS_PATH ROOT "progress.bin"
#define COMMON_VM_PATH ASSET_ROOT "common_vm.bin"
#define UI_DATA_PATH ASSET_ROOT "ui060.bin"
#define UI_ICONSET_PATH ASSET_ROOT "ui_iconset.rgba4444"
#define TITLE_EN_PATH ASSET_ROOT "title_en.rgba8888"
#define TITLE_JA_PATH ASSET_ROOT "title_ja.rgba8888"
#define TITLE_ZHCN_PATH ASSET_ROOT "title_zhcn.rgba8888"
#define TITLE_ZHTW_PATH ASSET_ROOT "title_zhtw.rgba8888"
#define TITLE_BGM_PATH ASSET_ROOT "bgm_title.pcm"
#define SE_MENU_OPEN_PATH ASSET_ROOT "se_menu_open.pcm"
#define SE_DECISION1_PATH ASSET_ROOT "se_decision1.pcm"
#define SE_DECISION2_PATH ASSET_ROOT "se_decision2.pcm"
#define SE_CANCEL2_PATH ASSET_ROOT "se_cancel2.pcm"
#define SE_CURSOR2_PATH ASSET_ROOT "se_cursor2.pcm"
#define SE_UI_CURSOR_PATH ASSET_ROOT "se_ui_cursor.pcm"
#define SE_UI_OK_PATH ASSET_ROOT "se_ui_ok.pcm"
#define SE_UI_CANCEL_PATH ASSET_ROOT "se_ui_cancel.pcm"
#define SE_UI_BUZZER_PATH ASSET_ROOT "se_ui_buzzer.pcm"
#define SE_UI_SAVE_PATH ASSET_ROOT "se_ui_save.pcm"
#define SE_UI_LOAD_PATH ASSET_ROOT "se_ui_load.pcm"
#define SAVE_SLOT_COUNT 20
#define UI_ICONSET_BYTES (512 * 512 * 2)
#define UI_ITEM_REC_BYTES 12
#define UI_HEADER_BYTES 20

#define CHAR_ATLAS_PATH ASSET_ROOT "enri_atlas.rgba8888"
#define BGM_PATH ASSET_ROOT "bgm_low.pcm"
#define A1_PATH ASSET_ROOT "a1_overlay.rgba8888"
#define FOG_A1_PATH ASSET_ROOT "fog_a1.rgba8888"
#define FOG_A1_BYTES (512 * 512 * 4)
#define KEY_ANIM_PATH ASSET_ROOT "key_anim.rgba8888"
#define KEY_ANIM_W 128
#define KEY_ANIM_H 128
#define KEY_ANIM_BYTES (KEY_ANIM_W * KEY_ANIM_H * 4)
#define MESSAGE_SURFACE_W 512
#define MESSAGE_SURFACE_H 256
#define MESSAGE_SURFACE_X 110
#define MESSAGE_SURFACE_SCALE 2
#define MESSAGE_SURFACE_Y 144
#define MESSAGE_SURFACE_BYTES (MESSAGE_SURFACE_W * MESSAGE_SURFACE_H * 4)
#define FALL_ATLAS_PATH ASSET_ROOT "fall_atlas.rgba8888"
#define LUCAS_FALL_ATLAS_PATH ASSET_ROOT "lucas_fall_atlas.rgba8888"
#define LUCAS_CORPSE_PATH ASSET_ROOT "lucas_corpse.rgba8888"
#define PORTRAIT_PATH ASSET_ROOT "enri_portrait.rgba8888"
#define SE_BONE_PATH ASSET_ROOT "se_bonecrush4.pcm"
#define SE_WATER_PATH ASSET_ROOT "se_water.pcm"
#define SE_WATER_70_80_PATH ASSET_ROOT "se_water_70_80.pcm"
#define SE_WATER_50_80_PATH ASSET_ROOT "se_water_50_80.pcm"
#define SE_SPLASH_PATH ASSET_ROOT "se_splash.pcm"
#define SE_SPLASH_STEP70_PATH ASSET_ROOT "se_splash_step70.pcm"
#define SE_SPLASH_STEP120_PATH ASSET_ROOT "se_splash_step120.pcm"
#define SE_SPLASH_20_70_PATH ASSET_ROOT "se_splash_20_70.pcm"
#define SE_BONE_100_PATH ASSET_ROOT "se_bonecrush4_100.pcm"
#define SE_EVASION1_PATH ASSET_ROOT "se_evasion1.pcm"
#define SE_SLIME_FALL_PATH ASSET_ROOT "se_slime_fall.pcm"
#define SE_SE7_PATH ASSET_ROOT "se_se7.pcm"
#define SE_SWITCH1_PATH ASSET_ROOT "se_switch1.pcm"
#define SE_SWITCH2_PATH ASSET_ROOT "se_switch2.pcm"
#define SE_MONITOR_PATH ASSET_ROOT "se_monitor.pcm"
#define SE_OPEN9_PATH ASSET_ROOT "se_open9.pcm"
#define SE_GATE1_PATH ASSET_ROOT "se_gate1.pcm"
#define SE_GATE2_PATH ASSET_ROOT "se_gate2.pcm"
#define SE_SWORD5_PATH ASSET_ROOT "se_sword5.pcm"
#define SE_HIT_AXE3_PATH ASSET_ROOT "se_hit_axe3.pcm"
#define SE_BONE5_PATH ASSET_ROOT "se_bonecrush5.pcm"
#define SE_EQUIP2_PATH ASSET_ROOT "se_equip2.pcm"
#define SE_SLASH7_PATH ASSET_ROOT "se_slash7.pcm"
#define SE_BLOW2_PATH ASSET_ROOT "se_blow2.pcm"
#define SE_MONSTER5_PATH ASSET_ROOT "se_monster5.pcm"
#define SE_HATCH_SLIDE_PATH ASSET_ROOT "se_hatch_slide.pcm"

#define AUDIO_FRAMES 4096
#define AUDIO_BYTES (AUDIO_FRAMES * 2 * (int)sizeof(int16_t))

static unsigned int __attribute__((aligned(16))) gu_list[65536];
static uint8_t *g_common_vm = NULL;
static size_t g_common_vm_size = 0;
static int g_common_vm_count = 0;
static int g_common_depth = 0;
static int g_language = 0;
static int g_always_dash = 0;
static int g_bgm_volume = 75;
static int g_se_volume = 75;
static int g_window_opacity = 195;
static int g_config_valid = 0;
/* 0.7.4 one-time compatibility migration.  Several 0.6/0.7 test builds
 * could award Map005's Red Key while its sprite was invisible.  Persist
 * whether that legacy save repair has already been offered. */
static int g_map5_key_migration_done = 1;
static int g_request_title = 0;
static int g_loaded_from_scene = 0;
static volatile int g_bgm_generation = 1;
static volatile int g_se_generation = 1;
static volatile unsigned long long g_bgm_fade_start = 0;
static volatile unsigned long long g_bgm_fade_us = 0;
static volatile int g_bgm_fade_generation = 0;
static void *g_draw_buffer = (void *)0;
static void *g_last_world_buffer = (void *)0;
static int g_last_world_buffer_valid = 0;
static char g_bgm_path[192] = BGM_PATH;

typedef struct {
    uint8_t *data;
    size_t size;
    int item_count;
    int label_count;
    const uint8_t *item_table;
    const uint8_t *label_table;
    const uint8_t *blob;
    size_t blob_size;
    void *iconset;
} UiState;
static UiState g_ui;

static int g_last_choice = -1;
static int g_choice_active = 0;
static int g_number_active,g_number_digits,g_number_cursor,g_number_value;
static int g_script_fade_alpha;
static int g_choice_count = 0;
static int g_choice_cursor = 0;
static const char *g_choice_labels[6];
static size_t g_choice_lengths[6];
#define MAX_ACTIVE_PICTURES 5
typedef struct {
    int number, resource_id, w, h, origin;
    float x, y, scale_x, scale_y, opacity;
    int blend, duration, total, easing;
    float from[5], target[5];
    int fit_screen;
    int source_w,source_h,portrait;
    float picture_offset_x,picture_offset_y,picture_region_w,picture_region_h;
    void *texture;
} PictureSlot;
static PictureSlot g_pictures[MAX_ACTIVE_PICTURES];
static volatile int g_audio_stop = 0;
static char g_scene_trace_path[512] = ASSET_ROOT "scene_trace.log";
static void scene_trace(int map, int event, int offset, int op)
{
    FILE *f = fopen(g_scene_trace_path, "a");
    if (!f) f = fopen(ASSET_ROOT "scene_trace.log", "a");
    if (!f) return;
    fprintf(f, "map=%d event=%d offset=%d op=%d\n", map,event,offset,op);
    fclose(f);
}

static uint8_t g_switches[MAX_SWITCHES];
static int g_save_enabled = 1;
static int32_t g_variables[MAX_VARIABLES];
static int16_t g_items[MAX_ITEMS];
static uint8_t g_self_switches[MAX_MAP_ID + 1][MAX_EVENT_ID];
static float g_event_shift_x[MAX_EVENT_ID];
static float g_event_shift_y[MAX_EVENT_ID];
static float g_event_jump_height[MAX_EVENT_ID];
static int8_t g_event_move_speed[MAX_EVENT_ID];
static int16_t g_event_active_page[MAX_EVENT_ID];
static int g_event_opacity[MAX_EVENT_ID];
static int g_event_direction[MAX_EVENT_ID];
static uint8_t g_event_direction_fix[MAX_EVENT_ID];
static uint8_t g_event_erased[MAX_EVENT_ID];
static uint8_t g_event_through[MAX_EVENT_ID];
typedef struct {
    uint8_t *records;
    int count,index,flags,remaining,total,dx,dy,base_x,base_y,jump_peak;
    float start_x,start_y;
} EventRoute;
static EventRoute g_routes[MAX_EVENT_ID];
static PlayerAnimation g_event_animation[MAX_EVENT_ID];
static int g_s003_paused;
static int g_factory_page[MAX_EVENT_ID];
static int g_factory_machine_frame,g_factory_corpse_phase;
static EventRoute g_player_route;
static int *g_route_player_x,*g_route_player_y,*g_route_player_direction;
static float g_route_real_x,g_route_real_y;
static int g_player_direction_fix=0;
static int g_player_walk_anime=1,g_player_step_anime=0;
static void clear_event_routes(void);
static void vm_tick_world_tint(void);

static int g_camera_locked = 0;
static float g_camera_lock_x = 0.0f;
static float g_camera_lock_y = 0.0f;
static void *g_a1_overlay = NULL;
static void *g_ui_char_atlas = NULL;
static void *g_fog_overlay = NULL;
static void *g_key_anim = NULL;
static uint32_t *g_runtime_message_surface = NULL;
static int g_runtime_message_surface_ready = 0;
static float g_fog_scroll = 0.0f;
static int g_fog_active_prev = 0;

/* Early story parallel events that matter to the Processing Plant route.
 * RPG Maker runs these while the player can still move; older PSP builds only
 * executed autoruns (trigger 3), so the two-Green-Key shutter never armed the
 * later Worm sequence. */
static int g_map8_drop_timer = 0;
static int g_map9_water_timer = 0;
/* One tick per rendered world frame.  Event pages with RPG Maker
 * stepAnime use this to cycle 1 -> 2 -> 1 -> 0 exactly while standing. */
static unsigned int g_world_render_frames = 0;
/* One persistent animation state for manual movement and event routes. */
static PlayerAnimation g_player_animation = {0, 1};
static int g_player_animation_moving = 0;
static int g_player_animation_jumping = 0;
static int g_player_animation_speed = 3;
static uint32_t g_playtime_frames = 0;
static void *g_lucas_fall_atlas = NULL;
static void *g_lucas_corpse = NULL;
static float g_actor_camera_x, g_actor_camera_y;
static int g_picture6_visible = 0;
static int g_picture6_alpha = 0;
/* RPG Maker MZ stores the player base move speed persistently.  NARAKU
 * deliberately changes it with Player Touch events (not by terrain type):
 * blood/sludge areas commonly use speed 3, while ordinary floor uses speed 4.
 * Dashing adds +1 to this base value, exactly like Game_Player::realMoveSpeed. */
static int g_player_move_speed_code = 3;
/* RPG Maker's Through flag belongs to the character, not to one individual
 * Set Movement Route command.  Some NARAKU scenes deliberately enable it in
 * one route, perform a jump/move in later routes, then disable it afterwards
 * (Map007 Event 25 is the early corpse-pile slide). */
static int g_player_through = 0;
static int g_player_visible = 1;
static float g_camera_scroll_x = 0.0f;
static float g_camera_scroll_y = 0.0f;
static int g_map_scroll_remaining, g_map_scroll_total;
static float g_map_scroll_start_x, g_map_scroll_start_y, g_map_scroll_target_x, g_map_scroll_target_y;
static float g_screen_shake_x = 0.0f;

/* RPG Maker screen tone persists between interpreter commands.  Keep the
 * actual RGB tone values instead of collapsing every non-black tone to zero.
 * NARAKU's normal early-game look uses [10,-10,-10,0], which is the subtle
 * red veil seen in the PC version after the opening. */
static int g_world_tone_r = 0;
static int g_world_tone_g = 0;
static int g_world_tone_b = 0;
static int g_world_tone_gray = 0;
static int g_world_tone_from_r = 0;
static int g_world_tone_from_g = 0;
static int g_world_tone_from_b = 0;
static int g_world_tone_from_gray = 0;
static int g_world_tone_target_r = 0;
static int g_world_tone_target_g = 0;
static int g_world_tone_target_b = 0;
static int g_world_tone_target_gray = 0;
static int g_world_tone_total = 0;
static int g_world_tone_remaining = 0;

/* Screen Flash (event command 224) is asynchronous in RPG Maker.  NARAKU's
 * axe/bone-hit flashes use wait=false, so keeping the flash only inside the
 * command handler made every red impact frame disappear in older ports. */
static int g_transfer_white = 0;
static int g_screen_flash_r = 0;
static int g_screen_flash_g = 0;
static int g_screen_flash_b = 0;
static int g_screen_flash_a = 0;
static int g_screen_flash_total = 0;
static int g_screen_flash_remaining = 0;

/* ------------------------------------------------------------------------- */
/* Basic types                                                               */
/* ------------------------------------------------------------------------- */

typedef struct {
    float u;
    float v;
    float x;
    float y;
    float z;
} TextureVertex;

typedef struct {
    float u;
    float v;
    uint32_t color;
    float x;
    float y;
    float z;
} TextureColorVertex;

typedef struct {
    uint32_t color;
    float x;
    float y;
    float z;
} ColorVertex;

typedef struct {
    char path[192];
    int generation;
} SeJob;

typedef struct {
    int id;
    int w;
    int h;
    int tile_px;

    uint8_t *map_bin;
    size_t map_size;
    int tile_count;
    int tile_atlas_count;
    void *tile_atlases[MAX_TILE_ATLASES];

    uint8_t *events_bin;
    size_t events_size;
    int transfer_count;
    int sprite_count;
    void *event_atlas;
    void *event_atlas_detail;

    const uint8_t *action_map;
    const uint8_t *step_map;
    const uint8_t *transfer_map;
    const uint8_t *block_map;
    const uint8_t *transfer_records;
    const uint8_t *sprite_records;

    uint8_t *vm_bin;
    size_t vm_size;
    int vm_event_count;
    int vm_page_count;
    const uint8_t *vm_events;
    const uint8_t *vm_pages;
    const uint8_t *vm_commands;
    size_t vm_command_size;
    uint32_t vm_flags;
} MapState;

typedef struct {
    int dest_map;
    int dest_x;
    int dest_y;
    int direction;
    int flags;
    int switch_id[3];
    int switch_value[3];
} TransferRecord;

typedef struct {
    int x;
    int y;
    int sx;
    int sy;
    int sw;
    int sh;
    int priority;
    int flags;
    int event_id;
} EventSpriteRecord;

typedef struct {
    int map_id;
    int tile_x;
    int tile_y;
    int direction_row;
    int intro_done;
} ProgressState;

typedef struct {
    uint8_t *map_bin;
    size_t map_size;
    int glyph_count;
    int page_count;
    void *pages[FONT_MAX_PAGES];
    uint32_t clut[256] __attribute__((aligned(16)));
} FontState;

typedef struct {
    int event_id;
    int x;
    int y;
    int first_page;
    int page_count;
} VmEventRecord;

typedef struct {
    int cond_flags;
    int trigger;
    int priority;
    int flags;
    int switch1;
    int switch2;
    int self_index;
    int supported;
    int sprite_ref;
    uint32_t cmd_offset;
    uint32_t cmd_size;
} VmPageRecord;

static FontState g_font;

static const char *g_runtime_speaker = NULL;
static size_t g_runtime_speaker_len = 0;
static const char *g_runtime_message = NULL;
static size_t g_runtime_message_len = 0;
static int g_pressing_room_frame = 0;
static int g_laser_room_frame = 0, g_laser_stop_count = 0, g_laser_route_index = 0;
static int g_runtime_message_active = 0;
static int g_runtime_message_openness = 0;

/* ------------------------------------------------------------------------- */
/* Small helpers                                                             */
/* ------------------------------------------------------------------------- */

static uint16_t read_u16_le(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static uint32_t read_u32_le(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void write_u16_le(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)(v & 0xFF);
    p[1] = (uint8_t)((v >> 8) & 0xFF);
}

static float clamp_float(float value, float min_value, float max_value)
{
    if (value < min_value) return min_value;
    if (value > max_value) return max_value;
    return value;
}

/* RPG Maker MZ rasterises its map/character/picture positions onto whole
 * screen pixels before Pixi finally draws them:
 *   Tilemap.updateTransform(): ox/oy = Math.ceil(origin.x/y)
 *   Game_CharacterBase.screenX/Y(): Math.floor(...)
 *   Sprite_Picture.updatePosition(): Math.round(picture.x/y)
 *
 * The PSP port used raw fractional GU coordinates instead.  With nearest
 * filtered tiles and the semi-transparent moving A1/Fog layers this causes a
 * one-pixel shimmer that is easiest to notice while an interaction freezes
 * the player and the world is otherwise still.  Keep these tiny helpers
 * local instead of depending on libm just for floor/ceil/round. */
static float render_floor_pixel(float value)
{
    int i = (int)value;
    if (value < 0.0f && (float)i != value) --i;
    return (float)i;
}

static float render_ceil_pixel(float value)
{
    int i = (int)value;
    if (value > 0.0f && (float)i != value) ++i;
    return (float)i;
}

static float render_round_pixel(float value)
{
    return value >= 0.0f
        ? (float)((int)(value + 0.5f))
        : (float)((int)(value - 0.5f));
}

static int clamp_move_speed_code(int speed_code)
{
    if (speed_code < 1) return 1;
    if (speed_code > 6) return 6;
    return speed_code;
}

static int player_real_move_speed(int dashing)
{
    int speed = clamp_move_speed_code(g_player_move_speed_code);
    if (dashing) speed += 1;
    /* MZ can therefore reach real speed 7 when base speed is 6. */
    if (speed > 7) speed = 7;
    return speed;
}

static float move_speed_px_per_frame(int real_speed)
{
    if (real_speed < 1) real_speed = 1;
    if (real_speed > 7) real_speed = 7;
    /* MZ: distancePerFrame = 2^realMoveSpeed / 256 tiles/frame. */
    return (float)TILE_PX * (float)(1 << real_speed) / 256.0f;
}

static int direction_to_row(int direction)
{
    if (direction == 2) return 0;
    if (direction == 4) return 1;
    if (direction == 6) return 2;
    if (direction == 8) return 3;
    return -1;
}

/* ------------------------------------------------------------------------- */
/* Exit callback                                                             */
/* ------------------------------------------------------------------------- */

static int exit_callback(int arg1, int arg2, void *common)
{
    (void)arg1;
    (void)arg2;
    (void)common;
    g_audio_stop = 1;
    sceKernelExitGame();
    return 0;
}

static int callback_thread(SceSize args, void *argp)
{
    (void)args;
    (void)argp;
    int cbid = sceKernelCreateCallback("Exit Callback", exit_callback, NULL);
    sceKernelRegisterExitCallback(cbid);
    sceKernelSleepThreadCB();
    return 0;
}

static void setup_callbacks(void)
{
    int thid = sceKernelCreateThread(
        "Callback Thread", callback_thread, 0x11, 0xFA0, 0, NULL
    );
    if (thid >= 0) sceKernelStartThread(thid, 0, NULL);
}

/* ------------------------------------------------------------------------- */
/* Files                                                                     */
/* ------------------------------------------------------------------------- */

static void fatal_error(const char *message)
{
    pspDebugScreenInit();
    pspDebugScreenClear();
    pspDebugScreenPrintf("\nNARAKU PSP 0.8.5\n\nERROR:\n%s\n", message);
    pspDebugScreenPrintf("\nHOME: exit\n");
    while (1) sceDisplayWaitVblankStart();
}

static void *load_exact_file(const char *path, size_t expected_size)
{
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;

    void *data = memalign(16, expected_size);
    if (!data) {
        fclose(f);
        return NULL;
    }

    size_t got = fread(data, 1, expected_size, f);
    int extra = fgetc(f);
    fclose(f);

    if (got != expected_size || extra != EOF) {
        free(data);
        return NULL;
    }

    sceKernelDcacheWritebackInvalidateAll();
    return data;
}

static void *load_whole_file(const char *path, size_t *out_size)
{
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;

    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return NULL;
    }

    long len = ftell(f);
    if (len <= 0) {
        fclose(f);
        return NULL;
    }

    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }

    void *data = memalign(16, (size_t)len);
    if (!data) {
        fclose(f);
        return NULL;
    }

    size_t got = fread(data, 1, (size_t)len, f);
    fclose(f);

    if (got != (size_t)len) {
        free(data);
        return NULL;
    }

    if (out_size) *out_size = (size_t)len;
    sceKernelDcacheWritebackInvalidateAll();
    return data;
}

/* ------------------------------------------------------------------------- */
/* Graphics                                                                  */
/* ------------------------------------------------------------------------- */

static void init_gu(void)
{
    sceGuInit();
    sceGuStart(GU_DIRECT, gu_list);
    sceGuDrawBuffer(GU_PSM_8888, (void *)0, BUF_W);
    sceGuDispBuffer(SCREEN_W, SCREEN_H, (void *)0x88000, BUF_W);
    sceGuOffset(2048 - SCREEN_W / 2, 2048 - SCREEN_H / 2);
    sceGuViewport(2048, 2048, SCREEN_W, SCREEN_H);
    sceGuScissor(0, 0, SCREEN_W, SCREEN_H);
    sceGuEnable(GU_SCISSOR_TEST);
    sceGuDisable(GU_DEPTH_TEST);
    sceGuEnable(GU_TEXTURE_2D);
    sceGuEnable(GU_BLEND);
    sceGuBlendFunc(GU_ADD, GU_SRC_ALPHA, GU_ONE_MINUS_SRC_ALPHA, 0, 0);
    sceGuTexFilter(GU_LINEAR, GU_LINEAR);
    sceGuTexWrap(GU_CLAMP, GU_CLAMP);
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuClearColor(0xFF000000);
    sceGuFinish();
    sceGuSync(0, 0);
    sceDisplayWaitVblankStart();
    sceGuDisplay(GU_TRUE);
}

static void bind_texture_8888(void *texture, int width, int height)
{
    sceGuTexMode(GU_PSM_8888, 0, 0, GU_FALSE);
    sceGuTexImage(0, width, height, width, texture);
}

/* Pixel-art/world textures must never inherit filtering/wrap state from a
 * previously drawn layer.  PSP GU state persists across draw calls AND across
 * display lists, so the LINEAR filter used by Fog A1/detail pictures could
 * leak into the first map/player draw of the next frame.  On atlas sprites
 * that produces a one-frame dark/light halo around every opaque edge -- most
 * visible exactly when a message box is dismissed before the next one opens. */
static void set_pixel_art_texture_state(void)
{
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    sceGuTexWrap(GU_CLAMP, GU_CLAMP);
    sceGuColor(0xFFFFFFFF);
}

static void draw_bound_rect(
    float src_x, float src_y, float src_w, float src_h,
    float dst_x, float dst_y, float dst_w, float dst_h)
{
    TextureVertex *v = (TextureVertex *)sceGuGetMemory(2 * sizeof(TextureVertex));
    v[0].u = src_x;
    v[0].v = src_y;
    v[0].x = dst_x;
    v[0].y = dst_y;
    v[0].z = 0.0f;

    v[1].u = src_x + src_w;
    v[1].v = src_y + src_h;
    v[1].x = dst_x + dst_w;
    v[1].y = dst_y + dst_h;
    v[1].z = 0.0f;

    sceGuDrawArray(
        GU_SPRITES,
        GU_TEXTURE_32BITF | GU_VERTEX_32BITF | GU_TRANSFORM_2D,
        2, NULL, v
    );
}

static void draw_bound_rect_color(
    float src_x, float src_y, float src_w, float src_h,
    float dst_x, float dst_y, float dst_w, float dst_h,
    uint32_t color)
{
    TextureColorVertex *v =
        (TextureColorVertex *)sceGuGetMemory(2 * sizeof(TextureColorVertex));
    v[0].u = src_x;
    v[0].v = src_y;
    v[0].color = color;
    v[0].x = dst_x;
    v[0].y = dst_y;
    v[0].z = 0.0f;

    v[1].u = src_x + src_w;
    v[1].v = src_y + src_h;
    v[1].color = color;
    v[1].x = dst_x + dst_w;
    v[1].y = dst_y + dst_h;
    v[1].z = 0.0f;

    sceGuDrawArray(
        GU_SPRITES,
        GU_TEXTURE_32BITF | GU_COLOR_8888 | GU_VERTEX_32BITF | GU_TRANSFORM_2D,
        2, NULL, v
    );
}

static void draw_texture_alpha(
    void *texture, int tex_w, int tex_h,
    float src_w, float src_h,
    float x, float y, float w, float h, int alpha)
{
    if (alpha < 0) alpha = 0;
    if (alpha > 255) alpha = 255;

    sceGuTexFunc(GU_TFX_MODULATE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    sceGuTexWrap(GU_CLAMP, GU_CLAMP);
    bind_texture_8888(texture, tex_w, tex_h);

    TextureColorVertex *v =
        (TextureColorVertex *)sceGuGetMemory(2 * sizeof(TextureColorVertex));
    uint32_t color = ((uint32_t)alpha << 24) | 0x00FFFFFFu;

    v[0].u = 0.0f;
    v[0].v = 0.0f;
    v[0].color = color;
    v[0].x = x;
    v[0].y = y;
    v[0].z = 0.0f;

    v[1].u = src_w;
    v[1].v = src_h;
    v[1].color = color;
    v[1].x = x + w;
    v[1].y = y + h;
    v[1].z = 0.0f;

    sceGuDrawArray(
        GU_SPRITES,
        GU_TEXTURE_32BITF | GU_COLOR_8888 | GU_VERTEX_32BITF | GU_TRANSFORM_2D,
        2, NULL, v
    );

    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
}

static void draw_solid_rect(float x, float y, float w, float h, int r, int g, int b, int a)
{
    sceGuDisable(GU_TEXTURE_2D);
    ColorVertex *v = (ColorVertex *)sceGuGetMemory(2 * sizeof(ColorVertex));
    uint32_t color = GU_RGBA(r, g, b, a);

    v[0].color = color;
    v[0].x = x;
    v[0].y = y;
    v[0].z = 0.0f;

    v[1].color = color;
    v[1].x = x + w;
    v[1].y = y + h;
    v[1].z = 0.0f;

    sceGuDrawArray(
        GU_SPRITES,
        GU_COLOR_8888 | GU_VERTEX_32BITF | GU_TRANSFORM_2D,
        2, NULL, v
    );
    sceGuEnable(GU_TEXTURE_2D);
}


/* ------------------------------------------------------------------------- */
/* Runtime UTF-8 font                                                        */
/* ------------------------------------------------------------------------- */

static int init_runtime_font(void)
{
    char path[192];
    int i;

    memset(&g_font, 0, sizeof(g_font));
    snprintf(path, sizeof(path), ASSET_ROOT "font_map.bin");
    g_font.map_bin = (uint8_t *)load_whole_file(path, &g_font.map_size);
    if (!g_font.map_bin || g_font.map_size < FONT_MAP_HEADER_BYTES) return 0;
    if (memcmp(g_font.map_bin, "NF30", 4) != 0) return 0;

    g_font.glyph_count = (int)read_u16_le(g_font.map_bin + 4);
    g_font.page_count = (int)g_font.map_bin[6];
    if (g_font.page_count < 1 || g_font.page_count > FONT_MAX_PAGES) return 0;
    if ((int)g_font.map_bin[7] != FONT_CELL_W ||
        (int)g_font.map_bin[8] != FONT_CELL_H ||
        (int)g_font.map_bin[9] != FONT_COLS) return 0;
    if (g_font.map_size != FONT_MAP_HEADER_BYTES +
        (size_t)g_font.glyph_count * FONT_GLYPH_BYTES) return 0;

    for (i = 0; i < 256; ++i)
        g_font.clut[i] = ((uint32_t)i << 24) | 0x00FFFFFFu;

    for (i = 0; i < g_font.page_count; ++i) {
        snprintf(path, sizeof(path), ASSET_ROOT "font_page%d.t8", i);
        g_font.pages[i] = load_exact_file(path, FONT_PAGE_BYTES);
        if (!g_font.pages[i]) return 0;
    }
    return 1;
}

static const uint8_t *font_find_glyph(uint32_t cp)
{
    int lo = 0;
    int hi = g_font.glyph_count - 1;
    const uint8_t *base = g_font.map_bin + FONT_MAP_HEADER_BYTES;

    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        const uint8_t *rec = base + (size_t)mid * FONT_GLYPH_BYTES;
        uint32_t rcp = read_u32_le(rec);
        if (rcp == cp) return rec;
        if (rcp < cp) lo = mid + 1;
        else hi = mid - 1;
    }
    return NULL;
}

static uint32_t utf8_next_cp(const char **pp, const char *end)
{
    const unsigned char *p = (const unsigned char *)*pp;
    uint32_t cp;
    if ((const char *)p >= end) return 0;
    if (p[0] < 0x80) {
        *pp = (const char *)(p + 1);
        return p[0];
    }
    if ((p[0] & 0xE0) == 0xC0 && (const char *)(p + 1) < end) {
        cp = ((uint32_t)(p[0] & 0x1F) << 6) | (uint32_t)(p[1] & 0x3F);
        *pp = (const char *)(p + 2);
        return cp;
    }
    if ((p[0] & 0xF0) == 0xE0 && (const char *)(p + 2) < end) {
        cp = ((uint32_t)(p[0] & 0x0F) << 12) |
             ((uint32_t)(p[1] & 0x3F) << 6) |
             (uint32_t)(p[2] & 0x3F);
        *pp = (const char *)(p + 3);
        return cp;
    }
    if ((p[0] & 0xF8) == 0xF0 && (const char *)(p + 3) < end) {
        cp = ((uint32_t)(p[0] & 0x07) << 18) |
             ((uint32_t)(p[1] & 0x3F) << 12) |
             ((uint32_t)(p[2] & 0x3F) << 6) |
             (uint32_t)(p[3] & 0x3F);
        *pp = (const char *)(p + 4);
        return cp;
    }
    *pp = (const char *)(p + 1);
    return (uint32_t)'?';
}

/* Exact 0..31 text palette sampled from NARAKU's original Window.png. */
static const uint8_t g_text_palette[32][3] = {
    {255,255,255},{32,160,214},{255,120,76},{102,204,64},
    {153,204,255},{204,192,255},{255,255,160},{128,128,128},
    {192,192,192},{32,128,204},{255,56,16},{0,160,16},
    {62,154,222},{160,152,255},{255,204,32},{0,0,0},
    {132,170,255},{255,255,64},{255,32,32},{32,32,64},
    {224,128,64},{240,192,64},{64,128,192},{64,192,240},
    {128,255,128},{192,128,128},{128,128,255},{255,128,255},
    {0,160,64},{0,224,96},{160,96,224},{192,128,255}
};

static void bind_font_page_color(int page, int r, int g, int b)
{
    int i;
    if (page < 0 || page >= g_font.page_count || !g_font.pages[page]) return;
    for (i = 0; i < 256; ++i)
        g_font.clut[i] = ((uint32_t)i << 24) |
                         ((uint32_t)(b & 255) << 16) |
                         ((uint32_t)(g & 255) << 8) |
                         (uint32_t)(r & 255);
    /* Recolouring the CLUT happens in cached CPU memory.  Flush it before
     * handing the palette to the GU; otherwise the PSP can keep using the
     * previous white palette and \\c[n] escapes look uncoloured. */
    sceKernelDcacheWritebackRange(g_font.clut, sizeof(g_font.clut));
    sceGuClutMode(GU_PSM_8888, 0, 0xFF, 0);
    sceGuClutLoad(32, g_font.clut);
    sceGuTexMode(GU_PSM_T8, 0, 0, GU_FALSE);
    sceGuTexImage(0, FONT_TEX_W, FONT_TEX_H, FONT_TEX_W, g_font.pages[page]);
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
}

static void bind_font_page(int page)
{
    bind_font_page_color(page, 255, 255, 255);
}

static float draw_glyph_cp_color(uint32_t cp, float x, float y, int r, int g, int b)
{
    const uint8_t *rec = font_find_glyph(cp);
    int page;
    int slot;
    int sx;
    int sy;
    int adv;

    if (!rec) rec = font_find_glyph((uint32_t)'?');
    if (!rec) return 7.5f;

    page = (int)rec[4];
    slot = (int)read_u16_le(rec + 5);
    adv = (int)rec[7];
    sx = (slot % FONT_COLS) * FONT_CELL_W;
    sy = (slot / FONT_COLS) * FONT_CELL_H;

    /* Keep the indexed font palette white/alpha-only and tint the glyph with
     * a vertex colour.  Re-loading a recoloured CLUT for every character was
     * unreliable on real PSP/GU and PPSSPP: \c[n] escapes parsed correctly,
     * but the cached white palette could still win.  Vertex modulation is the
     * same colour path used by the rest of the renderer and is deterministic. */
    bind_font_page_color(page, 255, 255, 255);
    sceGuTexFunc(GU_TFX_MODULATE, GU_TCC_RGBA);
    sceGuTexFilter(GU_LINEAR, GU_LINEAR);
    draw_bound_rect_color(
        (float)sx, (float)sy, (float)adv, (float)FONT_CELL_H,
        x, y + 3.5f, adv * 0.75f, FONT_CELL_H * 0.75f,
        0xFF000000u | ((uint32_t)(b & 255) << 16) |
        ((uint32_t)(g & 255) << 8) | (uint32_t)(r & 255)
    );
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    return adv * 0.75f;
}

static int draw_glyph_cp(uint32_t cp, float x, float y)
{
    return draw_glyph_cp_color(cp, x, y, 255, 255, 255);
}

static int parse_text_color_escape(const char **pp, const char *end, int *out_index)
{
    const char *p = *pp;
    int value = 0;
    int digits = 0;
    if (p + 3 >= end || p[0] != '\\' || (p[1] != 'c' && p[1] != 'C') || p[2] != '[')
        return 0;
    p += 3;
    while (p < end && *p >= '0' && *p <= '9') {
        value = value * 10 + (*p - '0');
        ++p;
        ++digits;
    }
    if (!digits || p >= end || *p != ']') return 0;
    ++p;
    if (value < 0) value = 0;
    if (value > 31) value = 31;
    *out_index = value;
    *pp = p;
    return 1;
}


static void rasterize_glyph_to_message_surface(
    uint32_t cp, int dst_x, int dst_y, int color_index, float scale)
{
    const uint8_t *rec = font_find_glyph(cp);
    const uint8_t *page_data;
    int page, slot, sx, sy, adv;
    int x, y;
    int r, g, b;

    /* Cache at twice screen resolution; downsample only when drawing. */
    dst_x = (dst_x - MESSAGE_SURFACE_X) * MESSAGE_SURFACE_SCALE;
    dst_y *= MESSAGE_SURFACE_SCALE;
    scale *= MESSAGE_SURFACE_SCALE;
    if (!g_runtime_message_surface) return;
    if (!rec) rec = font_find_glyph((uint32_t)'?');
    if (!rec) return;

    page = (int)rec[4];
    slot = (int)read_u16_le(rec + 5);
    adv = (int)rec[7];
    if (page < 0 || page >= g_font.page_count || !g_font.pages[page]) return;
    if (color_index < 0) color_index = 0;
    if (color_index > 31) color_index = 31;

    sx = (slot % FONT_COLS) * FONT_CELL_W;
    sy = (slot / FONT_COLS) * FONT_CELL_H;
    page_data = (const uint8_t *)g_font.pages[page];
    r = g_text_palette[color_index][0];
    g = g_text_palette[color_index][1];
    b = g_text_palette[color_index][2];

    /* Sample the source alpha at destination pixel centres, just like the
     * linearly filtered menu font. Keep the cached RGBA surface so inline
     * colours remain deterministic and no per-frame glyph work is added. */
    for (y = 0; y < (int)(FONT_CELL_H * scale); ++y) {
        int py = dst_y + y;
        float fy = (y + 0.5f) / scale - 0.5f;
        int iy = (int)fy;
        float wy = fy - iy;
        if (py < 0 || py >= MESSAGE_SURFACE_H) continue;
        for (x = 0; x < (int)(adv * scale); ++x) {
            int px = dst_x + x;
            float fx = (x + 0.5f) / scale - 0.5f;
            int ix = (int)fx;
            float wx = fx - ix;
            float alpha = 0.0f;
            int dx, dy, qx, qy;
            uint8_t a;
            if (px < 0 || px >= MESSAGE_SURFACE_W) continue;
            /* Four subpixel samples preserve thin stems when reducing. */
            for (qy = 0; qy < 2; ++qy) {
                for (qx = 0; qx < 2; ++qx) {
                    fx = (x + 0.25f + qx * 0.5f) / scale - 0.5f;
                    fy = (y + 0.25f + qy * 0.5f) / scale - 0.5f;
                    ix = (int)fx; iy = (int)fy;
                    if (fx < ix) --ix;
                    if (fy < iy) --iy;
                    wx = fx - ix; wy = fy - iy;
                    for (dy = 0; dy < 2; ++dy) {
                        for (dx = 0; dx < 2; ++dx) {
                            int sample_x = ix + dx, sample_y = iy + dy;
                            if (sample_x >= 0 && sample_x < adv &&
                                sample_y >= 0 && sample_y < FONT_CELL_H)
                                alpha += 0.25f * page_data[(sy + sample_y) * FONT_TEX_W + sx + sample_x] *
                                    (dx ? wx : 1.0f - wx) * (dy ? wy : 1.0f - wy);
                        }
                    }
                }
            }
            a = (uint8_t)(alpha + 0.5f);
            if (a == 0) continue;
            g_runtime_message_surface[py * MESSAGE_SURFACE_W + px] =
                ((uint32_t)a << 24) | ((uint32_t)b << 16) |
                ((uint32_t)g << 8) | (uint32_t)r;
        }
    }
}

static int latin_word_cp(uint32_t cp)
{
    return (cp >= 'A' && cp <= 'Z') || (cp >= 'a' && cp <= 'z') ||
           (cp >= '0' && cp <= '9') || cp == '\'' || cp == '-';
}

static int latin_word_width(const char *p, const char *end)
{
    int width = 0, color = 0;
    while (p < end) {
        uint32_t cp;
        const uint8_t *rec;
        if (parse_text_color_escape(&p, end, &color)) continue;
        cp = utf8_next_cp(&p, end);
        if (!latin_word_cp(cp)) break;
        rec = font_find_glyph(cp);
        if (!rec) rec = font_find_glyph('?');
        width += rec ? rec[7] : 10;
    }
    return width;
}

static int message_word_width(const char *p, const char *end, float scale)
{
    int width = 0, color = 0;
    while (p < end) {
        const uint8_t *rec;
        uint32_t cp;
        if (parse_text_color_escape(&p, end, &color)) continue;
        cp = utf8_next_cp(&p,end);
        if (!latin_word_cp(cp)) break;
        rec = font_find_glyph(cp);
        if (!rec) rec = font_find_glyph('?');
        width += rec ? (int)(rec[7] * scale) : 5;
    }
    return width;
}

static void rasterize_utf8_wrapped_to_message_surface(
    const char *text, size_t len,
    int start_x, int start_y, int max_x, int max_lines, float scale)
{
    const char *p = text;
    const char *end = text + len;
    int x = start_x;
    int y = start_y;
    int line = 0;
    int color_index = 0;
    int in_word = 0;

    while (p < end && line < max_lines) {
        const char *before = p;
        uint32_t cp;
        const uint8_t *rec;
        int adv;
        int parsed_color = color_index;

        if (parse_text_color_escape(&p, end, &parsed_color)) {
            color_index = parsed_color;
            continue;
        }

        cp = utf8_next_cp(&p, end);
        if (latin_word_cp(cp) && !in_word) {
            int width = message_word_width(before, end, scale);
            if (width <= max_x - start_x && x + width > max_x && x > start_x) {
                x = start_x; y += 14; ++line;
                if (line >= max_lines) break;
            }
        }
        in_word = latin_word_cp(cp);
        if (cp == '\r') continue;
        if (cp == '\n') {
            x = start_x;
            y += 14;
            ++line;
            continue;
        }

        rec = font_find_glyph(cp);
        if (!rec) rec = font_find_glyph((uint32_t)'?');
        adv = rec ? (int)(rec[7] * scale) : 5;

        if (x + adv > max_x && x > start_x) {
            x = start_x;
            y += 14;
            ++line;
            if (line >= max_lines) break;
        }

        if (cp == ' ')
            x += adv;
        else {
            rasterize_glyph_to_message_surface(cp, x, y, color_index, scale);
            x += adv;
        }

        if (p == before) break;
    }
}

/* Original ITB_ResizeMessageWindow: 54% width, three rows, bottom anchored.
 * Scale its 816x624 layout onto the PSP screen; text is top/left aligned. */
#define MESSAGE_BOX_X 110
#define MESSAGE_BOX_Y 210
#define MESSAGE_BOX_W 260
#define MESSAGE_BOX_H 62
#define MESSAGE_NAME_H 26
static int runtime_message_text_y(void) { return MESSAGE_BOX_Y + 8; }

static int runtime_speaker_width(void)
{
    const char *p = g_runtime_speaker, *end = p ? p + g_runtime_speaker_len : p;
    int width = 16, color = 0;
    while (p && p < end) {
        const uint8_t *rec;
        if (parse_text_color_escape(&p, end, &color)) continue;
        rec = font_find_glyph(utf8_next_cp(&p, end));
        width += rec ? (int)(rec[7] * 0.75f) : 5;
    }
    return width > MESSAGE_BOX_W ? MESSAGE_BOX_W : width;
}

static void rebuild_runtime_message_surface(void)
{
    const int top = MESSAGE_BOX_Y;
    if (!g_runtime_message_surface) {
        g_runtime_message_surface = (uint32_t *)memalign(16, MESSAGE_SURFACE_BYTES);
        if (!g_runtime_message_surface) {
            g_runtime_message_surface_ready = 0;
            return;
        }
    }

    memset(g_runtime_message_surface, 0, MESSAGE_SURFACE_BYTES);

    if (g_runtime_speaker && g_runtime_speaker_len > 0) {
        rasterize_utf8_wrapped_to_message_surface(
            g_runtime_speaker, g_runtime_speaker_len,
            MESSAGE_BOX_X + 8, (top - MESSAGE_NAME_H + 5) - MESSAGE_SURFACE_Y,
            MESSAGE_BOX_X + runtime_speaker_width() - 6, 1, 0.75f
        );
    }
    if (g_runtime_message && g_runtime_message_len > 0) {
        rasterize_utf8_wrapped_to_message_surface(
            g_runtime_message, g_runtime_message_len,
            MESSAGE_BOX_X + 9, runtime_message_text_y() - MESSAGE_SURFACE_Y,
            MESSAGE_BOX_X + MESSAGE_BOX_W - 9, 3, 0.55f
        );
    }

    sceKernelDcacheWritebackRange(g_runtime_message_surface, MESSAGE_SURFACE_BYTES);
    g_runtime_message_surface_ready = 1;
}

static void draw_utf8_wrapped(
    const char *text, size_t len,
    float start_x, float start_y, float max_x, int max_lines)
{
    const char *p = text;
    const char *end = text + len;
    float x = start_x;
    float y = start_y;
    int line = 0;
    int color_index = 0;
    int in_word = 0;

    while (p < end && line < max_lines) {
        const char *before = p;
        uint32_t cp;
        const uint8_t *rec;
        float adv;
        int parsed_color;

        parsed_color = color_index;
        if (parse_text_color_escape(&p, end, &parsed_color)) {
            color_index = parsed_color;
            continue;
        }

        cp = utf8_next_cp(&p, end);
        if (latin_word_cp(cp) && !in_word) {
            float width = latin_word_width(before, end) * 0.75f;
            if (width <= max_x - start_x && x + width > max_x && x > start_x) {
                x = start_x; y += 25; ++line;
                if (line >= max_lines) break;
            }
        }
        in_word = latin_word_cp(cp);
        if (cp == '\r') continue;
        if (cp == '\n') {
            x = start_x;
            y += 25.0f;
            line++;
            continue;
        }

        rec = font_find_glyph(cp);
        if (!rec) rec = font_find_glyph((uint32_t)'?');
        adv = (rec ? (int)rec[7] : 10) * 0.75f;

        if (x + adv > max_x && x > start_x) {
            x = start_x;
            y += 25.0f;
            line++;
            if (line >= max_lines) break;
        }

        if (cp == ' ') {
            x += adv;
        } else {
            const uint8_t *rgb = g_text_palette[color_index];
            x += (float)draw_glyph_cp_color(cp, x, y, rgb[0], rgb[1], rgb[2]);
        }

        if (p == before) break;
    }
}

static void draw_naraku_window(float x, float y, float w, float h, int alpha)
{
    /* NARAKU's PC windows are almost-black with a thin blood-red frame.
     * Keep that identity at 480x272 instead of the generic blue/grey PSP box. */
    draw_solid_rect(x, y, w, h, 10, 2, 4, alpha);
    draw_solid_rect(x, y, w, 2.0f, 210, 0, 0, 255);
    draw_solid_rect(x, y + h - 2.0f, w, 2.0f, 210, 0, 0, 255);
    draw_solid_rect(x, y, 2.0f, h, 210, 0, 0, 255);
    draw_solid_rect(x + w - 2.0f, y, 2.0f, h, 210, 0, 0, 255);
    draw_solid_rect(x + 3.0f, y + 3.0f, w - 6.0f, 1.0f, 70, 0, 0, 230);
}

/* Scale the frame itself, including horizontal border thickness, just like
 * MZ Window._container.scale.y. Text lives outside that scaled container. */
static void draw_message_window_reveal(float x, float y, float w, float h, int alpha)
{
    float scale = g_runtime_message_openness / 255.0f;
    float height = h * scale;
    y += (h - height) * 0.5f;
    draw_solid_rect(x, y, w, height, 10, 2, 4, alpha);
    draw_solid_rect(x, y, w, 2.0f * scale, 210, 0, 0, 255);
    draw_solid_rect(x, y + height - 2.0f * scale, w, 2.0f * scale, 210, 0, 0, 255);
    draw_solid_rect(x, y, 2.0f, height, 210, 0, 0, 255);
    draw_solid_rect(x + w - 2.0f, y, 2.0f, height, 210, 0, 0, 255);
    draw_solid_rect(x + 3.0f, y + 3.0f * scale, w - 6.0f, scale, 70, 0, 0, 230);
}

static int g_choice_window_width = 96;

static void rebuild_choice_text_surface(void)
{
    int i, width = 0;
    for (i = 0; i < g_choice_count; ++i) {
        const char *p = g_choice_labels[i], *end = p + g_choice_lengths[i];
        int line_width = 0, color = 0;
        while (p < end) {
            const uint8_t *rec;
            if (parse_text_color_escape(&p, end, &color)) continue;
            rec = font_find_glyph(utf8_next_cp(&p, end));
            if (!rec) rec = font_find_glyph('?');
            line_width += rec ? (int)(rec[7] * 0.55f) : 5;
        }
        if (line_width > width) width = line_width;
    }
    g_choice_window_width = width + 24;
    if (g_choice_window_width < 96) g_choice_window_width = 96;
    if (g_choice_window_width > SCREEN_W) g_choice_window_width = SCREEN_W;
}

static void draw_choice_text(int index, float x, float y)
{
    const char *p = g_choice_labels[index], *end = p + g_choice_lengths[index];
    int color = 0;
    while (p < end) {
        const uint8_t *rec;
        int slot, adv;
        uint32_t tint;
        if (parse_text_color_escape(&p, end, &color)) continue;
        rec = font_find_glyph(utf8_next_cp(&p, end));
        if (!rec) rec = font_find_glyph('?');
        if (!rec) continue;
        slot = read_u16_le(rec + 5); adv = rec[7];
        bind_font_page_color(rec[4], 255, 255, 255);
        sceGuTexFunc(GU_TFX_MODULATE, GU_TCC_RGBA);
        sceGuTexFilter(GU_LINEAR, GU_LINEAR);
        tint = 0xff000000u | g_text_palette[color][0] |
            (g_text_palette[color][1] << 8) | (g_text_palette[color][2] << 16);
        draw_bound_rect_color((slot % FONT_COLS) * FONT_CELL_W,
            (slot / FONT_COLS) * FONT_CELL_H, adv, FONT_CELL_H,
            x, y, adv * 0.55f, FONT_CELL_H * 0.55f, tint);
        x += (int)(adv * 0.55f);
    }
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
}

static void draw_runtime_choice_overlay(void)
{
    int i;
    float h, x, y;
    if (!g_choice_active) return;
    h = g_choice_count * 16 + 12;
    x = SCREEN_W - g_choice_window_width;
    /* Original Window_ChoiceList.windowY anchors above the bottom message box,
     * even when that box is currently closed. Default choice position is right. */
    y = MESSAGE_BOX_Y - h;
    if (y < 0) y = 0;
    draw_naraku_window(x, y, g_choice_window_width, h, g_window_opacity);
    for (i = 0; i < g_choice_count; ++i) {
        if (i == g_choice_cursor)
            draw_solid_rect(x + 5, y + 6 + i * 16,
                g_choice_window_width - 10, 16, 160, 0, 0, 150);
    }
    for (i = 0; i < g_choice_count; ++i)
        draw_choice_text(i, x + 10, y + 6 + i * 16);
}

/* Original number-input command, adapted to the PSP direction buttons. */
static void draw_runtime_number_overlay(void)
{
    int i, divisor=1;
    float w=g_number_digits*20+24,x=(SCREEN_W-w)*0.5f,y=MESSAGE_BOX_Y-38;
    if(!g_number_active)return;
    draw_naraku_window(x,y,w,36,g_window_opacity);
    draw_solid_rect(x+12+g_number_cursor*20,y+8,20,20,160,0,0,150);
    for(i=1;i<g_number_digits;++i)divisor*=10;
    for(i=0;i<g_number_digits;++i) {
        const uint8_t *rec=font_find_glyph('0'+(g_number_value/divisor)%10);
        if(rec) {
            int slot=read_u16_le(rec+5),adv=rec[7];
            bind_font_page_color(rec[4],255,255,255);
            sceGuTexFunc(GU_TFX_MODULATE,GU_TCC_RGBA);
            sceGuTexFilter(GU_LINEAR,GU_LINEAR);
            draw_bound_rect_color((slot%FONT_COLS)*FONT_CELL_W,(slot/FONT_COLS)*FONT_CELL_H,
                adv,FONT_CELL_H,x+12+i*20+(20-adv*0.75f)*0.5f,y+7,adv*0.75f,FONT_CELL_H*0.75f,0xffffffffu);
        }
        divisor/=10;
    }
    set_pixel_art_texture_state();
}

static void draw_runtime_message_overlay(void)
{
    float top;
    int has_speaker;
    if (!g_runtime_message_active || g_runtime_message_openness <= 0) return;

    has_speaker = g_runtime_speaker && g_runtime_speaker_len > 0;
    top = MESSAGE_BOX_Y;

    draw_message_window_reveal(MESSAGE_BOX_X, top, MESSAGE_BOX_W,
                               MESSAGE_BOX_H, g_window_opacity);

    if (has_speaker) {
        /* Separate name plate, matching the small bordered speaker box in the
         * original rather than consuming the first line of the message box. */
        draw_message_window_reveal(MESSAGE_BOX_X, top - MESSAGE_NAME_H,
                                   runtime_speaker_width(), MESSAGE_NAME_H,
                                   g_window_opacity);
    }

    if (g_runtime_message_openness < 255) return;

    /* High-resolution RGBA cache preserves inline colours and lets the GU
     * filter the final reduction, matching the smoothly scaled menu font. */
    if (g_runtime_message_surface_ready && g_runtime_message_surface) {
        bind_texture_8888(g_runtime_message_surface, MESSAGE_SURFACE_W, MESSAGE_SURFACE_H);
        sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
        sceGuTexFilter(GU_LINEAR, GU_LINEAR);
        sceGuColor(0xFFFFFFFF);
        draw_bound_rect(
            0.0f, 0.0f, MESSAGE_SURFACE_W, MESSAGE_SURFACE_H,
            MESSAGE_SURFACE_X, MESSAGE_SURFACE_Y,
            MESSAGE_SURFACE_W / MESSAGE_SURFACE_SCALE,
            MESSAGE_SURFACE_H / MESSAGE_SURFACE_SCALE
        );
        sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    } else {
        if (has_speaker)
            draw_utf8_wrapped(g_runtime_speaker, g_runtime_speaker_len,
                              MESSAGE_BOX_X + 8, top - MESSAGE_NAME_H + 5,
                              MESSAGE_BOX_X + runtime_speaker_width() - 6, 1);
        if (g_runtime_message && g_runtime_message_len > 0)
            draw_utf8_wrapped(g_runtime_message, g_runtime_message_len,
                              MESSAGE_BOX_X + 9, runtime_message_text_y(),
                              MESSAGE_BOX_X + MESSAGE_BOX_W - 9, 3);
    }

}

static void render_picture_frame(void *texture, int alpha)
{
    sceGuStart(GU_DIRECT, gu_list);
    sceGuClearColor(0xFF000000);
    sceGuClear(GU_COLOR_BUFFER_BIT);
    draw_texture_alpha(
        texture, PIC_TEX_W, PIC_TEX_H,
        (float)SCREEN_W, (float)SCREEN_H,
        0.0f, 0.0f, (float)SCREEN_W, (float)SCREEN_H, alpha
    );
    sceGuFinish();
    sceGuSync(0, 0);
    sceDisplayWaitVblankStart();
    g_draw_buffer = sceGuSwapBuffers();
}

static void fade_picture(void *texture, int from, int to, int frames)
{
    int i;
    if (frames <= 0) {
        render_picture_frame(texture, to);
        return;
    }
    for (i = 0; i < frames; ++i) {
        int a = from + (to - from) * i / frames;
        render_picture_frame(texture, a);
    }
    render_picture_frame(texture, to);
}

/* ------------------------------------------------------------------------- */
/* Input / language                                                          */
/* ------------------------------------------------------------------------- */

static void wait_cross(void)
{
    SceCtrlData pad;
    uint32_t prev;
    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;

    while (1) {
        sceCtrlPeekBufferPositive(&pad, 1);
        if ((pad.Buttons & ~prev) & PSP_CTRL_CROSS) return;
        prev = pad.Buttons;
        sceDisplayWaitVblankStart();
    }
}

/* PPSSPP can report no buttons during the very first frame after launch.
 * Sample a short startup window so SELECT/TRIANGLE are reliable. */
static uint32_t read_boot_hotkeys(void)
{
    SceCtrlData pad;
    uint32_t seen = 0;
    int i;

    for (i = 0; i < 36; ++i) {
        sceCtrlPeekBufferPositive(&pad, 1);
        seen |= pad.Buttons;
        sceDisplayWaitVblankStart();
    }
    return seen;
}

static void config_defaults(void)
{
    g_language = 0;
    g_always_dash = 0;
    g_bgm_volume = 75;
    g_se_volume = 75;
    g_window_opacity = 195;
    g_map5_key_migration_done = 1;
    g_config_valid = 0;
}

static void save_config(void);

static int load_config(void)
{
    FILE *f;
    unsigned char b[16];
    size_t n;
    config_defaults();
    f = fopen(CONFIG_PATH, "rb");
    if (!f) return 0;
    n = fread(b, 1, sizeof(b), f);
    fclose(f);

    if (n >= 10 && memcmp(b, "NPS9", 4) == 0) {
        if (b[4] <= 3) g_language = (int)b[4];
        g_always_dash = b[5] ? 1 : 0;
        g_bgm_volume = b[6] <= 100 ? (int)b[6] : 75;
        g_se_volume = b[7] <= 100 ? (int)b[7] : 75;
        g_window_opacity = b[8] >= 64 ? (int)b[8] : 195;
        g_map5_key_migration_done = b[9] ? 1 : 0;
        g_config_valid = 1;
        return 1;
    }
    if (n >= 10 && memcmp(b, "NPS8", 4) == 0) {
        if (b[4] <= 3) g_language = (int)b[4];
        g_always_dash = b[5] ? 1 : 0;
        g_bgm_volume = b[6] <= 100 ? (int)b[6] : 75;
        g_se_volume = b[7] <= 100 ? (int)b[7] : 75;
        g_window_opacity = b[8] >= 64 ? (int)b[8] : 195;
        /* Old test saves may have picked the invisible Red Key.  Keep the
         * migration pending across restarts until Map005 is actually loaded. */
        g_map5_key_migration_done = 0;
        g_config_valid = 1;
        save_config();
        return 1;
    }
    if (n >= 10 && memcmp(b, "NPS7", 4) == 0) {
        /* 0.6.0/0.6.1 could accidentally persist Japanese/Chinese while the
         * title was still English.  Migrate once to an English baseline,
         * preserving the user's other option values.  From NPS8 onward the
         * language is a normal persistent user preference. */
        g_language = 0;
        g_always_dash = b[5] ? 1 : 0;
        g_bgm_volume = b[6] <= 100 ? (int)b[6] : 75;
        g_se_volume = b[7] <= 100 ? (int)b[7] : 75;
        g_window_opacity = b[8] >= 64 ? (int)b[8] : 195;
        g_map5_key_migration_done = 0;
        g_config_valid = 1;
        save_config();
        return 1;
    }
    if (n >= 5 && memcmp(b, "NPS6", 4) == 0) {
        g_language = 0;
        g_map5_key_migration_done = 0;
        g_config_valid = 1;
        save_config();
        return 1;
    }
    return 0;
}

static void save_config(void)
{
    FILE *f;
    unsigned char b[16];
    memset(b, 0, sizeof(b));
    memcpy(b, "NPS9", 4);
    b[4] = (unsigned char)g_language;
    b[5] = (unsigned char)(g_always_dash ? 1 : 0);
    b[6] = (unsigned char)g_bgm_volume;
    b[7] = (unsigned char)g_se_volume;
    b[8] = (unsigned char)g_window_opacity;
    b[9] = (unsigned char)(g_map5_key_migration_done ? 1 : 0);
    f = fopen(CONFIG_PATH, "wb");
    if (!f) return;
    fwrite(b, 1, sizeof(b), f);
    fclose(f);
    g_config_valid = 1;
}

static int load_saved_language(void)
{
    load_config();
    return g_config_valid ? g_language : -1;
}

static void save_language(int lang)
{
    if (lang < 0) lang = 0;
    if (lang > 3) lang = 3;
    g_language = lang;
    save_config();
}

static uint32_t ui_ok_mask(void)
{
    return PSP_CTRL_CROSS;
}

static uint32_t ui_cancel_mask(void)
{
    return PSP_CTRL_CIRCLE;
}

static int choose_language(int selected)
{
    SceCtrlData pad;
    uint32_t prev = 0;
    const char *names[4] = {
        "English",
        "Japanese",
        "Simplified Chinese",
        "Traditional Chinese"
    };

    if (selected < 0 || selected > 3) selected = 0;
    pspDebugScreenInit();
    sceCtrlSetSamplingCycle(0);
    sceCtrlSetSamplingMode(PSP_CTRL_MODE_ANALOG);

    while (1) {
        int i;
        pspDebugScreenClear();
        pspDebugScreenSetXY(0, 1);
        pspDebugScreenPrintf("NARAKU PSP 0.8.5\n\n");
        pspDebugScreenPrintf("Choose language:\n\n");

        for (i = 0; i < 4; ++i)
            pspDebugScreenPrintf("%c %s\n", i == selected ? '>' : ' ', names[i]);

        pspDebugScreenPrintf("\nD-PAD: select   X: confirm\n");

        sceCtrlPeekBufferPositive(&pad, 1);
        {
            uint32_t pressed = pad.Buttons & ~prev;
            if (pressed & PSP_CTRL_UP) selected = (selected + 3) & 3;
            if (pressed & PSP_CTRL_DOWN) selected = (selected + 1) & 3;
            if (pressed & PSP_CTRL_CROSS) {
                save_language(selected);
                do {
                    sceCtrlPeekBufferPositive(&pad, 1);
                    sceDisplayWaitVblankStart();
                } while (pad.Buttons & PSP_CTRL_CROSS);
                return selected;
            }
        }
        prev = pad.Buttons;
        sceDisplayWaitVblankStart();
    }
}

static const char *lang_tag(int lang)
{
    switch (lang) {
        case 1: return "ja";
        case 2: return "zhcn";
        case 3: return "zhtw";
        default: return "en";
    }
}

/* ------------------------------------------------------------------------- */
/* Audio                                                                     */
/* ------------------------------------------------------------------------- */

static void set_bgm_track(const char *path)
{
    if (!path) path = "";
    strncpy(g_bgm_path, path, sizeof(g_bgm_path) - 1);
    g_bgm_path[sizeof(g_bgm_path) - 1] = '\0';
    g_bgm_fade_us = 0;
    g_bgm_generation++;
}

static int bgm_thread(SceSize args, void *argp)
{
    FILE *f = NULL;
    int channel;
    int16_t *buffer;
    int seen_generation = -1;
    int fade_stopped = 0;

    (void)args;
    (void)argp;

    channel = sceAudioChReserve(
        PSP_AUDIO_NEXT_CHANNEL, AUDIO_FRAMES, PSP_AUDIO_FORMAT_STEREO
    );
    if (channel < 0) return 0;

    buffer = (int16_t *)memalign(64, AUDIO_BYTES);
    if (!buffer) {
        sceAudioChRelease(channel);
        return 0;
    }

    while (!g_audio_stop) {
        if (seen_generation != g_bgm_generation) {
            char path[192];
            if (f) { fclose(f); f = NULL; }
            strncpy(path, g_bgm_path, sizeof(path) - 1);
            path[sizeof(path) - 1] = '\0';
            seen_generation = g_bgm_generation;
            fade_stopped = 0;
            if (path[0]) f = fopen(path, "rb");
        }

        if (!f || fade_stopped) {
            sceKernelDelayThread(10000);
            continue;
        }

        {
            size_t got = fread(buffer, 1, AUDIO_BYTES, f);
            if (got < AUDIO_BYTES) {
                if (feof(f)) {
                    size_t more;
                    fseek(f, 0, SEEK_SET);
                    more = fread((uint8_t *)buffer + got, 1, AUDIO_BYTES - got, f);
                    got += more;
                }
                if (got < AUDIO_BYTES)
                    memset((uint8_t *)buffer + got, 0, AUDIO_BYTES - got);
            }
            {
                int vol = PSP_AUDIO_VOLUME_MAX * g_bgm_volume / 100;
                if (vol < 0) vol = 0;
                if (vol > PSP_AUDIO_VOLUME_MAX) vol = PSP_AUDIO_VOLUME_MAX;
                if (g_bgm_fade_us && g_bgm_fade_generation == seen_generation) {
                    unsigned long long elapsed = sceKernelGetSystemTimeWide() - g_bgm_fade_start;
                    unsigned long long duration = g_bgm_fade_us;
                    if (elapsed >= duration) { vol = 0; fade_stopped = 1; }
                    else vol = (int)((unsigned long long)vol * (duration - elapsed) / duration);
                }
                sceAudioOutputBlocking(channel, vol, buffer);
            }
        }
    }

    if (f) fclose(f);
    free(buffer);
    sceAudioChRelease(channel);
    return 0;
}

static void start_bgm(void)
{
    int thid = sceKernelCreateThread(
        "NARAKU BGM", bgm_thread, 0x12, 0x2000, 0, NULL
    );
    if (thid >= 0) sceKernelStartThread(thid, 0, NULL);
}

static int se_thread(SceSize args, void *argp)
{
    int generation;
    SeJob *job;
    FILE *f;
    int channel;
    int16_t *buffer;

    if (args < sizeof(SeJob) || !argp) sceKernelExitDeleteThread(0);
    job = (SeJob *)argp;
    generation = job->generation;
    f = fopen(job->path, "rb");
    if (!f) sceKernelExitDeleteThread(0);

    channel = sceAudioChReserve(
        PSP_AUDIO_NEXT_CHANNEL, AUDIO_FRAMES, PSP_AUDIO_FORMAT_STEREO
    );
    if (channel < 0) {
        fclose(f);
        sceKernelExitDeleteThread(0);
    }

    buffer = (int16_t *)memalign(64, AUDIO_BYTES);
    if (!buffer) {
        sceAudioChRelease(channel);
        fclose(f);
        sceKernelExitDeleteThread(0);
    }

    while (!g_audio_stop && generation == g_se_generation) {
        size_t got = fread(buffer, 1, AUDIO_BYTES, f);
        if (got == 0) break;
        if (got < AUDIO_BYTES)
            memset((uint8_t *)buffer + got, 0, AUDIO_BYTES - got);
        {
            int vol = PSP_AUDIO_VOLUME_MAX * g_se_volume / 100;
            if (vol < 0) vol = 0;
            if (vol > PSP_AUDIO_VOLUME_MAX) vol = PSP_AUDIO_VOLUME_MAX;
            sceAudioOutputBlocking(channel, vol, buffer);
        }
        if (got < AUDIO_BYTES) break;
    }

    free(buffer);
    sceAudioChRelease(channel);
    fclose(f);
    sceKernelExitDeleteThread(0);
    return 0;
}

static void play_se_async(const char *path)
{
    SeJob job;
    int thid;

    memset(&job, 0, sizeof(job));
    job.generation = g_se_generation;
    strncpy(job.path, path, sizeof(job.path) - 1);

    thid = sceKernelCreateThread(
        "NARAKU SE", se_thread, 0x13, 0x2000, 0, NULL
    );
    if (thid >= 0) sceKernelStartThread(thid, sizeof(job), &job);
}

static void play_vm_se_params(int se_id, int volume, int pitch, int pan)
{
    if (se_id >= 1000) {
        char path[180];
        snprintf(path, sizeof(path), ASSET_ROOT "se_exact_%04d.pcm", se_id);
        play_se_async(path);
        return;
    }
    (void)pan; /* New exact PCM assets include volume, pitch and pan. */

    /* The blood/water floor sound is reused with materially different event
     * parameters.  0.6.8 discarded them and always played the opening splash
     * (20%, pitch 50), making footsteps far too loud and low.  Pick the exact
     * pre-rendered variant from the command's original MZ volume/pitch. */
    if (se_id == 3) {
        if (volume == 5 && pitch == 70) play_se_async(SE_SPLASH_STEP70_PATH);
        else if (volume == 5 && pitch == 120) play_se_async(SE_SPLASH_STEP120_PATH);
        else if (volume == 20 && pitch == 70) play_se_async(SE_SPLASH_20_70_PATH);
        else play_se_async(SE_SPLASH_PATH); /* canonical 20%, pitch 50 */
        return;
    }

    /* Other early sounds already have their story-used event parameters baked
     * into their PCM assets.  Runtime master SE volume (default 75) is applied
     * once in se_thread, matching the original Options setting. */
    if (se_id == 1) play_se_async(SE_BONE_PATH);              /* 40%, pitch 70 */
    else if (se_id == 2) {
        if (volume == 70 && pitch == 80) play_se_async(SE_WATER_70_80_PATH);
        else if (volume == 50 && pitch == 80) play_se_async(SE_WATER_50_80_PATH);
        else play_se_async(SE_WATER_PATH);                    /* canonical 90%, pitch 100 */
    }
    else if (se_id == 4) play_se_async(SE_SPLASH_STEP70_PATH);/* legacy alias */
    else if (se_id == 5) play_se_async(SE_SPLASH_STEP120_PATH);/* legacy alias */
    else if (se_id == 6) play_se_async(SE_BONE_100_PATH);     /* 90%, pitch 100 */
    else if (se_id == 7) play_se_async(SE_MENU_OPEN_PATH);
    else if (se_id == 8) play_se_async(SE_DECISION1_PATH);
    else if (se_id == 9) play_se_async(SE_DECISION2_PATH);
    else if (se_id == 10) play_se_async(SE_CANCEL2_PATH);
    else if (se_id == 11) play_se_async(SE_CURSOR2_PATH);
    else if (se_id == 12) play_se_async(SE_EVASION1_PATH);
    else if (se_id == 13) play_se_async(SE_SLIME_FALL_PATH);
    else if (se_id == 14) play_se_async(SE_SE7_PATH);
    else if (se_id == 15) play_se_async(SE_SWITCH1_PATH);
    else if (se_id == 16) play_se_async(SE_SWITCH2_PATH);
    else if (se_id == 17) play_se_async(SE_MONITOR_PATH);
    else if (se_id == 18) play_se_async(SE_OPEN9_PATH);
    else if (se_id == 19) play_se_async(SE_GATE1_PATH);
    else if (se_id == 20) play_se_async(SE_GATE2_PATH);
    else if (se_id == 21) play_se_async(SE_SWORD5_PATH);
    else if (se_id == 22) play_se_async(SE_HIT_AXE3_PATH);
    else if (se_id == 23) play_se_async(SE_BONE5_PATH);
    else if (se_id == 24) play_se_async(SE_EQUIP2_PATH);
    else if (se_id == 25) play_se_async(SE_SLASH7_PATH);
    else if (se_id == 26) play_se_async(SE_BLOW2_PATH);
    else if (se_id == 27) play_se_async(SE_MONSTER5_PATH);
    else if (se_id == 28) play_se_async(SE_HATCH_SLIDE_PATH);
}

static void play_vm_se(int se_id)
{
    play_vm_se_params(se_id, 90, 100, 0);
}

/* ------------------------------------------------------------------------- */
/* Progress / switches                                                       */
/* ------------------------------------------------------------------------- */

static void reset_runtime_game_state(void)
{
    int i;
    g_save_enabled = 1;
    memset(g_switches, 0, sizeof(g_switches));
    memset(g_variables, 0, sizeof(g_variables));
    memset(g_items, 0, sizeof(g_items));
    memset(g_self_switches, 0, sizeof(g_self_switches));
    clear_event_routes();
    memset(g_event_shift_x, 0, sizeof(g_event_shift_x));
    memset(g_event_shift_y, 0, sizeof(g_event_shift_y));
    memset(g_event_move_speed, 0, sizeof(g_event_move_speed));
    for (i = 0; i < MAX_EVENT_ID; ++i) g_event_active_page[i] = -1;
    for (i = 0; i < MAX_ACTIVE_PICTURES; ++i) {
        if (g_pictures[i].texture) free(g_pictures[i].texture);
        memset(&g_pictures[i], 0, sizeof(g_pictures[i]));
    }
    g_picture6_visible = 0;
    g_picture6_alpha = 0;
    g_player_move_speed_code = 3;
    g_player_direction_fix = 0;
    g_player_walk_anime=1;g_player_step_anime=0;
    g_player_through = 0;
    g_player_visible = 1;
    g_camera_scroll_x = 0.0f;
    g_camera_scroll_y = 0.0f;
    g_map_scroll_remaining = 0;
    g_screen_shake_x = 0.0f;
    g_fog_scroll = 0.0f;
    g_fog_active_prev = 0;
    g_map8_drop_timer = 0;
    g_map9_water_timer = 0;
    g_world_render_frames = 0;
    g_script_fade_alpha=g_number_active=0;
    player_animation_reset(&g_player_animation);
    g_player_animation_moving = g_player_animation_jumping = 0;
    g_player_animation_speed = 3;
    g_playtime_frames = 0;
    g_world_tone_r = 0;
    g_world_tone_g = 0;
    g_world_tone_b = 0;
    g_world_tone_gray = 0;
    g_world_tone_from_r = 0;
    g_world_tone_from_g = 0;
    g_world_tone_from_b = 0;
    g_world_tone_from_gray = 0;
    g_world_tone_target_r = 0;
    g_world_tone_target_g = 0;
    g_world_tone_target_b = 0;
    g_world_tone_target_gray = 0;
    g_world_tone_total = 0;
    g_world_tone_remaining = 0;
    g_screen_flash_r = 0;
    g_screen_flash_g = 0;
    g_screen_flash_b = 0;
    g_screen_flash_a = 0;
    g_screen_flash_total = 0;
    g_screen_flash_remaining = 0;
    g_last_choice = -1;
    g_request_title = 0;
    g_loaded_from_scene = 0;
}

static void clear_progress(void)
{
    remove(PROGRESS_PATH);
    reset_runtime_game_state();
}

static int read_progress_file(const char *path, ProgressState *out)
{
    FILE *f;
    uint8_t header[16];
    size_t n;

    memset(out, 0, sizeof(*out));
    reset_runtime_game_state();

    f = fopen(path, "rb");
    if (!f) return 0;

    n = fread(header, 1, 4, f);
    if (n != 4) {
        fclose(f);
        return 0;
    }

    if (memcmp(header, "PG60", 4) == 0 ||
        memcmp(header, "PG40", 4) == 0 || memcmp(header, "PG30", 4) == 0) {
        if (fread(header + 4, 1, 12, f) != 12) {
            fclose(f);
            return 0;
        }

        out->map_id = (int)read_u16_le(header + 4);
        out->tile_x = (int)read_u16_le(header + 6);
        out->tile_y = (int)read_u16_le(header + 8);
        out->direction_row = (int)header[10];
        out->intro_done = (int)header[11];

        if (memcmp(header, "PG60", 4) == 0 || memcmp(header, "PG40", 4) == 0) {
            g_picture6_visible = header[12] ? 1 : 0;
            g_picture6_alpha = g_picture6_visible ? (header[13] ? (int)header[13] : 255) : 0;
            if (header[14] >= 1 && header[14] <= 6)
                g_player_move_speed_code = (int)header[14];
            if (memcmp(header, "PG60", 4) == 0)
                g_player_visible = (header[15] & 1) ? 1 : 0;
            if (memcmp(header, "PG60", 4) == 0)
                g_save_enabled = (header[15] & 2) ? 0 : 1;
        } else {
            g_picture6_visible = out->intro_done ? 1 : 0;
            g_picture6_alpha = g_picture6_visible ? 255 : 0;
        }

        if (fread(g_switches, 1, sizeof(g_switches), f) != sizeof(g_switches) ||
            fread(g_variables, 1, sizeof(g_variables), f) != sizeof(g_variables) ||
            fread(g_items, 1, sizeof(g_items), f) != sizeof(g_items) ||
            fread(g_self_switches, 1, sizeof(g_self_switches), f) != sizeof(g_self_switches)) {
            fclose(f);
            reset_runtime_game_state();
            return 0;
        }
        {
            uint8_t pt[4];
            if (fread(pt, 1, 4, f) == 4)
                g_playtime_frames = read_u32_le(pt) * 60u;
        }
        fclose(f);
    } else if (memcmp(header, "PG10", 4) == 0) {
        uint8_t old[136];
        if (fread(old, 1, sizeof(old), f) != sizeof(old)) {
            fclose(f);
            return 0;
        }
        fclose(f);
        out->map_id = (int)read_u16_le(old + 0);
        out->tile_x = (int)read_u16_le(old + 2);
        out->tile_y = (int)read_u16_le(old + 4);
        out->direction_row = (int)old[6];
        out->intro_done = (int)old[7];
        g_picture6_visible = out->intro_done ? 1 : 0;
        g_picture6_alpha = g_picture6_visible ? 255 : 0;
        memcpy(g_switches, old + 8, 128);
    } else {
        fclose(f);
        return 0;
    }

    if (out->map_id < 1 || out->map_id > MAX_MAP_ID) {
        reset_runtime_game_state();
        return 0;
    }
    if (out->direction_row < 0 || out->direction_row > 3) out->direction_row = 0;
    return 1;
}

static int write_progress_file(
    const char *path,
    int map_id, int tile_x, int tile_y, int direction_row, int intro_done)
{
    FILE *f;
    uint8_t header[16];

    memset(header, 0, sizeof(header));
    memcpy(header, "PG60", 4);
    write_u16_le(header + 4, (uint16_t)map_id);
    write_u16_le(header + 6, (uint16_t)tile_x);
    write_u16_le(header + 8, (uint16_t)tile_y);
    header[10] = (uint8_t)direction_row;
    header[11] = (uint8_t)(intro_done ? 1 : 0);
    header[12] = (uint8_t)(g_picture6_visible ? 1 : 0);
    header[13] = (uint8_t)(g_picture6_visible ? g_picture6_alpha : 0);
    header[14] = (uint8_t)clamp_move_speed_code(g_player_move_speed_code);
    header[15] = (uint8_t)((g_player_visible ? 1 : 0) | (g_save_enabled ? 0 : 2));

    f = fopen(path, "wb");
    if (!f) return 0;
    if (fwrite(header, 1, sizeof(header), f) != sizeof(header) ||
        fwrite(g_switches, 1, sizeof(g_switches), f) != sizeof(g_switches) ||
        fwrite(g_variables, 1, sizeof(g_variables), f) != sizeof(g_variables) ||
        fwrite(g_items, 1, sizeof(g_items), f) != sizeof(g_items) ||
        fwrite(g_self_switches, 1, sizeof(g_self_switches), f) != sizeof(g_self_switches)) {
        fclose(f);
        return 0;
    }
    {
        uint32_t seconds = g_playtime_frames / 60u;
        uint8_t pt[4];
        pt[0] = (uint8_t)(seconds & 0xFFu);
        pt[1] = (uint8_t)((seconds >> 8) & 0xFFu);
        pt[2] = (uint8_t)((seconds >> 16) & 0xFFu);
        pt[3] = (uint8_t)((seconds >> 24) & 0xFFu);
        if (fwrite(pt, 1, 4, f) != 4) { fclose(f); return 0; }
    }
    fclose(f);
    return 1;
}

static int load_progress(ProgressState *out)
{
    return read_progress_file(PROGRESS_PATH, out);
}

static void save_progress(
    int map_id, int tile_x, int tile_y, int direction_row, int intro_done)
{
    write_progress_file(PROGRESS_PATH, map_id, tile_x, tile_y, direction_row, intro_done);
}

static void save_slot_path(int slot, char *path, size_t path_size)
{
    if (slot < 1) slot = 1;
    if (slot > SAVE_SLOT_COUNT) slot = SAVE_SLOT_COUNT;
    snprintf(path, path_size, ROOT "save%02d.bin", slot);
}

static int save_slot_exists(int slot)
{
    char path[192];
    FILE *f;
    save_slot_path(slot, path, sizeof(path));
    f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f);
    return 1;
}

static int any_save_slots(void)
{
    int i;
    for (i = 1; i <= SAVE_SLOT_COUNT; ++i)
        if (save_slot_exists(i)) return 1;
    return 0;
}

static int save_to_slot(
    int slot, int map_id, int tile_x, int tile_y, int direction_row)
{
    char path[192];
    save_slot_path(slot, path, sizeof(path));
    return write_progress_file(path, map_id, tile_x, tile_y, direction_row, 1);
}

static int load_from_slot(int slot, ProgressState *out)
{
    char path[192];
    save_slot_path(slot, path, sizeof(path));
    return read_progress_file(path, out);
}

static int save_slot_metadata(
    int slot, int *map_id, int *tile_x, int *tile_y, uint32_t *playtime_seconds)
{
    char path[192];
    FILE *f;
    uint8_t h[16];
    uint8_t pt[4];
    long playtime_offset = 16L + (long)sizeof(g_switches) +
                           (long)sizeof(g_variables) + (long)sizeof(g_items) +
                           (long)sizeof(g_self_switches);
    save_slot_path(slot, path, sizeof(path));
    f = fopen(path, "rb");
    if (!f) return 0;
    if (fread(h, 1, sizeof(h), f) != sizeof(h)) {
        fclose(f); return 0;
    }
    if (memcmp(h, "PG60", 4) != 0 && memcmp(h, "PG40", 4) != 0 &&
        memcmp(h, "PG30", 4) != 0) { fclose(f); return 0; }
    if (map_id) *map_id = (int)read_u16_le(h + 4);
    if (tile_x) *tile_x = (int)read_u16_le(h + 6);
    if (tile_y) *tile_y = (int)read_u16_le(h + 8);
    if (playtime_seconds) {
        *playtime_seconds = 0;
        if (fseek(f, playtime_offset, SEEK_SET) == 0 && fread(pt, 1, 4, f) == 4)
            *playtime_seconds = read_u32_le(pt);
    }
    fclose(f);
    return 1;
}


/* ------------------------------------------------------------------------- */
/* Native PSP UI: original NARAKU menu/save/options bridge                  */
/* ------------------------------------------------------------------------- */

static void draw_character_frame(int pattern, int direction_row, float foot_x, float foot_y);

enum {
    UI_L_ITEMS = 0,
    UI_L_KEY_ITEMS = 1,
    UI_L_SAVE_PROMPT = 2,
    UI_L_LOAD_PROMPT = 3,
    UI_L_FILE = 4,
    UI_L_SETTINGS = 5,
    UI_L_BACK = 6,
    UI_L_SAVE = 7,
    UI_L_LOAD = 8,
    UI_L_RETURN_TITLE = 9,
    UI_L_CANCEL = 10,
    UI_L_NEW_GAME = 11,
    UI_L_CONTINUE = 12,
    UI_L_ALWAYS_DASH = 13,
    UI_L_BGM_VOLUME = 14,
    UI_L_SE_VOLUME = 15,
    UI_L_WINDOW_OPACITY = 16,
    UI_L_LANGUAGE = 17,
    UI_L_ON = 18,
    UI_L_OFF = 19,
    UI_L_EMPTY = 20,
    UI_L_INVENTORY_TITLE = 21,
    UI_L_OPTIONS_TITLE = 22,
    UI_L_RETURN_TITLE_CONFIRM = 23,
    UI_L_SHUTDOWN = 24
};

static int init_ui_data(void)
{
    uint32_t item_off, label_off, blob_off;
    memset(&g_ui, 0, sizeof(g_ui));
    g_ui.data = (uint8_t *)load_whole_file(UI_DATA_PATH, &g_ui.size);
    if (!g_ui.data || g_ui.size < UI_HEADER_BYTES) return 0;
    if (memcmp(g_ui.data, "NU60", 4) != 0) return 0;
    g_ui.item_count = (int)read_u16_le(g_ui.data + 4);
    g_ui.label_count = (int)read_u16_le(g_ui.data + 6);
    item_off = read_u32_le(g_ui.data + 8);
    label_off = read_u32_le(g_ui.data + 12);
    blob_off = read_u32_le(g_ui.data + 16);
    if (g_ui.item_count < 1 || g_ui.item_count > MAX_ITEMS ||
        g_ui.label_count < 1 || g_ui.label_count > 128) return 0;
    if (item_off > g_ui.size || label_off > g_ui.size || blob_off > g_ui.size) return 0;
    if ((size_t)item_off + (size_t)g_ui.item_count * UI_ITEM_REC_BYTES > g_ui.size) return 0;
    if ((size_t)label_off + (size_t)g_ui.label_count * 4u > g_ui.size) return 0;
    g_ui.item_table = g_ui.data + item_off;
    g_ui.label_table = g_ui.data + label_off;
    g_ui.blob = g_ui.data + blob_off;
    g_ui.blob_size = g_ui.size - blob_off;
    g_ui.iconset = load_exact_file(UI_ICONSET_PATH, UI_ICONSET_BYTES);
    if (!g_ui.iconset) return 0;
    return 1;
}

static int ui_label_text(int id, int lang, const char **text, size_t *len)
{
    uint32_t off;
    const uint8_t *p;
    uint16_t lens[4];
    int i;
    if (!g_ui.data || id < 0 || id >= g_ui.label_count || lang < 0 || lang > 3) return 0;
    off = read_u32_le(g_ui.label_table + id * 4);
    if (off + 8u > g_ui.blob_size) return 0;
    p = g_ui.blob + off;
    for (i = 0; i < 4; ++i) lens[i] = read_u16_le(p + i * 2);
    p += 8;
    for (i = 0; i < 4; ++i) {
        if ((size_t)(p - g_ui.blob) + lens[i] > g_ui.blob_size) return 0;
        if (i == lang) {
            if (text) *text = (const char *)p;
            if (len) *len = lens[i];
            return 1;
        }
        p += lens[i];
    }
    return 0;
}

static int ui_item_text(
    int item_id, int lang,
    const char **name, size_t *name_len,
    const char **desc, size_t *desc_len,
    int *icon, int *itype, int *occasion)
{
    const uint8_t *rec;
    uint32_t off, size;
    const uint8_t *p;
    uint16_t lens[8];
    int i;
    if (!g_ui.data || item_id < 0 || item_id >= g_ui.item_count || lang < 0 || lang > 3) return 0;
    rec = g_ui.item_table + item_id * UI_ITEM_REC_BYTES;
    off = read_u32_le(rec + 4);
    size = read_u32_le(rec + 8);
    if (!size || off + size > g_ui.blob_size || size < 16) return 0;
    if (icon) *icon = (int)read_u16_le(rec + 0);
    if (itype) *itype = (int)rec[2];
    if (occasion) *occasion = (int)rec[3];
    p = g_ui.blob + off;
    for (i = 0; i < 8; ++i) lens[i] = read_u16_le(p + i * 2);
    p += 16;
    for (i = 0; i < 4; ++i) {
        size_t nl = lens[i * 2 + 0];
        size_t dl = lens[i * 2 + 1];
        if ((size_t)(p - (g_ui.blob + off)) + nl + dl > size) return 0;
        if (i == lang) {
            if (name) *name = (const char *)p;
            if (name_len) *name_len = nl;
            if (desc) *desc = (const char *)(p + nl);
            if (desc_len) *desc_len = dl;
            return 1;
        }
        p += nl + dl;
    }
    return 0;
}

static void ui_draw_label(int id, float x, float y, float max_x, int lines)
{
    const char *text = NULL;
    size_t len = 0;
    if (ui_label_text(id, g_language, &text, &len))
        draw_utf8_wrapped(text, len, x, y, max_x, lines);
}

static void ui_frame_begin(void)
{
    sceGuStart(GU_DIRECT, gu_list);
    sceGuClearColor(0xFF000000);
    sceGuClear(GU_COLOR_BUFFER_BIT);
}

static void ui_frame_end(void)
{
    sceGuFinish();
    sceGuSync(0, 0);
    sceDisplayWaitVblankStart();
    g_draw_buffer = sceGuSwapBuffers();
}

static void ui_panel(float x, float y, float w, float h)
{
    int alpha = g_window_opacity;
    if (alpha < 64) alpha = 64;
    if (alpha > 255) alpha = 255;
    draw_solid_rect(x, y, w, h, 8, 8, 12, alpha);
    draw_solid_rect(x + 2, y + 2, w - 4, 1, 210, 210, 220, 210);
}

#include "runtime/inventory.inc"

static void ui_draw_value_number(int value, float x, float y)
{
    char buf[32];
    snprintf(buf, sizeof(buf), "%d", value);
    draw_utf8_wrapped(buf, strlen(buf), x, y, SCREEN_W - 18.0f, 1);
}

static void ui_options_scene(void)
{
    SceCtrlData pad;
    uint32_t prev;
    int cursor = 0;
    int running = 1;
    const int rows = 6;

    /* Settings is normally entered with X.  Do not reinterpret that still-
     * held X as an immediate press on the Language row (the 0.6.1 bug that
     * changed English to Japanese every time Settings was opened). */
    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;

    while (running) {
        int i;
        ui_frame_begin();
        ui_panel(20, 12, SCREEN_W - 40, 248);
        ui_draw_label(UI_L_OPTIONS_TITLE, 34, 20, 450, 1);
        for (i = 0; i < rows; ++i) {
            float y = 56.0f + i * 31.0f;
            if (i == cursor)
                draw_solid_rect(29, y - 3, 422, 29, 58, 68, 94, 210);
            if (i == 0) {
                static const char *langs[4] = {"English", "日本語", "简体中文", "繁體中文"};
                ui_draw_label(UI_L_LANGUAGE, 38, y, 280, 1);
                draw_utf8_wrapped(langs[g_language], strlen(langs[g_language]), 300, y, 444, 1);
            } else if (i == 1) {
                ui_draw_label(UI_L_ALWAYS_DASH, 38, y, 300, 1);
                ui_draw_label(g_always_dash ? UI_L_ON : UI_L_OFF, 360, y, 444, 1);
            } else if (i == 2) {
                ui_draw_label(UI_L_BGM_VOLUME, 38, y, 300, 1);
                ui_draw_value_number(g_bgm_volume, 382, y);
            } else if (i == 3) {
                ui_draw_label(UI_L_SE_VOLUME, 38, y, 300, 1);
                ui_draw_value_number(g_se_volume, 382, y);
            } else if (i == 4) {
                ui_draw_label(UI_L_WINDOW_OPACITY, 38, y, 300, 1);
                ui_draw_value_number(g_window_opacity, 382, y);
            } else {
                ui_draw_label(UI_L_BACK, 38, y, 444, 1);
            }
        }
        ui_frame_end();

        sceCtrlPeekBufferPositive(&pad, 1);
        {
            uint32_t pressed = pad.Buttons & ~prev;
            int delta = 0;
            if (pressed & PSP_CTRL_UP) { cursor = (cursor + rows - 1) % rows; play_se_async(SE_UI_CURSOR_PATH); }
            if (pressed & PSP_CTRL_DOWN) { cursor = (cursor + 1) % rows; play_se_async(SE_UI_CURSOR_PATH); }
            if (pressed & PSP_CTRL_LEFT) delta = -1;
            if (pressed & PSP_CTRL_RIGHT) delta = 1;
            if (pressed & ui_ok_mask()) {
                if (cursor == 0) delta = 1;
                else if (cursor == 1) { g_always_dash = !g_always_dash; play_se_async(SE_UI_OK_PATH); }
                else if (cursor == 5) { running = 0; play_se_async(SE_UI_CANCEL_PATH); }
            }
            if (delta) {
                if (cursor == 0) {
                    g_language = (g_language + (delta > 0 ? 1 : 3)) & 3;
                    save_config();
                    play_se_async(SE_UI_CURSOR_PATH);
                } else if (cursor == 1) {
                    g_always_dash = !g_always_dash;
                    play_se_async(SE_UI_CURSOR_PATH);
                } else if (cursor == 2) {
                    g_bgm_volume += delta * 5;
                    if (g_bgm_volume < 0) g_bgm_volume = 0;
                    if (g_bgm_volume > 100) g_bgm_volume = 100;
                    play_se_async(SE_UI_CURSOR_PATH);
                } else if (cursor == 3) {
                    g_se_volume += delta * 5;
                    if (g_se_volume < 0) g_se_volume = 0;
                    if (g_se_volume > 100) g_se_volume = 100;
                    play_se_async(SE_UI_CURSOR_PATH);
                } else if (cursor == 4) {
                    g_window_opacity += delta * 16;
                    if (g_window_opacity < 64) g_window_opacity = 64;
                    if (g_window_opacity > 255) g_window_opacity = 255;
                }
            }
            if (pressed & ui_cancel_mask()) {
                running = 0;
                play_se_async(SE_UI_CANCEL_PATH);
            }
        }
        prev = pad.Buttons;
    }
    save_config();
}

static void ui_draw_save_background(void)
{
    int i;
    /* The original save/load scenes sit on a black -> deep blood-red vertical
     * gradient, not on the gameplay frame.  Sixteen bands are visually smooth
     * enough at the PSP's 272px height and cost almost nothing. */
    for (i = 0; i < 16; ++i) {
        int r = 34 - i * 2;
        if (r < 2) r = 2;
        draw_solid_rect(0.0f, (float)(i * 17), (float)SCREEN_W, 17.0f,
                        r, 0, 3, 255);
    }
}

static void ui_format_playtime(uint32_t seconds, char *buf, size_t size)
{
    uint32_t h = seconds / 3600u;
    uint32_t m = (seconds / 60u) % 60u;
    uint32_t s = seconds % 60u;
    snprintf(buf, size, "%02u:%02u:%02u",
             (unsigned int)h, (unsigned int)m, (unsigned int)s);
}

static int ui_save_load_scene(
    int saving,
    int current_map, int current_x, int current_y, int current_dir,
    ProgressState *loaded)
{
    SceCtrlData pad;
    uint32_t prev = 0;
    int cursor = 0;
    int scroll = 0;
    const int visible = 5;

    if (saving && !g_save_enabled) return 0;

    /* The X press that opened Save/Load must never also activate File 1.
     * The slot screen is armed only after that physical press is released. */
    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;

    while (1) {
        int i;
        if (cursor < scroll) scroll = cursor;
        if (cursor >= scroll + visible) scroll = cursor - visible + 1;
        if (scroll < 0) scroll = 0;
        if (scroll > SAVE_SLOT_COUNT - visible) scroll = SAVE_SLOT_COUNT - visible;

        ui_frame_begin();
        ui_draw_save_background();
        draw_naraku_window(4.0f, 18.0f, 472.0f, 38.0f, 230);
        {
            const char *prompt;
            size_t prompt_len;
            if (ui_label_text(saving ? UI_L_SAVE_PROMPT : UI_L_LOAD_PROMPT,
                              g_language, &prompt, &prompt_len))
                ui_inventory_name(prompt, prompt_len, 14, 21, 448);
        }

        draw_naraku_window(4.0f, 60.0f, 472.0f, 207.0f, 225);
        for (i = 0; i < visible; ++i) {
            int slot = scroll + i + 1;
            float y = 65.0f + i * 39.0f;
            int map_id = 0, sx = 0, sy = 0;
            uint32_t playtime = 0;
            int exists = save_slot_metadata(slot, &map_id, &sx, &sy, &playtime);
            char slot_text[32];

            if (slot - 1 == cursor)
                draw_solid_rect(10.0f, y, 460.0f, 36.0f, 72, 8, 20, 220);
            else if ((i & 1) == 0)
                draw_solid_rect(10.0f, y, 460.0f, 36.0f, 12, 8, 9, 135);

            if (g_language == 0) {
                snprintf(slot_text, sizeof(slot_text), "file %d", slot);
                ui_inventory_name(slot_text, strlen(slot_text), 16, y + 2, 98);
            } else {
                const char *label;
                size_t label_len;
                if (ui_label_text(UI_L_FILE, g_language, &label, &label_len))
                    ui_inventory_name(label, label_len, 16, y + 2, 60);
                snprintf(slot_text, sizeof(slot_text), "%d", slot);
                ui_inventory_name(slot_text, strlen(slot_text), 82, y + 2, 32);
            }

            if (exists) {
                char time_text[32];
                /* The original puts Enri's standing sprite in every occupied
                 * slot.  Use the same runtime atlas rather than a placeholder. */
                if (g_ui_char_atlas) {
                    bind_texture_8888(g_ui_char_atlas, CHAR_ATLAS_W, CHAR_ATLAS_H);
                    set_pixel_art_texture_state();
                    sceGuTexFilter(GU_LINEAR, GU_LINEAR);
                    draw_bound_rect(CHAR_SLOT_W + 1, 1, CHAR_SRC_W, CHAR_SRC_H,
                        142, y + 2, 32.0f * CHAR_SRC_W / CHAR_SRC_H, 32);
                    set_pixel_art_texture_state();
                }
                ui_format_playtime(playtime, time_text, sizeof(time_text));
                ui_inventory_name(time_text, strlen(time_text), 364, y + 2, 102);
            }
        }
        ui_frame_end();

        sceCtrlPeekBufferPositive(&pad, 1);
        {
            uint32_t pressed = pad.Buttons & ~prev;
            if (pressed & PSP_CTRL_UP) {
                cursor = (cursor + SAVE_SLOT_COUNT - 1) % SAVE_SLOT_COUNT;
                play_se_async(SE_UI_CURSOR_PATH);
            }
            if (pressed & PSP_CTRL_DOWN) {
                cursor = (cursor + 1) % SAVE_SLOT_COUNT;
                play_se_async(SE_UI_CURSOR_PATH);
            }
            if (pressed & PSP_CTRL_LTRIGGER) {
                cursor -= visible; if (cursor < 0) cursor = 0;
                play_se_async(SE_UI_CURSOR_PATH);
            }
            if (pressed & PSP_CTRL_RTRIGGER) {
                cursor += visible; if (cursor >= SAVE_SLOT_COUNT) cursor = SAVE_SLOT_COUNT - 1;
                play_se_async(SE_UI_CURSOR_PATH);
            }
            if (pressed & ui_ok_mask()) {
                int slot = cursor + 1;
                if (saving) {
                    if (save_to_slot(slot, current_map, current_x, current_y, current_dir)) {
                        play_se_async(SE_UI_SAVE_PATH);
                        return 1;
                    }
                } else if (save_slot_exists(slot) && loaded && load_from_slot(slot, loaded)) {
                    play_se_async(SE_UI_LOAD_PATH);
                    return 1;
                } else {
                    play_se_async(SE_UI_BUZZER_PATH);
                }
            }
            if (pressed & ui_cancel_mask()) {
                play_se_async(SE_UI_CANCEL_PATH);
                return 0;
            }
        }
        prev = pad.Buttons;
    }
}

static const char *title_path_for_language(int lang)
{
    if (lang == 1) return TITLE_JA_PATH;
    if (lang == 2) return TITLE_ZHCN_PATH;
    if (lang == 3) return TITLE_ZHTW_PATH;
    return TITLE_EN_PATH;
}

typedef struct {
    uint32_t held;
    int fresh;
    unsigned long long next;
} MenuNav;

static int menu_nav_step(MenuNav *nav,uint32_t buttons,unsigned long long now)
{
    uint32_t direction=buttons & (PSP_CTRL_UP|PSP_CTRL_DOWN);
    int step;
    nav->fresh = 0;
    if(!direction || direction==(PSP_CTRL_UP|PSP_CTRL_DOWN)) {
        nav->held=0;nav->next=0;return 0;
    }
    step=direction==PSP_CTRL_UP?-1:1;
    if(direction!=nav->held) {
        nav->held=direction;nav->fresh=1;nav->next=now+400000;return step;
    }
    if(nav->next && now>=nav->next) {
        nav->next=now+100000;return step;
    }
    return 0;
}

/* Held repeat stops at an edge; only a fresh press can wrap. */
static int menu_nav_cursor(int cursor, int rows, int step, int fresh)
{
    int next = cursor + step;
    if (next < 0) return fresh ? rows - 1 : 0;
    if (next >= rows) return fresh ? 0 : rows - 1;
    return next;
}

static void ui_title_label(int id, float y)
{
    const char *text, *p, *end;
    size_t len;
    int width = 0;
    if (!ui_label_text(id, g_language, &text, &len)) return;
    p = text; end = text + len;
    while (p < end) {
        uint32_t cp = utf8_next_cp(&p, end);
        const uint8_t *rec = font_find_glyph(cp);
        if (!rec) rec = font_find_glyph((uint32_t)'?');
        width += rec ? rec[7] : 10;
    }
    draw_utf8_wrapped(text, len, 130.0f - width * 0.75f / 2.0f, y, 234, 1);
}

/* Returns 1 = new game, 2 = loaded save. */
static int ui_title_scene(ProgressState *loaded)
{
    SceCtrlData pad;
    uint32_t prev = 0;
    int cursor = 0;
    int continue_ok = any_save_slots();
    MenuNav nav;
    void *title = NULL;
    int loaded_lang = -1;
    const int rows = 4;
    const uint32_t nav_mask = PSP_CTRL_UP | PSP_CTRL_DOWN;
    set_bgm_track(TITLE_BGM_PATH);

    /* Ignore directions already held when entering the title, then allow
     * fresh presses, direction changes and the original 24/6-frame repeat. */
    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;
    nav.held = pad.Buttons & nav_mask;
    nav.next = 0;

    while (1) {
        if (loaded_lang != g_language || !title) {
            if (title) free(title);
            title = load_exact_file(title_path_for_language(g_language), PIC_TEX_BYTES);
            loaded_lang = g_language;
        }

        sceCtrlPeekBufferPositive(&pad, 1);
        {
            uint32_t pressed = pad.Buttons & ~prev;

            int step = menu_nav_step(&nav,pad.Buttons,sceKernelGetSystemTimeWide());
            if(step) {
                int next = menu_nav_cursor(cursor, rows, step, nav.fresh);
                if (next != cursor) {
                    cursor = next;
                    play_se_async(SE_UI_CURSOR_PATH);
                }
            }

            if (pressed & ui_ok_mask()) {
                if (cursor == 0) {
                    play_se_async(SE_UI_OK_PATH);
                    if (title) free(title);
                    set_bgm_track(BGM_PATH);
                    return 1;
                }
                if (cursor == 1) {
                    if (!continue_ok) {
                        /* Original-style disabled command feedback: the row
                         * stays grey and X produces only the buzzer SE. */
                        play_se_async(SE_UI_BUZZER_PATH);
                        goto title_draw;
                    }
                    if (ui_save_load_scene(0, 0, 0, 0, 0, loaded)) {
                        if (title) free(title);
                        set_bgm_track(BGM_PATH);
                        return 2;
                    }
                    continue_ok = any_save_slots();
                    sceCtrlPeekBufferPositive(&pad, 1);
                    prev = pad.Buttons;
                    nav.held = pad.Buttons & nav_mask;
                    nav.next = 0;
                    continue;
                }
                if (cursor == 2) {
                    play_se_async(SE_UI_OK_PATH);
                    ui_options_scene();
                    sceCtrlPeekBufferPositive(&pad, 1);
                    prev = pad.Buttons;
                    nav.held = pad.Buttons & nav_mask;
                    nav.next = 0;
                    continue;
                }
                if (cursor == 3) {
                    play_se_async(SE_UI_OK_PATH);
                    if (title) free(title);
                    /* Let main own the actual process shutdown.  0.6.4 called
                     * sceKernelExitGame() here, then fell through as if this
                     * were a loaded save when the emulator returned from the
                     * syscall. */
                    return 0;
                }
            }
        }
title_draw:
        prev = pad.Buttons;
        ui_frame_begin();
        if (title)
            draw_texture_alpha(title, 512, 512, 480, 272, 0, 0, 480, 272, 255);

        /* Closer to the original PC title: compact four-row menu at lower
         * left, while keeping the PSP font readable at native 480x272. */
        /* Black outer/inner edges and a thin red frame, as in Window.png.
         * Keep the current readable PSP dimensions. */
        draw_solid_rect(18, 145, 224, 123, 0, 0, 0, 255);
        draw_solid_rect(19, 146, 222, 121, 190, 0, 0, 255);
        draw_solid_rect(21, 148, 218, 117, 0, 0, 0, 255);
        draw_solid_rect(22, 149, 216, 115, 28, 28, 28, 235);
        {
            int row;
            for (row = 0; row < rows; ++row)
                draw_solid_rect(26, 151 + row * 27, 208, 25,
                                row == cursor ? 65 : 0, 0, 0,
                                row == cursor ? 225 : 100);
        }
        ui_title_label(UI_L_NEW_GAME, 151);
        ui_title_label(UI_L_CONTINUE, 178);
        ui_title_label(UI_L_SETTINGS, 205);
        ui_title_label(UI_L_SHUTDOWN, 232);
        if (!continue_ok)
            draw_solid_rect(28, 180, 204, 23, 0, 0, 0, 120);
        ui_frame_end();

    }
}

/* ------------------------------------------------------------------------- */
/* Map loading                                                               */
/* ------------------------------------------------------------------------- */

static void free_map(MapState *m)
{
    int i;
    if (m->map_bin) free(m->map_bin);
    for (i = 0; i < MAX_TILE_ATLASES; ++i) {
        if (m->tile_atlases[i]) free(m->tile_atlases[i]);
    }
    if (m->events_bin) free(m->events_bin);
    if (m->event_atlas) free(m->event_atlas);
    if (m->event_atlas_detail) free(m->event_atlas_detail);
    if (m->vm_bin) free(m->vm_bin);
    memset(m, 0, sizeof(*m));
}

static int load_map(MapState *m, int map_id)
{
    char path[192];
    size_t cells;
    size_t expected_map;
    size_t min_events;
    size_t offset;
    int i;

    free_map(m);
    clear_event_routes();
    memset(g_event_shift_x, 0, sizeof(g_event_shift_x));
    memset(g_event_shift_y, 0, sizeof(g_event_shift_y));
    memset(g_event_move_speed, 0, sizeof(g_event_move_speed));
    for (i = 0; i < MAX_EVENT_ID; ++i) g_event_active_page[i] = -1;
    g_camera_scroll_x = 0.0f;
    g_camera_scroll_y = 0.0f;
    g_map_scroll_remaining = 0;
    g_screen_shake_x = 0.0f;

    if (map_id < 1 || map_id > MAX_MAP_ID) return 0;

    snprintf(path, sizeof(path), ASSET_ROOT "map%03d.bin", map_id);
    m->map_bin = (uint8_t *)load_whole_file(path, &m->map_size);
    if (!m->map_bin || m->map_size < MAP_HEADER_BYTES) goto fail;
    if (memcmp(m->map_bin, "NM40", 4) != 0) goto fail;

    m->w = (int)read_u16_le(m->map_bin + 4);
    m->h = (int)read_u16_le(m->map_bin + 6);
    m->tile_px = (int)read_u16_le(m->map_bin + 8);
    m->tile_count = (int)read_u16_le(m->map_bin + 14);
    m->tile_atlas_count = (m->tile_count + 99) / 100;
    if (m->tile_atlas_count < 1) m->tile_atlas_count = 1;
    if (m->w <= 0 || m->h <= 0 || m->tile_px != TILE_PX) goto fail;
    if (m->tile_atlas_count > MAX_TILE_ATLASES) goto fail;

    cells = (size_t)m->w * (size_t)m->h;
    expected_map = MAP_HEADER_BYTES + cells * 4u * 2u + cells * 2u;
    if (m->map_size != expected_map) goto fail;

    {
        int atlas_index;
        for (atlas_index = 0; atlas_index < m->tile_atlas_count; ++atlas_index) {
            snprintf(
                path, sizeof(path),
                ASSET_ROOT "map%03d_atlas%d.rgba8888",
                map_id, atlas_index
            );
            m->tile_atlases[atlas_index] = load_exact_file(path, TILE_ATLAS_BYTES);
            if (!m->tile_atlases[atlas_index]) goto fail;
        }
    }

    snprintf(path, sizeof(path), ASSET_ROOT "map%03d_events.bin", map_id);
    m->events_bin = (uint8_t *)load_whole_file(path, &m->events_size);
    if (!m->events_bin || m->events_size < EVENT_HEADER_BYTES) goto fail;
    if (memcmp(m->events_bin, "NE10", 4) != 0) goto fail;
    if ((int)read_u16_le(m->events_bin + 4) != m->w ||
        (int)read_u16_le(m->events_bin + 6) != m->h) goto fail;

    m->transfer_count = (int)read_u16_le(m->events_bin + 8);
    m->sprite_count = (int)read_u16_le(m->events_bin + 10);

    min_events = EVENT_HEADER_BYTES + cells * 2u + cells * 3u +
                 (size_t)m->transfer_count * TRANSFER_RECORD_BYTES +
                 (size_t)m->sprite_count * SPRITE_RECORD_BYTES;
    if (m->events_size != min_events) goto fail;

    offset = EVENT_HEADER_BYTES;
    m->action_map = m->events_bin + offset;
    offset += cells * 2u;
    m->step_map = m->events_bin + offset;
    offset += cells;
    m->transfer_map = m->events_bin + offset;
    offset += cells;
    m->block_map = m->events_bin + offset;
    offset += cells;
    m->transfer_records = m->events_bin + offset;
    offset += (size_t)m->transfer_count * TRANSFER_RECORD_BYTES;
    m->sprite_records = m->events_bin + offset;

    if (m->sprite_count > 0) {
        snprintf(path, sizeof(path), ASSET_ROOT "map%03d_event_atlas.rgba8888", map_id);
        m->event_atlas = load_exact_file(path, EVENT_ATLAS_BYTES);
        if (!m->event_atlas) goto fail;
        if (map_id==32 || map_id==39 || map_id==40) {
            snprintf(path,sizeof(path),ASSET_ROOT "map%03d_event_atlas1.rgba8888",map_id);
            m->event_atlas_detail=load_exact_file(path,EVENT_ATLAS_BYTES);
            if(!m->event_atlas_detail)goto fail;
        }
    }

    snprintf(path, sizeof(path), ASSET_ROOT "map%03d_vm.bin", map_id);
    m->vm_bin = (uint8_t *)load_whole_file(path, &m->vm_size);
    if (m->vm_bin) {
        uint32_t cmd_off;
        uint32_t cmd_size;
        size_t need;
        if (m->vm_size < VM_HEADER_BYTES || memcmp(m->vm_bin, "NV40", 4) != 0) goto fail;
        m->vm_event_count = (int)read_u16_le(m->vm_bin + 4);
        m->vm_page_count = (int)read_u16_le(m->vm_bin + 6);
        cmd_off = read_u32_le(m->vm_bin + 8);
        cmd_size = read_u32_le(m->vm_bin + 12);
        m->vm_flags = read_u32_le(m->vm_bin + 16);
        need = VM_HEADER_BYTES + (size_t)m->vm_event_count * VM_EVENT_BYTES +
               (size_t)m->vm_page_count * VM_PAGE_BYTES;
        if (cmd_off != need || (size_t)cmd_off + (size_t)cmd_size > m->vm_size) goto fail;
        m->vm_events = m->vm_bin + VM_HEADER_BYTES;
        m->vm_pages = m->vm_events + (size_t)m->vm_event_count * VM_EVENT_BYTES;
        m->vm_commands = m->vm_bin + cmd_off;
        m->vm_command_size = (size_t)cmd_size;
    }

    m->id = map_id;
    return 1;

fail:
    free_map(m);
    return 0;
}

static uint16_t map_word(const MapState *m, int z, int x, int y)
{
    int cell = (z * m->h + y) * m->w + x;
    return read_u16_le(m->map_bin + MAP_HEADER_BYTES + cell * 2);
}

static uint8_t pass_mask_at(const MapState *m, int x, int y)
{
    size_t cells;
    size_t pass_offset;
    if (x < 0 || y < 0 || x >= m->w || y >= m->h) return 0;
    cells = (size_t)m->w * (size_t)m->h;
    pass_offset = MAP_HEADER_BYTES + cells * 4u * 2u;
    return m->map_bin[pass_offset + (size_t)y * m->w + x];
}

static uint16_t action_event_at(const MapState *m, int x, int y)
{
    size_t cell;
    if (x < 0 || y < 0 || x >= m->w || y >= m->h) return 0;
    cell = (size_t)y * m->w + x;
    return read_u16_le(m->action_map + cell * 2u);
}

static uint8_t transfer_index_at(const MapState *m, int x, int y)
{
    if (x < 0 || y < 0 || x >= m->w || y >= m->h) return 0;
    return m->transfer_map[(size_t)y * m->w + x];
}

static uint8_t event_block_at(const MapState *m, int x, int y)
{
    if (x < 0 || y < 0 || x >= m->w || y >= m->h) return 1;
    return m->block_map[(size_t)y * m->w + x];
}

static int read_transfer_record(const MapState *m, int index, TransferRecord *out)
{
    const uint8_t *p;
    if (index <= 0 || index > m->transfer_count) return 0;
    p = m->transfer_records + (size_t)(index - 1) * TRANSFER_RECORD_BYTES;

    out->dest_map = (int)read_u16_le(p + 0);
    out->dest_x = (int)read_u16_le(p + 2);
    out->dest_y = (int)read_u16_le(p + 4);
    out->direction = (int)p[6];
    out->flags = (int)p[7];

    out->switch_id[0] = (int)read_u16_le(p + 8);
    out->switch_value[0] = (int)p[10];
    out->switch_id[1] = (int)read_u16_le(p + 12);
    out->switch_value[1] = (int)p[14];
    out->switch_id[2] = (int)read_u16_le(p + 16);
    out->switch_value[2] = (int)p[18];
    return 1;
}

static int read_sprite_record(const MapState *m, int index, EventSpriteRecord *out)
{
    const uint8_t *p;
    if (index < 0 || index >= m->sprite_count) return 0;
    p = m->sprite_records + (size_t)index * SPRITE_RECORD_BYTES;

    out->x = (int)read_u16_le(p + 0);
    out->y = (int)read_u16_le(p + 2);
    out->sx = (int)read_u16_le(p + 4);
    out->sy = (int)read_u16_le(p + 6);
    out->sw = (int)read_u16_le(p + 8);
    out->sh = (int)read_u16_le(p + 10);
    out->priority = (int)p[12];
    out->flags = (int)p[13];
    out->event_id = (int)read_u16_le(p + 14);
    return 1;
}


/* ------------------------------------------------------------------------- */
/* v0.4.0 event VM page selection                                            */
/* ------------------------------------------------------------------------- */

static int vm_read_event(const MapState *m, int index, VmEventRecord *out)
{
    const uint8_t *p;
    if (!m->vm_bin || index < 0 || index >= m->vm_event_count) return 0;
    p = m->vm_events + (size_t)index * VM_EVENT_BYTES;
    out->event_id = (int)read_u16_le(p + 0);
    out->x = (int)read_u16_le(p + 2);
    out->y = (int)read_u16_le(p + 4);
    out->first_page = (int)read_u16_le(p + 6);
    out->page_count = (int)p[8];
    return 1;
}

static int vm_read_page(const MapState *m, int index, VmPageRecord *out)
{
    const uint8_t *p;
    if (!m->vm_bin || index < 0 || index >= m->vm_page_count) return 0;
    p = m->vm_pages + (size_t)index * VM_PAGE_BYTES;
    out->cond_flags = (int)p[0];
    out->trigger = (int)p[1];
    out->priority = (int)p[2];
    out->flags = (int)p[3];
    out->switch1 = (int)read_u16_le(p + 4);
    out->switch2 = (int)read_u16_le(p + 6);
    out->self_index = (int)p[8];
    out->supported = (int)p[9];
    out->sprite_ref = (int)read_u16_le(p + 10);
    out->cmd_offset = read_u32_le(p + 12);
    out->cmd_size = read_u32_le(p + 16);
    return 1;
}

static int vm_page_conditions_true(const MapState *m, int event_id, const VmPageRecord *p)
{
    if ((p->cond_flags & 0x01) &&
        (p->switch1 <= 0 || p->switch1 >= MAX_SWITCHES || !g_switches[p->switch1]))
        return 0;
    if ((p->cond_flags & 0x02) &&
        (p->switch2 <= 0 || p->switch2 >= MAX_SWITCHES || !g_switches[p->switch2]))
        return 0;
    if (p->cond_flags & 0x04) {
        uint8_t bits;
        if (m->id < 1 || m->id > MAX_MAP_ID || event_id < 0 || event_id >= MAX_EVENT_ID)
            return 0;
        bits = g_self_switches[m->id][event_id];
        if ((bits & (1u << p->self_index)) == 0) return 0;
    }
    return 1;
}

static int vm_active_page_index(
    const MapState *m, const VmEventRecord *ev, VmPageRecord *out, int *index_out)
{
    int i;
    int found = 0;
    int found_index = -1;
    if(ev->event_id>=0 && ev->event_id<MAX_EVENT_ID && g_event_erased[ev->event_id])return 0;
    VmPageRecord tmp;
    for (i = 0; i < ev->page_count; ++i) {
        int idx = ev->first_page + i;
        if (!vm_read_page(m, idx, &tmp)) continue;
        if (vm_page_conditions_true(m, ev->event_id, &tmp)) {
            *out = tmp;
            found = 1;
            found_index = idx;
        }
    }
    if (index_out) *index_out = found_index;
    return found;
}

static int vm_active_page(const MapState *m, const VmEventRecord *ev, VmPageRecord *out)
{
    return vm_active_page_index(m, ev, out, NULL);
}

static int is_chase_enemy(int map_id,int id)
{
    return ((map_id==24 || map_id==25) && id==3) ||
           (map_id==32 && id==23) || (map_id==33 && id==46) ||
           (map_id==34 && id==51);
}
static int is_chase_map(int map_id)
{
    return map_id==24 || map_id==25 || (map_id>=32 && map_id<=34);
}

static void vm_event_contact_cell(const MapState *m, const VmEventRecord *ev, int *x, int *y)
{
    int id=ev->event_id;
    *x=ev->x; *y=ev->y;
    if(id<0 || id>=MAX_EVENT_ID) return;
    if(is_chase_enemy(m->id,id)) {
        const EventRoute *r=&g_routes[id];
        float sx=g_event_shift_x[id], sy=g_event_shift_y[id];
        if(r->records && r->remaining>0) {sx=r->start_x+r->dx;sy=r->start_y+r->dy;}
        *x+=(int)(sx+(sx<0?-.5f:.5f));
        *y+=(int)(sy+(sy<0?-.5f:.5f));
    } else {
        *x+=(int)g_event_shift_x[id];
        *y+=(int)g_event_shift_y[id];
    }
}

static int vm_find_event_at(
    const MapState *m, int x, int y, int trigger,
    VmEventRecord *ev_out, VmPageRecord *page_out)
{
    int i;
    VmEventRecord ev;
    VmPageRecord pg;
    if (!m->vm_bin) return 0;
    for (i = 0; i < m->vm_event_count; ++i) {
        if (!vm_read_event(m, i, &ev)) continue;
        {
            int cell_x,cell_y;
            vm_event_contact_cell(m,&ev,&cell_x,&cell_y);
            if(cell_x!=x || cell_y!=y) continue;
        }
        if (!vm_active_page(m, &ev, &pg)) continue;
        if (!pg.supported || pg.cmd_size <= 1) continue;
        /* Negative trigger requests MZ checkEventTriggerTouchFront: only
         * same-priority Player Touch events on the blocked destination cell. */
        if (trigger == -2 || trigger == -3) {
            /* MZ action: current cell below/above actors, front cell normal
             * priority. Empty pages cannot set Game_Event._starting. */
            if(pg.trigger!=0 || (trigger==-2 ? pg.priority==1 : pg.priority!=1))continue;
        } else if (trigger < 0) {
            if (pg.trigger != 1 || pg.priority != 1) continue;
        } else if (pg.trigger != trigger) continue;
        if (ev_out) *ev_out = ev;
        if (page_out) *page_out = pg;
        return 1;
    }
    return 0;
}

static int vm_event_blocks_except(const MapState *m, int x, int y, int except_id)
{
    int i;
    VmEventRecord ev;
    VmPageRecord pg;
    if (!m->vm_bin) return event_block_at(m, x, y);
    for (i = 0; i < m->vm_event_count; ++i) {
        if (!vm_read_event(m, i, &ev)) continue;
        if (ev.event_id == except_id) continue;
        {
            int cell_x,cell_y;
            vm_event_contact_cell(m,&ev,&cell_x,&cell_y);
            if(cell_x!=x || cell_y!=y) continue;
        }
        if (!vm_active_page(m, &ev, &pg)) continue;
        if (pg.priority == 1 && !(pg.flags & 0x01) &&
            !(ev.event_id>=0 && ev.event_id<MAX_EVENT_ID && g_event_through[ev.event_id])) return 1;
    }
    return 0;
}

static int vm_event_blocks_at(const MapState *m, int x, int y)
{
    return vm_event_blocks_except(m, x, y, -1);
}


/* A supported active VM page owns this cell, including an empty page
 * selected after a one-shot cutscene. Never revive its legacy transfer. */
static int vm_cell_owns_transfer(const MapState *m, int x, int y)
{
    int i;
    VmEventRecord ev;
    VmPageRecord pg;
    if (!m->vm_bin) return 0;
    for (i = 0; i < m->vm_event_count; ++i) {
        if (!vm_read_event(m, i, &ev)) continue;
        if (ev.x != x || ev.y != y) continue;
        if (vm_active_page(m, &ev, &pg) && pg.supported) return 1;
    }
    return 0;
}

static int vm_touch_transfer_at(const MapState *m, int x, int y)
{
    int i;
    VmEventRecord ev;
    VmPageRecord pg;
    if (!m->vm_bin) return transfer_index_at(m, x, y) != 0;
    for (i = 0; i < m->vm_event_count; ++i) {
        if (!vm_read_event(m, i, &ev)) continue;
        {
            int cell_x,cell_y;
            vm_event_contact_cell(m,&ev,&cell_x,&cell_y);
            if(cell_x!=x || cell_y!=y) continue;
        }
        if (!vm_active_page(m, &ev, &pg)) continue;
        if (pg.trigger == 1 && (pg.flags & 0x02)) return 1;
    }
    return !vm_cell_owns_transfer(m, x, y) && transfer_index_at(m, x, y) != 0;
}

/* ------------------------------------------------------------------------- */
/* World rendering                                                           */
/* ------------------------------------------------------------------------- */

static void vm_begin_map_scroll(int direction,int distance,int speed)
{
    if(speed<1)speed=1;
    if(speed>6)speed=6;
    g_map_scroll_start_x=g_camera_scroll_x;g_map_scroll_start_y=g_camera_scroll_y;
    g_map_scroll_target_x=g_camera_scroll_x;g_map_scroll_target_y=g_camera_scroll_y;
    if(direction==2)g_map_scroll_target_y+=distance*TILE_PX;
    else if(direction==4)g_map_scroll_target_x-=distance*TILE_PX;
    else if(direction==6)g_map_scroll_target_x+=distance*TILE_PX;
    else if(direction==8)g_map_scroll_target_y-=distance*TILE_PX;
    g_map_scroll_total=distance*256/(1<<speed);
    if(g_map_scroll_total<1)g_map_scroll_total=1;
    g_map_scroll_remaining=g_map_scroll_total;
}
static void tick_map_scroll(void)
{
    float t;
    if(g_map_scroll_remaining<=0)return;
    --g_map_scroll_remaining;
    t=(float)(g_map_scroll_total-g_map_scroll_remaining)/g_map_scroll_total;
    g_camera_scroll_x=g_map_scroll_start_x+(g_map_scroll_target_x-g_map_scroll_start_x)*t;
    g_camera_scroll_y=g_map_scroll_start_y+(g_map_scroll_target_y-g_map_scroll_start_y)*t;
}

static void compute_camera(
    const MapState *m, float player_x, float player_y,
    float *camera_x, float *camera_y, float *origin_x, float *origin_y)
{
    float map_w = (float)(m->w * TILE_PX);
    float map_h = (float)(m->h * TILE_PX);
    float max_x = map_w > SCREEN_W ? map_w - SCREEN_W : 0.0f;
    float max_y = map_h > SCREEN_H ? map_h - SCREEN_H : 0.0f;

    *origin_x = map_w < SCREEN_W ? (SCREEN_W - map_w) * 0.5f : 0.0f;
    *origin_y = map_h < SCREEN_H ? (SCREEN_H - map_h) * 0.5f : 0.0f;

    /* These rooms have asymmetric empty map margins. Centre their visible
     * geometry without changing event coordinates, collision or vertical scroll. */
    if (m->id == 11 || m->id == 21 || m->id == 23 || m->id == 27) *origin_x += TILE_PX;
    if (m->id == 13) {
        *origin_x = TILE_PX * 0.5f;
        max_x = 0.0f;
    }

    if (g_camera_locked) {
        *camera_x = clamp_float(g_camera_lock_x + g_camera_scroll_x, 0.0f, max_x);
        *camera_y = clamp_float(g_camera_lock_y + g_camera_scroll_y, 0.0f, max_y);
        return;
    }

    *camera_x = max_x > 0.0f
        ? clamp_float(player_x - SCREEN_W * 0.5f + g_camera_scroll_x, 0.0f, max_x)
        : 0.0f;
    *camera_y = max_y > 0.0f
        ? clamp_float(player_y - SCREEN_H * 0.5f + g_camera_scroll_y, 0.0f, max_y)
        : 0.0f;

}

static void draw_map_slot_local(uint16_t local_slot, float x, float y)
{
    int index;
    int sx;
    int sy;

    if (local_slot == 0) return;
    index = (int)local_slot - 1;
    sx = (index % TILE_ATLAS_COLS) * TILE_SLOT + 1;
    sy = (index / TILE_ATLAS_COLS) * TILE_SLOT + 1;

    draw_bound_rect(
        (float)sx, (float)sy, (float)TILE_SOURCE, (float)TILE_SOURCE,
        x, y, (float)TILE_PX, (float)TILE_PX
    );
}

static void draw_character_frame(
    int pattern, int direction_row, float foot_x, float foot_y)
{
    int sx, sy;
    if (pattern < 0 || pattern > 2) pattern = 1;
    if (direction_row < 0 || direction_row > 3) direction_row = 0;
    sx = pattern * CHAR_SLOT_W + 1;
    sy = direction_row * CHAR_SLOT_H + 1;
    /* MZ Game_CharacterBase.screenX/screenY use Math.floor(). */
    draw_bound_rect(
        (float)sx, (float)sy, (float)CHAR_SRC_W, (float)CHAR_SRC_H,
        foot_x - CHAR_DST_W * 0.5f,
        foot_y - CHAR_DST_H,
        (float)CHAR_DST_W, (float)CHAR_DST_H
    );
}

static void draw_fall_frame(int slot, float foot_x, float foot_y)
{
    int sx = slot * FALL_SLOT_W + 1;
    foot_x = render_floor_pixel(foot_x);
    foot_y = render_floor_pixel(foot_y);
    draw_bound_rect(
        (float)sx, 1.0f, (float)FALL_SRC_W, (float)FALL_SRC_H,
        foot_x - FALL_DST_W * 0.5f,
        foot_y - FALL_DST_H,
        (float)FALL_DST_W, (float)FALL_DST_H
    );
}

static void draw_map_pass(
    const MapState *m, int upper,
    float camera_x, float camera_y, float origin_x, float origin_y)
{
    int y;
    int bound_atlas = -1;

    /* Never let Fog A1 / monitor / fitted-picture GU_LINEAR state bleed into
     * map-atlas sampling.  The atlases have transparent gutters, so LINEAR for
     * even one frame creates a visible contour around bricks and sprites. */
    set_pixel_art_texture_state();

    for (y = 0; y < m->h; ++y) {
        float dy = origin_y + (float)(y * TILE_PX) - camera_y;
        int x;
        if (dy <= -TILE_PX || dy >= SCREEN_H) continue;

        for (x = 0; x < m->w; ++x) {
            float dx = origin_x + (float)(x * TILE_PX) - camera_x;
            int z;
            if (dx <= -TILE_PX || dx >= SCREEN_W) continue;

            for (z = 0; z < 4; ++z) {
                uint16_t word = map_word(m, z, x, y);
                uint16_t global_slot;
                int is_upper;
                int atlas_index;
                uint16_t local_slot;

                if (word == 0) continue;
                is_upper = (word & 0x8000) != 0;
                if (is_upper != upper) continue;

                global_slot = word & 0x3FFF;
                atlas_index = ((int)global_slot - 1) / 100;
                local_slot = (uint16_t)(((global_slot - 1) % 100) + 1);
                if (atlas_index < 0 || atlas_index >= m->tile_atlas_count) continue;

                if (bound_atlas != atlas_index) {
                    bind_texture_8888(
                        m->tile_atlases[atlas_index],
                        TILE_ATLAS_W, TILE_ATLAS_H
                    );
                    bound_atlas = atlas_index;
                }
                if(word & 0x4000)sceGuTexFilter(GU_LINEAR,GU_LINEAR);
                draw_map_slot_local(local_slot, dx, dy);
                if(word & 0x4000)sceGuTexFilter(GU_NEAREST,GU_NEAREST);
            }
        }
    }
}

/* Crowded source sheets use one detail page, freed on map transfer. */
static void *g_event_texture_base,*g_event_texture_detail,*g_event_texture_bound;

static void draw_event_sprite_record(
    const EventSpriteRecord *sp, int map_id,
    float camera_x, float camera_y, float origin_x, float origin_y)
{
    float shift_x = sp->event_id >= 0 && sp->event_id < MAX_EVENT_ID
        ? g_event_shift_x[sp->event_id] : 0.0f;
    float shift_y = sp->event_id >= 0 && sp->event_id < MAX_EVENT_ID
        ? g_event_shift_y[sp->event_id] : 0.0f;
    /* At native PSP scale the slow fall moves only 0.375 px/frame.
     * Preserve its fractional position with isolated high-resolution frames;
     * all other pixel-art sprites keep their established integer alignment. */
    int smooth_fall = (map_id == 1 && sp->event_id == 5 && g_routes[5].remaining > 0) ||
                      (map_id == 16 && sp->event_id == 36) ||
                      (map_id == 12 && (sp->flags & 0x04)) || (map_id == 30 && (sp->flags & 0x04)) || (map_id == 39 && (sp->flags & 0x04)) ||
                      is_chase_enemy(map_id,sp->event_id) || (map_id==32 && sp->event_id==19);
    if ((map_id == 1 && sp->event_id == 5) || (map_id == 16 && sp->event_id == 36)) {
        camera_x = g_actor_camera_x;
        camera_y = g_actor_camera_y;
    }
    float foot_x = origin_x + ((float)sp->x + shift_x + 0.5f) * TILE_PX - camera_x;
    float foot_y = origin_y + ((float)sp->y + shift_y + 1.0f) * TILE_PX - camera_y;
    if(sp->event_id>=0 && sp->event_id<MAX_EVENT_ID)foot_y-=g_event_jump_height[sp->event_id];
    if (!smooth_fall) {
        foot_x = render_floor_pixel(foot_x);
        foot_y = render_floor_pixel(foot_y);
    }
    void *texture=(sp->sx>>12) ? g_event_texture_detail : g_event_texture_base;
    if(texture && texture!=g_event_texture_bound) {
        bind_texture_8888(texture,EVENT_ATLAS_W,EVENT_ATLAS_H);
        g_event_texture_bound=texture;
    }
    float src_x = (float)(sp->sx & 0x0FFF);
    float src_y = (float)sp->sy;
    if((sp->flags&0x40) && sp->event_id>=0 && sp->event_id<MAX_EVENT_ID && g_event_direction[sp->event_id]>=0) {
        int row=g_event_direction[sp->event_id];
        if ((is_chase_enemy(map_id,sp->event_id) || (map_id==27 && sp->event_id==1) || (map_id==35 && sp->event_id==7) || (map_id==36 && sp->event_id==16) || map_id==39) && (sp->flags&0x84)==0x84) {
            src_x+=(row&1)*3*sp->sw;
            src_y+=(row>>1)*sp->sh;
        } else if(map_id==43 && (sp->flags&4)) {
            src_x+=(row&1)*sp->sw;src_y+=(row>>1)*sp->sh;
        } else src_y+=row*sp->sh;
    }
    float dst_w = (float)sp->sw;
    float dst_h = (float)sp->sh;
    float shift = (sp->flags & 0x01) ? 0.0f : 3.0f;

    /* Sprite flag bit 1 means that the atlas stores the three RPG Maker
     * patterns horizontally.  Step animation uses the engine's standing
     * cadence: animationWait=(9-moveSpeed)*3 and visual sequence
     * 1 -> 2 -> 1 -> 0.  This restores animated SAVE arrows, key monitors,
     * keys, etc. instead of baking a single middle frame forever. */
    if (sp->flags & 0x80) {
        int id = sp->event_id;
        int pattern = id > 0 && id < MAX_EVENT_ID
            ? g_event_animation[id].pattern : 1;
        if (pattern >= 3) pattern = 1;
        /* Map035's escape scene forces seven up steps and thirteen right
         * steps at speed5 (one tile per eight frames). Keep the visible gait
         * tied to those actual steps even during blocking scene playback.
         * Pauses and look-around commands retain the regular idle state. */
        if(map_id==35 && id==7 && g_routes[id].records &&
           (g_routes[id].dx || g_routes[id].dy)) {
            static const int gait[4]={1,2,1,0};
            float x=g_event_shift_x[id],y=g_event_shift_y[id];
            int steps=(int)((x<0?-x:x)+(y<0?-y:y));
            pattern=gait[steps&3];
        }
        src_x += pattern * sp->sw;
    }
    if (sp->flags & 0x02) {
        static const int sequence[4] = {1, 2, 1, 0};
        int speed = (sp->flags >> 3) & 0x07;
        int wait_frames;
        int phase;
        if (speed < 1) speed = 3;
        if (speed > 6) speed = 6;
        wait_frames = (9 - speed) * 3;
        if (wait_frames < 1) wait_frames = 1;
        phase = (int)((g_world_render_frames / (unsigned int)wait_frames) & 3u);
        src_x += (float)(sequence[phase] * sp->sw);
    }

    /* Flag bit 2 keeps a wide/detail-heavy source sprite at original PC
     * resolution in the atlas, but renders it at PSP half size.  Hardware
     * linear filtering preserves the tiny monitor lettering much better than
     * throwing away every other pixel during conversion. */
    if (sp->flags & 0x04) {
        float scale = (((map_id==21 || map_id==23 || map_id==27) && sp->sw==36 && sp->sh==144) || ((map_id==27 || (map_id>=32 && map_id<=39)) && sp->sw==54 && sp->sh==108) || (map_id==40 && sp->sw==108 && sp->sh==324)) ? (2.0f/3.0f) : 0.5f;
        dst_w *= scale;
        dst_h *= scale;
        sceGuTexFilter(GU_LINEAR, GU_LINEAR);
    } else {
        sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    }

    if((map_id==33 || map_id==34) && sp->sw==144 && sp->sh==96)
        sceGuTexFilter(GU_NEAREST,GU_NEAREST);

    if (map_id == 16 || ((map_id == 24 || map_id == 25) && sp->event_id == 3))
        sceGuTexFilter(GU_LINEAR, GU_LINEAR);

    if(sp->event_id>=0 && sp->event_id<MAX_EVENT_ID && g_event_opacity[sp->event_id]!=255) {
        sceGuTexFunc(GU_TFX_MODULATE,GU_TCC_RGBA);
        sceGuColor(((unsigned int)g_event_opacity[sp->event_id]<<24)|0xFFFFFFu);
    }
    draw_bound_rect(
        src_x, src_y, (float)sp->sw, (float)sp->sh,
        foot_x - dst_w * 0.5f,
        foot_y - shift - dst_h,
        dst_w, dst_h
    );

    set_pixel_art_texture_state();
}

static int is_dedicated_story_key_event(int map_id, int event_id)
{
    return (map_id == 5 && event_id == 7) ||
           (map_id == 15 && event_id == 12) ||
           (map_id == 19 && event_id == 2);
}

/* MZ sorts equal-priority sprites by foot Y. This keeps moving characters
 * behind foreground tentacles and corpse barricades at the correct depth. */
static void draw_tentacle_room_sprites(
    const MapState *m, int priority, int side, float player_y,
    float camera_x, float camera_y, float origin_x, float origin_y)
{
    EventSpriteRecord sprites[MAX_EVENT_ID];
    float ys[MAX_EVENT_ID];
    int count=0,i;
    for(i=0;i<m->vm_event_count && count<MAX_EVENT_ID;++i) {
        VmEventRecord ev;VmPageRecord pg;EventSpriteRecord sp;
        int active,j;float y;
        if(!vm_read_event(m,i,&ev) || !vm_active_page_index(m,&ev,&pg,&active)) continue;
        if(pg.priority!=priority || !pg.sprite_ref || !read_sprite_record(m,pg.sprite_ref-1,&sp)) continue;
        if(ev.event_id>0 && ev.event_id<MAX_EVENT_ID) {
            int id=ev.event_id;
            if(g_event_active_page[id]!=active) {
                g_event_active_page[id]=active;
                g_event_direction[id]=(pg.flags>>5)&3;
                g_event_move_speed[id]=(pg.flags>>2)&7;
                g_event_direction_fix[id]=!!(pg.flags&0x80);
                g_event_through[id]=!!(pg.flags&1);
                g_event_opacity[id]=255;
                player_animation_reset(&g_event_animation[id]);
            }
        }
        y=(ev.y+1.0f+(ev.event_id<MAX_EVENT_ID?g_event_shift_y[ev.event_id]:0))*TILE_PX;
        if(ev.event_id>=0 && ev.event_id<MAX_EVENT_ID)y-=g_event_jump_height[ev.event_id];
        if(priority==1 && ((side<0 && y>player_y)||(side>0 && y<=player_y))) continue;
        j=count;
        while(j>0 && (ys[j-1]>y || (ys[j-1]==y && sprites[j-1].event_id>sp.event_id))) {
            sprites[j]=sprites[j-1];ys[j]=ys[j-1];--j;
        }
        sprites[j]=sp;ys[j]=y;++count;
    }
    for(i=0;i<count;++i)
        draw_event_sprite_record(&sprites[i],m->id,camera_x,camera_y,origin_x,origin_y);
}

static void draw_event_sprites(
    const MapState *m, int priority, int side_of_player,
    float player_world_y,
    float camera_x, float camera_y, float origin_x, float origin_y)
{
    int i;
    if (!m->event_atlas || m->sprite_count <= 0) return;

    g_event_texture_base=m->event_atlas;g_event_texture_detail=m->event_atlas_detail;
    bind_texture_8888(m->event_atlas, EVENT_ATLAS_W, EVENT_ATLAS_H);
    g_event_texture_bound=m->event_atlas;
    if((m->id==16 || m->id==30 || (m->id>=32 && m->id<=45)) && (m->vm_flags&1) && m->vm_bin) {
        draw_tentacle_room_sprites(m,priority,side_of_player,player_world_y,
                                  camera_x,camera_y,origin_x,origin_y);
        return;
    }

    /* 0.6.4 atlases contain a sprite record for every visual event page and
     * each VM page points at its matching record.  This is essential for the
     * original switch-driven cutscenes: falling Enri/Lucas, corpses, the meat
     * wall, key shutters, etc.  Older assets keep the static 0.5.x path. */
    if ((m->vm_flags & 0x01u) && m->vm_bin) {
        for (i = 0; i < m->vm_event_count; ++i) {
            VmEventRecord ev;
            VmPageRecord pg;
            EventSpriteRecord sp;
            float event_y;
            int sprite_index;
            int active_index;

            if (!vm_read_event(m, i, &ev)) continue;
            if (g_key_anim && is_dedicated_story_key_event(m->id, ev.event_id)) continue;
            if (!vm_active_page_index(m, &ev, &pg, &active_index)) continue;
            if ((m->id == 12 || m->id == 24 || m->id == 25 || m->id == 27 || m->id == 30 || (m->id >= 32 && m->id <= 45)) && ev.event_id > 0 && ev.event_id < MAX_EVENT_ID &&
                g_event_active_page[ev.event_id] != active_index) {
                g_event_active_page[ev.event_id] = active_index;
                g_event_direction[ev.event_id] = (pg.flags >> 5) & 3;
                g_event_move_speed[ev.event_id] = (pg.flags >> 2) & 7;
                g_event_direction_fix[ev.event_id] = !!(pg.flags & 0x80);
                g_event_through[ev.event_id] = !!(pg.flags & 1);
                g_event_opacity[ev.event_id] = 255;
                player_animation_reset(&g_event_animation[ev.event_id]);
            }
            if (pg.sprite_ref <= 0) continue;
            if (pg.priority != priority) continue;

            sprite_index = pg.sprite_ref - 1;
            if (!read_sprite_record(m, sprite_index, &sp)) continue;
            if(ev.event_id>=0 && ev.event_id<MAX_EVENT_ID && g_event_direction[ev.event_id]<0)
                g_event_direction[ev.event_id]=(pg.flags>>5)&3;

            if (priority == 1 && side_of_player != 0) {
                event_y = ((float)ev.y + 1.0f +
                    (ev.event_id < MAX_EVENT_ID ? g_event_shift_y[ev.event_id] : 0.0f)) * TILE_PX;
                if (side_of_player < 0 && event_y > player_world_y) continue;
                if (side_of_player > 0 && event_y <= player_world_y) continue;
            }

            draw_event_sprite_record(&sp, m->id, camera_x, camera_y, origin_x, origin_y);
        }
        return;
    }

    for (i = 0; i < m->sprite_count; ++i) {
        EventSpriteRecord sp;
        float event_y;
        if (!read_sprite_record(m, i, &sp)) continue;
        if (g_key_anim && is_dedicated_story_key_event(m->id, sp.event_id)) continue;
        if (sp.priority != priority) continue;

        if (priority == 1 && side_of_player != 0) {
            event_y = ((float)sp.y + 1.0f +
                (sp.event_id < MAX_EVENT_ID ? g_event_shift_y[sp.event_id] : 0)) * TILE_PX;
            if (side_of_player < 0 && event_y > player_world_y) continue;
            if (side_of_player > 0 && event_y <= player_world_y) continue;
        }

        draw_event_sprite_record(&sp, m->id, camera_x, camera_y, origin_x, origin_y);
    }
}

/* Dedicated early key rendering.
 *
 * The original !鍵 sheet uses direction rows as key colours.  Several PSP
 * builds had correct VM state but the tiny page sprite still vanished behind
 * the early map/event-atlas path.  0.7.4 keeps the original three animation
 * frames in a tiny dedicated texture and draws these story keys after the
 * upper tile pass.  Switches remain authoritative, so collected keys vanish. */
static void draw_story_key_foreground(
    const MapState *m,
    float camera_x, float camera_y, float origin_x, float origin_y,
    int side_of_player, float player_world_y)
{
    static const int sequence[4] = {1, 2, 1, 0};
    int row = -1;
    int tx = 0, ty = 0;
    int speed = 3;
    int wait_frames, phase;
    float foot_x, foot_y;

    if (!m || !g_key_anim) return;

    if (m->id == 5 && !g_switches[144]) {
        row = 0; tx = 2; ty = 3;      /* Red Key */
    } else if (m->id == 15 && !g_switches[142]) {
        row = 1; tx = 2; ty = 4;      /* Iron Key */
    } else if (m->id == 19 && !g_switches[143]) {
        row = 2; tx = 6; ty = 2;      /* Green Key */
    } else {
        return;
    }

    if (side_of_player < 0 && (ty + 1.0f) * TILE_PX > player_world_y) return;
    if (side_of_player > 0 && (ty + 1.0f) * TILE_PX <= player_world_y) return;
    wait_frames = (9 - speed) * 3;
    phase = (int)((g_world_render_frames / (unsigned int)wait_frames) & 3u);
    foot_x = origin_x + ((float)tx + 0.5f) * TILE_PX - camera_x;
    foot_y = origin_y + ((float)ty + 1.0f) * TILE_PX - camera_y;

    bind_texture_8888(g_key_anim, KEY_ANIM_W, KEY_ANIM_H);
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    sceGuColor(0xFFFFFFFF);
    draw_bound_rect(
        (float)(sequence[phase] * 32), (float)(row * 32), 24.0f, 24.0f,
        /* !-prefixed RPG Maker object characters use no 6px foot offset. */
        foot_x - 12.0f, foot_y - 24.0f, 24.0f, 24.0f
    );
}

static PictureSlot *picture_slot(int number)
{
    int i;
    PictureSlot *empty = NULL;
    if (number < 1 || number > 100) return NULL;
    for (i = 0; i < MAX_ACTIVE_PICTURES; ++i) {
        if (g_pictures[i].number == number) return &g_pictures[i];
        if (!g_pictures[i].number) empty = &g_pictures[i];
    }
    return empty;
}

static void erase_picture_slot(int number)
{
    int i;
    for (i = 0; i < MAX_ACTIVE_PICTURES; ++i) {
        if (g_pictures[i].number != number) continue;
        if (g_pictures[i].texture) free(g_pictures[i].texture);
        memset(&g_pictures[i], 0, sizeof(g_pictures[i]));
        return;
    }
}

static void picture_show(int number, int resource_id, int origin,
                         int x, int y, int zoomx, int zoomy, int opacity)
{
    char path[180];
    unsigned char header[8],portrait_header[12];
    int portrait=0;
    FILE *fp;
    PictureSlot *slot;
    void *data;
    if (number == 6 && resource_id == 0) {
        g_picture6_alpha = opacity;
        g_picture6_visible = opacity > 0;
        return;
    }
    if (resource_id < 1) return;
    erase_picture_slot(number);
    if (number == 6) { g_picture6_visible = 0; g_picture6_alpha = 0; }
    slot = picture_slot(number);
    if (!slot) return; /* PSP-1000 memory cap: max five pictures */
    snprintf(path, sizeof(path), ASSET_ROOT "pic_%03d.p44", resource_id);
    fp = fopen(path,"rb");
    if (!fp) return;
    if (fread(header,1,8,fp) != 8 ||
        (memcmp(header,"NP50",4) != 0 && memcmp(header,"NGO1",4) != 0 && memcmp(header,"NPR1",4) != 0)) {
        fclose(fp);return;
    }
    portrait=memcmp(header,"NPR1",4)==0;
    if(portrait && fread(portrait_header,1,12,fp)!=12) {fclose(fp);return;}
    if(read_u16_le(header+4)<1 || read_u16_le(header+6)<1 ||
       read_u16_le(header+4)>512 || read_u16_le(header+6)>512) {fclose(fp);return;}
    data = memalign(16, 512 * 512 * 2);
    if (!data) { fclose(fp); return; }
    if (fread(data,1,512*512*2,fp) != 512*512*2) {
        free(data); fclose(fp);return;
    }
    fclose(fp);
    sceKernelDcacheWritebackInvalidateAll();
    slot->number = number; slot->resource_id = resource_id;
    slot->w = (int)read_u16_le(header+4);slot->h=(int)read_u16_le(header+6);
    slot->source_w=slot->w;slot->source_h=slot->h;slot->portrait=portrait;
    if(portrait) {
        slot->w=read_u16_le(portrait_header);slot->h=read_u16_le(portrait_header+2);
        slot->picture_offset_x=read_u16_le(portrait_header+4)*0.5f;
        slot->picture_offset_y=read_u16_le(portrait_header+6)*0.5f;
        slot->picture_region_w=read_u16_le(portrait_header+8)*0.5f;
        slot->picture_region_h=read_u16_le(portrait_header+10)*0.5f;
    }
    slot->origin=origin;slot->x=x;slot->y=y;
    slot->scale_x=zoomx;slot->scale_y=zoomy;slot->opacity=opacity;
    /* Keep the NGO1 asset tag, but also recognise the canonical NARAKU
     * Game Over resource IDs / dimensions at runtime.  This makes old picture
     * manifests harmless: the 816x624 originals (408x312 PSP assets) are
     * always fitted inside 480x272 instead of being cropped at y=-20. */
    slot->fit_screen =
        (memcmp(header,"NGO1",4) == 0) ||
        (resource_id == 9 && slot->w == SCREEN_W && slot->h == SCREEN_H) ||
        (resource_id >= 90 && resource_id <= 97) ||
        (!portrait && number == 11 && slot->w == 408 && slot->h == 312);
    slot->texture=data;
}

static void draw_fog_a1_overlay(int effect_active)
{
    float u;

    /* Original Common Event 15 ("フォグ起動") moves picture #7 by exactly
     * 816 source pixels over 816 frames.  On the 816px PC viewport that is a
     * clean one-pixel step every frame.  Earlier PSP builds resized one period
     * to 480px and then MOVED the destination quad by 480/816 px per frame.
     * Even with linear filtering this makes the translucent mask interact with
     * PPSSPP's final screen scaling and can look like the bricks/body piles are
     * trembling while the world is otherwise still (messages/scripts).
     *
     * 0.7.7 keeps the screen quad completely fixed.  The 816px period is
     * prepared as a 512-texel seamless strip, GU_REPEAT wraps U, and only the
     * texture coordinate advances by 512/816 texels per vblank.  This retains
     * the original 816-frame loop while removing geometry/raster stepping. */
    if (!g_fog_overlay || !effect_active) {
        g_fog_scroll = 0.0f;
        g_fog_active_prev = 0;
        return;
    }

    if (!g_fog_active_prev) {
        g_fog_scroll = 0.0f;
        g_fog_active_prev = 1;
    }

    u = g_fog_scroll;
    sceGuTexMode(GU_PSM_8888, 0, 0, GU_FALSE);
    sceGuTexImage(0, 512, 512, 512, g_fog_overlay);
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_LINEAR, GU_LINEAR);
    sceGuTexWrap(GU_REPEAT, GU_CLAMP);
    sceGuColor(0xFFFFFFFF);

    /* One complete 512-texel fog period is mapped across the whole PSP screen.
     * Sampling beyond u=512 wraps seamlessly to the same strip. */
    draw_bound_rect(
        u, 0.0f, 512.0f, (float)SCREEN_H,
        0.0f, 0.0f, (float)SCREEN_W, (float)SCREEN_H
    );

    /* Restore the canonical pixel-art state immediately.  In 0.7.7 the fog
     * left GU_LINEAR active, and because GU state persists between frames the
     * next map pass could be linearly sampled for exactly one frame. */
    set_pixel_art_texture_state();

    g_fog_scroll += 512.0f / 816.0f;
    if (g_fog_scroll >= 512.0f)
        g_fog_scroll -= 512.0f;
}

static void clear_event_routes(void)
{
    g_s003_paused = 0;
    memset(g_factory_page,0,sizeof(g_factory_page));
    g_factory_machine_frame=g_factory_corpse_phase=0;
    g_pressing_room_frame = 0;
    g_laser_room_frame = g_laser_stop_count = g_laser_route_index = 0;
    int i;
    free(g_player_route.records);memset(&g_player_route,0,sizeof(g_player_route));
    for(i=0;i<MAX_EVENT_ID;++i) {
        free(g_routes[i].records);memset(&g_routes[i],0,sizeof(EventRoute));
        g_event_jump_height[i]=0;g_event_opacity[i]=255;g_event_through[i]=0;g_event_direction[i]=-1;g_event_direction_fix[i]=0;g_event_erased[i]=0;
        player_animation_reset(&g_event_animation[i]);
    }
}

static int event_route_can_step(const MapState *m, int id, int x, int y, int code)
{
    int dx=code==2?-1:(code==3?1:0), dy=code==1?1:(code==4?-1:0);
    int bit=code==1?1:(code==2?2:(code==3?4:8));
    int reverse=code==1?8:(code==2?4:(code==3?2:1));
    return code>=1 && code<=4 && (pass_mask_at(m,x,y)&bit) &&
           (pass_mask_at(m,x+dx,y+dy)&reverse) &&
           !vm_event_blocks_except(m,x+dx,y+dy,id);
}

static int g_s003_player_x, g_s003_player_y;
static void tick_event_routes(const MapState *m)
{
    int id;
    for(id=1;id<MAX_EVENT_ID;++id) {
        EventRoute *r=&g_routes[id];
        int budget=128;
        if(!r->records)continue;
        if(r->remaining>0) {
            float t=(float)(r->total-r->remaining+1)/r->total;
            g_event_shift_x[id]=r->start_x+r->dx*t;
            g_event_shift_y[id]=r->start_y+r->dy*t;
            --r->remaining;
            if(r->jump_peak>0) {
                int d=abs(r->remaining-r->jump_peak);
                g_event_jump_height[id]=(r->jump_peak*r->jump_peak-d*d)*.25f;
            }
            continue;
        }
        while(r->records && budget-->0) {
            const uint8_t *p;int code,n;
            if(r->index>=r->count) {
                if((r->flags&1) && r->count) {r->index=0;break;}
                free(r->records);memset(r,0,sizeof(*r));break;
            }
            p=r->records+r->index*5;code=p[0];n=(int16_t)read_u16_le(p+1);
            ++r->index;
            r->jump_peak=0;g_event_jump_height[id]=0;
            if(code==14) {
                int dx=n,dy=(int16_t)read_u16_le(p+3),sq=dx*dx+dy*dy,distance=0;
                int speed=g_event_move_speed[id]>0?g_event_move_speed[id]:3;
                while((distance+1)*(distance+1)<=sq)++distance;
                if(sq-distance*distance >= (distance+1)*(distance+1)-sq)++distance;
                if(!g_event_direction_fix[id]) {
                    if(abs(dx)>abs(dy) && dx)g_event_direction[id]=dx<0?1:2;
                    else if(dy)g_event_direction[id]=dy<0?3:0;
                }
                player_animation_reset(&g_event_animation[id]);
                r->jump_peak=10+distance-speed;
                if(r->jump_peak<1)r->jump_peak=1;
                r->dx=dx;r->dy=dy;r->start_x=g_event_shift_x[id];r->start_y=g_event_shift_y[id];
                r->total=r->jump_peak*2;r->remaining=r->total-1;
                g_event_shift_x[id]=r->start_x+(float)dx/r->total;
                g_event_shift_y[id]=r->start_y+(float)dy/r->total;
                g_event_jump_height[id]=(2*r->jump_peak-1)*.25f;
                break;
            }
            if(code==9)code=1+rand()%4;
            if(code==10) {
                int x=r->base_x+(int)(g_event_shift_x[id]+(g_event_shift_x[id]<0?-.5f:.5f));
                int y=r->base_y+(int)(g_event_shift_y[id]+(g_event_shift_y[id]<0?-.5f:.5f));
                int dx=g_s003_player_x-x, dy=g_s003_player_y-y;
                int secondary;
                if (abs(dx)>abs(dy)) {
                    code=dx>0?3:2; secondary=dy>0?1:(dy<0?4:0);
                } else {
                    code=dy>0?1:(dy<0?4:0); secondary=dx>0?3:(dx<0?2:0);
                }
                if (code && !g_event_through[id] && !event_route_can_step(m,id,x,y,code) &&
                    secondary && event_route_can_step(m,id,x,y,secondary)) code=secondary;
            }
            if(code==13)code=4-g_event_direction[id];
            if(code==29)g_event_move_speed[id]=n<1?1:(n>6?6:n);
            else if(code>=16 && code<=19) {
                if(!g_event_direction_fix[id])g_event_direction[id]=code-16;
                /* MZ updates these rotating sensors once per frame. Consuming
                 * all four turns at once would display only the last beam. */
                if(m->id==43 && (id==5 || id==8))break;
            }
            else if(code==35)g_event_direction_fix[id]=1;
            else if(code==36)g_event_direction_fix[id]=0;
            else if(code==37)g_event_through[id]=1;
            else if(code==38)g_event_through[id]=0;
            else if(code==39)g_event_opacity[id]=0;
            else if(code==40)g_event_opacity[id]=255;
            else if(code==42)g_event_opacity[id]=n<0?0:(n>255?255:n);
            else if(code==44)play_vm_se_params(n,90,100,0);
            else if(code==15 || (code>=1 && code<=4)) {
                int speed=g_event_move_speed[id];
                r->dx=code==2?-1:(code==3?1:0);r->dy=code==1?1:(code==4?-1:0);
                if(code!=15 && !g_event_through[id]) {
                    int x=r->base_x+(int)(g_event_shift_x[id] + (g_event_shift_x[id] < 0 ? -0.5f : 0.5f));
                    int y=r->base_y+(int)(g_event_shift_y[id] + (g_event_shift_y[id] < 0 ? -0.5f : 0.5f));
                    int nx=x+r->dx,ny=y+r->dy;
                    int bit=code==1?1:(code==2?2:(code==3?4:8));
                    int reverse=code==1?8:(code==2?4:(code==3?2:1));
                    if(!(pass_mask_at(m,x,y)&bit) || !(pass_mask_at(m,nx,ny)&reverse) || vm_event_blocks_except(m,nx,ny,id)) {
                        r->dx=r->dy=0;
                        if (!(r->flags & 2)) {
                            /* One record per blocked command, not every frame. */
                            static int last_map = -1, last_id = -1, last_index = -1;
                            if (last_map != m->id || last_id != id || last_index != r->index) {
                                FILE *log = fopen(g_scene_trace_path, "a");
                                if (log) {
                                    fprintf(log, "map=%d event=%d step=%d code=%d from=%d,%d to=%d,%d pass=%d reverse=%d event_block=%d\n",
                                            m->id,id,r->index,p[0],x,y,nx,ny,
                                            pass_mask_at(m,x,y)&bit,pass_mask_at(m,nx,ny)&reverse,
                                            vm_event_blocks_except(m,nx,ny,id));
                                    fclose(log);
                                }
                                last_map=m->id;last_id=id;last_index=r->index;
                            }
                            --r->index;
                        }
                        break;
                    }
                }
                if(code>=1 && code<=4 && p[0]!=13 && !g_event_direction_fix[id])
                    g_event_direction[id]=code-1;
                r->start_x=g_event_shift_x[id];r->start_y=g_event_shift_y[id];
                r->total=code==15?n:(256/(1<<(speed>0?speed:3)));
                r->remaining=r->total;
                if(r->remaining>0) {
                    g_event_shift_x[id]+= (float)r->dx/r->total;
                    g_event_shift_y[id]+= (float)r->dy/r->total;
                    --r->remaining;break;
                }
            }
        }
    }
    for (id = 1; id < MAX_EVENT_ID; ++id) {
        EventRoute *r = &g_routes[id];
        int moving = r->records && r->remaining > 0 && (r->dx || r->dy);
        player_animation_tick(&g_event_animation[id], moving, r->jump_peak>0 && r->remaining>0,
                              g_event_move_speed[id] > 0 ? g_event_move_speed[id] : 3,
                              1, (m->id == 30 && id == 3) || (m->id == 39 && id >= 2 && id <= 4));
    }
    (void)m;
}

static int start_event_route(const MapState *m,int id,const uint8_t *records,int count,int flags)
{
    EventRoute *r; int i;
    if(id<1 || id>=MAX_EVENT_ID || count<=0)return 0;
    r=&g_routes[id];free(r->records);memset(r,0,sizeof(*r));g_event_jump_height[id]=0;
    r->records=malloc(count*5);if(!r->records)return 0;
    memcpy(r->records,records,count*5);r->count=count;r->flags=flags;
    for(i=0;i<m->vm_event_count;++i) {
        VmEventRecord ev;VmPageRecord pg;int page_index;
        if(vm_read_event(m,i,&ev) && ev.event_id==id && vm_active_page_index(m,&ev,&pg,&page_index)) {
            if(g_event_active_page[id]!=page_index || !g_event_move_speed[id]) {
                g_event_active_page[id]=page_index;
                g_event_move_speed[id]=(pg.flags>>2)&7;
                g_event_direction[id]=(pg.flags>>5)&3;g_event_direction_fix[id]=!!(pg.flags&0x80);
                g_event_through[id]=!!(pg.flags&1);
                g_event_opacity[id]=255;
            }
            r->base_x=ev.x;r->base_y=ev.y;break;
        }
    }
    return 1;
}

#include "runtime/s003_routes.h"
static void tick_s003_autonomous(const MapState *m, float player_x, float player_y)
{
    int i;
    g_s003_player_x=(int)(player_x/TILE_PX);
    g_s003_player_y=(int)(player_y/TILE_PX)-1;
    if (g_s003_paused || (m->id != 24 && m->id != 25)) return;
    for(i=0;i<m->vm_event_count;++i) {
        VmEventRecord ev; VmPageRecord pg; int page;
        if (!vm_read_event(m,i,&ev) || ev.event_id!=3 ||
            !vm_active_page_index(m,&ev,&pg,&page)) continue;
        if ((m->id==24 && page==ev.first_page+5) || (m->id==25 && page==ev.first_page+1)) {
            if (!g_routes[3].records) {
                const uint8_t *route=m->id==24?s003_route_24:s003_route_25;
                int count=(m->id==24?sizeof(s003_route_24):sizeof(s003_route_25))/5;
                start_event_route(m,3,route,count,3);
            }
        }
        return;
    }
}

#include "runtime/factory_routes.h"
static void tick_factory_autonomous(const MapState *m)
{
    unsigned int i;
    if((m->id<32 || m->id>34) && m->id!=43)return;
    if(g_s003_paused)return;
    for(i=0;i<sizeof(factory_routes)/sizeof(factory_routes[0]);++i) {
        const FactoryRoute *fr=&factory_routes[i];
        int k,active;VmEventRecord ev;VmPageRecord pg;
        if(fr->map!=m->id)continue;
        for(k=0;k<m->vm_event_count;++k) {
            if(!vm_read_event(m,k,&ev) || ev.event_id!=fr->id)continue;
            if(!vm_active_page_index(m,&ev,&pg,&active))break;
            active-=ev.first_page;
            if(active!=fr->page) {
                /* Page changes cancel an autonomous route, as in MZ. */
                if(g_factory_page[fr->id]==fr->page+1) {
                    free(g_routes[fr->id].records);memset(&g_routes[fr->id],0,sizeof(EventRoute));
                    g_factory_page[fr->id]=0;
                }
                break;
            }
            if(!g_routes[fr->id].records) {
                start_event_route(m,fr->id,fr->records,fr->count,fr->flags);
                g_factory_page[fr->id]=fr->page+1;
            }
            break;
        }
    }
}

static void tick_player_route(const MapState *m)
{
    EventRoute *r=&g_player_route;int budget=128;
    if(!r->records)return;
    if(r->remaining>0) {
        float t=(float)(r->total-r->remaining+1)/r->total;
        g_route_real_x=(r->start_x+r->dx*t+0.5f)*TILE_PX;
        g_route_real_y=(r->start_y+r->dy*t+1.0f)*TILE_PX;
        --r->remaining;return;
    }
    while(r->records && budget-->0) {
        const uint8_t *p;int code,n,dx=0,dy=0;
        if(r->index>=r->count) {
            if((r->flags&1) && r->count){r->index=0;break;}
            free(r->records);memset(r,0,sizeof(*r));break;
        }
        p=r->records+r->index*5;code=p[0];n=(int16_t)read_u16_le(p+1);++r->index;
        if(code==29)g_player_move_speed_code=n<1?1:(n>6?6:n);
        else if(code>=16 && code<=19 && !g_player_direction_fix)*g_route_player_direction=code-16;
        else if(code==31)g_player_walk_anime=1;
        else if(code==32)g_player_walk_anime=0;
        else if(code==33)g_player_step_anime=1;
        else if(code==34)g_player_step_anime=0;
        else if(code==35)g_player_direction_fix=1;
        else if(code==36)g_player_direction_fix=0;
        else if(code==37)g_player_through=1;
        else if(code==38)g_player_through=0;
        else if(code==39)g_player_visible=0;
        else if(code==40)g_player_visible=1;
        else if(code==44)play_vm_se_params(n,90,100,0);
        else if(code==15 || (code>=1 && code<=4) || code==12 || code==13) {
            int nx,ny,bit,reverse;
            if (code != 15) player_route_delta(code, *g_route_player_direction, &dx, &dy);
            nx=*g_route_player_x+dx;ny=*g_route_player_y+dy;
            bit=dy>0?1:(dx<0?2:(dx>0?4:8));
            reverse=dy>0?8:(dx<0?4:(dx>0?2:1));
            if(code>=1 && code<=4 && !g_player_direction_fix)*g_route_player_direction=code-1;
            if(code!=15 && (nx<0 || ny<0 || nx>=m->w || ny>=m->h ||
               (!g_player_through &&
                (!(pass_mask_at(m,*g_route_player_x,*g_route_player_y)&bit) ||
                 !(pass_mask_at(m,nx,ny)&reverse) || vm_event_blocks_at(m,nx,ny))))) {
                if(!(r->flags&2))--r->index;
                break;
            }
            r->start_x=*g_route_player_x;r->start_y=*g_route_player_y;
            *g_route_player_x=nx;*g_route_player_y=ny;r->dx=dx;r->dy=dy;
            r->total=code==15?n:256/(1<<clamp_move_speed_code(g_player_move_speed_code));
            r->remaining=r->total;
            if(r->remaining>0) {
                float t=1.0f/r->total;
                g_route_real_x=(r->start_x+dx*t+0.5f)*TILE_PX;
                g_route_real_y=(r->start_y+dy*t+1.0f)*TILE_PX;
                --r->remaining;break;
            }
        }
    }
}

static int start_player_route(const uint8_t *records,int count,int flags,int *x,int *y,int *direction)
{
    EventRoute *r=&g_player_route;int i;
    for(i=0;i<count;++i)if(records[i*5]==14)return 0; /* jumping still uses the synchronous path */
    free(r->records);memset(r,0,sizeof(*r));
    if(count<=0)return 1;
    r->records=malloc(count*5);if(!r->records)return 0;
    memcpy(r->records,records,count*5);r->count=count;r->flags=flags;
    g_route_player_x=x;g_route_player_y=y;g_route_player_direction=direction;
    g_route_real_x=(*x+0.5f)*TILE_PX;g_route_real_y=(*y+1.0f)*TILE_PX;
    /* Speed/facing/flags-only routes take effect without locking input for
     * an extra frame on every floor tile. Timed/repeating routes stay queued. */
    if (!(flags & 1)) {
        int instant = 1;
        for (i = 0; i < count; ++i) {
            int code = records[i * 5];
            if (!((code >= 16 && code <= 19) || code == 29 ||
                  (code >= 31 && code <= 40) || code == 44)) {
                instant = 0; break;
            }
        }
        if (instant) tick_player_route(NULL);
    }
    return 1;
}

static float picture_ease(float t, int kind)
{
    if (kind == 1) return t*t;
    if (kind == 2) return 1.0f-(1.0f-t)*(1.0f-t);
    if (kind == 3) return t < 0.5f ? 2.0f*t*t : 1.0f-2.0f*(1.0f-t)*(1.0f-t);
    return t;
}

static void tick_pictures(void)
{
    int i;
    for (i=0; i<MAX_ACTIVE_PICTURES; ++i) {
        PictureSlot *p=&g_pictures[i];
        float t, v[5]; int j;
        if (!p->number || p->duration <= 0) continue;
        t=picture_ease((float)(p->total-p->duration+1)/p->total,p->easing);
        for(j=0;j<5;++j) v[j]=p->from[j]+(p->target[j]-p->from[j])*t;
        p->x=v[0];p->y=v[1];p->scale_x=v[2];p->scale_y=v[3];p->opacity=v[4];
        --p->duration;
    }
}

static void move_picture_start(PictureSlot *p,int origin,int x,int y,int zx,int zy,
                               int alpha,int blend,int duration,int easing)
{
    if (!p || !p->number) return;
    p->origin=origin;p->blend=blend;p->easing=easing;
    p->from[0]=p->x;p->from[1]=p->y;p->from[2]=p->scale_x;
    p->from[3]=p->scale_y;p->from[4]=p->opacity;
    p->target[0]=x;p->target[1]=y;p->target[2]=zx;p->target[3]=zy;p->target[4]=alpha;
    p->duration=p->total=duration;
    /* MZ duration=0 records a target without running updateMove. */
}

static void draw_vm_pictures(int below_a1)
{
    int i,j,order[MAX_ACTIVE_PICTURES];
    for(i=0;i<MAX_ACTIVE_PICTURES;++i)order[i]=i;
    for(i=1;i<MAX_ACTIVE_PICTURES;++i)for(j=i;j>0 &&
        g_pictures[order[j]].number<g_pictures[order[j-1]].number;--j) {
        int tmp=order[j];order[j]=order[j-1];order[j-1]=tmp;
    }
    for(i=0;i<MAX_ACTIVE_PICTURES;++i) {
        PictureSlot *p = &g_pictures[order[i]];
        float x,y,w,h;
        if(!p->number || !p->texture || p->opacity<1)continue;
        if ((p->number < 6) != below_a1) continue;
        w=(float)p->w * p->scale_x / 100.0f;
        h=(float)p->h * p->scale_y / 100.0f;
        {
            int fit_screen = p->fit_screen ||
                (p->resource_id >= 90 && p->resource_id <= 97) ||
                (!p->portrait && p->number == 11 && p->w == 408 && p->h == 312);
            if (p->resource_id >= 90 && p->resource_id <= 97) {
                w = SCREEN_W; h = SCREEN_H; x = 0; y = 0;
            } else if (fit_screen) {
                float sx = (float)SCREEN_W / w;
                float sy = (float)SCREEN_H / h;
                float scale = sx < sy ? sx : sy;
                w *= scale;
                h *= scale;
                x = ((float)SCREEN_W - w) * 0.5f;
                y = ((float)SCREEN_H - h) * 0.5f;
            } else {
            x=render_round_pixel(36.0f+(float)p->x*0.5f);
            y=render_round_pixel(-20.0f+(float)p->y*0.5f);
            if(p->origin==1){x-=w*0.5f;y-=h*0.5f;}
            /* Sprite_Picture.updatePosition() rounds the final picture
             * coordinate after origin handling. */
            x=render_round_pixel(x);
            y=render_round_pixel(y);
            }
        }
        sceGuTexMode(GU_PSM_4444,0,0,GU_FALSE);
        sceGuTexImage(0,512,512,512,p->texture);
        sceGuTexFunc(GU_TFX_MODULATE,GU_TCC_RGBA);
        {
            int fit_filter = p->portrait || p->fit_screen ||
                (p->resource_id >= 90 && p->resource_id <= 97) ||
                (!p->portrait && p->number == 11 && p->w == 408 && p->h == 312);
            sceGuTexFilter(fit_filter ? GU_LINEAR : GU_NEAREST,
                           fit_filter ? GU_LINEAR : GU_NEAREST);
        }
        if (p->blend == 1) sceGuBlendFunc(GU_ADD,GU_SRC_ALPHA,GU_FIX,0,0xFFFFFFFF);
        else if (p->blend == 2) sceGuBlendFunc(GU_ADD,GU_DST_COLOR,GU_ONE_MINUS_SRC_ALPHA,0,0);
        else if (p->blend == 3) sceGuBlendFunc(GU_ADD,GU_FIX,GU_ONE_MINUS_SRC_COLOR,0xFFFFFFFF,0);
        else sceGuBlendFunc(GU_ADD,GU_SRC_ALPHA,GU_ONE_MINUS_SRC_ALPHA,0,0);
        sceGuColor(((unsigned int)p->opacity<<24)|0x00FFFFFFu);
        if(p->portrait) {
            float zx=p->scale_x/100.0f,zy=p->scale_y/100.0f;
            draw_bound_rect(1,1,p->source_w,p->source_h,
                x+p->picture_offset_x*zx,y+p->picture_offset_y*zy,
                p->picture_region_w*zx,p->picture_region_h*zy);
        } else draw_bound_rect(0,0,(float)p->w,(float)p->h,x,y,w,h);
        sceGuBlendFunc(GU_ADD,GU_SRC_ALPHA,GU_ONE_MINUS_SRC_ALPHA,0,0);
        sceGuColor(0xFFFFFFFF);
        sceGuTexFunc(GU_TFX_REPLACE,GU_TCC_RGBA);
    }
}


static int lucas_fall_frame_from_switches(void)
{
    /* RPG Maker selects the last valid event page.  Event 45 uses switches
     * 45..49 for the five visible frames; switch 50 makes it blank again. */
    if (g_switches[50]) return -1;
    if (g_switches[49]) return 4;
    if (g_switches[48]) return 3;
    if (g_switches[47]) return 2;
    if (g_switches[46]) return 1;
    if (g_switches[45]) return 0;
    return -1;
}

static void draw_lucas_fall_event(
    const MapState *m,
    float camera_x, float camera_y, float origin_x, float origin_y)
{
    int slot;
    float foot_x, foot_y;
    TextureVertex *v;
    float src_x;

    if (!m || m->id != 1 || !g_lucas_fall_atlas) return;
    slot = lucas_fall_frame_from_switches();
    if (slot < 0) return;

    foot_x = render_floor_pixel(
        origin_x +
        ((float)LUCAS_FALL_EVENT_X + g_event_shift_x[45] + 0.5f) * TILE_PX - camera_x
    );
    foot_y = render_floor_pixel(
        origin_y +
        ((float)LUCAS_FALL_EVENT_Y + g_event_shift_y[45] + 1.0f) * TILE_PX - camera_y
    );

    bind_texture_8888(g_lucas_fall_atlas, LUCAS_FALL_ATLAS_W, LUCAS_FALL_ATLAS_H);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    src_x = (float)(slot * LUCAS_FALL_SLOT_W + 1);
    v = (TextureVertex *)sceGuGetMemory(2 * sizeof(TextureVertex));
    v[0].u = src_x;
    v[0].v = 1.0f;
    v[0].x = foot_x - (float)LUCAS_FALL_SRC_W * 0.5f;
    v[0].y = foot_y - (float)LUCAS_FALL_SRC_H;
    v[0].z = 0.0f;
    v[1].u = src_x + (float)LUCAS_FALL_SRC_W;
    v[1].v = 1.0f + (float)LUCAS_FALL_SRC_H;
    v[1].x = foot_x + (float)LUCAS_FALL_SRC_W * 0.5f;
    v[1].y = foot_y;
    v[1].z = 0.0f;
    sceGuDrawArray(
        GU_SPRITES,
        GU_TEXTURE_32BITF | GU_VERTEX_32BITF | GU_TRANSFORM_2D,
        2, NULL, v
    );
}

static void draw_lucas_corpse_event(
    const MapState *m,
    float camera_x, float camera_y, float origin_x, float origin_y)
{
    float foot_x, foot_y;
    TextureVertex *v;
    if (!m || m->id != 1 || !g_lucas_corpse) return;
    /* Event 39 becomes the fallen Lucas body when switch 51 is ON and stays
     * as the same corpse on page 3 while switch 52 is ON. */
    if (!g_switches[51] && !g_switches[52]) return;

    foot_x = render_floor_pixel(
        origin_x + ((float)LUCAS_CORPSE_EVENT_X + 0.5f) * TILE_PX - camera_x
    );
    foot_y = render_floor_pixel(
        origin_y + ((float)LUCAS_CORPSE_EVENT_Y + 1.0f) * TILE_PX - camera_y
    );

    bind_texture_8888(g_lucas_corpse, LUCAS_CORPSE_TEX_W, LUCAS_CORPSE_TEX_H);
    v = (TextureVertex *)sceGuGetMemory(2 * sizeof(TextureVertex));
    v[0].u = 1.0f; v[0].v = 1.0f;
    v[0].x = foot_x - (float)LUCAS_CORPSE_SRC_W * 0.5f;
    v[0].y = foot_y - (float)LUCAS_CORPSE_SRC_H;
    v[0].z = 0.0f;
    v[1].u = 1.0f + (float)LUCAS_CORPSE_SRC_W;
    v[1].v = 1.0f + (float)LUCAS_CORPSE_SRC_H;
    v[1].x = foot_x + (float)LUCAS_CORPSE_SRC_W * 0.5f;
    v[1].y = foot_y;
    v[1].z = 0.0f;
    sceGuDrawArray(GU_SPRITES, GU_TEXTURE_32BITF | GU_VERTEX_32BITF | GU_TRANSFORM_2D,
                   2, NULL, v);
}


static void repair_map005_key_state(const MapState *m)
{
    if (!m || m->id != 5) return;

    /* 0.7.4: one-time legacy-save repair.  Builds where the Map005 key was
     * invisible could still let Event 7 run, leaving switch 144 + item 52 set
     * even though the player never saw the pickup.  For users upgrading from
     * those builds, restore the original pre-pickup state once while the
     * Processing Plant shutter has not yet opened.  The key then becomes both
     * visible and normally actionable again. */
    if (!g_map5_key_migration_done) {
        if (!g_switches[16]) {
            g_switches[144] = 0;
            g_items[52] = 0;
        }
        g_map5_key_migration_done = 1;
        save_config();
    }

    /* Also repair the narrower inconsistent state for any future save: a
     * pickup switch without the actual Red Key item cannot be valid before
     * the Processing Plant door has opened. */
    if (!g_switches[16] && g_switches[144] && g_items[52] <= 0)
        g_switches[144] = 0;
}

static void vm_begin_screen_flash(int r, int g, int b, int a, int frames);

/* Map026 parallel event3 and sensor event4's autonomous turn route.
 * MZ frequency5 waits until stopCount > 0; route-end consumes one extra
 * update without resetting stopCount before the next downward turn. */
static void tick_laser_room(const MapState *m)
{
    if (!m || m->id != 26 || g_switches[137]) {
        g_laser_room_frame = g_laser_stop_count = g_laser_route_index = 0;
        return;
    }
    if (++g_laser_room_frame >= 500) {
        play_vm_se_params(1031,50,80,0);
        g_switches[134] = g_switches[135] = g_switches[136] = g_switches[137] = 1;
        g_event_direction[4] = 0;
        return;
    }
    if (!g_routes[4].records && ++g_laser_stop_count > 0) {
        if (g_laser_route_index < 4) {
            g_event_direction[4] = g_laser_route_index++;
            g_laser_stop_count = 0;
        } else g_laser_route_index = 0;
    }
}

static void tick_pressing_room(const MapState *m)
{
    int phase = pressing_room_tick(&g_pressing_room_frame,
                                   m && m->id == 24 && !g_switches[191]);
    if (phase == 1) { g_switches[184] = 0; g_switches[183] = 1; }
    else if (phase == 2) {
        vm_begin_screen_flash(255,0,0,255,5);
        g_switches[183] = 0; g_switches[184] = 1;
        play_vm_se_params(1133,90,100,0);
    } else if (phase == 3) { g_switches[184] = 0; g_switches[183] = 0; }
}

/* Map032 parallel pages 19/20. Their waits and routes run while the
 * player keeps moving; running them through the blocking scene VM loses input. */
static void tick_factory_parallel(const MapState *m)
{
    if(m->id!=32)return;
    if(g_switches[237]) {
        int f=++g_factory_machine_frame;
        if(f==300)play_vm_se_params(1059,90,50,0);
        if(f>=300 && f<=420) {
            int phase=((f-300)/10)&1;
            g_switches[233]=g_switches[235]=!phase;
            g_switches[234]=g_switches[236]=phase;
        }
        if(f>=430) {
            g_switches[233]=g_switches[234]=g_switches[235]=g_switches[236]=0;
            g_switches[237]=0;play_vm_se_params(1077,90,100,0);
            /* Original Set Event Location: event 19 returns to (14,16). */
            free(g_routes[19].records);memset(&g_routes[19],0,sizeof(EventRoute));
            g_event_shift_x[19]=g_event_shift_y[19]=0;
            g_switches[257]=0;g_factory_machine_frame=0;g_factory_corpse_phase=0;
        }
    } else g_factory_machine_frame=0;
    if(g_switches[256] && !g_factory_corpse_phase) {
        static const uint8_t down[]={37,0,0,0,0,1,0,0,0,0,1,0,0,0,0,38,0,0,0,0};
        start_event_route(m,19,down,4,0);g_factory_corpse_phase=1;
    }
    if(g_factory_corpse_phase==1 && !g_routes[19].records) {
        play_vm_se_params(1134,90,70,0);vm_begin_screen_flash(255,0,0,255,10);
        g_switches[256]=0;g_switches[258]=1;g_factory_corpse_phase=2;
    }
    if(g_switches[258] && g_factory_corpse_phase!=3) {
        static const uint8_t left[]={29,3,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,2,0,0,0,0};
        start_event_route(m,19,left,11,0);g_factory_corpse_phase=3;
    }
    if(g_factory_corpse_phase==3 && !g_routes[19].records) {
        g_switches[258]=0;g_factory_corpse_phase=0;
    }
}

static void render_world(
    const MapState *m, void *char_atlas,
    void *a1_overlay, void *fall_atlas,
    int player_visible,
    float player_world_x, float player_world_y,
    int player_pattern, int player_direction,
    int fall_slot, float fall_y_tiles,
    void *portrait, void *dialog,
    int flash_red_alpha, int black_alpha, int show_blank_box)
{
    float camera_x, camera_y, origin_x, origin_y;
    float player_screen_x, player_screen_y;

    /* Snapshot movement before route ticking so its final interpolation frame
     * keeps the walking phase even when remaining becomes zero. */
    int subpixel_jump = g_player_animation_jumping;
    int had_player_route = g_player_route.records != NULL;
    int route_moving = had_player_route && g_player_route.remaining > 0 &&
        (g_player_route.dx || g_player_route.dy);
    tick_player_route(m);
    if(had_player_route) {
        player_world_x=g_route_real_x;player_world_y=g_route_real_y;
        player_direction=*g_route_player_direction;
        player_visible=g_player_visible;
        route_moving |= g_player_route.remaining > 0 &&
            (g_player_route.dx || g_player_route.dy);
        g_player_animation_speed = clamp_move_speed_code(g_player_move_speed_code);
    }
    {
        int route_arrival = route_moving && g_player_route.remaining == 0;
        player_pattern = player_animation_tick(&g_player_animation,
        g_player_animation_moving || (route_moving && !route_arrival),
        g_player_animation_jumping || route_arrival,
        g_player_animation_speed, g_player_walk_anime, g_player_step_anime);
    }
    g_player_animation_moving = g_player_animation_jumping = 0;
    repair_map005_key_state(m);

    tick_map_scroll();
    compute_camera(
        m, player_world_x, player_world_y,
        &camera_x, &camera_y, &origin_x, &origin_y
    );
    /* MZ Tilemap.updateTransform() ceils the pixel origin before placing the
     * lower/upper tile layers.  Reproduce that rasterisation on the native
     * 480x272 PSP framebuffer instead of feeding fractional coordinates to
     * nearest-filtered map tiles. */
    /* Keep the actor anchored to the continuous camera; only tiles use the
     * integer camera origin. Otherwise following produces a one-pixel sawtooth. */
    float actor_camera_x = camera_x;
    float actor_camera_y = camera_y;
    g_actor_camera_x = actor_camera_x;
    g_actor_camera_y = actor_camera_y;
    camera_x = render_ceil_pixel(camera_x);
    camera_y = render_ceil_pixel(camera_y);
    origin_x = render_round_pixel(origin_x);
    origin_y = render_round_pixel(origin_y);
    /* Spriteset_Base.updatePosition(): Math.round(screen.shake()). */
    origin_x += render_round_pixel(g_screen_shake_x);

    player_screen_x = origin_x + player_world_x - actor_camera_x;
    player_screen_y = origin_y + player_world_y - actor_camera_y;
    if (m->id == 1 && !subpixel_jump) {
        player_screen_x = render_floor_pixel(player_screen_x);
        player_screen_y = render_floor_pixel(player_screen_y);
    }

    tick_pictures();
    tick_pressing_room(m);
    tick_laser_room(m);
    tick_s003_autonomous(m,player_world_x,player_world_y);
    tick_factory_autonomous(m);
    tick_event_routes(m);
    tick_factory_parallel(m);
    vm_tick_world_tint();
    sceGuStart(GU_DIRECT, gu_list);
    sceGuClearColor(0xFF000000);
    sceGuClear(GU_COLOR_BUFFER_BIT);

    /* GU state survives the previous frame.  Start every world frame from a
     * canonical nearest/clamped state so a dialogue transition cannot expose
     * one LINEAR-filtered world frame. */
    set_pixel_art_texture_state();
    draw_map_pass(m, 0, camera_x, camera_y, origin_x, origin_y);

    draw_event_sprites(
        m, 0, 0, player_world_y,
        camera_x, camera_y, origin_x, origin_y
    );

    if (fall_slot >= 0 && fall_atlas && m->id == 1) {
        float fall_foot_x = origin_x + ((float)FALL_EVENT_X + 0.5f) * TILE_PX - camera_x;
        float fall_foot_y = origin_y + ((fall_y_tiles + 1.0f) * TILE_PX) - camera_y;
        bind_texture_8888(fall_atlas, FALL_ATLAS_W, FALL_ATLAS_H);
        set_pixel_art_texture_state();
        draw_fall_frame(fall_slot, fall_foot_x, fall_foot_y);
    }

    draw_event_sprites(
        m, 1, -1, player_world_y,
        camera_x, camera_y, origin_x, origin_y
    );
    draw_story_key_foreground(m, actor_camera_x, actor_camera_y, origin_x, origin_y,
                              -1, player_world_y);

    if (player_visible) {
        bind_texture_8888(char_atlas, CHAR_ATLAS_W, CHAR_ATLAS_H);
        set_pixel_art_texture_state();
        sceGuTexFilter(GU_LINEAR, GU_LINEAR);
        draw_character_frame(
            player_pattern, player_direction,
            player_screen_x, player_screen_y
        );
        set_pixel_art_texture_state();
    }

    draw_event_sprites(
        m, 1, 1, player_world_y,
        camera_x, camera_y, origin_x, origin_y
    );
    draw_story_key_foreground(m, actor_camera_x, actor_camera_y, origin_x, origin_y,
                              1, player_world_y);

    draw_map_pass(m, 1, camera_x, camera_y, origin_x, origin_y);

    draw_event_sprites(
        m, 2, 0, player_world_y,
        camera_x, camera_y, origin_x, origin_y
    );

    /* 0.5.x atlases omitted switch-driven Lucas pages; keep the old fallback
     * only for legacy assets.  0.6.4 renders them through active VM pages. */
    if (!(m->vm_flags & 0x01u)) {
        draw_lucas_fall_event(m, camera_x, camera_y, origin_x, origin_y);
        draw_lucas_corpse_event(m, camera_x, camera_y, origin_x, origin_y);
    }

    /* Gray is MZ/Pixi ColorFilter saturation (HSL lightness), before RGB tone.
     * Only gray needs readback. Split and sync the GU list before accessing VRAM;
     * the uncached alias prevents stale CPU cache lines after GE writes. */
    if (g_world_tone_gray > 0) {
        int x,y,gray=g_world_tone_gray > 255 ? 255 : g_world_tone_gray;
        volatile uint32_t *fb=(volatile uint32_t *)(0x44000000u | (uintptr_t)g_draw_buffer);
        sceGuFinish();sceGuSync(0,0);
        for(y=0;y<SCREEN_H;++y) for(x=0;x<SCREEN_W;++x) {
            uint32_t c=fb[y*BUF_W+x];
            int r=c&255,g=(c>>8)&255,b=(c>>16)&255;
            int hi=r>g?r:g,lo=r<g?r:g;
            int l;
            if (b > hi) hi = b;
            if (b < lo) lo = b;
            l = (hi + lo + 1) / 2;
            r=(r*(255-gray)+l*gray+127)/255;
            g=(g*(255-gray)+l*gray+127)/255;
            b=(b*(255-gray)+l*gray+127)/255;
            fb[y*BUF_W+x]=(c&0xFF000000u)|r|(g<<8)|(b<<16);
        }
        sceGuStart(GU_DIRECT,gu_list);
        sceGuTexFlush();
    }
    {
        int r=g_world_tone_r,g=g_world_tone_g,b=g_world_tone_b;
        /* Fixed-factor additive/subtractive passes preserve per-channel tone. */
        sceGuBlendFunc(GU_ADD,GU_FIX,GU_FIX,0xFFFFFFFF,0xFFFFFFFF);
        draw_solid_rect(0,0,SCREEN_W,SCREEN_H,r>0?r:0,g>0?g:0,b>0?b:0,255);
        sceGuBlendFunc(GU_REVERSE_SUBTRACT,GU_FIX,GU_FIX,0xFFFFFFFF,0xFFFFFFFF);
        draw_solid_rect(0,0,SCREEN_W,SCREEN_H,r<0?-r:0,g<0?-g:0,b<0?-b:0,255);
        sceGuBlendFunc(GU_ADD,GU_SRC_ALPHA,GU_ONE_MINUS_SRC_ALPHA,0,0);
    }

    draw_vm_pictures(1);
    {
        int veil_active = (a1_overlay != NULL) || g_picture6_visible || g_switches[20];

        /* Save files produced by several 0.6.x builds could lose switch 20 and
         * Picture #6 independently during transfers.  In the original game the
         * first Processing Plant arc keeps A1 + Fog continuously from Map001
         * through Map009; Map010 is the first place that explicitly switches
         * 20 OFF and erases pictures 6/7.  Repair that early legacy state on
         * sight instead of letting the veil randomly disappear by map. */
        if (!veil_active && m && m->id >= 2 && m->id <= 9) {
            veil_active = 1;
            g_switches[20] = 1;
            g_picture6_visible = 1;
            g_picture6_alpha = 255;
        }

        if (!a1_overlay && veil_active)
            a1_overlay = g_a1_overlay;

        if (a1_overlay) {
            int a1_alpha = 255;
            if (a1_overlay == g_a1_overlay && g_picture6_visible)
                a1_alpha = g_picture6_alpha;
            if (a1_alpha > 0) {
                draw_texture_alpha(
                    a1_overlay, PIC_TEX_W, PIC_TEX_H,
                    (float)SCREEN_W, (float)SCREEN_H,
                    0.0f, 0.0f, (float)SCREEN_W, (float)SCREEN_H, a1_alpha
                );
            }
        }

        /* Picture #7 in the original: animated black fog/vignette above A1. */
        draw_fog_a1_overlay(veil_active);
    }

    draw_vm_pictures(0);

    if (portrait) {
        draw_texture_alpha(
            portrait, PIC_TEX_W, PIC_TEX_H,
            (float)SCREEN_W, (float)SCREEN_H,
            0.0f, 0.0f, (float)SCREEN_W, (float)SCREEN_H, 255
        );
    }

    if (show_blank_box) {
        draw_solid_rect(
            6.0f, (float)(SCREEN_H - DIALOG_VISIBLE_H + 4),
            (float)(SCREEN_W - 12), (float)(DIALOG_VISIBLE_H - 8),
            10, 10, 14, 220
        );
    }

    if (dialog) {
        draw_texture_alpha(
            dialog, DIALOG_TEX_W, DIALOG_TEX_H,
            (float)SCREEN_W, (float)DIALOG_VISIBLE_H,
            0.0f, (float)(SCREEN_H - DIALOG_VISIBLE_H),
            (float)SCREEN_W, (float)DIALOG_VISIBLE_H, 255
        );
    }

    draw_runtime_message_overlay();
    draw_runtime_choice_overlay();
    draw_runtime_number_overlay();

    if (flash_red_alpha > 0) {
        draw_solid_rect(
            0.0f, 0.0f, (float)SCREEN_W, (float)SCREEN_H,
            255, 0, 0, flash_red_alpha
        );
    }

    if (g_screen_flash_remaining > 0 && g_screen_flash_total > 0 &&
        g_screen_flash_a > 0) {
        int fa = g_screen_flash_a * g_screen_flash_remaining / g_screen_flash_total;
        if (fa > 0)
            draw_solid_rect(
                0.0f, 0.0f, (float)SCREEN_W, (float)SCREEN_H,
                g_screen_flash_r, g_screen_flash_g, g_screen_flash_b, fa
            );
    }

    if (g_script_fade_alpha>black_alpha) black_alpha=g_script_fade_alpha;
    if (black_alpha > 0) {
        draw_solid_rect(
            0.0f, 0.0f, (float)SCREEN_W, (float)SCREEN_H,
            g_transfer_white?255:0,g_transfer_white?255:0,g_transfer_white?255:0,black_alpha
        );
    }

    sceGuFinish();
    sceGuSync(0, 0);
    sceDisplayWaitVblankStart();
    g_last_world_buffer = g_draw_buffer;
    g_last_world_buffer_valid = 1;
    g_draw_buffer = sceGuSwapBuffers();
    ++g_world_render_frames;
    ++g_playtime_frames;
    if (g_screen_flash_remaining > 0) {
        --g_screen_flash_remaining;
        if (g_screen_flash_remaining <= 0) {
            g_screen_flash_remaining = 0;
            g_screen_flash_total = 0;
        }
    }
}


/* ------------------------------------------------------------------------- */
/* v0.4.0 synchronous event VM                                               */
/* ------------------------------------------------------------------------- */

static void vm_begin_screen_flash(int r, int g, int b, int a, int frames)
{
    if (r < 0) r = 0;
    if (r > 255) r = 255;
    if (g < 0) g = 0;
    if (g > 255) g = 255;
    if (b < 0) b = 0;
    if (b > 255) b = 255;
    if (a < 0) a = 0;
    if (a > 255) a = 255;
    if (frames < 0) frames = 0;
    g_screen_flash_r = r;
    g_screen_flash_g = g;
    g_screen_flash_b = b;
    g_screen_flash_a = a;
    g_screen_flash_total = frames;
    g_screen_flash_remaining = frames;
}

static void vm_begin_world_tint(int r, int g, int b, int gray, int frames)
{
    if (r < -255) r = -255;
    if (r > 255) r = 255;
    if (g < -255) g = -255;
    if (g > 255) g = 255;
    if (b < -255) b = -255;
    if (b > 255) b = 255;
    if (gray < 0) gray = 0;
    if (gray > 255) gray = 255;
    if (frames <= 0) {
        g_world_tone_r = r;
        g_world_tone_g = g;
        g_world_tone_b = b;
        g_world_tone_gray = gray;
        g_world_tone_from_r = r;
        g_world_tone_from_g = g;
        g_world_tone_from_b = b;
        g_world_tone_from_gray = gray;
        g_world_tone_target_r = r;
        g_world_tone_target_g = g;
        g_world_tone_target_b = b;
        g_world_tone_target_gray = gray;
        g_world_tone_total = 0;
        g_world_tone_remaining = 0;
        return;
    }
    g_world_tone_from_r = g_world_tone_r;
    g_world_tone_from_g = g_world_tone_g;
    g_world_tone_from_b = g_world_tone_b;
    g_world_tone_from_gray = g_world_tone_gray;
    g_world_tone_target_r = r;
    g_world_tone_target_g = g;
    g_world_tone_target_b = b;
    g_world_tone_target_gray = gray;
    g_world_tone_total = frames;
    g_world_tone_remaining = frames;
}

static void vm_tick_world_tint(void)
{
    int done;
    if (g_world_tone_remaining <= 0 || g_world_tone_total <= 0) return;
    done = g_world_tone_total - g_world_tone_remaining + 1;
    g_world_tone_r = g_world_tone_from_r +
        (g_world_tone_target_r - g_world_tone_from_r) * done / g_world_tone_total;
    g_world_tone_g = g_world_tone_from_g +
        (g_world_tone_target_g - g_world_tone_from_g) * done / g_world_tone_total;
    g_world_tone_b = g_world_tone_from_b +
        (g_world_tone_target_b - g_world_tone_from_b) * done / g_world_tone_total;
    g_world_tone_gray = g_world_tone_from_gray +
        (g_world_tone_target_gray - g_world_tone_from_gray) * done / g_world_tone_total;
    g_world_tone_remaining--;
    if (g_world_tone_remaining <= 0) {
        g_world_tone_r = g_world_tone_target_r;
        g_world_tone_g = g_world_tone_target_g;
        g_world_tone_b = g_world_tone_target_b;
        g_world_tone_gray = g_world_tone_target_gray;
        g_world_tone_total = 0;
    }
}

static int vm_text_has_visible_content(const char *text, size_t len)
{
    size_t i = 0;
    if (!text || len == 0) return 0;
    while (i < len) {
        unsigned char c = (unsigned char)text[i];
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            ++i;
            continue;
        }
        /* U+3000 IDEOGRAPHIC SPACE, used by Japanese blank input gates. */
        if (i + 2 < len &&
            (unsigned char)text[i] == 0xE3 &&
            (unsigned char)text[i + 1] == 0x80 &&
            (unsigned char)text[i + 2] == 0x80) {
            i += 3;
            continue;
        }
        return 1;
    }
    return 0;
}

static void vm_render_frame(
    const MapState *m, void *char_atlas,
    int tile_x, int tile_y, int direction_row,
    int black_alpha, int red_alpha)
{
    float wx = ((float)tile_x + 0.5f) * TILE_PX;
    float wy = ((float)tile_y + 1.0f) * TILE_PX;
    g_player_animation_speed = clamp_move_speed_code(g_player_move_speed_code);
    render_world(
        m, char_atlas, NULL, NULL,
        g_player_visible, wx, wy, 1, direction_row,
        -1, 0.0f, NULL, NULL, red_alpha, black_alpha, 0
    );
}

static void vm_wait_frames(
    int frames, const MapState *m, void *char_atlas,
    int tile_x, int tile_y, int direction_row)
{
    int i;
    for (i = 0; i < frames; ++i)
        vm_render_frame(m, char_atlas, tile_x, tile_y, direction_row, 0, 0);
}

/* Dialogue-only English styling; preserve surrounding color escapes. */
static char *style_green_key_dialogue(const char *text, size_t len, size_t *out_len)
{
    const char *p = text, *end = text + len;
    char *out = malloc(len * 3 + 1), *dst = out;
    int color = 0;
    if (!out) return NULL;
    while (p < end) {
        const char *before = p;
        if (parse_text_color_escape(&p, end, &color)) {
            memcpy(dst, before, p - before); dst += p - before;
            continue;
        }
        {
            static const char *names[] = {"Green key", "Iron key", "Red key", "Gold key", "Cleaver"};
            static const int colors[] = {3, -1, 18, 14, -1};
            int k, matched = 0;
            for (k = 0; k < 5; ++k) {
                size_t n = strlen(names[k]), j;
                if ((size_t)(end-p) < n ||
                    (p != text && latin_word_cp((unsigned char)p[-1])) ||
                    ((size_t)(end-p) > n && latin_word_cp((unsigned char)p[n]))) continue;
                for (j = 0; j < n; ++j) {
                    unsigned char c = p[j], expected = names[k][j];
                    if (c >= 'A' && c <= 'Z') c += 'a'-'A';
                    if (expected >= 'A' && expected <= 'Z') expected += 'a'-'A';
                    if (c != expected) break;
                }
                if (j != n) continue;
                if (colors[k] >= 0) dst += sprintf(dst, "\\c[%d]", colors[k]);
                memcpy(dst, p, n);
                dst += n;
                if (colors[k] >= 0) dst += sprintf(dst, "\\c[%d]", color);
                p += n; matched = 1; break;
            }
            if (matched) continue;
        }
        *dst++ = *p;
        ++p;
    }
    *dst = 0; *out_len = (size_t)(dst - out);
    return out;
}

static void vm_wait_text_page(
    const MapState *m, void *char_atlas,
    int tile_x, int tile_y, int direction_row,
    const char *speaker, size_t speaker_len,
    const char *message, size_t message_len, int continue_message)
{
    SceCtrlData pad;
    uint32_t prev;
    char *styled = NULL;
    int auto_advance = 0, auto_frames = 0;
    /* A trailing RPG Maker control suppresses the input pause. Never print it. */
    if (message) {
        size_t visible_len = message_len;
        while (visible_len && (message[visible_len-1]=='\n' ||
               message[visible_len-1]=='\r' || message[visible_len-1]==' ')) --visible_len;
        if (visible_len >= 2 && message[visible_len-2]=='\\' && message[visible_len-1]=='^') {
            auto_advance = 1;
            message_len = visible_len-2;
        }
    }

    /* This shutter notification fits two native PSP rows. Ignore the PC
     * source wraps (including a trailing newline) before choosing its layout. */
    if (g_language == 0 && message && message_len < 128) {
        char flat[128]; size_t i, n=0; int space=0;
        for (i=0;i<message_len;++i) {
            char c=message[i];
            if (c==' ' || c=='\n' || c=='\r' || c=='\t') {space=n>0;continue;}
            if (space) flat[n++]=' ';
            space=0;flat[n++]=c;
        }
        flat[n]=0;
        if (!strcmp(flat,"It seems two keys are required to open the shutter.")) {
            message="It seems two keys are required\nto open the shutter.";
            message_len=strlen(message);
        }
    }
    if (g_language == 0 && message &&
        ((message_len == 16 && !memcmp(message,"Obtained an Axe.",16)) ||
         (message_len == 17 && !memcmp(message,"Obtained an Axe.\n",17)))) {
        message = "Obtained an \\c[8]Axe\\c[0].";
        message_len = strlen(message);
    }

    /* Map020 gold door: remove the PC-specific wrap and repair the missing
     * sentence space. Both sentences fit at the existing PSP font size. */
    if (g_language == 0 && message &&
        (message_len == sizeof("An old door made from gold plate. It won't \nopen.It's locked.") - 1 ||
         (message_len == sizeof("An old door made from gold plate. It won't \nopen.It's locked.") && message[message_len - 1] == '\n')) &&
        !memcmp(message, "An old door made from gold plate. It won't \nopen.It's locked.",
                sizeof("An old door made from gold plate. It won't \nopen.It's locked.") - 1)) {
        message = "An old door made from gold plate.\nIt won't open. It's locked.";
        message_len = strlen(message);
    }
    if (g_language == 0 && message && message_len) {
        styled = style_green_key_dialogue(message, message_len, &message_len);
        if (styled) message = styled;
    }

    g_runtime_speaker = speaker;
    g_runtime_speaker_len = speaker_len;
    g_runtime_message = message;
    g_runtime_message_len = message_len;

    /* NARAKU uses empty, transparent Show Text commands as an input gate
     * while a full-screen picture is visible (e.g. equations / controls).
     * Drawing our normal dialogue box for those commands was incorrect and
     * also made the controls board look like a modal menu. */
    g_runtime_message_active =
        (vm_text_has_visible_content(speaker, speaker_len) ||
         vm_text_has_visible_content(message, message_len)) ? 1 : 0;
    if (g_runtime_message_active)
        rebuild_runtime_message_surface();
    else
        g_runtime_message_surface_ready = 0;

    if (g_runtime_message_active) {
        while (g_runtime_message_openness < 255) {
            g_runtime_message_openness += 32;
            if (g_runtime_message_openness > 255) g_runtime_message_openness = 255;
            vm_render_frame(m, char_atlas, tile_x, tile_y, direction_row, 0, 0);
        }
    } else g_runtime_message_openness = 0;

    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;
    while (1) {
        /* Empty Show Text is only an invisible input gate in NARAKU.
         * Force the overlay off every frame so a stale previous text box
         * can never leak under full-screen pictures such as A2. */
        if (!vm_text_has_visible_content(speaker, speaker_len) &&
            !vm_text_has_visible_content(message, message_len))
            g_runtime_message_active = 0;
        vm_render_frame(m, char_atlas, tile_x, tile_y, direction_row, 0, 0);
        sceCtrlPeekBufferPositive(&pad, 1);
        if (auto_advance && ++auto_frames >= 30) break;
        if ((pad.Buttons & ~prev) & (PSP_CTRL_CROSS | PSP_CTRL_CIRCLE)) break;
        prev = pad.Buttons;
    }

    if (g_runtime_message_active && !continue_message) {
        while (g_runtime_message_openness > 0) {
            g_runtime_message_openness -= 32;
            if (g_runtime_message_openness < 0) g_runtime_message_openness = 0;
            vm_render_frame(m, char_atlas, tile_x, tile_y, direction_row, 0, 0);
        }
    }
    g_runtime_message_active = 0;
    g_runtime_speaker = NULL;
    g_runtime_message = NULL;
    g_runtime_speaker_len = 0;
    g_runtime_message_len = 0;
    g_runtime_message_surface_ready = 0;
    free(styled);
}

/* Reflow the PC-authored flashback prose at native PSP size. Explicit source
 * line breaks are layout hints here; paginate rather than drop a fourth row. */
static void vm_wait_text(
    const MapState *m, void *char_atlas,
    int tile_x, int tile_y, int direction_row,
    const char *speaker, size_t speaker_len,
    const char *message, size_t message_len, int continue_message)
{
    const char *p = message, *end = message + message_len;
    char *page, *dst;
    int width = 0, line = 0;
    const uint8_t *space_rec;
    int space_width;
    if (g_language != 0 || !message_len) {
        vm_wait_text_page(m,char_atlas,tile_x,tile_y,direction_row,
                          speaker,speaker_len,message,message_len,continue_message);
        return;
    }
    page = malloc(message_len * 2 + 4);
    if (!page) {
        vm_wait_text_page(m,char_atlas,tile_x,tile_y,direction_row,
                          speaker,speaker_len,message,message_len,continue_message);
        return;
    }
    space_rec = font_find_glyph(' ');
    space_width = space_rec ? (int)(space_rec[7] * 0.55f) : 5;
    dst = page;
    while (p < end) {
        const char *word, *q;
        int word_width = 0;
        while (p < end && (*p == ' ' || *p == '\n' || *p == '\r' || *p == '\t')) ++p;
        if (p == end) break;
        word = p;
        while (p < end && *p != ' ' && *p != '\n' && *p != '\r' && *p != '\t') ++p;
        q = word;
        while (q < p) {
            const uint8_t *rec;
            /* Colour and auto-close controls have no visible advance. */
            if (p-q >= 2 && q[0] == '\\' && q[1] == '^') { q += 2; continue; }
            if (p-q >= 5 && q[0] == '\\' && (q[1]=='c'||q[1]=='C') && q[2]=='[') {
                const char *control=q+3;
                while(control<p && *control>='0' && *control<='9') ++control;
                if(control<p && *control==']') {q=control+1;continue;}
            }
            rec = font_find_glyph(utf8_next_cp(&q,p));
            if (!rec) rec = font_find_glyph('?');
            word_width += rec ? (int)(rec[7] * 0.55f) : 5;
        }
        if (width && width + space_width + word_width > MESSAGE_BOX_W - 18) {
            width = 0;
            if (++line == 3) {
                vm_wait_text_page(m,char_atlas,tile_x,tile_y,direction_row,
                                  speaker,speaker_len,page,(size_t)(dst-page),1);
                dst = page; line = 0;
            } else *dst++ = '\n';
        }
        if (width) { *dst++ = ' '; width += space_width; }
        memcpy(dst,word,(size_t)(p-word)); dst += p-word;
        width += word_width;
    }
    vm_wait_text_page(m,char_atlas,tile_x,tile_y,direction_row,
                      speaker,speaker_len,page,(size_t)(dst-page),continue_message);
    free(page);
}

static int vm_wait_choices(
    const MapState *m, void *char_atlas,
    int tile_x, int tile_y, int direction_row,
    int count, int default_index, int cancel_index)
{
    SceCtrlData pad;
    uint32_t prev;
    if (count < 1 || count > 6) return -1;
    g_choice_active = 1;
    g_choice_count = count;
    rebuild_choice_text_surface();
    g_choice_cursor = (default_index >= 0 && default_index < count) ? default_index : 0;
    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;
    while (1) {
        uint32_t pressed;
        vm_render_frame(m, char_atlas, tile_x, tile_y, direction_row, 0, 0);
        sceCtrlPeekBufferPositive(&pad, 1);
        pressed = pad.Buttons & ~prev;
        prev = pad.Buttons;
        if (pressed & PSP_CTRL_UP) {
            g_choice_cursor = (g_choice_cursor + count - 1) % count;
            play_se_async(SE_UI_CURSOR_PATH);
        }
        if (pressed & PSP_CTRL_DOWN) {
            g_choice_cursor = (g_choice_cursor + 1) % count;
            play_se_async(SE_UI_CURSOR_PATH);
        }
        if (pressed & ui_ok_mask()) {
            play_se_async(SE_UI_OK_PATH);
            break;
        }
        if (pressed & ui_cancel_mask()) {
            if (cancel_index >= 0 && cancel_index < count) {
                g_choice_cursor = cancel_index;
                play_se_async(SE_UI_CANCEL_PATH);
                break;
            } else {
                play_se_async(SE_UI_BUZZER_PATH);
            }
        }
    }
    g_choice_active = 0;
    return g_choice_cursor;
}

static int number_input_change_digit(int value,int digits,int cursor,int change)
{
    int place=1,i,digit;
    for(i=cursor+1;i<digits;++i)place*=10;
    digit=(value/place)%10;
    return value+(((digit+change+10)%10)-digit)*place;
}

static int vm_wait_number_input(const MapState *m,void *char_atlas,
    int tile_x,int tile_y,int direction_row,int value,int digits)
{
    SceCtrlData pad;uint32_t prev,held=0;int held_frames=0,max=1,i;
    if(digits<1 || digits>8)return value;
    for(i=0;i<digits;++i)max*=10;
    g_number_value=value<0?0:(value>=max?max-1:value);
    g_number_digits=digits;g_number_cursor=0;g_number_active=1;
    sceCtrlPeekBufferPositive(&pad,1);prev=pad.Buttons;
    while(1) {
        uint32_t pressed,nav;
        vm_render_frame(m,char_atlas,tile_x,tile_y,direction_row,0,0);
        sceCtrlPeekBufferPositive(&pad,1);pressed=pad.Buttons&~prev;prev=pad.Buttons;
        nav=pad.Buttons&(PSP_CTRL_UP|PSP_CTRL_DOWN|PSP_CTRL_LEFT|PSP_CTRL_RIGHT);
        if(nav!=held) {held=nav;held_frames=0;}
        else if(nav && ++held_frames>=28 && (held_frames-28)%5==0)pressed|=nav;
        if(pressed&PSP_CTRL_LEFT)g_number_cursor=(g_number_cursor+digits-1)%digits;
        if(pressed&PSP_CTRL_RIGHT)g_number_cursor=(g_number_cursor+1)%digits;
        if(pressed&PSP_CTRL_UP)g_number_value=number_input_change_digit(g_number_value,digits,g_number_cursor,1);
        if(pressed&PSP_CTRL_DOWN)g_number_value=number_input_change_digit(g_number_value,digits,g_number_cursor,-1);
        if(pressed&(PSP_CTRL_UP|PSP_CTRL_DOWN|PSP_CTRL_LEFT|PSP_CTRL_RIGHT))play_se_async(SE_UI_CURSOR_PATH);
        if(pressed&ui_ok_mask()) {play_se_async(SE_UI_OK_PATH);break;}
        if(pressed&ui_cancel_mask())play_se_async(SE_UI_BUZZER_PATH);
    }
    g_number_active=0;
    return g_number_value;
}

static void fade_game_world(
    const MapState *m, void *char_atlas, void *a1,
    float player_x, float player_y,
    int player_pattern, int player_dir,
    int from, int to, int frames);

static int vm_move_player_one(
    MapState *m, void *char_atlas,
    int *tile_x, int *tile_y, int *direction_row,
    int dx, int dy, int speed_code, int through, int keep_direction)
{
    int nx = *tile_x + dx;
    int ny = *tile_y + dy;
    int bit = 0;
    int reverse_bit = 0;
    int frames;
    int i;
    float step_px;
    float start_x;
    float start_y;

    if (dx == 0 && dy > 0) { bit = 0x01; reverse_bit = 0x08; if (!keep_direction && !g_player_direction_fix) *direction_row = 0; }
    else if (dx < 0 && dy == 0) { bit = 0x02; reverse_bit = 0x04; if (!keep_direction && !g_player_direction_fix) *direction_row = 1; }
    else if (dx > 0 && dy == 0) { bit = 0x04; reverse_bit = 0x02; if (!keep_direction && !g_player_direction_fix) *direction_row = 2; }
    else if (dx == 0 && dy < 0) { bit = 0x08; reverse_bit = 0x01; if (!keep_direction && !g_player_direction_fix) *direction_row = 3; }
    else return 0;

    if (nx < 0 || ny < 0 || nx >= m->w || ny >= m->h) return 0;
    if (!through) {
        uint8_t a = pass_mask_at(m, *tile_x, *tile_y);
        uint8_t b = pass_mask_at(m, nx, ny);
        if (!(a & bit) || !(b & reverse_bit) || vm_event_blocks_at(m, nx, ny)) return 0;
    }

    speed_code = clamp_move_speed_code(speed_code);
    step_px = move_speed_px_per_frame(speed_code);
    frames = (int)((float)TILE_PX / step_px + 0.999f);
    if (frames < 1) frames = 1;

    start_x = ((float)*tile_x + 0.5f) * TILE_PX;
    start_y = ((float)*tile_y + 1.0f) * TILE_PX;
    for (i = 1; i <= frames; ++i) {
        float t = (float)i / (float)frames;
        float wx = start_x + (float)dx * TILE_PX * t;
        float wy = start_y + (float)dy * TILE_PX * t;
        g_player_animation_moving = i < frames;
        g_player_animation_jumping = i == frames; /* arrival: stop count is still zero */
        g_player_animation_speed = speed_code;
        render_world(
            m, char_atlas, NULL, NULL,
            g_player_visible, wx, wy, 1, *direction_row,
            -1, 0.0f, NULL, NULL, 0, 0, 0
        );
    }
    *tile_x = nx;
    *tile_y = ny;
    return 1;
}

static void vm_execute_move_route(
    MapState *m, void *char_atlas,
    int *tile_x, int *tile_y, int *direction_row,
    const uint8_t *records, int count, int target_id)
{
    int speed_code = 3;
    int i;
    if (target_id >= 0 && target_id < MAX_EVENT_ID) {
        VmEventRecord target_ev;
        VmPageRecord target_pg;
        int active_page_index = -1;
        int ei;

        /* RPG Maker resets an event's move speed when its active page changes,
         * then Change Speed inside a move route persists until another page
         * refresh.  This matters twice immediately: Map001's falling Enri
         * changes page speeds 6 -> 5 -> 4 -> 2, while Map004's hatch grate
         * starts at 6 and its first route deliberately changes it to 2 before
         * the second route moves it back. */
        for (ei = 0; m && ei < m->vm_event_count; ++ei) {
            if (!vm_read_event(m, ei, &target_ev)) continue;
            if (target_ev.event_id != target_id) continue;
            if (vm_active_page_index(m, &target_ev, &target_pg, &active_page_index)) {
                int page_speed = (target_pg.flags >> 2) & 0x07;
                if (page_speed < 1 || page_speed > 6) page_speed = 3;
                if (g_event_active_page[target_id] != active_page_index) {
                    g_event_active_page[target_id] = (int16_t)active_page_index;
                    g_event_move_speed[target_id] = (int8_t)page_speed;
                }
            }
            break;
        }
        if (g_event_move_speed[target_id] >= 1 && g_event_move_speed[target_id] <= 6)
            speed_code = g_event_move_speed[target_id];

        /* NPC/event routes.  Positions stay in tile units, with interpolation
           during synchronous Wait move-route commands. */
        for (i = 0; i < count; ++i) {
            const uint8_t *r = records + (size_t)i * 5u;
            int code = r[0];
            int n = (int16_t)read_u16_le(r + 1);
            int dx = 0, dy = 0, f, frames;
            float old_x, old_y;
            if (code == 29) {
                speed_code = clamp_move_speed_code(n);
                g_event_move_speed[target_id] = (int8_t)speed_code;
                continue;
            }
            if (code == 15) {
                vm_wait_frames(n,m,char_atlas,*tile_x,*tile_y,*direction_row);
                continue;
            }
            if (code == 44) {
                int packed = (int16_t)read_u16_le(r + 3);
                int volume = (packed >> 8) & 0xFF;
                int pitch = packed & 0xFF;
                if (volume <= 0) volume = 90;
                if (pitch <= 0) pitch = 100;
                play_vm_se_params(n, volume, pitch, 0);
                continue;
            }
            if (code == 1) dy = 1;
            else if (code == 2) dx = -1;
            else if (code == 3) dx = 1;
            else if (code == 4) dy = -1;
            else continue;
            if (speed_code < 1) speed_code = 1;
            if (speed_code > 6) speed_code = 6;
            old_x = g_event_shift_x[target_id];
            old_y = g_event_shift_y[target_id];
            frames = 256/(1 << speed_code);
            if (frames < 1) frames = 1;
            for (f = 1; f <= frames; ++f) {
                float t = (float)f/(float)frames;
                g_event_shift_x[target_id] = old_x + dx*t;
                g_event_shift_y[target_id] = old_y + dy*t;
                vm_render_frame(m,char_atlas,*tile_x,*tile_y,*direction_row,0,0);
            }
        }
        return;
    }
    /* Player move routes begin at the character's current persistent speed,
     * just like RPG Maker; Change Speed (route code 29) survives the route.
     * Preserve animation phase across successive routes. */
    speed_code = clamp_move_speed_code(g_player_move_speed_code);
    g_player_animation_speed = speed_code;
    for (i = 0; i < count; ++i) {
        const uint8_t *r = records + (size_t)i * 5u;
        int code = (int)r[0];
        int p1 = (int16_t)read_u16_le(r + 1);
        int p2 = (int16_t)read_u16_le(r + 3);
        int dx = 0, dy = 0;
        if (code == 1) { dy = 1; vm_move_player_one(m,char_atlas,tile_x,tile_y,direction_row,dx,dy,speed_code,g_player_through,0); }
        else if (code == 2) { dx = -1; vm_move_player_one(m,char_atlas,tile_x,tile_y,direction_row,dx,dy,speed_code,g_player_through,0); }
        else if (code == 3) { dx = 1; vm_move_player_one(m,char_atlas,tile_x,tile_y,direction_row,dx,dy,speed_code,g_player_through,0); }
        else if (code == 4) { dy = -1; vm_move_player_one(m,char_atlas,tile_x,tile_y,direction_row,dx,dy,speed_code,g_player_through,0); }
        else if (code == 12 || code == 13) {
            player_route_delta(code, *direction_row, &dx, &dy);
            vm_move_player_one(m,char_atlas,tile_x,tile_y,direction_row,dx,dy,speed_code,g_player_through,1);
        } else if (code == 14) {
            /* Match Game_CharacterBase::jump/updateJump from RPG Maker MZ.
             * The logical destination is reached regardless of tile collision;
             * the sprite follows the same parabolic jumpHeight curve, scaled
             * 1:2 together with the rest of NARAKU's 48px -> PSP 24px world. */
            int tx = *tile_x + p1;
            int ty = *tile_y + p2;
            int f;
            int sq = p1 * p1 + p2 * p2;
            int distance = 0;
            int jump_peak;
            int jump_count;
            float sx = ((float)*tile_x + 0.5f) * TILE_PX;
            float sy = ((float)*tile_y + 1.0f) * TILE_PX;
            if (!g_player_direction_fix && abs(p1) > abs(p2)) {
                if (p1 < 0) *direction_row = 1;
                else if (p1 > 0) *direction_row = 2;
            } else if (!g_player_direction_fix && p2 != 0) {
                if (p2 < 0) *direction_row = 3;
                else *direction_row = 0;
            }
            while ((distance + 1) * (distance + 1) <= sq) distance++;
            if (distance * distance != sq) {
                int lo = sq - distance * distance;
                int hi = (distance + 1) * (distance + 1) - sq;
                if (hi <= lo) distance++;
            }
            if (g_player_walk_anime || g_player_step_anime)
                player_animation_reset(&g_player_animation);
            jump_peak = 10 + distance - speed_code;
            if (jump_peak < 1) jump_peak = 1;
            jump_count = jump_peak * 2;
            if (tx >= 0 && ty >= 0 && tx < m->w && ty < m->h) {
                int old_camera_locked = g_camera_locked;
                float old_camera_x = g_camera_lock_x;
                float old_camera_y = g_camera_lock_y;
                for (f = 1; f <= jump_count; ++f) {
                    int remain = jump_count - f;
                    int d = abs(remain - jump_peak);
                    float jump_h = ((float)(jump_peak * jump_peak - d * d) * 0.5f) * 0.5f;
                    float t = (float)f / (float)jump_count;
                    float base_x = sx + p1 * TILE_PX * t;
                    float base_y = sy + p2 * TILE_PX * t;
                    float map_w = (float)(m->w * TILE_PX);
                    float map_h = (float)(m->h * TILE_PX);
                    float max_x = map_w > SCREEN_W ? map_w - SCREEN_W : 0.0f;
                    float max_y = map_h > SCREEN_H ? map_h - SCREEN_H : 0.0f;
                    /* Camera follows _realX/_realY, not the visual jumpHeight. */
                    g_camera_locked = 1;
                    g_camera_lock_x = max_x > 0.0f
                        ? clamp_float(base_x - SCREEN_W * 0.5f, 0.0f, max_x) : 0.0f;
                    g_camera_lock_y = max_y > 0.0f
                        ? clamp_float(base_y - SCREEN_H * 0.5f, 0.0f, max_y) : 0.0f;
                    g_player_animation_jumping = 1;
                    g_player_animation_moving = remain > 0 && (p1 || p2);
                    render_world(m,char_atlas,NULL,NULL,g_player_visible,
                        base_x, base_y - jump_h,
                        1,*direction_row,-1,0.0f,NULL,NULL,0,0,0);
                }
                g_camera_locked = old_camera_locked;
                g_camera_lock_x = old_camera_x;
                g_camera_lock_y = old_camera_y;
                *tile_x = tx; *tile_y = ty;
            }
        } else if (code == 15) {
            vm_wait_frames(p1, m, char_atlas, *tile_x, *tile_y, *direction_row);
        } else if (code == 16 && !g_player_direction_fix) *direction_row = 0;
        else if (code == 17 && !g_player_direction_fix) *direction_row = 1;
        else if (code == 18 && !g_player_direction_fix) *direction_row = 2;
        else if (code == 19 && !g_player_direction_fix) *direction_row = 3;
        else if (code == 31) g_player_walk_anime=1;
        else if (code == 32) g_player_walk_anime=0;
        else if (code == 33) g_player_step_anime=1;
        else if (code == 34) g_player_step_anime=0;
        else if (code == 35) g_player_direction_fix=1;
        else if (code == 36) g_player_direction_fix=0;
        else if (code == 29) {
            speed_code = clamp_move_speed_code(p1);
            g_player_move_speed_code = speed_code;
            g_player_animation_speed = speed_code;
        }
        else if (code == 44) {
            int volume = (p2 >> 8) & 0xFF;
            int pitch = p2 & 0xFF;
            if (volume <= 0) volume = 90;
            if (pitch <= 0) pitch = 100;
            play_vm_se_params(p1, volume, pitch, 0);
        }
        else if (code == 37) g_player_through = 1;
        else if (code == 38) g_player_through = 0;
        else if (code == 39) g_player_visible = 0;
        else if (code == 40) g_player_visible = 1;
        /* Animation and direction-fix state persist across routes. */
    }
}

static int vm_transfer_player(
    MapState *m, void *char_atlas,
    int *tile_x, int *tile_y, int *direction_row,
    int dest_map, int dest_x, int dest_y, int direction, int fade)
{
    float old_x = ((float)*tile_x + 0.5f) * TILE_PX;
    float old_y = ((float)*tile_y + 1.0f) * TILE_PX;
    int new_row;
    int frames = fade == 2 ? 0 : 24;
    int old_white=g_transfer_white;
    g_transfer_white=(fade==1);

    if (dest_map < 1 || dest_map > MAX_MAP_ID) {g_transfer_white=old_white;return 0;}

    if (frames > 0) {
        fade_game_world(
            m, char_atlas, NULL,
            old_x, old_y, g_player_visible, *direction_row,
            0, 255, frames
        );
    }

    if (!load_map(m, dest_map)) {g_transfer_white=old_white;return 0;}
    *tile_x = dest_x;
    *tile_y = dest_y;
    new_row = direction_to_row(direction);
    if (new_row >= 0) *direction_row = new_row;

    if (frames > 0) {
        float nx = ((float)*tile_x + 0.5f) * TILE_PX;
        float ny = ((float)*tile_y + 1.0f) * TILE_PX;
        fade_game_world(
            m, char_atlas, NULL,
            nx, ny, g_player_visible, *direction_row,
            255, 0, frames
        );
    }
    g_transfer_white=old_white;
    return 1;
}

static void load_common_vm(void)
{
    g_common_vm = (uint8_t *)load_whole_file(COMMON_VM_PATH, &g_common_vm_size);
    if (!g_common_vm || g_common_vm_size < 8 || memcmp(g_common_vm, "NC50", 4) != 0)
        fatal_error("Missing or invalid common_vm.bin");
    g_common_vm_count = (int)read_u16_le(g_common_vm + 4);
    if (g_common_vm_count > 256 || g_common_vm_size < 8u + (size_t)g_common_vm_count * 8u)
        fatal_error("Bad Common Event table");
}

static int vm_execute_page(
    MapState *m, const VmEventRecord *ev, const VmPageRecord *pg,
    void *char_atlas, int lang,
    int *tile_x, int *tile_y, int *direction_row);

static void vm_call_common(
    MapState *m, const VmEventRecord *ev, int common_id,
    void *char_atlas, int lang,
    int *tile_x, int *tile_y, int *direction_row)
{
    uint32_t offset, size;
    const uint8_t *original_cmds;
    size_t original_size;
    VmPageRecord page;
    if (!g_common_vm || common_id < 1 || common_id >= g_common_vm_count || g_common_depth >= 8)
        return;
    offset = read_u32_le(g_common_vm + 8 + common_id * 8);
    size = read_u32_le(g_common_vm + 8 + common_id * 8 + 4);
    if (!size || offset >= g_common_vm_size || size > g_common_vm_size - offset)
        return;
    memset(&page, 0, sizeof(page));
    page.supported = 1;
    page.cmd_offset = 0;
    page.cmd_size = size;
    original_cmds = m->vm_commands;
    original_size = m->vm_command_size;
    m->vm_commands = g_common_vm + offset;
    m->vm_command_size = size;
    ++g_common_depth;
    vm_execute_page(m, ev, &page, char_atlas, lang, tile_x, tile_y, direction_row);
    --g_common_depth;
    /* A map transfer during a Common Event can change the MapState. */
    if (m->vm_commands == g_common_vm + offset) {
        m->vm_commands = original_cmds;
        m->vm_command_size = original_size;
    }
}

static int vm_execute_page(
    MapState *m, const VmEventRecord *ev, const VmPageRecord *pg,
    void *char_atlas, int lang,
    int *tile_x, int *tile_y, int *direction_row)
{
    const uint8_t *p;
    const uint8_t *end;
    const uint8_t *base;
    uint8_t *cmd_copy;
    int source_map_id;
    int source_event_id;
    int did_transfer = 0;

    if (!pg->supported || !m->vm_commands) return 0;
    if ((size_t)pg->cmd_offset + (size_t)pg->cmd_size > m->vm_command_size) return 0;

    /* RPG Maker's Game_Interpreter owns its command list independently of
     * Game_Map.  A Transfer Player can load another map, but the current
     * event keeps executing after the transfer.  Our map loader frees the
     * old map VM blob, so executing directly from m->vm_commands made that
     * impossible and could leave cutscenes half-finished (invisible/frozen
     * player, switches not restored, etc.).  Keep a private copy for the
     * lifetime of this interpreter invocation. */
    cmd_copy = (uint8_t *)malloc(pg->cmd_size ? (size_t)pg->cmd_size : 1u);
    if (!cmd_copy) return 0;
    if (pg->cmd_size)
        memcpy(cmd_copy, m->vm_commands + pg->cmd_offset, (size_t)pg->cmd_size);
    source_map_id = m->id;
    source_event_id = ev ? ev->event_id : 0;
    p = cmd_copy;
    base = p;
    end = p + pg->cmd_size;

    while (p < end) {
        if (source_map_id == 12) scene_trace(source_map_id,source_event_id,(int)(p-base),*p);
        int op = *p++;
        if (op == VM_OP_END) break;

        if (op == VM_OP_TEXT) {
            uint16_t sl[4], ml[4];
            const char *speaker = NULL;
            const char *message = NULL;
            size_t speaker_len = 0;
            size_t message_len = 0;
            int i;
            const uint8_t *q;
            if (end - p < 16) break;
            for (i = 0; i < 4; ++i) {
                sl[i] = read_u16_le(p + i * 4 + 0);
                ml[i] = read_u16_le(p + i * 4 + 2);
            }
            q = p + 16;
            for (i = 0; i < 4; ++i) {
                if (q + sl[i] + ml[i] > end) goto vm_done;
                if (i == lang) {
                    speaker = (const char *)q;
                    speaker_len = sl[i];
                    message = (const char *)(q + sl[i]);
                    message_len = ml[i];
                }
                q += sl[i] + ml[i];
            }
            p = q;
            vm_wait_text(
                m, char_atlas, *tile_x, *tile_y, *direction_row,
                speaker ? speaker : "", speaker_len,
                message ? message : "", message_len,
                p < end && *p == VM_OP_TEXT
            );
        } else if (op == VM_OP_NUMBER_INPUT) {
            int id,digits;
            if(end-p<3)break;
            id=read_u16_le(p);digits=p[2];p+=3;
            if(id>0 && id<MAX_VARIABLES && digits>=1 && digits<=8)
                g_variables[id]=vm_wait_number_input(m,char_atlas,*tile_x,*tile_y,*direction_row,g_variables[id],digits);
        } else if (op == VM_OP_FADE_SCREEN) {
            int from,to,i;
            if(end-p<1)break;
            from=g_script_fade_alpha;to=*p++?255:0;
            for(i=1;i<=24;++i) {
                g_script_fade_alpha=from+(to-from)*i/24;
                vm_render_frame(m,char_atlas,*tile_x,*tile_y,*direction_row,0,0);
            }
        } else if (op == VM_OP_SWITCH) {
            int first, last, value, i;
            if (end - p < 5) break;
            first = (int)read_u16_le(p + 0);
            last = (int)read_u16_le(p + 2);
            value = (int)p[4];
            p += 5;
            if (first < 0) first = 0;
            if (last >= MAX_SWITCHES) last = MAX_SWITCHES - 1;
            for (i = first; i <= last; ++i) g_switches[i] = (uint8_t)value;
        } else if (op == VM_OP_SELF_SWITCH) {
            int idx, value;
            if (end - p < 2) break;
            idx = (int)p[0]; value = (int)p[1]; p += 2;
            if (source_map_id >= 1 && source_map_id <= MAX_MAP_ID &&
                source_event_id >= 0 && source_event_id < MAX_EVENT_ID && idx >= 0 && idx < 4) {
                if (value) g_self_switches[source_map_id][source_event_id] |= (uint8_t)(1u << idx);
                else g_self_switches[source_map_id][source_event_id] &= (uint8_t)~(1u << idx);
            }
        } else if (op == VM_OP_WAIT) {
            int frames;
            if (end - p < 2) break;
            frames = (int)read_u16_le(p); p += 2;
            vm_wait_frames(frames, m, char_atlas, *tile_x, *tile_y, *direction_row);
        } else if (op == VM_OP_TRANSFER) {
            int dest_map, dest_x, dest_y, direction, fade;
            if (end - p < 8) break;
            dest_map = (int)read_u16_le(p + 0);
            dest_x = (int)read_u16_le(p + 2);
            dest_y = (int)read_u16_le(p + 4);
            direction = (int)p[6];
            fade = (int)p[7];
            p += 8;
            if (vm_transfer_player(
                    m, char_atlas, tile_x, tile_y, direction_row,
                    dest_map, dest_x, dest_y, direction, fade)) {
                did_transfer = 1;
                /* Do not return here.  MZ waits for the transfer and then
                 * resumes the same Game_Interpreter command list. */
            }
        } else if (op == VM_OP_SE) {
            int se_id, volume, pitch, pan;
            if (end - p < 5) break;
            se_id = (int)read_u16_le(p + 0);
            volume = (int)p[2];
            pitch = (int)p[3];
            pan = (int)p[4] - 100;
            p += 5;
            play_vm_se_params(se_id, volume, pitch, pan);
        } else if (op == VM_OP_ITEM) {
            int item_id;
            int16_t delta;
            if (end - p < 4) break;
            item_id = (int)read_u16_le(p + 0);
            delta = (int16_t)read_u16_le(p + 2);
            p += 4;
            if (item_id >= 0 && item_id < MAX_ITEMS) {
                int v = (int)g_items[item_id] + (int)delta;
                if (v < 0) v = 0;
                if (v > 999) v = 999;
                g_items[item_id] = (int16_t)v;
            }
        } else if (op == VM_OP_TRANSPARENCY) {
            if (end - p < 1) break;
            /* RPG Maker MZ command211: setTransparent(params[0] === 0).
             * Parameter 0 means Transparency ON (player hidden), parameter 1
             * means Transparency OFF (player visible).  Earlier PSP builds
             * had this inverted, so Map004's autorun hid Enri exactly when
             * the original game restores her after the hatch transition. */
            g_player_visible = p[0] ? 1 : 0;
            p += 1;
        } else if (op == VM_OP_TINT) {
            int r, g, b, gray, duration, wait;
            if (end - p < 11) break;
            r = (int16_t)read_u16_le(p + 0);
            g = (int16_t)read_u16_le(p + 2);
            b = (int16_t)read_u16_le(p + 4);
            gray = (int16_t)read_u16_le(p + 6);
            duration = (int)read_u16_le(p + 8);
            wait = (int)p[10];
            p += 11;

            /* MZ keeps the complete screen tone after command 223.  0.6.4
             * reduced everything except full black to zero, which removed
             * NARAKU's persistent red veil [10,-10,-10,0]. */
            vm_begin_world_tint(r, g, b, gray, duration);
            if (wait && duration > 0)
                vm_wait_frames(duration, m, char_atlas,
                               *tile_x, *tile_y, *direction_row);
        } else if (op == VM_OP_FLASH) {
            int r, g, b, a, duration, wait;
            if (end - p < 11) break;
            r = (int16_t)read_u16_le(p + 0);
            g = (int16_t)read_u16_le(p + 2);
            b = (int16_t)read_u16_le(p + 4);
            a = (int16_t)read_u16_le(p + 6);
            duration = (int)read_u16_le(p + 8);
            wait = (int)p[10];
            p += 11;
            vm_begin_screen_flash(r, g, b, a, duration);
            if (wait && duration > 0)
                vm_wait_frames(duration, m, char_atlas,
                               *tile_x, *tile_y, *direction_row);
        } else if (op == VM_OP_SCROLL_MAP) {
            int direction,distance,speed,wait;
            if(end-p<4)break;
            direction=p[0];distance=p[1];speed=p[2];wait=p[3];p+=4;
            vm_begin_map_scroll(direction,distance,speed);
            if(wait)vm_wait_frames(g_map_scroll_total,m,char_atlas,*tile_x,*tile_y,*direction_row);
        } else if (op == VM_OP_SHAKE) {
            int power, speed, duration, wait, i;
            if (end - p < 5) break;
            power = (int)p[0];
            speed = (int)p[1];
            duration = (int)read_u16_le(p + 2);
            wait = (int)p[4];
            p += 5;
            if (duration < 0) duration = 0;
            if (wait) {
                for (i = 0; i < duration; ++i) {
                    int period = 18 - speed;
                    float phase;
                    if (period < 2) period = 2;
                    phase = (float)(i % period) / (float)period;
                    /* Triangular shake is inexpensive and close to MZ's
                     * oscillating screen shake at PSP scale. */
                    g_screen_shake_x = ((phase < 0.5f ? phase * 4.0f - 1.0f
                                                      : 3.0f - phase * 4.0f)
                                        * (float)power * 0.5f);
                    vm_render_frame(m, char_atlas, *tile_x, *tile_y, *direction_row, 0, 0);
                }
            }
            g_screen_shake_x = 0.0f;
        } else if (op == VM_OP_BGM) {
            int bgm_id;
            if (end - p < 5) break;
            bgm_id = (int)read_u16_le(p + 0);
            p += 5;
            if (bgm_id >= 1000) {
                char path[180];
                snprintf(path,sizeof(path),ASSET_ROOT "bgm_exact_%04d.pcm",bgm_id);
                set_bgm_track(path);
            }
            else if (bgm_id == 1) set_bgm_track(BGM_PATH);
            else if (bgm_id == 2) set_bgm_track("");
        } else if (op == VM_OP_FADE_BGM) {
            int seconds;
            if (end - p < 2) break;
            seconds=read_u16_le(p);p+=2;
            g_bgm_fade_start=sceKernelGetSystemTimeWide();
            g_bgm_fade_generation=g_bgm_generation;
            g_bgm_fade_us=seconds ? (unsigned long long)seconds*1000000u : 1;
        } else if (op == VM_OP_STOP_SE) {
            ++g_se_generation;
        } else if (op == VM_OP_ERASE_EVENT) {
            if(m->id==source_map_id && source_event_id>0 && source_event_id<MAX_EVENT_ID)
                g_event_erased[source_event_id]=1;
        } else if (op == VM_OP_PICTURE6) {
            if (end - p < 1) break;
            g_picture6_alpha = (int)p[0];
            g_picture6_visible = g_picture6_alpha > 0;
            p += 1;
        } else if (op == VM_OP_VARIABLE) {
            int first, last, oper, i;
            int32_t value;
            if (end - p < 9) break;
            first = (int)read_u16_le(p + 0);
            last = (int)read_u16_le(p + 2);
            oper = (int)p[4];
            value = (int32_t)read_u32_le(p + 5);
            p += 9;
            if (first < 0) first = 0;
            if (last >= MAX_VARIABLES) last = MAX_VARIABLES - 1;
            for (i = first; i <= last; ++i) {
                if (oper == 0) g_variables[i] = value;
                else if (oper == 1) g_variables[i] += value;
                else if (oper == 2) g_variables[i] -= value;
                else if (oper == 3) g_variables[i] *= value;
                else if (oper == 4 && value != 0) g_variables[i] /= value;
                else if (oper == 5 && value != 0) g_variables[i] %= value;
            }
        } else if (op == VM_OP_COND_SWITCH) {
            int id, expected;
            uint32_t target;
            if (end - p < 7) break;
            id = (int)read_u16_le(p + 0);
            expected = (int)p[2];
            target = read_u32_le(p + 3);
            p += 7;
            if (id <= 0 || id >= MAX_SWITCHES || (!!g_switches[id]) != expected) {
                if (target >= pg->cmd_size) break;
                p = base + target;
            }
        } else if (op == VM_OP_COND_VAR) {
            int id, oper;
            int32_t value, actual;
            int ok = 0;
            uint32_t target;
            if (end - p < 11) break;
            id = (int)read_u16_le(p + 0);
            oper = (int)p[2];
            value = (int32_t)read_u32_le(p + 3);
            target = read_u32_le(p + 7);
            p += 11;
            actual = (id >= 0 && id < MAX_VARIABLES) ? g_variables[id] : 0;
            if (oper == 0) ok = (actual == value);
            else if (oper == 1) ok = (actual >= value);
            else if (oper == 2) ok = (actual <= value);
            else if (oper == 3) ok = (actual > value);
            else if (oper == 4) ok = (actual < value);
            else if (oper == 5) ok = (actual != value);
            if (!ok) {
                if (target >= pg->cmd_size) break;
                p = base + target;
            }
        } else if (op == VM_OP_COND_ITEM) {
            int id;
            uint32_t target;
            if (end - p < 6) break;
            id = (int)read_u16_le(p + 0);
            target = read_u32_le(p + 2);
            p += 6;
            if (id < 0 || id >= MAX_ITEMS || g_items[id] <= 0) {
                if (target >= pg->cmd_size) break;
                p = base + target;
            }
        } else if (op == VM_OP_COND_LANG) {
            int expected;
            uint32_t target;
            if (end - p < 5) break;
            expected = (int)p[0];
            target = read_u32_le(p + 1);
            p += 5;
            if (lang != expected) {
                if (target >= pg->cmd_size) break;
                p = base + target;
            }
        } else if (op == VM_OP_JUMP) {
            uint32_t target;
            if (end - p < 4) break;
            target = read_u32_le(p);
            if (target >= pg->cmd_size) break;
            p = base + target;
        } else if (op == VM_OP_SHOW_PICTURE_EX) {
            int id,rid,origin,x,y,zx,zy,alpha,blend;
            PictureSlot *slot;
            if(end-p<21) break;
            id=read_u16_le(p);rid=read_u16_le(p+2);origin=p[4];
            x=(int32_t)read_u32_le(p+5);y=(int32_t)read_u32_le(p+9);
            zx=read_u16_le(p+13);zy=read_u16_le(p+15);alpha=p[17];blend=p[18];
            if(p[19]) { x=(x>=0 && x<MAX_VARIABLES)?g_variables[x]:0;
                         y=(y>=0 && y<MAX_VARIABLES)?g_variables[y]:0; }
            p+=21;
            picture_show(id,rid,origin,x,y,zx,zy,alpha);
            slot=picture_slot(id);if(slot && slot->number) slot->blend=blend;
        } else if (op == VM_OP_MOVE_PICTURE_EX) {
            int id,origin,x,y,zx,zy,alpha,blend,duration,wait,easing;
            if(end-p<22) break;
            id=read_u16_le(p);origin=p[2];x=(int32_t)read_u32_le(p+3);
            y=(int32_t)read_u32_le(p+7);zx=read_u16_le(p+11);zy=read_u16_le(p+13);
            alpha=p[15];blend=p[16];duration=read_u16_le(p+17);wait=p[19];easing=p[20];
            if(p[21]) { x=(x>=0 && x<MAX_VARIABLES)?g_variables[x]:0;
                         y=(y>=0 && y<MAX_VARIABLES)?g_variables[y]:0; }
            p+=22;
            move_picture_start(picture_slot(id),origin,x,y,zx,zy,alpha,blend,duration,easing);
            if(wait) vm_wait_frames(duration,m,char_atlas,*tile_x,*tile_y,*direction_row);
        } else if (op == VM_OP_SHOW_PICTURE) {
            int id,rid,origin,x,y,zx,zy,alpha;
            if (end - p < 16) break;
            id=read_u16_le(p); rid=read_u16_le(p+2);origin=p[4];
            x=(int32_t)read_u32_le(p+5);y=(int32_t)read_u32_le(p+9);
            zx=p[13];zy=p[14];alpha=p[15];p+=16;
            picture_show(id,rid,origin,x,y,zx,zy,alpha);
        } else if (op == VM_OP_MOVE_PICTURE) {
            int id,x,y,zx,zy,alpha,duration,wait,i;
            PictureSlot *slot;
            int ox,oy,oa;
            if (end - p < 17) break;
            id=read_u16_le(p);x=(int32_t)read_u32_le(p+2);
            y=(int32_t)read_u32_le(p+6);
            zx=p[10];zy=p[11];alpha=p[12];
            duration=read_u16_le(p+13);wait=p[15];
            p+=17;
            if (id == 6) {
                /* A1 is a dedicated full-screen texture rather than a generic
                 * PictureSlot.  Preserve MZ Move Picture opacity fades too. */
                int oa6 = g_picture6_visible ? g_picture6_alpha : 0;
                if (wait && duration > 0 && duration <= 600) {
                    for (i = 1; i <= duration; ++i) {
                        g_picture6_alpha = oa6 + (alpha - oa6) * i / duration;
                        g_picture6_visible = g_picture6_alpha > 0;
                        vm_render_frame(m,char_atlas,*tile_x,*tile_y,*direction_row,0,0);
                    }
                }
                g_picture6_alpha = alpha;
                g_picture6_visible = alpha > 0;
                continue;
            }
            slot=picture_slot(id);
            if (!slot || !slot->number) continue;
            ox=slot->x; oy=slot->y; oa=slot->opacity;
            if (wait && duration > 0 && duration <= 600) {
                for(i=1;i<=duration;++i) {
                    slot->x=ox+(x-ox)*i/duration;
                    slot->y=oy+(y-oy)*i/duration;
                    slot->opacity=oa+(alpha-oa)*i/duration;
                    vm_render_frame(m,char_atlas,*tile_x,*tile_y,*direction_row,0,0);
                }
            }
            slot->x=x;slot->y=y;slot->scale_x=zx;
            slot->scale_y=zy;slot->opacity=alpha;
        } else if (op == VM_OP_ERASE_PICTURE) {
            int id;
            if (end - p < 2) break;
            id=read_u16_le(p);p+=2;
            erase_picture_slot(id);
            if(id==6){g_picture6_visible=0;g_picture6_alpha=0;}
        } else if (op == VM_OP_CHOICES) {
            int count, cancel_index, default_index, ci, li;
            const uint8_t *q;
            if (end - p < 3) break;
            count = (int)p[0];
            cancel_index = (int)(int8_t)p[1];
            default_index = (int)(int8_t)p[2];
            p += 3;
            if (count < 1 || count > 6) break;
            q = p;
            for (ci = 0; ci < count; ++ci) {
                uint16_t lens[4];
                if (end - q < 8) goto vm_done;
                for (li = 0; li < 4; ++li) lens[li] = read_u16_le(q + li * 2);
                q += 8;
                for (li = 0; li < 4; ++li) {
                    if ((size_t)(end - q) < lens[li]) goto vm_done;
                    if (li == lang) {
                        g_choice_labels[ci] = (const char *)q;
                        g_choice_lengths[ci] = lens[li];
                    }
                    q += lens[li];
                }
            }
            p = q;
            g_last_choice = vm_wait_choices(m, char_atlas, *tile_x, *tile_y,
                                            *direction_row, count, default_index, cancel_index);
        } else if (op == VM_OP_COND_CHOICE) {
            int choice;
            uint32_t target;
            if (end - p < 5) break;
            choice = (int)p[0]; target = read_u32_le(p + 1); p += 5;
            if (g_last_choice != choice) {
                if (target >= pg->cmd_size) break;
                p = base + target;
            }
        } else if (op == VM_OP_COMMON_EVENT) {
            int common_id;
            if (end - p < 2) break;
            common_id = (int)read_u16_le(p); p += 2;
            vm_call_common(m, ev, common_id, char_atlas, lang, tile_x, tile_y, direction_row);
            lang = g_language;
            if (g_request_title || g_loaded_from_scene) goto vm_done;
        } else if (op == VM_OP_SAVE_ACCESS) {
            if (end - p < 1) break;
            g_save_enabled = *p++ ? 1 : 0;
        } else if (op == VM_OP_SCENE) {
            int scene_id;
            if (end - p < 1) break;
            scene_id = (int)*p++;
            if (scene_id == SCENE_ITEM) {
                ui_inventory_scene();
                lang = g_language;
            } else if (scene_id == SCENE_SAVE) {
                ui_save_load_scene(1, m->id, *tile_x, *tile_y, *direction_row, NULL);
            } else if (scene_id == SCENE_LOAD) {
                ProgressState loaded_state;
                if (ui_save_load_scene(0, 0, 0, 0, 0, &loaded_state)) {
                    if (!load_map(m, loaded_state.map_id))
                        fatal_error("Could not load selected save map");
                    *tile_x = loaded_state.tile_x;
                    *tile_y = loaded_state.tile_y;
                    *direction_row = loaded_state.direction_row;
                    if (*tile_x < 0 || *tile_x >= m->w || *tile_y < 0 || *tile_y >= m->h) {
                        *tile_x = 0;
                        *tile_y = 0;
                    }
                    did_transfer = 1;
                    g_loaded_from_scene = 1;
                    goto vm_done;
                }
            } else if (scene_id == SCENE_OPTIONS) {
                ui_options_scene();
                lang = g_language;
            } else if (scene_id == SCENE_TITLE) {
                g_request_title = 1;
                goto vm_done;
            }
        } else if (op == VM_OP_MOVE_ROUTE_EX) {
            int target,count,flags;
            if(end-p<5)break;
            target=(int16_t)read_u16_le(p);count=read_u16_le(p+2);flags=p[4];p+=5;
            if(end-p<count*5)break;
            if(target>=0 && m->id!=source_map_id){p+=count*5;continue;}
            if(target==0)target=source_event_id;
            if(target>0) {
                if(start_event_route(m,target,p,count,flags) && (flags&4))
                    while(g_routes[target].records)
                        vm_render_frame(m,char_atlas,*tile_x,*tile_y,*direction_row,0,0);
            } else if((flags&4) || !start_player_route(p,count,flags,tile_x,tile_y,direction_row)) {
                free(g_player_route.records);memset(&g_player_route,0,sizeof(g_player_route));
                vm_execute_move_route(m,char_atlas,tile_x,tile_y,direction_row,p,count,target);
            }
            p+=count*5;
        } else if (op == VM_OP_MOVE_ROUTE) {
            int target, count;
            if (end - p < 4) break;
            target = (int16_t)read_u16_le(p);
            count = (int)read_u16_le(p + 2);
            p += 4;
            if (count < 0 || end - p < count * 5) break;
            if (target >= 0 && m->id != source_map_id) {
                /* Game_Interpreter.character() returns null for map events
                 * after transferring away from the interpreter's source map.
                 * The player target (-1) remains valid. */
                p += count * 5;
                continue;
            }
            if (target == 0) target = source_event_id;
            vm_execute_move_route(m, char_atlas, tile_x, tile_y, direction_row,
                                  p, count, target);
            p += count * 5;
        } else if (op == VM_OP_EXIT) {
            break;
        } else {
            break;
        }
    }

vm_done:
    free(cmd_copy);
    return did_transfer;
}

static int vm_run_event_at(
    MapState *m, int x, int y, int trigger,
    void *char_atlas, int lang,
    int *tile_x, int *tile_y, int *direction_row)
{
    VmEventRecord ev;
    VmPageRecord pg;
    if (!vm_find_event_at(m, x, y, trigger, &ev, &pg)) return 0;
    if (is_chase_enemy(m->id,ev.event_id) && trigger == 2) {
        g_s003_paused = 1;
        free(g_routes[ev.event_id].records); memset(&g_routes[ev.event_id],0,sizeof(g_routes[ev.event_id]));
    }
    return 1 + vm_execute_page(
        m, &ev, &pg, char_atlas, lang, tile_x, tile_y, direction_row
    );
}

static void vm_run_autoruns(
    MapState *m, void *char_atlas, int lang,
    int *tile_x, int *tile_y, int *direction_row)
{
    int pass;
    for (pass = 0; pass < 12; ++pass) {
        int i;
        int ran = 0;
        for (i = 0; i < m->vm_event_count; ++i) {
            VmEventRecord ev;
            VmPageRecord pg;
            if (!vm_read_event(m, i, &ev)) continue;
            if (!vm_active_page(m, &ev, &pg)) continue;
            if (pg.trigger != 3 || !pg.supported) continue;
            vm_execute_page(m, &ev, &pg, char_atlas, lang, tile_x, tile_y, direction_row);
            lang = g_language;
            if (g_request_title || g_loaded_from_scene) return;
            ran = 1;
            break;
        }
        if (!ran) break;
    }
}

/* Run the two early one-shot parallel events that gate the Worm route without
 * freezing player input.  This mirrors the relevant RPG Maker trigger-4
 * pages frame-for-frame instead of executing their Wait commands synchronously.
 *
 * Map006 Event 13 (second Green Key) sets switch 16 ON.  Once the player later
 * reaches Map008, Event 70 waits 180 frames, plays the water cue, then sets
 * switch 22 ON.  That activates Map009 Event 4 page 5; touching the opened meat
 * wall starts the original Worm cutscene, whose animation is driven by
 * switches 41-44 and Map009 Event 7.
 */
static void vm_tick_story_parallel(const MapState *m)
{
    if (!m) return;

    /* If an older save somehow contains the "timer finished" flag without the
     * immediately-following Worm-arm flag, repair that impossible original
     * state on Map009.  In RPG Maker those two switch writes are consecutive. */
    if (m->id == 9 && g_switches[16] && g_switches[17] && !g_switches[22])
        g_switches[22] = 1;

    /* Map008 Event 70 is the delayed off-screen water cue that arms the
     * Map009 Worm route.  Older builds reset this 180-frame timer as soon as
     * the player transferred out of Map008, so a quick walk into Map009 could
     * leave switch 22 permanently OFF.  Once started, carry the timer through
     * the immediate Map008 -> Map009 transfer.  If an old save is already on
     * Map009 with switch 16 set but the tail never fired, repair it there. */
    if (g_switches[16] && !g_switches[17]) {
        if (m->id == 8) {
            if (g_map8_drop_timer < 1)
                g_map8_drop_timer = 1;
            else
                ++g_map8_drop_timer;
        } else if (m->id == 9) {
            if (g_map8_drop_timer < 1)
                g_map8_drop_timer = 180;
            else
                ++g_map8_drop_timer;
        }

        if (g_map8_drop_timer >= 180) {
            play_vm_se_params(2, 70, 80, 80); /* 【魔王魂】 水01 */
            g_switches[17] = 1;
            g_switches[13] = 0;
            g_switches[22] = 1;
            g_map8_drop_timer = 0;
        }
    } else if (!g_switches[16] || g_switches[17]) {
        g_map8_drop_timer = 0;
    }

    /* Map009 Event 115: delayed off-screen water sound after taking the Green
     * Key from the corpse. */
    if (m->id == 9 && g_switches[26]) {
        if (++g_map9_water_timer >= 200) {
            play_vm_se_params(2, 50, 80, 80);
            g_switches[26] = 0;
            g_map9_water_timer = 0;
        }
    } else {
        g_map9_water_timer = 0;
    }
}

/* ------------------------------------------------------------------------- */
/* Opening / Map001 intro                                                    */
/* ------------------------------------------------------------------------- */

static const char *opening1_path(int lang)
{
    switch (lang) {
        case 1: return ASSET_ROOT "opening1_ja.rgba8888";
        case 2: return ASSET_ROOT "opening1_zhcn.rgba8888";
        case 3: return ASSET_ROOT "opening1_zhtw.rgba8888";
        default: return ASSET_ROOT "opening1_en.rgba8888";
    }
}

static const char *opening2_path(int lang)
{
    return lang == 0
        ? ASSET_ROOT "opening2_en.rgba8888"
        : ASSET_ROOT "opening2_default.rgba8888";
}

static const char *dialog_path(int lang, int which)
{
    static const char *paths[4][2] = {
        {ASSET_ROOT "dialog1_en.rgba8888", ASSET_ROOT "dialog2_en.rgba8888"},
        {ASSET_ROOT "dialog1_ja.rgba8888", ASSET_ROOT "dialog2_ja.rgba8888"},
        {ASSET_ROOT "dialog1_zhcn.rgba8888", ASSET_ROOT "dialog2_zhcn.rgba8888"},
        {ASSET_ROOT "dialog1_zhtw.rgba8888", ASSET_ROOT "dialog2_zhtw.rgba8888"}
    };
    if (lang < 0 || lang > 3) lang = 0;
    if (which < 0 || which > 1) which = 0;
    return paths[lang][which];
}

static void run_opening(int lang)
{
    void *pic1 = load_exact_file(opening1_path(lang), PIC_TEX_BYTES);
    void *pic2;

    if (!pic1) fatal_error("Could not load Opening 1 texture");
    fade_picture(pic1, 0, 255, 120);
    wait_cross();
    fade_picture(pic1, 255, 0, 60);
    free(pic1);

    pic2 = load_exact_file(opening2_path(lang), PIC_TEX_BYTES);
    if (!pic2) fatal_error("Could not load Opening 2 texture");
    fade_picture(pic2, 0, 255, 120);
    wait_cross();
    fade_picture(pic2, 255, 0, 60);
    free(pic2);
}

static void wait_scene_frames(
    int frames, const MapState *m, void *char_atlas,
    void *a1, void *fall_atlas, int player_visible,
    float player_x, float player_y, int player_pattern, int player_dir,
    int fall_slot, float fall_y, int black_alpha)
{
    int i;
    for (i = 0; i < frames; ++i) {
        render_world(
            m, char_atlas, a1, fall_atlas,
            player_visible, player_x, player_y,
            player_pattern, player_dir,
            fall_slot, fall_y,
            NULL, NULL, 0, black_alpha, 0
        );
    }
}

static void fade_black_scene(
    int from, int to, int frames,
    const MapState *m, void *char_atlas,
    void *a1, void *fall_atlas,
    int player_visible, float player_x, float player_y,
    int fall_slot, float fall_y)
{
    int i;
    for (i = 1; i <= frames; ++i) {
        int a = from + (to - from) * i / frames;
        render_world(
            m, char_atlas, a1, fall_atlas,
            player_visible, player_x, player_y, 1, 0,
            fall_slot, fall_y,
            NULL, NULL, 0, a, 0
        );
    }
}

static void flash_red_scene(
    int frames, const MapState *m, void *char_atlas,
    void *a1, void *fall_atlas, int fall_slot, float fall_y)
{
    int i;
    for (i = 0; i < frames; ++i) {
        int a = 255 - (255 * i / frames);
        render_world(
            m, char_atlas, a1, fall_atlas,
            0, 0.0f, 0.0f, 1, 0,
            fall_slot, fall_y,
            NULL, NULL, a, 0, 0
        );
    }
}

static float animate_fall_move(
    int slot, float start_y, int tiles, int frames_per_tile,
    const MapState *m, void *char_atlas, void *a1, void *fall_atlas)
{
    int total = tiles * frames_per_tile;
    float end_y = start_y + (float)tiles;
    int i;

    for (i = 1; i <= total; ++i) {
        float t = (float)i / (float)total;
        float y = start_y + (end_y - start_y) * t;
        render_world(
            m, char_atlas, a1, fall_atlas,
            0, 0.0f, 0.0f, 1, 0,
            slot, y,
            NULL, NULL, 0, 0, 0
        );
    }
    return end_y;
}

static void wait_blank_message(
    const MapState *m, void *char_atlas,
    void *a1, void *fall_atlas, int fall_slot, float fall_y)
{
    SceCtrlData pad;
    uint32_t prev;

    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;

    while (1) {
        render_world(
            m, char_atlas, a1, fall_atlas,
            0, 0.0f, 0.0f, 1, 0,
            fall_slot, fall_y,
            NULL, NULL, 0, 0, 1
        );

        sceCtrlPeekBufferPositive(&pad, 1);
        if ((pad.Buttons & ~prev) & PSP_CTRL_CROSS) return;
        prev = pad.Buttons;
    }
}

static void wait_dialog(
    void *dialog, const MapState *m, void *char_atlas,
    void *a1, void *portrait,
    float player_x, float player_y)
{
    SceCtrlData pad;
    uint32_t prev;

    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;

    while (1) {
        render_world(
            m, char_atlas, a1, NULL,
            1, player_x, player_y, 1, 0,
            -1, 0.0f,
            portrait, dialog, 0, 0, 0
        );

        sceCtrlPeekBufferPositive(&pad, 1);
        if ((pad.Buttons & ~prev) & PSP_CTRL_CROSS) return;
        prev = pad.Buttons;
    }
}

static void run_map001_intro(
    int lang, const MapState *m, void *char_atlas,
    void *a1, void *fall_atlas, int start_x, int start_y)
{
    float player_x = ((float)start_x + 0.5f) * TILE_PX;
    float player_y = ((float)start_y + 1.0f) * TILE_PX;
    float fall_y = 0.0f;

    /* The falling event is a separate sprite.  v0.2.0 accidentally let
     * helper calls with player=(0,0) recalculate the camera, which caused
     * the visible up/down snap during the abyss fall.  Keep the Map001
     * camera fixed for the whole intro, exactly like a scripted MZ scene. */
    {
        float map_w = (float)(m->w * TILE_PX);
        float map_h = (float)(m->h * TILE_PX);
        float max_x = map_w > SCREEN_W ? map_w - SCREEN_W : 0.0f;
        float max_y = map_h > SCREEN_H ? map_h - SCREEN_H : 0.0f;
        g_camera_lock_x = max_x > 0.0f ? clamp_float(player_x - SCREEN_W * 0.5f, 0.0f, max_x) : 0.0f;
        g_camera_lock_y = max_y > 0.0f ? clamp_float(player_y - SCREEN_H * 0.5f, 0.0f, max_y) : 0.0f;
        g_camera_locked = 1;
    }
    void *portrait;
    void *dialog1;
    void *dialog2;

    wait_scene_frames(
        120, m, char_atlas, NULL, fall_atlas,
        0, player_x, player_y, 1, 0, -1, 0.0f, 255
    );

    g_picture6_visible = 1;
    g_picture6_alpha = 255;
    fade_black_scene(
        255, 0, 60, m, char_atlas,
        a1, fall_atlas, 0, player_x, player_y, -1, 0.0f
    );

    wait_scene_frames(
        40, m, char_atlas, a1, fall_atlas,
        0, player_x, player_y, 1, 0, -1, 0.0f, 0
    );

    fall_y = animate_fall_move(0, fall_y, 6, 4, m, char_atlas, a1, fall_atlas);
    play_se_async(SE_BONE_PATH);
    flash_red_scene(20, m, char_atlas, a1, fall_atlas, 0, fall_y);

    fall_y = animate_fall_move(1, fall_y, 1, 8, m, char_atlas, a1, fall_atlas);
    fall_y = animate_fall_move(2, fall_y, 1, 16, m, char_atlas, a1, fall_atlas);

    play_se_async(SE_WATER_PATH);
    fall_y = animate_fall_move(3, fall_y, 1, 64, m, char_atlas, a1, fall_atlas);

    wait_scene_frames(
        20, m, char_atlas, a1, fall_atlas,
        0, player_x, player_y, 1, 0, 3, fall_y, 0
    );

    /* Original NARAKU uses transparent, blank Show Text entries here.
     * On the PC build they do not present the player with a visible/useful
     * confirmation step.  The old PSP intro turned them into two dark X-gates,
     * producing the fake "jerk on X" pauses reported during the fall. */

    play_se_async(SE_SPLASH_PATH);
    wait_scene_frames(10, m, char_atlas, a1, fall_atlas, 0, player_x, player_y, 1, 0, 4, fall_y, 0);
    wait_scene_frames(10, m, char_atlas, a1, fall_atlas, 0, player_x, player_y, 1, 0, 5, fall_y, 0);
    wait_scene_frames(10, m, char_atlas, a1, fall_atlas, 0, player_x, player_y, 1, 0, 3, fall_y, 0);

    /* Original NARAKU uses transparent, blank Show Text entries here.
     * On the PC build they do not present the player with a visible/useful
     * confirmation step.  The old PSP intro turned them into two dark X-gates,
     * producing the fake "jerk on X" pauses reported during the fall. */

    play_se_async(SE_SPLASH_PATH);
    wait_scene_frames(10, m, char_atlas, a1, fall_atlas, 0, player_x, player_y, 1, 0, 4, fall_y, 0);
    wait_scene_frames(10, m, char_atlas, a1, fall_atlas, 0, player_x, player_y, 1, 0, 5, fall_y, 0);
    wait_scene_frames(10, m, char_atlas, a1, fall_atlas, 0, player_x, player_y, 1, 0, 3, fall_y, 0);

    fade_black_scene(
        0, 255, 50, m, char_atlas,
        a1, fall_atlas, 0, player_x, player_y, 3, fall_y
    );
    play_se_async(SE_WATER_PATH);

    wait_scene_frames(
        60, m, char_atlas, a1, fall_atlas,
        0, player_x, player_y, 1, 0, -1, 0.0f, 255
    );

    fade_black_scene(
        255, 0, 50, m, char_atlas,
        a1, NULL, 1, player_x, player_y, -1, 0.0f
    );

    portrait = load_exact_file(PORTRAIT_PATH, PIC_TEX_BYTES);
    if (!portrait) fatal_error("Could not load Enri portrait");

    dialog1 = load_exact_file(dialog_path(lang, 0), DIALOG_TEX_BYTES);
    if (!dialog1) fatal_error("Could not load first dialogue texture");
    wait_dialog(dialog1, m, char_atlas, a1, portrait, player_x, player_y);
    free(dialog1);

    dialog2 = load_exact_file(dialog_path(lang, 1), DIALOG_TEX_BYTES);
    if (!dialog2) fatal_error("Could not load second dialogue texture");
    wait_dialog(dialog2, m, char_atlas, a1, portrait, player_x, player_y);
    free(dialog2);
    free(portrait);

    g_camera_locked = 0;
    g_switches[3] = 1;
}

/* ------------------------------------------------------------------------- */
/* Runtime messages / fades                                                  */
/* ------------------------------------------------------------------------- */

static void event_texture_path(
    char *out, size_t out_size, int map_id, int event_id, int lang)
{
    snprintf(
        out, out_size,
        ASSET_ROOT "m%03d_e%03d_%s.rgba8888",
        map_id, event_id, lang_tag(lang)
    );
}

static void wait_event_message(
    int event_id, int lang,
    const MapState *m, void *char_atlas, void *a1,
    float player_x, float player_y,
    int player_pattern, int player_dir)
{
    char path[192];
    void *dialog;
    SceCtrlData pad;
    uint32_t prev;

    event_texture_path(path, sizeof(path), m->id, event_id, lang);
    dialog = load_exact_file(path, DIALOG_TEX_BYTES);
    if (!dialog) return;

    do {
        render_world(
            m, char_atlas, a1, NULL,
            g_player_visible, player_x, player_y, player_pattern, player_dir,
            -1, 0.0f, NULL, dialog, 0, 0, 0
        );
        sceCtrlPeekBufferPositive(&pad, 1);
    } while (pad.Buttons & PSP_CTRL_CROSS);

    prev = pad.Buttons;
    while (1) {
        render_world(
            m, char_atlas, a1, NULL,
            g_player_visible, player_x, player_y, player_pattern, player_dir,
            -1, 0.0f, NULL, dialog, 0, 0, 0
        );
        sceCtrlPeekBufferPositive(&pad, 1);
        if ((pad.Buttons & ~prev) & PSP_CTRL_CROSS) break;
        prev = pad.Buttons;
    }

    do {
        sceCtrlPeekBufferPositive(&pad, 1);
        sceDisplayWaitVblankStart();
    } while (pad.Buttons & PSP_CTRL_CROSS);

    free(dialog);
}

static void fade_game_world(
    const MapState *m, void *char_atlas, void *a1,
    float player_x, float player_y,
    int player_pattern, int player_dir,
    int from, int to, int frames)
{
    int i;
    for (i = 1; i <= frames; ++i) {
        int a = from + (to - from) * i / frames;
        render_world(
            m, char_atlas, a1, NULL,
            g_player_visible, player_x, player_y, player_pattern, player_dir,
            -1, 0.0f, NULL, NULL, 0, a, 0
        );
    }
}

/* ------------------------------------------------------------------------- */
/* Main                                                                      */
/* ------------------------------------------------------------------------- */

int main(int argc, char *argv[])
{
    int lang;
    int title_choice;
    ProgressState progress;
    MapState map;
    void *char_atlas;
    uint32_t boot_buttons;

    int tile_x = 0;
    int tile_y = 0;
    int target_x = 0;
    int target_y = 0;
    int direction_row = 0;
    int moving = 0;
    int move_dx = 0;
    int move_dy = 0;
    float move_progress = 0.0f;
    float current_move_speed = move_speed_px_per_frame(3);
    int current_real_move_speed = 3;
    int walk_finish_hold = 0;

    SceCtrlData pad;
    uint32_t prev_buttons = 0;

    (void)argc;
    if (argc > 0 && argv && argv[0]) {
        const char *slash = strrchr(argv[0], '/');
        if (slash && (size_t)(slash - argv[0]) < sizeof(g_scene_trace_path) - 32) {
            size_t n = (size_t)(slash - argv[0]) + 1;
            memcpy(g_scene_trace_path, argv[0], n);
            strcpy(g_scene_trace_path + n, "assets/scene_trace.log");
        }
    }
    scene_trace(0,0,0,109);
    (void)argv;

    memset(&map, 0, sizeof(map));
    reset_runtime_game_state();

    setup_callbacks();
    sceCtrlSetSamplingCycle(0);
    sceCtrlSetSamplingMode(PSP_CTRL_MODE_ANALOG);

    boot_buttons = read_boot_hotkeys();

    /* SELECT at boot remains only as an emergency language fallback.  The
     * normal language control now lives in NARAKU's Options scene.  The old
     * TRIANGLE "delete progress" shortcut is intentionally gone: the PC game
     * has no equivalent and 0.6.0 uses explicit save slots. */
    lang = load_saved_language();
    if (lang < 0) {
        /* Fresh installs start in English.  Language selection is an Option,
         * not a mandatory first-boot wizard in the PSP port. */
        g_language = 0;
        save_config();
        lang = 0;
    }
    if (boot_buttons & PSP_CTRL_SELECT)
        lang = choose_language(lang);
    g_language = lang;

    char_atlas = load_exact_file(CHAR_ATLAS_PATH, CHAR_ATLAS_BYTES);
    if (!char_atlas) fatal_error("Could not load enri_atlas.rgba8888");
    g_ui_char_atlas = char_atlas;

    g_a1_overlay = load_exact_file(A1_PATH, PIC_TEX_BYTES);
    if (!g_a1_overlay) fatal_error("Could not load a1_overlay.rgba8888");
    g_fog_overlay = load_exact_file(FOG_A1_PATH, FOG_A1_BYTES);
    if (!g_fog_overlay) fatal_error("Could not load fog_a1.rgba8888");
    g_key_anim = load_exact_file(KEY_ANIM_PATH, KEY_ANIM_BYTES);
    if (!g_key_anim) fatal_error("Could not load key_anim.rgba8888");
    g_lucas_fall_atlas = load_exact_file(LUCAS_FALL_ATLAS_PATH, LUCAS_FALL_ATLAS_BYTES);
    if (!g_lucas_fall_atlas) fatal_error("Could not load lucas_fall_atlas.rgba8888");
    g_lucas_corpse = load_exact_file(LUCAS_CORPSE_PATH, LUCAS_CORPSE_TEX_BYTES);
    if (!g_lucas_corpse) fatal_error("Could not load lucas_corpse.rgba8888");

    init_gu();
    if (!init_runtime_font())
        fatal_error("Could not load v0.7.9 runtime font assets");
    if (!init_ui_data())
        fatal_error("Could not load v0.7.9 UI assets");
    load_common_vm();
    set_bgm_track(TITLE_BGM_PATH);
    start_bgm();

TITLE_ENTRY:
    g_request_title = 0;
    g_loaded_from_scene = 0;
    moving = 0;
    move_progress = 0.0f;
    player_animation_reset(&g_player_animation);

    title_choice = ui_title_scene(&progress);
    lang = g_language;

    if (title_choice == 0) {
        /* Shutdown is a real terminal title command.  Stop audio first, give
         * the confirmation SE a moment to reach the mixer, then ask PSP/PPSSPP
         * to terminate the game.  Most importantly, never continue into the
         * save-load path with an uninitialised ProgressState. */
        g_audio_stop = 1;
        sceKernelDelayThread(120000);
        sceKernelExitGame();
        return 0;
    }

    if (title_choice == 1) {
        const int start_x = 12;
        const int start_y = 9;

        reset_runtime_game_state();
        /* System.json has optTransparent=true.  The original starts Map001
         * with the real Player hidden and uses Event 5 as the falling Enri
         * sprite; command211[1] restores the Player near the end of the intro. */
        g_player_visible = 0;
        if (!load_map(&map, 1))
            fatal_error("Could not load Map001 v0.7.9 assets");

        /* 0.6.9 no longer re-enacts the opening in hand-written C.  The real
         * Map001 autorun is now executed by the VM together with its switch
         * driven event sprites, so the fall, pauses and post-fall pose follow
         * the original event data instead of a second approximation. */
        g_player_move_speed_code = 3;
        progress.map_id = 1;
        progress.tile_x = start_x;
        progress.tile_y = start_y;
        progress.direction_row = 0;
        progress.intro_done = 0;
    } else {
        /* ui_title_scene() has already restored switches/variables/items and
         * player state from the selected manual slot. */
        if (!load_map(&map, progress.map_id))
            fatal_error("Could not load selected save map assets");
    }

    tile_x = progress.tile_x;
    tile_y = progress.tile_y;
    direction_row = progress.direction_row;
    if (tile_x < 0 || tile_x >= map.w || tile_y < 0 || tile_y >= map.h) {
        tile_x = 0;
        tile_y = 0;
    }

    vm_run_autoruns(&map, char_atlas, lang, &tile_x, &tile_y, &direction_row);
    lang = g_language;
    if (g_request_title) goto TITLE_ENTRY;
    g_loaded_from_scene = 0;

    target_x = tile_x;
    target_y = tile_y;
    moving = 0;
    move_dx = 0;
    move_dy = 0;
    move_progress = 0.0f;

    sceCtrlPeekBufferPositive(&pad, 1);
    prev_buttons = pad.Buttons;

    while (1) {
        uint32_t pressed;
        walk_finish_hold = 0;
        sceCtrlPeekBufferPositive(&pad, 1);
        pressed = pad.Buttons & ~prev_buttons;

        vm_tick_story_parallel(&map);

        if (!moving && !g_player_route.records) {
            uint8_t mask = pass_mask_at(&map, tile_x, tile_y);
            int bit = 0;
            int dx = 0;
            int dy = 0;
            int row = direction_row;

            if (pad.Buttons & PSP_CTRL_DOWN) {
                bit = 0x01; dy = 1; row = 0;
            } else if (pad.Buttons & PSP_CTRL_LEFT) {
                bit = 0x02; dx = -1; row = 1;
            } else if (pad.Buttons & PSP_CTRL_RIGHT) {
                bit = 0x04; dx = 1; row = 2;
            } else if (pad.Buttons & PSP_CTRL_UP) {
                bit = 0x08; dy = -1; row = 3;
            }

            if (bit != 0) {
                int nx = tile_x + dx;
                int ny = tile_y + dy;
                if (!g_player_direction_fix) direction_row = row;

                {
                    int inside = (nx >= 0 && ny >= 0 && nx < map.w && ny < map.h);
                    int reverse_bit = bit == 0x01 ? 0x08 :
                                      bit == 0x08 ? 0x01 :
                                      bit == 0x02 ? 0x04 : 0x02;
                    uint8_t target_mask = inside ? pass_mask_at(&map, nx, ny) : 0;
                    int can_enter = inside && (
                        g_player_through ||
                        ((mask & bit) && (target_mask & reverse_bit) &&
                         !vm_event_blocks_at(&map, nx, ny))
                    );

                    if (inside && is_chase_map(map.id) && !g_s003_paused &&
                        vm_run_event_at(&map,nx,ny,2,char_atlas,lang,&tile_x,&tile_y,&direction_row)) {
                        moving=0; move_progress=0; target_x=tile_x; target_y=tile_y;
                        vm_run_autoruns(&map,char_atlas,lang,&tile_x,&tile_y,&direction_row);
                        if(g_request_title) goto TITLE_ENTRY;
                        continue;
                    }
                    if (inside && !can_enter &&
                        vm_run_event_at(&map,nx,ny,-1,char_atlas,lang,&tile_x,&tile_y,&direction_row)) {
                        moving=0; move_progress=0; target_x=tile_x; target_y=tile_y;
                        vm_run_autoruns(&map,char_atlas,lang,&tile_x,&tile_y,&direction_row);
                        if(g_request_title) goto TITLE_ENTRY;
                        continue;
                    }
                    if (can_enter) {
                        int dash_button = (pad.Buttons & PSP_CTRL_RTRIGGER) != 0;
                        int dashing = g_always_dash ? !dash_button : dash_button;
                        target_x = nx;
                        target_y = ny;
                        move_dx = dx;
                        move_dy = dy;
                        move_progress = 0.0f;
                        current_real_move_speed = player_real_move_speed(dashing);
                        current_move_speed = move_speed_px_per_frame(current_real_move_speed);
                        moving = 1;
                    }
                }
            }

            /* MenuCallCommon is active in the original project.  The RPG Maker
             * cancel/menu input invokes Common Event 1, whose real command list
             * plays 【魔王魂】-SE1 and pushes Scene_Item. */
            if (!moving && !g_player_route.records && (pressed & ui_cancel_mask())) {
                VmEventRecord menu_event;
                memset(&menu_event, 0, sizeof(menu_event));
                /* Capture before Common Event 1 can show its menu pictures.
                 * Every menu opening takes a fresh snapshot of this location. */
                free(g_menu_world_backdrop);
                g_menu_world_backdrop = ui_inventory_backdrop();
                vm_call_common(
                    &map, &menu_event, 1, char_atlas, lang,
                    &tile_x, &tile_y, &direction_row
                );
                free(g_menu_world_backdrop);
                g_menu_world_backdrop = NULL;
                lang = g_language;
                if (g_request_title) goto TITLE_ENTRY;
                if (g_loaded_from_scene) {
                    g_loaded_from_scene = 0;
                    vm_run_autoruns(&map, char_atlas, lang, &tile_x, &tile_y, &direction_row);
                    lang = g_language;
                    if (g_request_title) goto TITLE_ENTRY;
                }
                target_x = tile_x;
                target_y = tile_y;
                sceCtrlPeekBufferPositive(&pad, 1);
                prev_buttons = pad.Buttons;
                continue;
            } else if (!moving && !g_player_route.records && (pressed & ui_ok_mask())) {
                int fx = tile_x;
                int fy = tile_y;
                int vm_result;
                uint16_t event_id;

                /* RPG Maker checks the current cell for below-character action
                 * events, then the cell in front of the player. */
                vm_result = vm_run_event_at(
                    &map, fx, fy, -2, char_atlas, lang,
                    &tile_x, &tile_y, &direction_row
                );

                if (!vm_result) {
                    if (direction_row == 0) fy++;
                    else if (direction_row == 1) fx--;
                    else if (direction_row == 2) fx++;
                    else if (direction_row == 3) fy--;
                    vm_result = vm_run_event_at(
                        &map, fx, fy, -3, char_atlas, lang,
                        &tile_x, &tile_y, &direction_row
                    );
                }

                lang = g_language;
                if (g_request_title) goto TITLE_ENTRY;

                if (vm_result) {
                    target_x = tile_x;
                    target_y = tile_y;
                    g_loaded_from_scene = 0;
                    vm_run_autoruns(&map, char_atlas, lang, &tile_x, &tile_y, &direction_row);
                    lang = g_language;
                    if (g_request_title) goto TITLE_ENTRY;
                    target_x = tile_x;
                    target_y = tile_y;
                    sceCtrlPeekBufferPositive(&pad, 1);
                    prev_buttons = pad.Buttons;
                    continue;
                }

                /* Compatibility fallback for the early pre-rendered simple
                 * text events.  It can be removed after all equivalent pages
                 * are handled by the VM. */
                fx = tile_x;
                fy = tile_y;
                event_id = action_event_at(&map, fx, fy);

                if (!event_id) {
                    if (direction_row == 0) fy++;
                    else if (direction_row == 1) fx--;
                    else if (direction_row == 2) fx++;
                    else if (direction_row == 3) fy--;
                    event_id = action_event_at(&map, fx, fy);
                }

                if (event_id) {
                    float world_x = ((float)tile_x + 0.5f) * TILE_PX;
                    float world_y = ((float)tile_y + 1.0f) * TILE_PX;
                    wait_event_message(
                        event_id, lang, &map, char_atlas, NULL,
                        world_x, world_y, 1, direction_row
                    );
                    sceCtrlPeekBufferPositive(&pad, 1);
                    prev_buttons = pad.Buttons;
                    continue;
                }
            }
        }

        if (moving) {
            move_progress += current_move_speed;

            if (move_progress >= TILE_PX) {
                uint8_t transfer_index;
                tile_x = target_x;
                tile_y = target_y;
                move_progress = 0.0f;
                moving = 0;
                /* Keep the current walk cel for the tile-arrival frame.
                 * Older builds snapped to the standing cel for one frame at
                 * every tile boundary, which made held movement look jerky. */
                walk_finish_hold = 1;

                {
                    unsigned int frames_before_touch = g_world_render_frames;
                    int map_before_touch = map.id;
                    int vm_touch = vm_run_event_at(
                        &map, tile_x, tile_y, 1, char_atlas, lang,
                        &tile_x, &tile_y, &direction_row
                    );
                    if (!vm_touch) {
                        vm_touch = vm_run_event_at(
                            &map, tile_x, tile_y, 2, char_atlas, lang,
                            &tile_x, &tile_y, &direction_row
                        );
                    }
                    lang = g_language;
                    if (g_request_title) goto TITLE_ENTRY;
                    if (vm_touch) {
                        target_x = tile_x;
                        target_y = tile_y;
                        g_loaded_from_scene = 0;
                        vm_run_autoruns(&map, char_atlas, lang, &tile_x, &tile_y, &direction_row);
                        lang = g_language;
                        if (g_request_title) goto TITLE_ENTRY;
                        target_x = tile_x;
                        target_y = tile_y;
                        if (map.id != map_before_touch)
                            player_animation_reset(&g_player_animation);
                        /* Instant floor/speed/SE events must still present the
                         * tile-arrival frame. A modal event already rendered it. */
                        if (g_world_render_frames == frames_before_touch) {
                            g_player_animation_speed = current_real_move_speed;
                            g_player_animation_jumping = 1; /* stop count still zero */
                            render_world(&map, char_atlas, NULL, NULL,
                                g_player_visible, (tile_x + 0.5f) * TILE_PX,
                                (tile_y + 1.0f) * TILE_PX, 1, direction_row,
                                -1, 0.0f, NULL, NULL, 0, 0, 0);
                        }
                        sceCtrlPeekBufferPositive(&pad, 1);
                        prev_buttons = pad.Buttons;
                        continue;
                    }
                }

                transfer_index = vm_cell_owns_transfer(&map, tile_x, tile_y)
                    ? 0 : transfer_index_at(&map, tile_x, tile_y);
                if (transfer_index) {
                    TransferRecord tr;
                    if (read_transfer_record(&map, transfer_index, &tr)) {
                        float old_x = ((float)tile_x + 0.5f) * TILE_PX;
                        float old_y = ((float)tile_y + 1.0f) * TILE_PX;
                        int k;

                        if (tr.flags & 0x01)
                            play_se_async(SE_SPLASH_PATH);

                        if (tr.dest_map < 1 || tr.dest_map > MAX_MAP_ID) {
                            char msg[128];
                            snprintf(
                                msg, sizeof(msg),
                                "Map %03d could not be loaded by v0.7.9.",
                                tr.dest_map
                            );
                            fatal_error(msg);
                        }

                        fade_game_world(
                            &map, char_atlas, NULL,
                            old_x, old_y, 1, direction_row,
                            0, 255, 10
                        );

                        for (k = 0; k < 5; ++k) {
                            if (tr.switch_id[k] > 0 && tr.switch_id[k] < MAX_SWITCHES)
                                g_switches[tr.switch_id[k]] = (uint8_t)tr.switch_value[k];
                        }

                        if (!load_map(&map, tr.dest_map))
                            fatal_error("Transfer destination assets could not be loaded");

                        tile_x = tr.dest_x;
                        tile_y = tr.dest_y;
                        target_x = tile_x;
                        target_y = tile_y;

                        {
                            int new_row = direction_to_row(tr.direction);
                            if (new_row >= 0) direction_row = new_row;
                        }

                        {
                            float new_x = ((float)tile_x + 0.5f) * TILE_PX;
                            float new_y = ((float)tile_y + 1.0f) * TILE_PX;
                            fade_game_world(
                                &map, char_atlas, NULL,
                                new_x, new_y, 1, direction_row,
                                255, 0, 10
                            );
                        }

                        vm_run_autoruns(&map, char_atlas, lang, &tile_x, &tile_y, &direction_row);
                        lang = g_language;
                        if (g_request_title) goto TITLE_ENTRY;
                        g_loaded_from_scene = 0;
                        target_x = tile_x;
                        target_y = tile_y;
                        player_animation_reset(&g_player_animation);

                        sceCtrlPeekBufferPositive(&pad, 1);
                        prev_buttons = pad.Buttons;
                        continue;
                    }
                }
            }
        }

        if (is_chase_map(map.id) && !g_s003_paused) {
            int contact = vm_run_event_at(&map,tile_x,tile_y,2,char_atlas,lang,
                                          &tile_x,&tile_y,&direction_row);
            if (!contact && moving)
                contact=vm_run_event_at(&map,target_x,target_y,2,char_atlas,lang,
                                       &tile_x,&tile_y,&direction_row);
            if (contact) {
                moving=0; move_progress=0;
                target_x=tile_x; target_y=tile_y;
                vm_run_autoruns(&map,char_atlas,lang,&tile_x,&tile_y,&direction_row);
                if (g_request_title) goto TITLE_ENTRY;
                continue;
            }
        }

        {
            float world_x = ((float)tile_x + 0.5f) * TILE_PX;
            float world_y = ((float)tile_y + 1.0f) * TILE_PX;
            int pattern;

            if (moving) {
                world_x += move_dx * move_progress;
                world_y += move_dy * move_progress;
            }

            pattern = 1; /* render_world owns the persistent animation phase. */
            g_player_animation_moving = moving;
            g_player_animation_jumping = walk_finish_hold;
            g_player_animation_speed = (moving || walk_finish_hold)
                ? current_real_move_speed : clamp_move_speed_code(g_player_move_speed_code);

            render_world(
                &map, char_atlas, NULL, NULL,
                g_player_visible, world_x, world_y, pattern, direction_row,
                -1, 0.0f, NULL, NULL, 0, 0, 0
            );
        }

        prev_buttons = pad.Buttons;
    }

    return 0;
}

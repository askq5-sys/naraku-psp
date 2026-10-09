/* Inventory implementation included after shared UI/font helpers. */
static void ui_draw_icon(int icon_index, float x, float y, float size)
{
    int sx, sy;
    if (!g_ui.iconset || icon_index < 0) return;
    sx = (icon_index % 16) * 32;
    sy = (icon_index / 16) * 32;
    if (sy >= 512) return;
    sceGuTexMode(GU_PSM_4444, 0, 0, GU_FALSE);
    sceGuTexImage(0, 512, 512, 512, g_ui.iconset);
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
    draw_bound_rect((float)sx, (float)sy, 32.0f, 32.0f, x, y, size, size);
}

typedef struct {
    const char *name, *desc;
    size_t name_len, desc_len;
    int icon, quantity;
} InventoryEntry;

typedef struct {
    InventoryEntry entries[2][MAX_ITEMS];
    int count[2];
} InventorySnapshot;

/* The scene pauses the VM and cannot use items or change language. Build both
 * categories once; all borrowed strings remain valid until the scene closes. */
static void ui_inventory_snapshot(InventorySnapshot *snapshot)
{
    int id;
    memset(snapshot, 0, sizeof(*snapshot));
    for (id = 1; id < g_ui.item_count && id < MAX_ITEMS; ++id) {
        InventoryEntry entry;
        int type, occasion, category;
        if (g_items[id] <= 0) continue;
        if (!ui_item_text(id, g_language, &entry.name, &entry.name_len,
            &entry.desc, &entry.desc_len, &entry.icon, &type, &occasion)) continue;
        if (type != 1 && type != 2) continue;
        category = type - 1;
        entry.quantity = g_items[id];
        snapshot->entries[category][snapshot->count[category]++] = entry;
    }
}

/* Compact inventory labels retain the full glyph cell (including descenders).
 * Fit long note titles into a column; do not truncate UTF-8 or color escapes. */
static void ui_inventory_name(const char *text, size_t len, float x, float y, float width)
{
    const char *p = text, *end = text + len;
    int total = 0, color = 0;
    float scale;
    while (p < end) {
        const uint8_t *rec;
        if (parse_text_color_escape(&p, end, &color)) continue;
        rec = font_find_glyph(utf8_next_cp(&p, end));
        if (rec) total += rec[7];
    }
    scale = 0.75f;
    if (total > 0 && total * scale > width) scale = width / total;
    /* y is the row top: center the complete scaled glyph cell vertically. */
    y += (32.0f - FONT_CELL_H * scale) * 0.5f;
    p = text; color = 0;
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
            x, y, adv * scale, FONT_CELL_H * scale, tint);
        x += adv * scale;
    }
    sceGuTexFunc(GU_TFX_REPLACE, GU_TCC_RGBA);
    sceGuTexFilter(GU_NEAREST, GU_NEAREST);
}

static uint32_t *g_menu_world_backdrop = NULL;

/* Snapshot the displayed world once: box downsampling gives the inventory
 * background its blur without rendering/ticking gameplay while paused. */
static uint32_t *ui_inventory_backdrop(void)
{
    int stride = BUF_W, x, y, dx, dy;
    uint32_t *texture, *readback;
    volatile const uint32_t *source;
    sceGuSync(0, 0);
    if (!g_last_world_buffer_valid) return NULL;
    texture = memalign(16, 256 * 256 * sizeof(uint32_t));
    if (!texture) return NULL;
    memset(texture, 0, 256 * 256 * sizeof(uint32_t));
    readback = memalign(16, BUF_W * SCREEN_H * sizeof(uint32_t));
    if (!readback) { free(texture); return NULL; }
    /* In buffered emulation the rendered color buffer can live on the host
     * GPU, while direct CPU VRAM reads still contain the old title pixels.
     * A GE transfer to RAM makes the framebuffer readback explicit. */
    sceKernelDcacheWritebackInvalidateAll();
    sceGuStart(GU_DIRECT, gu_list);
    sceGuCopyImage(GU_PSM_8888, 0, 0, SCREEN_W, SCREEN_H, BUF_W,
        (void *)(0x04000000u | (uintptr_t)g_last_world_buffer),
        0, 0, BUF_W, readback);
    sceGuFinish();
    sceGuSync(0, 0);
    source = (volatile const uint32_t *)((uintptr_t)readback | 0x40000000u);
    for (y = 0; y < 136; ++y) for (x = 0; x < 240; ++x) {
        unsigned r = 0, g = 0, b = 0;
        for (dy = 0; dy < 2; ++dy) for (dx = 0; dx < 2; ++dx) {
            uint32_t c = source[(y * 2 + dy) * stride + x * 2 + dx];
            r += c & 255; g += (c >> 8) & 255; b += (c >> 16) & 255;
        }
        texture[y * 256 + x] = 0xff000000u | (r / 4) |
            ((g / 4) << 8) | ((b / 4) << 16);
    }
    free(readback);
    sceKernelDcacheWritebackAll();
    return texture;
}

static void ui_inventory_scene(void)
{
    SceCtrlData pad;
    uint32_t prev;
    int category = 0, cursor = 0, scroll = 0, in_list = 0, running = 1;
    InventorySnapshot snapshot;
    int owns_backdrop = g_menu_world_backdrop == NULL;
    uint32_t *backdrop = owns_backdrop ? ui_inventory_backdrop() : g_menu_world_backdrop;
    ui_inventory_snapshot(&snapshot);
    sceCtrlPeekBufferPositive(&pad, 1);
    prev = pad.Buttons;
    while (running) {
        const InventoryEntry *entries = snapshot.entries[category];
        int count = snapshot.count[category];
        int i;
        if (cursor >= count) cursor = count > 0 ? count - 1 : 0;
        if (cursor < 0) cursor = 0;
        if (cursor < scroll) scroll = (cursor / 2) * 2;
        if (cursor >= scroll + 8) scroll = (cursor / 2 - 3) * 2;
        ui_frame_begin();
        if (backdrop) {
            sceGuTexFlush();
            draw_texture_alpha(backdrop, 256, 256, 240, 136,
                               0, 0, SCREEN_W, SCREEN_H, 192);
        }
        /* Original Scene_MenuBase backdrop opacity and OptionEx window opacity. */
        draw_naraku_window(4, 8, 472, 44, g_window_opacity);
        draw_solid_rect(category ? 240 : 12, 15, 224, 29, 160, 0, 0, 150);
        ui_draw_label(UI_L_ITEMS, 22, 15.5f, 230, 1);
        ui_draw_label(UI_L_KEY_ITEMS, 250, 15.5f, 464, 1);
        draw_naraku_window(4, 56, 472, 144, g_window_opacity);
        if (!count) ui_draw_label(UI_L_EMPTY, 18, 70, 462, 1);
        for (i = 0; i < 8 && scroll + i < count; ++i) {
            const InventoryEntry *entry = &entries[scroll + i];
            float x = 12 + (i % 2) * 232, y = 63 + (i / 2) * 33;
            char qty[24];
            if (in_list && scroll + i == cursor)
                draw_solid_rect(x, y, 224, 32, 160, 0, 0, 150);
            ui_draw_icon(entry->icon, x + 3, y + 7, 18);
            ui_inventory_name(entry->name, entry->name_len, x + 25, y, category ? 195 : 158);
            if (!category) {
                snprintf(qty, sizeof(qty), ":%d", entry->quantity);
                ui_inventory_name(qty, strlen(qty), x + 185, y, 38);
            }
        }
        draw_naraku_window(4, 204, 472, 64, g_window_opacity);
        if (in_list && count > 0) {
            const InventoryEntry *entry = &entries[cursor];
            if (entry->desc_len > 0)
                draw_utf8_wrapped(entry->desc, entry->desc_len, 14, 211, 464, 2);
        }
        ui_frame_end();
        sceCtrlPeekBufferPositive(&pad, 1);
        {
            uint32_t pressed = pad.Buttons & ~prev;
            int old_cursor = cursor, old_category = category;
            if (pressed & ui_cancel_mask()) {
                if (in_list) in_list = 0;
                else running = 0;
                play_se_async(SE_UI_CANCEL_PATH);
            } else if (!in_list) {
                if (pressed & (PSP_CTRL_LEFT | PSP_CTRL_RIGHT |
                               PSP_CTRL_LTRIGGER | PSP_CTRL_RTRIGGER)) {
                    category ^= 1; cursor = scroll = 0;
                }
                if ((pressed & ui_ok_mask()) && count > 0) {
                    in_list = 1;
                    play_se_async(SE_UI_CURSOR_PATH);
                }
            } else {
                if ((pressed & PSP_CTRL_LEFT) && cursor % 2) --cursor;
                if ((pressed & PSP_CTRL_RIGHT) && !(cursor % 2) && cursor + 1 < count) ++cursor;
                if ((pressed & PSP_CTRL_UP) && cursor >= 2) cursor -= 2;
                if ((pressed & PSP_CTRL_DOWN) && cursor + 2 < count) cursor += 2;
            }
            if (cursor != old_cursor || category != old_category)
                play_se_async(SE_UI_CURSOR_PATH);
        }
        prev = pad.Buttons;
    }
    if (owns_backdrop) free(backdrop);
}


static int ui_collect_owned_items(int category, int *ids, int max_ids)
{
    int id, count = 0;
    int wanted_type = category == 0 ? 1 : 2;
    for (id = 1; id < g_ui.item_count && id < MAX_ITEMS; ++id) {
        int icon, itype, occasion;
        const char *n, *d;
        size_t nl, dl;
        if (g_items[id] <= 0) continue;
        if (!ui_item_text(id, g_language, &n, &nl, &d, &dl, &icon, &itype, &occasion)) continue;
        if (itype != wanted_type) continue;
        if (count < max_ids) ids[count++] = id;
    }
    return count;
}

/* Compact inventory labels: end of original collector reference. */

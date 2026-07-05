"""
================= PLAYLIST =================
مدیریت پلی‌لیست‌ها: افزودن/حذف آهنگ، کارت‌های UI، درگ‌اند‌دراپ و
ساخت/حذف/تغییرنام پلی‌لیست.
"""

import os

import customtkinter as ctk
from tkinter import filedialog, simpledialog

from state import state
from theme import colors
from animations import animate_color
from settings_manager import save_settings
from i18n import t


def switch_playlist(name):
    state.current_playlist = name
    state.current_index = None
    state._last_highlighted_index = None

    for c, _ in state.cards:
        c.destroy()

    state.cards.clear()

    for song in state.playlists[state.current_playlist]:
        if os.path.exists(song):
            # فقط UI بساز بدون append دوباره
            add_song_ui_only(song)

    save_settings()


def add_song_ui_only(path):
    from audio_engine import play

    c = colors()

    card = ctk.CTkFrame(
        state.playlist_frame,
        fg_color=c["card"],
        corner_radius=16,
        height=72,
        border_width=0,
    )
    card.pack(fill="x", pady=6, padx=15)
    card.pack_propagate(False)

    icon = ctk.CTkLabel(
        card,
        text="🎵",
        font=("Segoe UI", 16),
        width=42,
        height=42,
        corner_radius=12,
        fg_color=c.get("hover", c["card"]),
        text_color=c["text"],
    )
    icon.place(x=16, rely=0.5, anchor="w")

    text_col = ctk.CTkFrame(card, fg_color="transparent")
    text_col.place(x=72, rely=0.5, anchor="w")

    title = ctk.CTkLabel(
        text_col,
        text=os.path.splitext(os.path.basename(path))[0],
        font=("Segoe UI", 14, "bold"),
        text_color=c["text"],
        anchor="w",
    )
    title.pack(anchor="w")

    subtitle = ctk.CTkLabel(
        text_col,
        text=t("local_audio_file"),
        font=("Segoe UI", 11),
        text_color=c.get("subtext", c["text"]),
        anchor="w",
    )
    subtitle.pack(anchor="w")

    card.bind("<Button-1>", lambda e, p=path: play(state.playlists[state.current_playlist].index(p)))
    card.bind("<ButtonPress-3>", lambda e, p=path: start_song_drag(p))

    card.bind("<Enter>", lambda e: animate_color(card, colors()["card"], colors()["hover"]))
    card.bind("<Leave>", lambda e: animate_color(card, colors()["hover"], colors()["card"]))

    state.cards.append((card, title))
    card.icon_label = icon
    card.subtitle_label = subtitle

    if state.show_delete_buttons:
        delete_btn = ctk.CTkButton(
            card,
            text="✖",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            text_color=c.get("subtext", c["text"]),
            hover_color=c.get("danger", "#ff5c7a"),
            command=lambda p=path: remove_song(state.playlists[state.current_playlist].index(p)),
        )
        delete_btn.place(relx=1.0, x=-16, rely=0.5, anchor="e")
        card.delete_btn = delete_btn


def remove_song(index):
    if index >= len(state.playlists[state.current_playlist]):
        return

    if state.current_index == index:
        state.player.stop()
        state.current_index = None
    elif state.current_index is not None and index < state.current_index:
        state.current_index -= 1

    state.playlists[state.current_playlist].pop(index)

    card, _ = state.cards.pop(index)
    card.destroy()
    state._last_highlighted_index = None

    save_settings()


def start_song_drag(path):
    state.dragged_song = path


def add_song(path):
    if path in state.playlists[state.current_playlist]:
        return

    state.playlists[state.current_playlist].append(path)
    add_song_ui_only(path)
    save_settings()


def highlight_active(force_full=False):
    c = colors()
    cur_idx = state.current_index if state.is_playing else None
    prev_idx = getattr(state, "_last_highlighted_index", None)

    def _paint(i):
        if i < 0 or i >= len(state.cards):
            return
        card, title = state.cards[i]
        icon = getattr(card, "icon_label", None)
        subtitle = getattr(card, "subtitle_label", None)

        if i == cur_idx:
            title.configure(text_color=c["accent"])
            card.configure(fg_color=c["hover"])
            if icon:
                icon.configure(fg_color=c["accent"], text_color="#ffffff", text="♫")
            if subtitle:
                subtitle.configure(text=t("status_playing"))
        else:
            title.configure(text_color=c["text"])
            card.configure(fg_color=c["card"])
            if icon:
                icon.configure(fg_color=c.get("hover", c["card"]), text_color=c["text"], text="🎵")
            if subtitle:
                subtitle.configure(text=t("local_audio_file"))

    if force_full:
        # وقتی کل تم/پس‌زمینه عوض شده، رنگ همه‌ی کارت‌ها باید به‌روز بشه
        for i in range(len(state.cards)):
            _paint(i)
    else:
        # حالت سریع: فقط کارتی که قبلاً هایلایت بود و کارتی که الان هایلایته
        # رو آپدیت می‌کنه، نه کل پلی‌لیست رو - این همون چیزیه که باعث می‌شد
        # دکمه‌های پخش/بعدی/قبلی روی پلی‌لیست‌های بزرگ لگ داشته باشن (چون هر
        # کلیک، رنگ صدها کارت رو دوباره تنظیم می‌کرد، نه فقط یکی/دوتا).
        for i in {prev_idx, cur_idx}:
            if i is not None:
                _paint(i)

    state._last_highlighted_index = cur_idx


# ================= LOAD =================

def load_music():
    files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
    for f in files:
        add_song(f)


def drop(event):
    files = state.app.tk.splitlist(event.data)

    for file in files:
        file = file.strip("{}")
        if file.lower().endswith(".mp3"):
            add_song(file)


def drop_on_playlist(event):
    if not state.dragged_song:
        return

    target_playlist = state.playlist_selector.get()

    if target_playlist == state.current_playlist:
        state.dragged_song = None
        return

    if state.dragged_song in state.playlists[state.current_playlist]:
        state.playlists[state.current_playlist].remove(state.dragged_song)

        if state.dragged_song not in state.playlists[target_playlist]:
            state.playlists[target_playlist].append(state.dragged_song)

        switch_playlist(state.current_playlist)
        save_settings()

    state.dragged_song = None


def toggle_delete_buttons(new_state):
    state.show_delete_buttons = new_state
    c = colors()

    # بازسازی تمام دکمه‌های حذف در playlist
    for i, (card, title) in enumerate(state.cards):
        # اگر قبلاً دکمه حذف ساخته نشده، بساز
        existing_btn = getattr(card, "delete_btn", None)
        if existing_btn:
            existing_btn.destroy()
            delattr(card, "delete_btn")

        if state.show_delete_buttons:
            path = state.playlists[state.current_playlist][i]
            delete_btn = ctk.CTkButton(
                card,
                text="✖",
                width=30,
                height=30,
                corner_radius=15,
                fg_color="transparent",
                text_color=c.get("subtext", c["text"]),
                hover_color=c.get("danger", "#ff5c7a"),
                command=lambda p=path: remove_song(state.playlists[state.current_playlist].index(p)),
            )
            delete_btn.place(relx=1.0, x=-16, rely=0.5, anchor="e")
            card.delete_btn = delete_btn

    save_settings()


def fix_playlist_height(event=None):
    total_height = state.app.winfo_height()
    player_height = state.player_bar.winfo_height()

    new_height = total_height - player_height - 30  # 30 فاصله بالا

    if new_height > 100:
        state.playlist_frame.configure(height=new_height)


# ================= PLAYLIST CRUD =================

def create_playlist():
    name = f"{t('playlist_prefix')} {len(state.playlists) + 1}"
    state.playlists[name] = []
    state.playlist_selector.configure(values=list(state.playlists.keys()))
    state.playlist_selector.set(name)
    switch_playlist(name)
    save_settings()


def delete_playlist():
    if state.current_playlist == "Default":
        return  # اجازه حذف Default رو نمیدیم

    state.playlists.pop(state.current_playlist)

    # رفتن به اولین پلی لیست موجود
    state.current_playlist = list(state.playlists.keys())[0]
    state.current_index = None

    state.playlist_selector.configure(values=list(state.playlists.keys()))
    state.playlist_selector.set(state.current_playlist)

    switch_playlist(state.current_playlist)
    save_settings()


def rename_playlist():
    if state.current_playlist == "Default":
        return

    new_name = simpledialog.askstring(t("rename_dialog_title"), t("rename_dialog_prompt"))

    if not new_name or new_name in state.playlists:
        return

    state.playlists[new_name] = state.playlists.pop(state.current_playlist)
    state.current_playlist = new_name

    state.playlist_selector.configure(values=list(state.playlists.keys()))
    state.playlist_selector.set(new_name)

    save_settings()


def refresh_cards_language():
    """بعد از تغییر زبان، زیرنویس کارت‌های پلی‌لیست رو به‌روز می‌کنه."""
    for i, (card, _title) in enumerate(state.cards):
        subtitle = getattr(card, "subtitle_label", None)
        if not subtitle:
            continue
        if i == state.current_index and state.is_playing:
            subtitle.configure(text=t("status_playing"))
        else:
            subtitle.configure(text=t("local_audio_file"))

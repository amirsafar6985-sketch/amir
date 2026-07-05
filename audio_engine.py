"""
================= AUDIO =================
پخش، توقف، ادامه، آهنگ بعدی/قبلی، اکولایزر VLC و مدیریت اسلایدر پیشرفت.
"""

import os
import threading
import time
import random

import vlc

from state import state
from constants import EQ_PRESETS
from utils import safe_ui, format_time  # noqa: F401 (format_time برای بقیه ماژول‌ها هم اکسپورت میشه)


def play_thread(path, start_pos=0):
    try:
        media = state.vlc_instance.media_new(path)
        state.player.set_media(media)
        state.player.play()

        time.sleep(0.3)

        if start_pos > 0:
            state.player.set_time(int(start_pos * 1000))

        state.song_length = state.player.get_length() // 1000
        state.is_playing = True

        safe_ui(lambda: state.progress.configure(to=state.song_length))
        safe_ui(lambda: state.total_time_label.configure(text=format_time(state.song_length)))
        safe_ui(lambda: state.now_playing_label.configure(text=os.path.basename(path)))
        safe_ui(update_play_button)
        safe_ui(apply_vlc_equalizer)
        safe_ui(highlight_active_safe)

    except Exception as e:
        print("VLC Error:", e)


def highlight_active_safe():
    from playlist_manager import highlight_active
    highlight_active()


def play(index=None, start_pos=0):
    if not state.playlists[state.current_playlist]:
        return
    if index is not None:
        state.current_index = index

    threading.Thread(
        target=play_thread,
        args=(state.playlists[state.current_playlist][state.current_index], start_pos),
        daemon=True,
    ).start()

    highlight_active_safe()


def pause():
    state.player.pause()
    state.is_playing = False
    update_play_button()


def resume():
    state.player.play()
    state.is_playing = True
    update_play_button()


def next_song(auto=False):
    if not state.playlists[state.current_playlist]:
        return

    # اگر هیچ آهنگی انتخاب نشده
    if state.current_index is None:
        state.current_index = 0
        play(state.current_index)
        return

    # ریپیت یک آهنگ (فقط وقتی آهنگ به صورت خودکار تموم شده)
    if state.repeat_mode == "one" and auto:
        play(state.current_index)
        return

    # اگر به آخر پلی لیست رسیدیم و ریپیت خاموش است، متوقف شو
    if (
        auto
        and not state.shuffle_mode
        and state.repeat_mode != "all"
        and state.current_index == len(state.playlists[state.current_playlist]) - 1
    ):
        state.player.stop()
        state.is_playing = False
        update_play_button()
        return

    # شافل واقعی
    if state.shuffle_mode and len(state.playlists[state.current_playlist]) > 1:
        available_indexes = list(range(len(state.playlists[state.current_playlist])))
        available_indexes.remove(state.current_index)
        state.current_index = random.choice(available_indexes)
    else:
        state.current_index = (state.current_index + 1) % len(state.playlists[state.current_playlist])

    play(state.current_index)


def prev_song():
    if state.current_index is None:
        return
    state.current_index = (state.current_index - 1) % len(state.playlists[state.current_playlist])
    play(state.current_index)


def apply_vlc_equalizer():
    if state.equalizer_mode == "Normal":
        state.player.set_equalizer(None)
        return

    eq = vlc.AudioEqualizer()

    if state.equalizer_mode == "Manual":
        preset = state.manual_eq
    else:
        preset = EQ_PRESETS.get(state.equalizer_mode, EQ_PRESETS["Normal"])

    # هر باند مقدار مخصوص خودش رو می‌گیره، نه یک مقدار میانگین یکسان برای همه
    for i in range(state.EQ_BAND_COUNT):
        value = preset[i] if i < len(preset) else 0
        eq.set_amp_at_index(float(value), i)

    state.player.set_equalizer(eq)


# ================= SLIDER =================

def start_drag():
    state.is_dragging = True


def stop_drag():
    state.is_dragging = False
    seek(state.progress.get())


def seek(val):
    if state.current_index is None:
        return
    state.player.set_time(int(float(val) * 1000))


def preview_seek(val):
    # فقط لیبل زمان رو در حین کشیدن اسلایدر آپدیت می‌کنه، بدون اینکه واقعاً
    # پخش رو seek کنه؛ چون seek کردن روی هر پیکسل حرکت باعث لگ/قطع صدا میشه.
    # seek واقعی همیشه توی stop_drag (رها کردن ماوس) انجام میشه.
    state.current_time_label.configure(text=format_time(float(val)))


def update_progress():
    vlc_state = state.player.get_state()

    if vlc_state == vlc.State.Playing and not state.is_dragging:
        current_time = state.player.get_time() // 1000
        state.progress.set(current_time)
        state.current_time_label.configure(text=format_time(current_time))
        state._song_ended_handled = False

    elif vlc_state == vlc.State.Ended and not state._song_ended_handled:
        state._song_ended_handled = True
        next_song(auto=True)

    state.app.after(500, update_progress)


def update_play_button():
    from animations import pulse
    from i18n import t

    if state.is_playing:
        state.play_btn.configure(text="⏸")
        if state.status_label:
            state.status_label.configure(text=t("status_playing"))
    else:
        state.play_btn.configure(text="▶")
        if state.status_label:
            has_song = state.current_index is not None
            state.status_label.configure(text=t("status_paused") if has_song else t("status_ready"))

    pulse(state.play_btn)


def toggle_play_pause():
    if state.is_playing:
        pause()
    else:
        if state.current_index is None and state.playlists[state.current_playlist]:
            play(0)
        else:
            resume()

"""
================= SETTINGS MANAGER =================
ذخیره و بازیابی تنظیمات برنامه (پلی‌لیست‌ها، صدا، اکولایزر، پس‌زمینه و ...)
از/به فایل JSON.
"""

import os
import json
import threading

import customtkinter as ctk

from state import state
from constants import SETTINGS_FILE, GRADIENT_PRESETS
from utils import debounce
from background import update_bg_transparency, render_background

_save_lock = threading.Lock()


def _build_settings_data():
    return {
        "shuffle": state.shuffle_mode,
        "repeat": state.repeat_mode,
        "playlists": state.playlists,
        "current_playlist": state.current_playlist,
        "last_index": state.current_index,
        "last_position": (state.player.get_time() // 1000) if state.current_index is not None else 0,
        "volume": state.volume.get(),
        "auto_resume": state.auto_resume,
        "equalizer": state.equalizer_mode,
        "manual_eq": state.manual_eq,
        "show_delete_buttons": state.show_delete_buttons,
        "background_mode": state.background_mode,
        "background_value": state.background_value,
        "language": state.language,
    }


def _write_settings_data(data):
    with _save_lock:
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Save settings error:", e)


def save_settings():
    # فقط ساخت دیکشنری داده‌ها (سریع، بدون I/O) روی ترد اصلی انجام میشه؛
    # نوشتن واقعی روی دیسک (که می‌تونه کند باشه و باعث لگ رابط کاربری بشه)
    # توی یه ترد جدا انجام می‌شه.
    data = _build_settings_data()
    threading.Thread(target=_write_settings_data, args=(data,), daemon=True).start()


def save_settings_sync():
    """نسخه‌ی همزمان (blocking) - فقط موقع بستن برنامه استفاده میشه تا مطمئن
    بشیم قبل از خروج کامل پروسه، تنظیمات واقعاً روی دیسک نوشته شدن (چون
    ترد daemon پس‌زمینه ممکنه قبل از تمومشدن نوشتن، با خروج برنامه کشته بشه)."""
    _write_settings_data(_build_settings_data())


def save_settings_debounced(delay=400):
    debounce("save_settings", save_settings, delay)


def load_settings():
    # این importها اینجا (داخل تابع) هستن تا از circular import با
    # audio_engine جلوگیری بشه (apply_vlc_equalizer به state ویجت‌هایی که
    # قبل از فراخوانی load_settings ساخته شدن نیاز داره).
    from audio_engine import apply_vlc_equalizer, play
    from theme import colors  # noqa: F401 (برای سازگاری در صورت نیاز آینده)
    from utils import format_time  # noqa: F401

    if not os.path.exists(SETTINGS_FILE):
        return

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    state.shuffle_mode = data.get("shuffle", False)
    state.repeat_mode = data.get("repeat", "all")
    state.auto_resume = data.get("auto_resume", False)
    state.playlists = data.get("playlists", {"Default": []})
    state.current_playlist = data.get("current_playlist", "Default")
    state.equalizer_mode = data.get("equalizer", "Normal")
    state.language = data.get("language", "en")

    loaded_manual_eq = data.get("manual_eq", [0.0] * state.EQ_BAND_COUNT)
    if isinstance(loaded_manual_eq, dict):
        # فرمت قدیمی (۳ باند low/mid/high) بود؛ به فرمت جدید ۱۰ باندی تبدیل می‌شه
        state.manual_eq = [0.0] * state.EQ_BAND_COUNT
    elif isinstance(loaded_manual_eq, list) and len(loaded_manual_eq) == state.EQ_BAND_COUNT:
        state.manual_eq = [float(v) for v in loaded_manual_eq]
    else:
        state.manual_eq = [0.0] * state.EQ_BAND_COUNT

    ctk.set_appearance_mode("Dark")

    if state.current_playlist not in state.playlists:
        state.current_playlist = "Default"

    state.show_delete_buttons = data.get("show_delete_buttons", False)
    state.delete_switch.select() if state.show_delete_buttons else state.delete_switch.deselect()

    state.current_index = data.get("last_index", None)
    last_position = data.get("last_position", 0)
    saved_volume = data.get("volume", 70)

    state.volume_value.set(saved_volume)
    state.volume_label.configure(text=f"{int(saved_volume)}%")
    state.player.audio_set_volume(int(saved_volume))

    from ui.player_bar import update_volume_icon
    update_volume_icon(saved_volume)

    if saved_volume == 0:
        state.is_muted = True
    else:
        state.last_volume_before_mute = saved_volume
        state.is_muted = False

    # مقادیر منوال اکولایزر برای هر ۱۰ باند
    for i, slider in enumerate(state.manual_sliders):
        slider.set(state.manual_eq[i] if i < len(state.manual_eq) else 0)
    state.equalizer_menu.set(state.equalizer_mode)

    # تنظیم وضعیت سوییچ‌ها
    state.shuffle_switch.select() if state.shuffle_mode else state.shuffle_switch.deselect()
    state.repeat_switch.select() if state.repeat_mode == "one" else state.repeat_switch.deselect()
    state.auto_resume_switch.select() if state.auto_resume else state.auto_resume_switch.deselect()

    if (
        state.current_index is not None
        and state.current_playlist in state.playlists
        and state.current_index < len(state.playlists[state.current_playlist])
    ):
        state.now_playing_label.configure(
            text=os.path.basename(state.playlists[state.current_playlist][state.current_index])
        )
        state.progress.set(0)

        if state.auto_resume:
            play(state.current_index, start_pos=last_position)
            state.progress.set(0)

    apply_vlc_equalizer()

    # ---- بازیابی تصویر زمینه ----
    loaded_bg_mode = data.get("background_mode", "default")
    loaded_bg_value = data.get("background_value", None)

    if loaded_bg_mode == "gradient" and loaded_bg_value in GRADIENT_PRESETS:
        state.background_mode = loaded_bg_mode
        state.background_value = loaded_bg_value
    elif loaded_bg_mode == "image" and loaded_bg_value and os.path.exists(loaded_bg_value):
        state.background_mode = loaded_bg_mode
        state.background_value = loaded_bg_value
    elif loaded_bg_mode == "custom" and loaded_bg_value:
        state.background_mode = loaded_bg_mode
        state.background_value = loaded_bg_value
    else:
        state.background_mode = "default"
        state.background_value = None

    from background import derive_bg_palette
    derive_bg_palette()

    update_bg_transparency()
    render_background()

    from i18n import apply_language
    apply_language()

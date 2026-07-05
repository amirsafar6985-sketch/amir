"""
================= THEME =================
تعریف رنگ‌های تم روشن/تاریک (با یک رنگ accent یکدست) و اعمال اون به همه‌ی
ویجت‌ها، تا کل اپ به جای رنگ خام سیاه/سفید، یک ظاهر مدرن و هماهنگ داشته باشه.
"""

import customtkinter as ctk

from state import state
from background import update_bg_transparency
from constants import ACCENT, ACCENT_HOVER, DANGER, DANGER_HOVER


def colors():
    # وقتی یه پس‌زمینه‌ی سفارشی (گرادینت/عکس) فعاله، رنگ‌ها از همون پس‌زمینه
    # مشتق میشن و دیگه با سوییچ تم روشن/تاریک عوض نمیشن؛ یعنی «ثابت» می‌مونن.
    if getattr(state, "background_mode", "default") != "default":
        palette = getattr(state, "background_palette", None)
        if palette:
            return palette

    mode = ctk.get_appearance_mode()

    if mode == "Dark":
        return {
            "bg": "#0b0b10",
            "glass": "#15151d",
            "card": "#1c1c26",
            "hover": "#26262f",
            "text": "#f5f5f7",
            "subtext": "#9a9aa8",
            "border": "#2a2a35",
            "btn": ACCENT,
            "btn_text": "#ffffff",
            "slider_bg": "#2a2a35",
            "accent": ACCENT,
            "accent_hover": ACCENT_HOVER,
            "danger": DANGER,
            "danger_hover": DANGER_HOVER,
        }
    else:
        return {
            "bg": "#f5f5f9",
            "glass": "#ffffff",
            "card": "#eeeef4",
            "hover": "#e2e2ec",
            "text": "#16161d",
            "subtext": "#6b6b7a",
            "border": "#e4e4ee",
            "btn": ACCENT,
            "btn_text": "#ffffff",
            "slider_bg": "#dcdce6",
            "accent": ACCENT,
            "accent_hover": ACCENT_HOVER,
            "danger": DANGER,
            "danger_hover": DANGER_HOVER,
        }


def refresh_theme():
    from playlist_manager import highlight_active

    c = colors()

    # App
    state.app.configure(bg=c["bg"])
    update_bg_transparency()
    state.player_bar.configure(
        fg_color=c["glass"],
        border_width=1,
        border_color=c.get("border", c["glass"]),
    )

    # Settings Panel
    if state.settings_panel:
        state.settings_panel.configure(
            fg_color=c["glass"],
            border_width=1,
            border_color=c.get("border", c["glass"]),
        )

    if state.settings_scroll:
        state.settings_scroll.configure(fg_color=c["glass"])
        state.settings_scroll._parent_frame.configure(fg_color=c["glass"])

    # Labels
    state.now_playing_label.configure(text_color=c["text"])
    state.current_time_label.configure(text_color=c.get("subtext", c["text"]))
    state.total_time_label.configure(text_color=c.get("subtext", c["text"]))
    state.volume_label.configure(text_color=c.get("subtext", c["text"]))

    # Buttons
    state.prev_btn.configure(text_color=c["text"], hover_color=c["hover"])
    state.next_btn.configure(text_color=c["text"], hover_color=c["hover"])

    state.play_btn.configure(
        fg_color=c["accent"],
        text_color=c["btn_text"],
        hover_color=c["accent_hover"],
    )

    if state.volume_icon:
        state.volume_icon.configure(text_color=c["text"], hover_color=c["hover"])

    if state.song_icon:
        state.song_icon.configure(fg_color=c["accent"])

    if state.status_label:
        state.status_label.configure(text_color=c["subtext"])

    # Sliders — رنگ فعال (progress/button) الان همون رنگ accent برندِ اپه،
    # نه سفید/سیاه خام
    state.progress.configure(
        progress_color=c["accent"],
        button_color=c["accent"],
        button_hover_color=c["accent_hover"],
        fg_color=c["slider_bg"],
    )

    state.volume.configure(
        progress_color=c["accent"],
        button_color=c["accent"],
        button_hover_color=c["accent_hover"],
        fg_color=c["slider_bg"],
    )

    for slider in getattr(state, "manual_sliders", []):
        slider.configure(
            progress_color=c["accent"],
            button_color=c["accent"],
            button_hover_color=c["accent_hover"],
            fg_color=c["slider_bg"],
        )

    # سوییچ‌های تنظیمات هم هماهنگ با رنگ accent
    for switch in (
        state.auto_resume_switch,
        state.shuffle_switch,
        state.repeat_switch,
        state.delete_switch,
    ):
        if switch:
            switch.configure(
                progress_color=c["accent"],
                button_color="#ffffff",
                button_hover_color=c["hover"],
                fg_color=c["slider_bg"],
                text_color=c["text"],
            )

    # منوهای کشویی (پلی‌لیست/اکولایزر)
    for menu in (state.playlist_selector, state.equalizer_menu):
        if menu:
            menu.configure(
                fg_color=c["card"],
                button_color=c["accent"],
                button_hover_color=c["accent_hover"],
                text_color=c["text"],
            )

    state.settings_btn.configure(
        text_color=c["text"],
        hover_color=c["hover"],
    )

    highlight_active(force_full=True)

    # نشانگر انتخاب سواچ پس‌زمینه رو (بدون بازسازی کل پنل) به‌روز می‌کنه
    try:
        from ui.settings_panel import refresh_background_selection
        refresh_background_selection()
    except Exception:
        pass

    # پشت نوار پخش و پنل تنظیمات رو با آخرین برش پس‌زمینه هماهنگ نگه می‌داره
    from background import refresh_bg_slices
    refresh_bg_slices()

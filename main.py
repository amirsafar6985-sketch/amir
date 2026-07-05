"""
================= MAIN =================
نقطه ورود برنامه. پنجره اصلی، فریم پلی‌لیست و پس‌زمینه رو می‌سازه، ماژول‌های
UI (نوار پخش و پنل تنظیمات) رو صدا می‌زنه و در نهایت لوپ‌های اصلی اجرایی
برنامه (mainloop و حلقه‌ی به‌روزرسانی پیشرفت پخش) رو اجرا می‌کنه.

اجرا:
    python main.py
"""

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

from state import state
from platform_utils import enable_windows_11_glass
from background import on_app_configure
from theme import refresh_theme
from settings_manager import save_settings_sync, load_settings
from playlist_manager import drop, switch_playlist
from audio_engine import update_progress
from ui.player_bar import build_player_bar
from ui.settings_panel import build_settings_panel


def build_main_window():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")  # فقط برای نرمال بودن داخلی

    state.app = TkinterDnD.Tk()
    state.app.grid_rowconfigure(0, weight=1)
    state.app.grid_columnconfigure(0, weight=1)
    state.app.geometry("1280x800")
    state.app.minsize(900, 560)
    state.app.title("🎧 Amir Player")

    state.app.update()

    enable_windows_11_glass(state.app)

    # ---- پس‌زمینه (تصویر زمینه) ----
    state.bg_label = ctk.CTkLabel(state.app, text="")
    state.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    state.bg_label.place_forget()  # تا وقتی بک‌گراندی انتخاب نشده، مخفی می‌مونه
    state.bg_label.lower()

    state.main = ctk.CTkFrame(state.app)
    # قبلاً برای دیده‌شدن پس‌زمینه فقط یه حاشیه‌ی باریک دور main نگه داشته
    # می‌شد (چون widgetهای customtkinter واقعاً "شفاف" نمیشن). الان به جاش
    # نوار پخش و پنل تنظیمات مستقیماً برش دقیقی از خود تصویر زمینه رو پشت
    # خودشون نشون می‌دن (background.py: attach_bg_slice) و main/لیست پخش هم
    # رنگ ثابتِ مشتق‌شده از همون پس‌زمینه رو می‌گیرن (theme.py). بنابراین
    # دیگه نیازی به این حاشیه نیست و پس‌زمینه کل پنجره رو پر می‌کنه.
    state.main.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    state.app.bind("<Configure>", on_app_configure)

    state.main.grid_rowconfigure(0, weight=1)
    state.main.grid_rowconfigure(1, weight=0, minsize=170)  # برای player_bar

    # ستون پلی لیست
    state.main.grid_columnconfigure(0, weight=1)
    # ستون پنل تنظیمات
    state.main.grid_columnconfigure(1, weight=0, minsize=0)

    state.playlist_frame = ctk.CTkScrollableFrame(state.main, corner_radius=18)
    state.playlist_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 20), pady=(20, 12))

    state.app.drop_target_register(DND_FILES)
    state.app.dnd_bind("<<Drop>>", drop)

    # نوار پخش پایین صفحه و پنل تنظیمات کناری
    build_player_bar()
    build_settings_panel()


def on_closing():
    save_settings_sync()
    state.app.destroy()


def main():
    build_main_window()

    state.app.protocol("WM_DELETE_WINDOW", on_closing)

    # ================= START =================
    load_settings()
    state.playlist_selector.configure(values=list(state.playlists.keys()))
    state.playlist_selector.set(state.current_playlist)
    switch_playlist(state.current_playlist)
    refresh_theme()

    # ---- حلقه‌ی اصلی به‌روزرسانی پیشرفت پخش (هر ۵۰۰ میلی‌ثانیه) ----
    update_progress()

    # ---- حلقه‌ی اصلی رابط کاربری Tkinter ----
    state.app.mainloop()


if __name__ == "__main__":
    main()
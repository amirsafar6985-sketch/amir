"""
================= STATE =================
این ماژول تمام متغیرهای مشترک، وضعیت پخش‌کننده و رفرنس ویجت‌ها رو نگه می‌داره.
به جای استفاده از global در هر فایل، همه ماژول‌ها یک شیء state واحد رو
import می‌کنن و مقادیر رو از طریق state.xxx می‌خونن/می‌نویسن. این کار مشکل
پراکندگی متغیرهای global بین چند فایل رو حل می‌کنه.
"""

import vlc

from constants import EQ_BAND_COUNT_DEFAULT, EQ_BAND_FREQS_DEFAULT


class AppState:
    def __init__(self):
        # ---------- VLC ----------
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        # ---------- Playlists ----------
        self.playlists = {"Default": []}
        self.current_playlist = "Default"
        self.current_index = None
        self.cards = []
        self.dragged_song = None

        # ---------- Playback ----------
        self.is_playing = False
        self.song_length = 0
        self.start_time = 0
        self.pause_offset = 0
        self.updating_slider = False
        self.is_dragging = False
        self.is_animating_panel = False
        self._song_ended_handled = False

        # ---------- Volume ----------
        self.is_muted = False
        self.last_volume_before_mute = 70

        # ---------- Modes ----------
        self.shuffle_mode = False
        self.repeat_mode = "all"
        self.auto_resume = False

        # ---------- Settings panel ----------
        self.settings_open = False
        self.panel_width = 340

        # ---------- Equalizer ----------
        self.equalizer_mode = "Normal"
        self.EQ_BAND_COUNT = EQ_BAND_COUNT_DEFAULT
        self.EQ_BAND_FREQS = list(EQ_BAND_FREQS_DEFAULT)
        self._load_real_eq_band_info()
        self.manual_eq = [0.0] * self.EQ_BAND_COUNT

        self.show_delete_buttons = False  # وضعیت نمایش دکمه حذف تکی

        # ---------- Language / i18n ----------
        self.language = "en"          # زبان پیش‌فرض انگلیسیه
        self._i18n_widgets = {}       # {translation_key: widget} برای رفرش سریع متن‌ها
        self._bg_swatch_buttons = {}  # {gradient_name: button} برای رفرش نشانگر انتخاب

        # ---------- Background ----------
        self.background_mode = "default"   # "default" | "gradient" | "image"
        self.background_value = None       # اسم گرادیان یا مسیر فایل عکس
        self._bg_source_image = None       # کش تصویر اصلی
        self._current_bg_ctk_image = None  # جلوگیری از garbage collection
        self.bg_label = None
        self._bg_thumb_refs = []           # جلوگیری از garbage collection عکس‌های کوچک

        # ---------- Debounce ----------
        self._debounce_jobs = {}

        # ---------- Tk root & containers (در main.py مقداردهی میشن) ----------
        self.app = None
        self.main = None
        self.playlist_frame = None
        self.player_bar = None
        self.settings_panel = None
        self.settings_scroll = None

        # ---------- Widgets (در ui/*.py مقداردهی میشن) ----------
        self.now_playing_label = None
        self.status_label = None
        self.song_icon = None
        self.current_time_label = None
        self.total_time_label = None
        self.volume_label = None
        self.volume_icon = None
        self.progress = None
        self.volume = None
        self.volume_value = None
        self.play_btn = None
        self.prev_btn = None
        self.next_btn = None
        self.settings_btn = None
        self.playlist_selector = None
        self.equalizer_menu = None
        self.manual_sliders = []
        self.delete_switch = None
        self.shuffle_switch = None
        self.repeat_switch = None
        self.auto_resume_switch = None

    def _load_real_eq_band_info(self):
        try:
            real_band_count = vlc.libvlc_audio_equalizer_get_band_count()
            if real_band_count and real_band_count > 0:
                self.EQ_BAND_COUNT = real_band_count
                self.EQ_BAND_FREQS = [
                    vlc.libvlc_audio_equalizer_get_band_frequency(i)
                    for i in range(real_band_count)
                ]
        except Exception:
            pass


# شیء واحد و مشترک وضعیت برنامه - همه ماژول‌ها همینو import می‌کنن
state = AppState()

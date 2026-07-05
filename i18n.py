"""
================= I18N (چندزبانگی) =================
متن‌های رابط کاربری برای دو زبان انگلیسی (پیش‌فرض) و فارسی + تابع t() برای
گرفتن متن ترجمه‌شده بر اساس زبان فعلی، و set_language()/apply_language()
برای عوض کردن زبان در حین اجرا بدون نیاز به بستن و باز کردن برنامه.
"""

from state import state

LANGUAGES = {
    "en": "English",
    "fa": "فارسی",
    "ar": "العربية",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
}

TEXT = {
    "en": {
        "settings_title": "⚙ Settings",
        "settings_subtitle": "Personalize your player",
        "section_language": "🌐 Language",
        "section_playlist": "🎵 Playlist",
        "section_playback": "▶ Playback",
        "section_background": "🖼 Background",
        "custom_color": "🎨 Custom Color",
        "section_equalizer": "🎚 Equalizer",
        "new_playlist": "➕ New Playlist",
        "rename_playlist": "✎ Rename",
        "delete_playlist": "🗑 Delete Playlist",
        "clear_songs": "Clear Songs",
        "add_song": "➕  Add Song",
        "auto_resume": "Resume automatically on startup",
        "shuffle": "Shuffle playback",
        "repeat_one": "Repeat one song",
        "show_delete_buttons": "Show single delete buttons",
        "choose_image": "📁 Choose Image",
        "remove_background": "♻ Remove Background",
        "nothing_playing": "Nothing Playing",
        "status_ready": "Ready to play",
        "status_playing": "Playing",
        "status_paused": "Paused",
        "local_audio_file": "Local audio file",
        "rename_dialog_title": "Rename Playlist",
        "rename_dialog_prompt": "Enter new name:",
        "playlist_prefix": "Playlist",
    },
    "fa": {
        "settings_title": "⚙ تنظیمات",
        "settings_subtitle": "پلیر رو مطابق سلیقه‌ات شخصی‌سازی کن",
        "section_language": "🌐 زبان",
        "section_playlist": "🎵 پلی‌لیست",
        "section_playback": "▶ پخش",
        "section_background": "🖼 پس‌زمینه",
        "custom_color": "🎨 رنگ دلخواه",
        "section_equalizer": "🎚 اکولایزر",
        "new_playlist": "➕ پلی‌لیست جدید",
        "rename_playlist": "✎ تغییر نام",
        "delete_playlist": "🗑 حذف پلی‌لیست",
        "clear_songs": "پاک‌کردن آهنگ‌ها",
        "add_song": "➕  افزودن آهنگ",
        "auto_resume": "ادامه‌ی خودکار هنگام باز شدن",
        "shuffle": "پخش تصادفی (Shuffle)",
        "repeat_one": "تکرار یک آهنگ",
        "show_delete_buttons": "نمایش دکمه‌ی حذف تکی",
        "choose_image": "📁 انتخاب عکس",
        "remove_background": "♻ حذف پس‌زمینه",
        "nothing_playing": "در حال حاضر پخشی نیست",
        "status_ready": "آماده‌ی پخش",
        "status_playing": "در حال پخش",
        "status_paused": "مکث شده",
        "local_audio_file": "فایل صوتی محلی",
        "rename_dialog_title": "تغییر نام پلی‌لیست",
        "rename_dialog_prompt": "نام جدید را وارد کنید:",
        "playlist_prefix": "پلی‌لیست",
    },
    "ar": {
        "settings_title": "⚙ الإعدادات",
        "settings_subtitle": "خصّص مشغلك الموسيقي",
        "section_language": "🌐 اللغة",
        "section_playlist": "🎵 قائمة التشغيل",
        "section_playback": "▶ التشغيل",
        "section_background": "🖼 الخلفية",
        "custom_color": "🎨 لون مخصص",
        "section_equalizer": "🎚 موازن الصوت",
        "new_playlist": "➕ قائمة تشغيل جديدة",
        "rename_playlist": "✎ إعادة تسمية",
        "delete_playlist": "🗑 حذف القائمة",
        "clear_songs": "مسح الأغاني",
        "add_song": "➕  إضافة أغنية",
        "auto_resume": "الاستئناف تلقائيًا عند البدء",
        "shuffle": "التشغيل العشوائي",
        "repeat_one": "تكرار أغنية واحدة",
        "show_delete_buttons": "إظهار أزرار الحذف الفردية",
        "choose_image": "📁 اختيار صورة",
        "remove_background": "♻ إزالة الخلفية",
        "nothing_playing": "لا يوجد تشغيل حاليًا",
        "status_ready": "جاهز للتشغيل",
        "status_playing": "قيد التشغيل",
        "status_paused": "متوقف مؤقتًا",
        "local_audio_file": "ملف صوتي محلي",
        "rename_dialog_title": "إعادة تسمية القائمة",
        "rename_dialog_prompt": "أدخل الاسم الجديد:",
        "playlist_prefix": "قائمة تشغيل",
    },
    "fr": {
        "settings_title": "⚙ Paramètres",
        "settings_subtitle": "Personnalisez votre lecteur",
        "section_language": "🌐 Langue",
        "section_playlist": "🎵 Playlist",
        "section_playback": "▶ Lecture",
        "section_background": "🖼 Arrière-plan",
        "custom_color": "🎨 Couleur personnalisée",
        "section_equalizer": "🎚 Égaliseur",
        "new_playlist": "➕ Nouvelle playlist",
        "rename_playlist": "✎ Renommer",
        "delete_playlist": "🗑 Supprimer la playlist",
        "clear_songs": "Effacer les titres",
        "add_song": "➕  Ajouter un titre",
        "auto_resume": "Reprendre automatiquement au démarrage",
        "shuffle": "Lecture aléatoire",
        "repeat_one": "Répéter un titre",
        "show_delete_buttons": "Afficher les boutons de suppression",
        "choose_image": "📁 Choisir une image",
        "remove_background": "♻ Retirer l'arrière-plan",
        "nothing_playing": "Aucune lecture en cours",
        "status_ready": "Prêt à lire",
        "status_playing": "Lecture en cours",
        "status_paused": "En pause",
        "local_audio_file": "Fichier audio local",
        "rename_dialog_title": "Renommer la playlist",
        "rename_dialog_prompt": "Entrez le nouveau nom :",
        "playlist_prefix": "Playlist",
    },
    "de": {
        "settings_title": "⚙ Einstellungen",
        "settings_subtitle": "Passe deinen Player an",
        "section_language": "🌐 Sprache",
        "section_playlist": "🎵 Playlist",
        "section_playback": "▶ Wiedergabe",
        "section_background": "🖼 Hintergrund",
        "custom_color": "🎨 Eigene Farbe",
        "section_equalizer": "🎚 Equalizer",
        "new_playlist": "➕ Neue Playlist",
        "rename_playlist": "✎ Umbenennen",
        "delete_playlist": "🗑 Playlist löschen",
        "clear_songs": "Titel leeren",
        "add_song": "➕  Titel hinzufügen",
        "auto_resume": "Beim Start automatisch fortsetzen",
        "shuffle": "Zufallswiedergabe",
        "repeat_one": "Einen Titel wiederholen",
        "show_delete_buttons": "Einzelne Löschen-Schaltflächen anzeigen",
        "choose_image": "📁 Bild wählen",
        "remove_background": "♻ Hintergrund entfernen",
        "nothing_playing": "Nichts wird wiedergegeben",
        "status_ready": "Bereit zur Wiedergabe",
        "status_playing": "Wird wiedergegeben",
        "status_paused": "Pausiert",
        "local_audio_file": "Lokale Audiodatei",
        "rename_dialog_title": "Playlist umbenennen",
        "rename_dialog_prompt": "Neuen Namen eingeben:",
        "playlist_prefix": "Playlist",
    },
    "es": {
        "settings_title": "⚙ Ajustes",
        "settings_subtitle": "Personaliza tu reproductor",
        "section_language": "🌐 Idioma",
        "section_playlist": "🎵 Lista de reproducción",
        "section_playback": "▶ Reproducción",
        "section_background": "🖼 Fondo",
        "custom_color": "🎨 Color personalizado",
        "section_equalizer": "🎚 Ecualizador",
        "new_playlist": "➕ Nueva lista",
        "rename_playlist": "✎ Renombrar",
        "delete_playlist": "🗑 Eliminar lista",
        "clear_songs": "Borrar canciones",
        "add_song": "➕  Añadir canción",
        "auto_resume": "Reanudar automáticamente al iniciar",
        "shuffle": "Reproducción aleatoria",
        "repeat_one": "Repetir una canción",
        "show_delete_buttons": "Mostrar botones de eliminación individual",
        "choose_image": "📁 Elegir imagen",
        "remove_background": "♻ Quitar fondo",
        "nothing_playing": "No se está reproduciendo nada",
        "status_ready": "Listo para reproducir",
        "status_playing": "Reproduciendo",
        "status_paused": "Pausado",
        "local_audio_file": "Archivo de audio local",
        "rename_dialog_title": "Renombrar lista",
        "rename_dialog_prompt": "Introduce el nuevo nombre:",
        "playlist_prefix": "Lista",
    },
}


def t(key):
    """متن ترجمه‌شده‌ی کلید داده‌شده رو بر اساس زبان فعلی برمی‌گردونه."""
    lang = getattr(state, "language", "en")
    table = TEXT.get(lang, TEXT["en"])
    return table.get(key, TEXT["en"].get(key, key))


def set_language(lang_code):
    """زبان برنامه رو عوض می‌کنه، تمام متن‌های رابط کاربری رو رفرش می‌کنه و ذخیره می‌کنه."""
    from settings_manager import save_settings

    if lang_code not in TEXT or lang_code == state.language:
        return

    state.language = lang_code
    apply_language()
    save_settings()


def apply_language():
    """متن تمام ویجت‌های زبان‌محور رو با زبان فعلی به‌روزرسانی می‌کنه."""
    try:
        from ui.settings_panel import refresh_settings_texts
        refresh_settings_texts()
    except Exception as e:
        print("i18n settings refresh error:", e)

    try:
        from ui.player_bar import refresh_player_bar_texts
        refresh_player_bar_texts()
    except Exception as e:
        print("i18n player bar refresh error:", e)

    try:
        from playlist_manager import refresh_cards_language
        refresh_cards_language()
    except Exception as e:
        print("i18n cards refresh error:", e)

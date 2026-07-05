"""
================= BACKGROUND (تصویر زمینه) =================
تولید و رندر گرادیان یا عکس دلخواه به عنوان پس‌زمینه پنجره.
"""

import os
import colorsys

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageOps, ImageStat

from state import state
from constants import GRADIENT_PRESETS
from utils import debounce

try:
    RESAMPLE_BICUBIC = Image.Resampling.BICUBIC
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_BICUBIC = Image.BICUBIC
    RESAMPLE_LANCZOS = Image.LANCZOS

# ---- attribute های جدید state که این ماژول اضافه می‌کنه (اگه از قبل توی
# state.py تعریف نشده باشن، این‌جا با مقدار پیش‌فرض ساخته میشن تا اجرای
# برنامه با AttributeError متوقف نشه) ----
for _attr, _default in (
    ("_bg_full_pil_image", None),
    ("background_palette", None),
    ("_bg_slice_labels", None),
    ("_bg_slice_images", None),
):
    if not hasattr(state, _attr):
        setattr(state, _attr, _default)


def generate_gradient_image(size, stops, angle=45):
    """یک تصویر گرادیان با ۲ یا ۳ رنگ (کل طیف رنگی) به اندازه‌ی size می‌سازه."""
    w, h = max(1, int(size[0])), max(1, int(size[1]))

    grad = Image.linear_gradient("L").rotate(angle, expand=True, resample=RESAMPLE_BICUBIC)
    gw, gh = grad.size

    if gw < w or gh < h:
        scale = max(w / gw, h / gh) * 1.05
        grad = grad.resize((max(1, int(gw * scale)), max(1, int(gh * scale))), RESAMPLE_BICUBIC)
        gw, gh = grad.size

    left = max(0, (gw - w) // 2)
    top = max(0, (gh - h) // 2)
    grad = grad.crop((left, top, left + w, top + h))

    if len(stops) >= 3:
        colored = ImageOps.colorize(grad, black=stops[0], white=stops[2], mid=stops[1])
    else:
        colored = ImageOps.colorize(grad, black=stops[0], white=stops[1])

    return colored.convert("RGB")


def cover_resize(img, size):
    """عکس رو مثل CSS background-size:cover تغییر سایز و کراپ می‌کنه تا کل فضا رو بپوشونه."""
    target_w, target_h = max(1, int(size[0])), max(1, int(size[1]))
    src_w, src_h = img.size
    if src_w == 0 or src_h == 0:
        return img

    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = max(1, int(src_w * scale) + 1), max(1, int(src_h * scale) + 1)
    resized = img.resize((new_w, new_h), RESAMPLE_LANCZOS)

    left = max(0, (new_w - target_w) // 2)
    top = max(0, (new_h - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def _load_bg_source_image(path):
    """
    عکس رو باز می‌کنه و اگه شفافیت (آلفا) داشته باشه، به‌جای اینکه مقادیر
    RGB خام (که توی نواحی شفاف خیلی از عکس‌های PNG صفر/سیاهه) مستقیم نگه
    داشته بشه، روی یه رنگ خنثی (نه سیاه مطلق) ترکیب می‌کنه. این همون دلیلیه
    که انتخاب یه عکس PNG شفاف قبلاً باعث می‌شد کل پس‌زمینه سیاه بشه: میانگین
    رنگ از روی پیکسل‌های شفافِ سیاه محاسبه می‌شد.
    """
    img = Image.open(path)

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        matte = Image.new("RGB", img.size, (24, 24, 32))
        matte.paste(img, mask=img.split()[-1])
        return matte

    return img.convert("RGB")


def _average_rgb(img):
    """میانگین واقعی رنگ یه عکس رو حساب می‌کنه (پایدارتر از resize به ۱x۱)."""
    small = img.resize((64, 64), RESAMPLE_BICUBIC) if max(img.size) > 64 else img
    stat = ImageStat.Stat(small)
    r, g, b = stat.mean[:3]
    return int(r), int(g), int(b)


def render_background():
    """تصویر زمینه فعلی (گرادیان یا عکس) رو با سایز فعلی پنجره رندر می‌کنه."""
    if state.bg_label is None:
        return

    if state.background_mode in ("default", "custom") or not state.background_value:
        state.bg_label.place_forget()
        state._bg_full_pil_image = None
        refresh_bg_slices()
        return

    state.app.update_idletasks()
    w = max(state.app.winfo_width(), 200)
    h = max(state.app.winfo_height(), 200)

    try:
        if state.background_mode == "gradient":
            stops = GRADIENT_PRESETS.get(state.background_value)
            if not stops:
                return
            pil_img = generate_gradient_image((w, h), stops)

        elif state.background_mode == "image":
            if not os.path.exists(state.background_value):
                return
            if state._bg_source_image is None:
                state._bg_source_image = _load_bg_source_image(state.background_value)
            pil_img = cover_resize(state._bg_source_image, (w, h))

        else:
            return

        # نگه‌داشتن نسخه‌ی خام PIL تا بشه از همین تصویر، برای نوار پخش و
        # پنل تنظیمات هم برش دقیق و پیوسته با بقیه‌ی زمینه گرفت
        state._bg_full_pil_image = pil_img

        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w, h))
        state._current_bg_ctk_image = ctk_img
        state.bg_label.configure(image=ctk_img, text="")
        state.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        state.bg_label.lower()

        refresh_bg_slices()

    except Exception as e:
        print("Background render error:", e)


def _luminance(rgb):
    r, g, b = rgb
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def _palette_from_rgb(sample_rgb):
    r, g, b = sample_rgb
    dark_card = f"#{max(r - 40, 0):02x}{max(g - 40, 0):02x}{max(b - 40, 0):02x}"
    dark_glass = f"#{max(r - 60, 0):02x}{max(g - 60, 0):02x}{max(b - 60, 0):02x}"
    hover = f"#{min(r + 25, 255):02x}{min(g + 25, 255):02x}{min(b + 25, 255):02x}"
    accent_hover = f"#{min(r + 55, 255):02x}{min(g + 45, 255):02x}{min(b + 65, 255):02x}"
    text_is_white = _luminance(sample_rgb) < 0.55

    return {
        "bg": dark_glass,
        "glass": dark_glass,
        "card": dark_card,
        "hover": hover,
        "text": "#ffffff" if text_is_white else "#000000",
        "subtext": "#c9c9d2" if text_is_white else "#4a4a55",
        "border": dark_card,
        "btn": "#ffffff" if text_is_white else "#000000",
        "btn_text": "#000000" if text_is_white else "#ffffff",
        "slider_bg": dark_card,
        "accent": hover,
        "accent_hover": accent_hover,
        "danger": "#ff5c7a",
        "danger_hover": "#ff7f95",
    }


def derive_bg_palette():
    """
    از روی گرادیان/عکس/رنگ دلخواه انتخابی، یه پالت رنگ ثابت می‌سازه
    (کارت/شیشه/هاور/متن...) که دیگه با سوییچ تم روشن/تاریک عوض نمیشه، بلکه
    همیشه هماهنگ با پس‌زمینه‌ی انتخابی می‌مونه. اگه پس‌زمینه‌ای فعال نباشه،
    پالت پاک میشه تا رنگ‌های پیش‌فرض روشن/تاریک در theme.py دوباره استفاده بشن.
    """
    mode = state.background_mode
    sample_rgb = None

    try:
        if mode == "gradient" and state.background_value in GRADIENT_PRESETS:
            stops = GRADIENT_PRESETS[state.background_value]
            mid_hex = stops[1] if len(stops) >= 2 else stops[0]
            mid_hex = mid_hex.lstrip("#")
            sample_rgb = tuple(int(mid_hex[i:i + 2], 16) for i in (0, 2, 4))

        elif mode == "image" and state.background_value and os.path.exists(state.background_value):
            if state._bg_source_image is None:
                state._bg_source_image = _load_bg_source_image(state.background_value)
            sample_rgb = _average_rgb(state._bg_source_image)

        elif mode == "custom" and state.background_value:
            hexv = state.background_value.lstrip("#")
            sample_rgb = tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))
    except Exception as e:
        print("Palette derive error:", e)

    if sample_rgb is None:
        state.background_palette = None
        return

    state.background_palette = _palette_from_rgb(sample_rgb)


def _crop_for_widget(widget):
    """برشی از تصویر کامل زمینه که دقیقاً موقعیت/سایز widget رو پوشش میده."""
    if state._bg_full_pil_image is None:
        return None
    try:
        state.app.update_idletasks()
        ax = widget.winfo_rootx() - state.app.winfo_rootx()
        ay = widget.winfo_rooty() - state.app.winfo_rooty()
        w = max(widget.winfo_width(), 1)
        h = max(widget.winfo_height(), 1)

        full = state._bg_full_pil_image
        fw, fh = full.size

        left = max(0, min(ax, fw - 1))
        top = max(0, min(ay, fh - 1))
        right = max(left + 1, min(ax + w, fw))
        bottom = max(top + 1, min(ay + h, fh))

        crop = full.crop((left, top, right, bottom))
        if crop.size != (w, h):
            crop = crop.resize((w, h), RESAMPLE_LANCZOS)
        return crop
    except Exception as e:
        print("Bg slice crop error:", e)
        return None


def attach_bg_slice(widget):
    """
    یه برش دقیق از پس‌زمینه رو به عنوان یه لایه‌ی زیرین داخل widget می‌ذاره
    (مثلاً نوار پخش یا پنل تنظیمات)، طوری که انگار همون تصویر زمینه‌ی اصلی
    از پشت این ویجت‌ها هم ادامه پیدا کرده. وقتی پس‌زمینه‌ای فعال نیست، این
    لایه برداشته میشه و ویجت به رنگ عادی خودش برمی‌گرده.
    """
    if widget is None:
        return

    if state._bg_slice_labels is None:
        state._bg_slice_labels = {}
    if state._bg_slice_images is None:
        state._bg_slice_images = {}

    if state.background_mode == "default" or state._bg_full_pil_image is None:
        label = state._bg_slice_labels.pop(widget, None)
        if label is not None:
            label.place_forget()
        return

    crop = _crop_for_widget(widget)
    if crop is None:
        return

    ctk_img = ctk.CTkImage(light_image=crop, dark_image=crop, size=crop.size)
    state._bg_slice_images[widget] = ctk_img  # جلوگیری از garbage collection

    label = state._bg_slice_labels.get(widget)
    if label is None:
        label = ctk.CTkLabel(widget, text="", image=ctk_img)
        state._bg_slice_labels[widget] = label
    else:
        label.configure(image=ctk_img)

    label.place(x=0, y=0, relwidth=1, relheight=1)
    label.lower()
    widget.configure(fg_color="transparent")


def refresh_bg_slices():
    """پشت نوار پخش و پنل تنظیمات رو با برش تازه‌ای از پس‌زمینه به‌روزرسانی می‌کنه."""
    for w in (getattr(state, "player_bar", None), getattr(state, "settings_panel", None)):
        attach_bg_slice(w)


def update_bg_transparency():
    """
    وقتی پس‌زمینه‌ی سفارشی فعاله، فریم‌های اصلی (main و لیست پخش) به جای
    رنگ‌های ثابت روشن/تاریک، از پالت رنگیِ مشتق‌شده از همون پس‌زمینه استفاده
    می‌کنن تا یکدست بمونن و با سوییچ تم عوض نشن.
    """
    from theme import colors  # جلوگیری از circular import در سطح ماژول

    c = colors()
    state.main.configure(fg_color=c["bg"])
    state.playlist_frame.configure(fg_color=c["glass"])


def set_background_gradient(name):
    from settings_manager import save_settings
    from theme import refresh_theme

    if name not in GRADIENT_PRESETS:
        return

    state.background_mode = "gradient"
    state.background_value = name
    derive_bg_palette()
    render_background()
    refresh_theme()
    save_settings()


def generate_hue_strip(width, height):
    """یه نوار عمودی از کل طیف رنگی (hue) می‌سازه - برای انتخاب رنگ دلخواه."""
    img = Image.new("RGB", (max(1, width), max(1, height)))
    px = img.load()
    h = max(height - 1, 1)
    for y in range(height):
        r, g, b = colorsys.hsv_to_rgb(y / h, 1.0, 1.0)
        color = (int(r * 255), int(g * 255), int(b * 255))
        for x in range(width):
            px[x, y] = color
    return img


def hex_for_hue_fraction(t):
    """t بین ۰ و ۱ (موقعیت روی نوار عمودی) رو به رنگ hex تبدیل می‌کنه."""
    t = min(max(t, 0.0), 1.0)
    r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def quick_preview_color(hex_color):
    """
    موقع کشیدن روی نوار رنگ صدا زده میشه: فقط رنگ چند تا کانتینر اصلی رو
    فوری عوض می‌کنه (بدون رفرش کامل تم که سنگین‌تره و باعث لگ حین کشیدن
    ماوس میشه، و بدون ذخیره روی دیسک). رفرش کامل و ذخیره، فقط موقع رها
    کردن ماوس در set_background_custom_color انجام میشه.
    """
    try:
        hexv = hex_color.lstrip("#")
        rgb = tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))
        palette = _palette_from_rgb(rgb)

        state.main.configure(fg_color=palette["bg"])
        state.playlist_frame.configure(fg_color=palette["glass"])
        if state.player_bar:
            state.player_bar.configure(fg_color=palette["glass"])
        if state.settings_panel:
            state.settings_panel.configure(fg_color=palette["glass"])
        if state.settings_scroll:
            state.settings_scroll.configure(fg_color=palette["glass"])
    except Exception:
        pass


def set_background_custom_color(hex_color):
    from settings_manager import save_settings
    from theme import refresh_theme

    state.background_mode = "custom"
    state.background_value = hex_color
    state._bg_full_pil_image = None
    if state.bg_label is not None:
        state.bg_label.place_forget()

    derive_bg_palette()
    refresh_bg_slices()
    refresh_theme()
    save_settings()


def pick_background_image():
    path = filedialog.askopenfilename(
        title="انتخاب تصویر زمینه",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")]
    )
    if not path:
        return
    set_background_image(path)


def set_background_image(path):
    from settings_manager import save_settings
    from theme import refresh_theme

    state.background_mode = "image"
    state.background_value = path
    state._bg_source_image = None  # فورس بارگذاری مجدد از مسیر جدید
    derive_bg_palette()
    render_background()
    refresh_theme()
    save_settings()


def clear_background():
    from settings_manager import save_settings
    from theme import refresh_theme

    state.background_mode = "default"
    state.background_value = None
    state.background_palette = None
    state._bg_full_pil_image = None
    if state.bg_label is not None:
        state.bg_label.place_forget()
    refresh_bg_slices()
    refresh_theme()
    save_settings()


def on_app_configure(event):
    if event.widget is not state.app or state.background_mode == "default":
        return

    size = (state.app.winfo_width(), state.app.winfo_height())
    if getattr(state, "_last_configure_size", None) == size:
        return  # فقط جابه‌جایی پنجره بوده، نه تغییر سایز واقعی؛ کاری لازم نیست

    state._last_configure_size = size
    debounce("bg_resize", render_background, 150)
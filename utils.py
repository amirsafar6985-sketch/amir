"""
================= UTILS =================
توابع کمکی عمومی که به state.app نیاز دارن.
"""

from state import state


def debounce(key, func, delay=250):
    """
    به جای اجرای فوری یک تابع روی هر رویداد (مثلاً هر پیکسل حرکت اسلایدر)،
    اجرا رو کمی به تعویق میندازه و اگه رویداد جدیدی بیاد، اجرای قبلی رو
    کنسل می‌کنه. این باعث میشه دیسک I/O و فراخوانی‌های سنگین VLC روی هر
    حرکت ریز اسلایدر انجام نشه و برنامه لگ نکنه.
    """
    existing = state._debounce_jobs.get(key)
    if existing:
        try:
            state.app.after_cancel(existing)
        except Exception:
            pass
    state._debounce_jobs[key] = state.app.after(delay, func)


def safe_ui(callback):
    """اجرای امن یک callback داخل thread اصلی رابط کاربری."""
    state.app.after(0, callback)


def format_time(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

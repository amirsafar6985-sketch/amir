"""
================= ANIMATION ENGINE =================
انیمیشن‌های ساده رابط کاربری: تغییر رنگ نرم، اسلاید پنل تنظیمات، پالس دکمه.
"""

from state import state


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def animate_color(widget, start_color, end_color, steps=15, delay=10):
    try:
        # اگه انیمیشن قبلی روی همین ویجت هنوز در حال اجراست، کنسلش کن تا
        # چند انیمیشن هم‌زمان روی هم جمع نشن و برنامه لگ نکنه
        prev_job = getattr(widget, "_anim_job", None)
        if prev_job:
            try:
                widget.after_cancel(prev_job)
            except Exception:
                pass

        gen = getattr(widget, "_anim_gen", 0) + 1
        widget._anim_gen = gen

        start = hex_to_rgb(start_color)
        end = hex_to_rgb(end_color)
        diff = [(end[i] - start[i]) / steps for i in range(3)]

        def step(count=0):
            # اگه یه انیمیشن جدیدتر روی این ویجت شروع شده باشه، این یکی متوقف میشه
            if getattr(widget, "_anim_gen", 0) != gen:
                return
            if count <= steps:
                new_color = tuple(int(start[i] + diff[i] * count) for i in range(3))
                widget.configure(fg_color=rgb_to_hex(new_color))
                widget._anim_job = widget.after(delay, lambda: step(count + 1))
        step()
    except Exception:
        pass


def smooth_slide(widget, start_x, end_x, duration=250):
    state.is_animating_panel = True

    steps = 30
    delay = duration // steps

    def ease_out(t):
        return 1 - (1 - t) * (1 - t)

    def slide(step=0):
        if step <= steps:
            progress = ease_out(step / steps)
            new_x = start_x + (end_x - start_x) * progress
            widget.place(x=new_x, y=0)
            widget.after(delay, lambda: slide(step + 1))
        else:
            widget.place(x=end_x, y=0)
            state.is_animating_panel = False

    slide()


def pulse(widget):
    try:
        # سایز واقعی رو فقط بار اول ذخیره می‌کنیم، نه هر بار از cget، وگرنه
        # اگه pulse قبل از تمومشدن انیمیشن قبلی دوباره صدا زده بشه، سایز
        # «بزرگ‌شده» به اشتباه به عنوان سایز پایه ذخیره میشه و ویجت هر بار
        # یه‌کم بزرگ‌تر از قبل باقی می‌مونه.
        base_w = getattr(widget, "_pulse_base_w", None)
        base_h = getattr(widget, "_pulse_base_h", None)
        if base_w is None or base_h is None:
            base_w = widget.cget("width")
            base_h = widget.cget("height")
            widget._pulse_base_w = base_w
            widget._pulse_base_h = base_h

        # اگه انیمیشن pulse قبلی هنوز در انتظار بازگشت به سایز اصلیه، کنسلش
        # کن تا دو تایمر هم‌زمان روی هم اثر نذارن
        prev_job = getattr(widget, "_pulse_job", None)
        if prev_job:
            try:
                widget.after_cancel(prev_job)
            except Exception:
                pass

        widget.configure(width=base_w + 6, height=base_h + 6)
        widget._pulse_job = widget.after(80, lambda: widget.configure(width=base_w, height=base_h))
    except Exception:
        pass

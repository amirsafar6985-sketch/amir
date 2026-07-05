"""
================= WINDOWS 11 GLASS EFFECT =================
"""

import sys
import ctypes


def enable_windows_11_glass(window):
    if sys.platform != "win32":
        return

    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())

        DWMWA_SYSTEMBACKDROP_TYPE = 38
        DWMSBT_MAINWINDOW = 2  # Mica

        value = ctypes.c_int(DWMSBT_MAINWINDOW)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
    except Exception:
        pass

# =============================================================================
# nanonis_labbook/clipboard.py
#
# Clipboard utilities and image-pasting into the target logbook application.
# The target application window title is set in config.LABBOOK_APP_TITLE.
# =============================================================================

import io
import time

import pyautogui
import pygetwindow as gw
import win32clipboard
from PIL import Image
from tkinter import messagebox

from .config import LABBOOK_APP_TITLE


def send_image_to_clipboard(img_path):
    """Load a PNG from disk and place it on the Windows clipboard as a DIB."""
    image = Image.open(img_path)
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def paste_image_into_app(img_path, scroll_to_bottom=True, n_page_down=5):
    """Copy img_path to the clipboard and paste it into the logbook application.

    The target application is identified by LABBOOK_APP_TITLE in config.py.
    The search is case-insensitive and matches any window whose title contains
    that string.
    """
    send_image_to_clipboard(img_path)
    time.sleep(0.5)

    title_lower = LABBOOK_APP_TITLE.lower()
    all_windows = gw.getAllWindows()
    matching = [w for w in all_windows if title_lower in w.title.lower()]

    if not matching:
        messagebox.showwarning(
            "Warning",
            f"No window found with title containing '{LABBOOK_APP_TITLE}'.\n"
            "Please bring it to the foreground and try again."
        )
        return

    target = matching[0]
    target.activate()
    time.sleep(0.5)

    if scroll_to_bottom:
        pyautogui.press("end")
        time.sleep(0.3)
        for _ in range(n_page_down):
            pyautogui.press("pagedown")
            time.sleep(0.1)

    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)

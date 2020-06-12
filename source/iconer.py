"""Small module for setting window icon."""
import os


def set_window_icon(window):
    """Check what OS we're on, and set the window icon if on Windows."""
    if os.path.isfile('assets/chem.ico'):
        icon_path = os.path.abspath('assets/chem.ico')
        if os.name == 'nt':
            window.wm_iconbitmap(icon_path)

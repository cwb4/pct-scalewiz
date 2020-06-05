"""Small module for setting window icon."""
import os


def set_window_icon(window):
    """Check what OS we're on, and set the window icon if on Windows."""
    try:
        if os.name == 'nt':
            window.iconbitmap('assets/chem.ico')
    except FileNotFoundError:
        print("The icon file at assets/chem.ico could not be found.")
    except Exception as error:
        print(error)

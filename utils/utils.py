import os
import sys

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    if not sys.stdout.isatty():
        return

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
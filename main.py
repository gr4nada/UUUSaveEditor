import tkinter as tk
from src.gui.app import EditorApp
import logging

logging.basicConfig(
    level=logging.INFO, # Change to logging.INFO later to hide debug prints
    format="%(asctime)s [%(levelname)s] %(name)s -> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def main():
    root = tk.Tk()
    app = EditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
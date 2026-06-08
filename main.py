import tkinter as tk
from src.gui.app import EditorApp

def main():
    root = tk.Tk()
    app = EditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
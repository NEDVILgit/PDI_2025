import tkinter as tk
try:
    import ttkbootstrap as ttkb
except ImportError:
    ttkb = None


from tps.tp0 import TP0Frame 
from tps.tp1 import TP1Frame

class App:
    def __init__(self):
        if ttkb:
            self.root = ttkb.Window(themename="superhero")
        else:
            self.root = tk.Tk()
        self.root.title("Procesamiento de Imágenes - TPs")
        self.root.geometry("1600x800")

        menu_frame = tk.Frame(self.root, bg="#2c3e50")
        menu_frame.pack(side="left", fill="y")

        content_frame = tk.Frame(self.root, bg="white")
        content_frame.pack(side="right", expand=True, fill="both")

        self.frames = {}
        self.content_frame = content_frame

        # Registrar TPs aquí
        
        self.register_tp("TP0", TP0Frame)
        self.register_tp("TP1", TP1Frame)

        for name in self.frames:
            btn = tk.Button(menu_frame, text=name, fg="white", bg="#34495e",
                            command=lambda n=name: self.show_frame(n))
            btn.pack(fill="x", pady=2)

        self.show_frame("TP0")

    def register_tp(self, name, frame_class):
        frame = frame_class(self.content_frame)
        self.frames[name] = frame
        frame.pack(fill="both", expand=True)
        frame.forget()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.forget()
        self.frames[name].pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()

import tkinter as tk
from PIL import Image, ImageTk

class TTRGui:
    @staticmethod
    def create_modern_button(parent, text, x, y, width=10, height=2, font=12):
        colour1 = "#ae2907"
        colour2 = "#ae2907"
        colour3 = "#841804"
        colour4 = "#ffffff"

        button = tk.Button(
            parent,
            background=colour1,
            foreground=colour4,
            activebackground=colour3,
            activeforeground=colour4,
            highlightthickness=2,
            highlightbackground=colour2,
            highlightcolor="WHITE",
            width=width,
            height=height,
            border=0,
            cursor='hand1',
            text=text,
            font=('Arial', font, 'bold')
        )
        button.place(x=x, y=y)
        return button

    @staticmethod
    def set_active_canvas_image(self, canvas_img_id, active_bool):
        if active_bool:
            # Görüntüyü görünür hale getir
            self.canvas.itemconfig(canvas_img_id, state=tk.NORMAL)
        else:
            # Görüntüyü gizle (deaktif yap)
            self.canvas.itemconfig(canvas_img_id, state=tk.HIDDEN)

    @staticmethod
    def change_image(self, canvas_img_id, canvas_img, new_image_path):
        current_image = canvas_img
        width, height = current_image.width(), current_image.height()

        new_image = Image.open(new_image_path)
        new_image = new_image.resize((width, height), Image.Resampling.LANCZOS)
        new_image_tk = ImageTk.PhotoImage(new_image)

        self.canvas.itemconfig(canvas_img_id, image=new_image_tk)

        return new_image_tk
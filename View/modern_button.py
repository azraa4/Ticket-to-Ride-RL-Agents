import tkinter as tk

class ModernButton(tk.Button):
    def __init__(self, parent, text, width=10, height=2, font_size=12, **kwargs):
        super().__init__(
            parent,
            background="#ae2907",  # Varsayılan arka plan rengi
            foreground="#ffffff",  # Varsayılan yazı rengi
            activebackground="#841804",  # Aktif arka plan rengi (hover)
            activeforeground="#ffffff",  # Aktif yazı rengi
            highlightthickness=2,  # Çerçeve kalınlığı
            highlightbackground="#d9390a",  # Çerçeve rengi
            highlightcolor="white",  # Çerçeve aktif renk
            width=width,  # Genişlik
            height=height,  # Yükseklik
            border=0,  # Kenar stili (düz görünüm için)
            cursor='hand1',  # İmleç tipi
            text=text,  # Düğme metni
            font=('Arial', font_size, 'bold'),  # Yazı tipi
            **kwargs  # Ek parametreler
        )

import tkinter as tk


class ModernOptionMenu(tk.OptionMenu):
    def __init__(self, master, variable, *values, **kwargs):
        super().__init__(master, variable, *values, **kwargs)
        # Seçili öğenin özelleştirilmesi
        self.config(
            bg="#ae2907",  # Kırmızı arka plan
            fg="white",  # Beyaz yazı rengi
            font=("Arial", 15, "bold"),  # Modern font
            relief="flat",  # Düz stil
            highlightthickness=0,  # Çerçeve kaldırıldı
            width=15  # Genişlik
        )

        # Dropdown menüsünün özelleştirilmesi
        menu = self.nametowidget(self.menuname)
        menu.config(
            bg="#ae2907",  # Menü arka planı (kırmızı)
            fg="white",  # Menü yazı rengi (beyaz)
            font=("Arial", 15, "bold")  # Menü yazı tipi
        )

        # Menüdeki öğelerin hover renklerinin ayarlanması
        for index, value in enumerate(values):
            padded_value = value.ljust(21)  # Öğeleri genişletmek için padding ekliyoruz
            menu.entryconfig(index, label=padded_value, background="#ae2907", foreground="white")  # Varsayılan renkler
            menu.entryconfig(index, activebackground="white", activeforeground="black")  # Hover renkleri

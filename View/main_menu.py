import tkinter as tk
from PIL import Image, ImageTk
from View.modern_option_menu import ModernOptionMenu

class MainMenu:
    def create_modern_button(self, parent, text, width=10, height=2, font=12):
        button = tk.Button(
            parent,
            background="#ae2907",
            foreground="#ffffff",
            activebackground="#841804",
            activeforeground="#ffffff",
            highlightthickness=2,
            highlightbackground="#d9390a",
            highlightcolor="WHITE",
            width=width,
            height=height,
            border=0,
            cursor='hand1',
            text=text,
            font=('Arial', font, 'bold')
        )
        return button
    def __init__(self, root, controller, start_game_callback):
        self.root = root
        self.controller = controller
        self.start_game_callback = start_game_callback
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")

        self.list_item_number = 0

        # Arka plan resmi ayarla
        self.background_image = Image.open("Assets/menu_background.jpg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self.frame, image=self.background_photo)
        self.background_label.place(relwidth=1, relheight=1)

        self.available_colors = ["Red", "Blue", "Green", "Yellow", "Black"]
        self.players = []  # Oyuncuları saklamak için bir liste

    def create_menu(self):
        # Bütün öğeleri sola dayamak için anchor ve side kullanarak pack fonksiyonlarını düzenledik
        self.create_add_player_section()

        start_button = self.create_modern_button(self.frame, "Start Game", width=23, height=1, font=20)
        start_button.config(command=self.start_game)
        start_button.pack(padx=65, pady=(0,5), anchor="w")

        quit_button = self.create_modern_button(self.frame, "Quit Game", width=23, height=1, font=20)
        quit_button.config(command=self.quit)
        quit_button.pack(padx=65, pady=(0,5), anchor="w")

        player_list_label = tk.Label(self.frame, text="Players List ", font=("Arial", 15, "bold"), fg="#ae2907",
                                     bg="#d5b570")
        player_list_label.pack(padx=65, pady=5, anchor="w")
        # Oyuncuları listelemek için bir liste alanı ekleyin
        self.player_listbox = tk.Listbox(self.frame, font=("Arial", 14, "bold"),  # Modern font
                                         bg="#d5b570",
                                         fg="#ae2907",
                                         selectbackground="#f4e1a1",
                                         selectforeground="black",
                                         relief="flat",
                                         activestyle="none",
                                         highlightthickness=0,
                                         width=40,
                                         height=5
                                         )
        self.player_listbox.pack(padx=65, pady=10, anchor="w")

    def create_add_player_section(self):
        self.player_name_var = tk.StringVar()
        player_name_frame = tk.Frame(self.frame, bg="#d5b570")
        player_name_frame.pack(padx=65, pady=(195, 0), anchor="w")
        player_name_label = tk.Label(player_name_frame, text="Player Name: ", font=("Arial", 20, "bold"), fg="#ae2907", bg="#d5b570")
        player_name_label.pack(side="left")
        player_name_entry = tk.Entry(
            player_name_frame,
            textvariable=self.player_name_var,
            font=("Arial", 19, "bold"),
            width=14,  # Genişlik
            bg="#f0f0f0",  # Arka plan rengi (modern açık gri)
            fg="#ae2907",
            relief="flat",  # Düz ve modern bir stil
            highlightbackground="#ccc",  # Çerçeve rengi
            highlightthickness=1  # Çerçeve kalınlığı
        )
        player_name_entry.pack(side="left")

        self.player_type_var = tk.StringVar(value="Select Type")
        player_type_frame = tk.Frame(self.frame, bg="#d5b570")
        player_type_frame.pack(padx=65, pady=5, anchor="w")
        player_type_label = tk.Label(player_type_frame, text="Player Type: ", font=("Arial", 20, "bold"), fg="#ae2907", bg="#d5b570")
        player_type_label.pack(side="left")
        player_type_options = ["Human", "RandomAgent", "AgentX"]
        player_type_dropdown = ModernOptionMenu(player_type_frame, self.player_type_var, *player_type_options)
        player_type_dropdown.pack(padx=11, side="left")

        self.color_var = tk.StringVar(value="Select a color")
        color_frame = tk.Frame(self.frame, bg="#d5b570")
        color_frame.pack(padx=65, pady=5, anchor="w")
        color_label = tk.Label(color_frame, text="Color: ", font=("Arial", 20, "bold"), fg="#ae2907", bg="#d5b570")
        color_label.pack(side="left")
        self.color_dropdown = ModernOptionMenu(color_frame, self.color_var, *self.available_colors)
        self.color_dropdown.pack(padx=(93,0),side="left")

        player_edit_frame = tk.Frame(self.frame, bg="#d5b570")

        add_player_button = self.create_modern_button(player_edit_frame, "Add Player", width=11, height=1, font=20)
        add_player_button.config(command=self.add_player)
        player_edit_frame.pack(padx=65, pady=10, anchor="w")
        add_player_button.pack(side="left", padx=(0,5))

        reset_players_list_button = self.create_modern_button(player_edit_frame, "Reset List", width=11, height=1, font=20)
        reset_players_list_button.config(command=self.reset_list)
        reset_players_list_button.pack(side="left")




    def add_player(self):
        player_name = self.player_name_var.get()
        selected_color = self.color_var.get()
        player_type = self.player_type_var.get()

        if len(player_name)>0 and selected_color != "Select a color" and player_type != "Select Type":
            # Oyuncu bilgilerini listeye ekle
            self.players.append((player_name, selected_color, player_type))

            self.list_item_number+=1
            self.player_listbox.insert(tk.END, f"Player {self.list_item_number}: {player_name} ({selected_color}) | {player_type}")

            print(f"GAME MENU: Player Added: {player_name} with color {selected_color}")
            self.controller.add_player_button(player_name, selected_color)
            if player_type == "RandomAgent":
                self.controller.add_ai(selected_color, player_type)
                print(f"GAME MENU: AI added with color {selected_color} and type {player_type}")
            elif player_type == "AgentX":
                self.controller.add_ai(selected_color, player_type)
                print(f"GAME MENU: AI added with color {selected_color} and type {player_type}")

            self.available_colors.remove(selected_color)
            self.update_color_dropdown()

            self.color_var.set("Select a color")

    def reset_list(self):
        self.controller.reset_player_list_button()
        self.players.clear()
        self.player_listbox.delete(0, tk.END)
        self.available_colors = ["Red", "Blue", "Green", "Yellow", "Black"]
        self.update_color_dropdown()

    def update_color_dropdown(self):
        """Dropdown menüsündeki renkleri güncelle"""
        menu = self.color_dropdown["menu"]
        menu.delete(0, "end")  # Eski seçenekleri kaldır
        for color in self.available_colors:
            menu.add_command(label=color, command=lambda value=color: self.color_var.set(value))

    def start_game(self):
        if len(self.players)>0:
            self.frame.pack_forget()
            self.start_game_callback()
        else:
            print("!     ERROR: Player Eklenmeli!")

    def force_start_game(self):
        self.frame.pack_forget()
        self.start_game_callback()

    def quit(self):
        self.root.destroy()
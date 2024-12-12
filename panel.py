import tkinter as tk
import multiprocessing
import os
import signal

class ControlPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game Control Panel")
        self.root.geometry("300x200")

        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(self.root, text="Stop Game", command=self.stop_game, state=tk.DISABLED)
        self.stop_button.pack(pady=20)

        self.game_process = None

    def start_game(self):
        if not self.game_process or not self.game_process.is_alive():
            self.game_process = multiprocessing.Process(target=self.run_game)
            self.game_process.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop_game(self):
        if self.game_process and self.game_process.is_alive():
            os.kill(self.game_process.pid, signal.SIGTERM)
            self.game_process.join()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    @staticmethod
    def run_game():
        os.system("python main_view.py")  # `main_view.py` dosyasının yolunu doğru yazın

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    panel = ControlPanel()
    panel.run()

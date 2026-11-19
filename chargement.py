import tkinter as tk
from tkinter import ttk
import pygame
from PIL import Image, ImageTk
import cv2
import time
import subprocess
import threading
import os
import sys



class ChargementApp:
    def __init__(self, root):
        self.root = root
        self.running = True  # Ajout d'un flag pour contrôler la boucle
        self.setup_window()
        self.create_widgets()
        self.play_music("b.mp3")  # Remplacez par votre chemin
        self.play_video("vid.mp4")  # Remplacez par votre chemin
        self.update_progress()

    def setup_window(self):
        self.root.title("Écran de Chargement")
        self.root.geometry("800x550")
        self.root.resizable(False, False)
        self.root.config(bg="black")
        pygame.mixer.init()

    def create_widgets(self):
        # Frame pour contenir la vidéo (maintient le ratio)
        self.video_frame = tk.Frame(self.root, bg="black")
        self.video_frame.place(relx=0.5, rely=0.4, anchor="center", width=800, height=450)

        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(fill="both", expand=True)

        self.progress = ttk.Progressbar(self.root, length=400)
        self.progress.place(relx=0.5, rely=0.85, anchor="center")

        self.loading_text = tk.Label(self.root, text="Chargement...",
                                     font=("Helvetica", 12), fg="white", bg="black")
        self.loading_text.place(relx=0.5, rely=0.9, anchor="center")

    def play_music(self, path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Erreur musique: {e}")

    def play_video(self, path):
        try:
            self.cap = cv2.VideoCapture(path)
            if not self.cap.isOpened():
                raise Exception("Impossible d'ouvrir la vidéo")

            self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Calculer le ratio pour le redimensionnement
            self.target_width = 800
            self.target_height = int(self.video_height * (self.target_width / self.video_width))

            self.update_video()
        except Exception as e:
            print(f"Erreur vidéo: {e}")

    def update_video(self):
        if not self.running:  # Ne pas mettre à jour si l'application est en train de fermer
            return

        try:
            ret, frame = self.cap.read()
            if ret:
                # Redimensionnement intelligent avec conservation du ratio
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img.thumbnail((self.target_width, self.target_height), Image.LANCZOS)

                # Centrer l'image
                bg = Image.new("RGB", (self.target_width, self.target_height), "black")
                bg.paste(img, ((self.target_width - img.width) // 2,
                               (self.target_height - img.height) // 2))

                imgtk = ImageTk.PhotoImage(image=bg)
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
                self.root.after(15, self.update_video)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.root.after(15, self.update_video)
        except Exception as e:
            if str(e) != "invalid command name \".!frame.!label\"":
                print(f"Erreur lors de la mise à jour vidéo: {e}")

    def update_progress(self):
        def _update():
            for i in range(101):
                if not self.running:
                    break
                self.progress['value'] = i
                self.root.update()
                time.sleep(0.15)

            # Cleanup
            self.running = False
            pygame.mixer.music.stop()
            if hasattr(self, 'cap'):
                self.cap.release()

            # Close window
            self.root.after(100, self.root.destroy)

            # Launch accueil.py
            time.sleep(0.5)
            try:
                # Use sys.argv[0] instead of __file__
                script_dir = os.path.dirname(sys.argv[0])
                script_path = os.path.join(script_dir, "accueil.py")

                # For debugging - print the path
                print(f"Attempting to launch: {script_path}")

                # Launch in a new console window (Windows)
                if os.name == 'nt':
                    subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen([sys.executable, script_path])
            except Exception as e:
                print(f"Error launching accueil.py: {e}")

        threading.Thread(target=_update, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChargementApp(root)
    root.mainloop()
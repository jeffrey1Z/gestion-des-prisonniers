from tkinter import *
from tkinter import ttk
from tkinter import messagebox
#
from PIL import Image, ImageTk
import photo
import subprocess
import sys
print("Python utilisé :", sys.executable)

# === Couleurs ===
COLOR_BACKGROUND_MAIN = "#F8F9FA"
COLOR_BORDER_SUBTLE = "#E9ECEF"
COLOR_TEXT_PRIMARY = "#343A40"
COLOR_BLUE_PRIMARY = "#007BFF"
COLOR_RED_ERROR = "#DC3545"

fenetre = Tk()
fenetre.title("Gestion de prisonniers")
fenetre.geometry("1000x600")
fenetre.config(background=COLOR_BORDER_SUBTLE)
fenetre.resizable(False, False)
def alternance(val):
    fenetre.destroy()
    subprocess.run(["python", val])
# === Partie titre ===
titre = Frame(fenetre, bd=20, bg=COLOR_BACKGROUND_MAIN)
titre.place(x=250, y=0, width=1050, height=50)

titre_label = Label(fenetre, text="Système de Gestion des Prisonniers", font=("Arial", 18, "bold"),
                    bg=COLOR_BACKGROUND_MAIN, fg=COLOR_TEXT_PRIMARY)
titre_label.place(x=400, y=10)

# === Menu latéral ===
titre2 = Frame(fenetre, bd=5, bg=COLOR_BACKGROUND_MAIN)
titre2.place(x=0, y=0, width=250, height=700)

# === Icônes menu avec animation glissante ===
def animer_icone(widget, x_start, x_end, y, delay=10, step=5):
    def animation():
        nonlocal x_start
        if x_start < x_end:
            x_start += step
            widget.place(x=x_start, y=y)
            fenetre.after(delay, animation)
        else:
            widget.place(x=x_end, y=y)
    animation()

icon = photo.generer_image(taille=(35, 35), chemin=r"C:/Users/HP/gestion des prisoniers/suspect.png")
gen = photo.icon(panel=titre2, position='left', texte='  Gestion Prisonniers', icon=icon, com=lambda:alternance(val="prisoniers.py"))
animer_icone(gen, x_start=-200, x_end=10, y=80)

icon_cellule = photo.generer_image(taille=(35, 35), chemin=r"C:/Users/HP/gestion des prisoniers/station.png")
gen_cellule = photo.icon(panel=titre2, position='left', texte='  Gestion des Cellule  ', icon=icon_cellule, com=lambda: alternance(val="cellule.py"))
animer_icone(gen_cellule, x_start=-200, x_end=10, y=140)

icon_visite = photo.generer_image(taille=(35, 35), chemin=r"C:/Users/HP/gestion des prisoniers/o.png")
gen_visite = photo.icon(panel=titre2, position='left', texte='  Gestion des Visite      ', icon=icon_visite, com=lambda:alternance(val="visite.py"))
animer_icone(gen_visite, x_start=-200, x_end=10, y=200)

icon_admin = photo.generer_image(taille=(35, 35), chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0026.jpg")
gen_admin = photo.icon(panel=titre2, position='left', texte=' Gestion des  Agent     ', icon=icon_admin, com=lambda: alternance(val="agents.py"))
animer_icone(gen_admin, x_start=-200, x_end=10, y=260)

# === Bouton de déconnexion ===
def graph():
    subprocess.run(["python", "directeur.py"])
def deconnexion():
    reponse = messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?")
    if reponse:
        fenetre.destroy()
        subprocess.run(["python", "connexion.py"])
btn_deconnexion = Button(titre2, text="Déconnexion", font=("Arial", 12), bg=COLOR_RED_ERROR, fg="white", command=deconnexion)
btn_deconnexion.place(x=60, y=500)

# === Zone centrale d’accueil avec animation pulsante ===
def pulsation(widget, size=150, delta=5, state=[1]):
    new_size = size + delta if state[0] else size - delta
    state[0] = not state[0]
    img = photo.generer_image(taille=(new_size, new_size), chemin=widget.chemin)
    widget.config(image=img)
    widget.image = img
    fenetre.after(600, pulsation, widget, size, delta, state)

icon2 = photo.generer_image(taille=(150, 150), chemin=r"C:/Users/HP/gestion des prisoniers/o.png")
gen2 = photo.icon(panel=fenetre, position='center', texte='', icon=icon2, com='')
gen2.chemin = r"C:/Users/HP/gestion des prisoniers/list.png"
gen2.place(x=450, y=250)
gen2.config(background=COLOR_BORDER_SUBTLE)
pulsation(gen2)

icon3 = photo.generer_image(taille=(150, 150), chemin=r"C:/Users/HP/gestion des prisoniers/te.png")
gen3 = photo.icon(panel=fenetre, position='center', texte='', icon=icon3, com=lambda: graph())
gen3.chemin = r"C:/Users/HP/gestion des prisoniers/te.png"
gen3.place(x=650, y=250)
gen3.config(background=COLOR_BORDER_SUBTLE)
pulsation(gen3)
# Durée maximale d'inactivité en millisecondes (ex: 60 000 ms = 1 minute)
TEMPS_INACTIVITE = 60000  # 60 secondes
timer_inactivite = None

# Fonction appelée lorsqu'on détecte une inactivité prolongée
def deconnexion_automatique():
    messagebox.showwarning("Inactivité", "Vous avez été déconnecté pour inactivité.")
    fenetre.destroy()
    subprocess.run(["python", "connexion.py"])  # Redirige vers ta page de connexion

# Réinitialise le timer à chaque activité détectée
def reinitialiser_inactivite(event=None):
    global timer_inactivite
    if timer_inactivite:
        fenetre.after_cancel(timer_inactivite)
    timer_inactivite = fenetre.after(TEMPS_INACTIVITE, deconnexion_automatique)

# Bind tous les événements d’activité utilisateur
evenements_utilisateur = ["<Motion>", "<Key>", "<Button>"]
for event in evenements_utilisateur:
    fenetre.bind_all(event, reinitialiser_inactivite)

# Démarrer le timer d’inactivité au lancement
reinitialiser_inactivite()

fenetre.mainloop()

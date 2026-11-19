efrom tkinter import *
from tkinter import ttk
from tkinter import ttk, messagebox
import mysql.connector
import time
from PIL import Image, ImageTk
import photo
import crud
import subprocess

COLOR_BACKGROUND_MAIN = "#F8F9FA"
COLOR_BORDER_SUBTLE = "#E9ECEF"
COLOR_TEXT_SECONDARY = "#6C757D"
COLOR_TEXT_PRIMARY = "#343A40"
COLOR_BLUE_PRIMARY = "#007BFF"
COLOR_BLUE_HOVER = "#0056B3"
COLOR_GREEN_SUCCESS = "#28A745"
COLOR_RED_ERROR = "#DC3545"
COLOR_ORANGE_WARNING = "#FFC107"

fenetre = Tk()
fenetre.title("Gestion de prisonniers")
fenetre.geometry("1300x700")
fenetre.config(background=COLOR_BORDER_SUBTLE)
fenetre.resizable(False, False)

# Cadres principaux
titre = Frame(fenetre, bd=20, bg=COLOR_BACKGROUND_MAIN)
titre.place(x=300, y=0, width=1000, height=200)

titre2 = Frame(fenetre, bd=20, bg=COLOR_BACKGROUND_MAIN)
titre2.place(x=0, y=0, width=300, height=700)

Label(titre, text="GESTION DES CELLULES", font=("Arial", 16, "bold"), bg=COLOR_BACKGROUND_MAIN).pack(side=TOP,
                                                                                                            fill=X)
# Champs de formulaire
numerocellule = Label(fenetre, text="Numero cellule", fg="black", font=("Bell MT", 10))
numerocellule.place(x=10, y=120)

numerocelluleentre = ttk.Combobox(fenetre, width=18)
numerocelluleentre['values'] = [str(i) for i in range(1, 1001)]
numerocelluleentre.place(x=150, y=120)

capacite = Label(fenetre, text="Capacite (m²)", background=COLOR_BACKGROUND_MAIN, fg="black", font=("Bell MT", 10))
capacite.place(x=10, y=150)

capaciteentre = ttk.Combobox(fenetre, width=18)
capaciteentre['values'] = [f"{i}m²" for i in range(10, 101, 10)]
capaciteentre.place(x=150, y=150)

type_label = Label(fenetre, text="Type", fg="black", font=("Bell MT", 10))
type_label.place(x=10, y=180)

typeentre = ttk.Combobox(fenetre, width=18)
typeentre['values'] = ['Partagé', 'Isolement', 'Haute sécurité', 'Quarantaine', 'Protection']
typeentre.place(x=150, y=180)

occupants_label = Label(fenetre, text="Nombre occupants", fg="black", font=("Bell MT", 10))
occupants_label.place(x=10, y=210)

occupants_entre = ttk.Combobox(fenetre, width=18)
occupants_entre['values'] = [str(i) for i in range(1, 11)]
occupants_entre.place(x=150, y=210)

# Treeview pour afficher les cellules
colonnes = ("id_cellule","numero", "capacite", "type", "occupants")
tree = ttk.Treeview(fenetre, columns=colonnes, show="headings", height=30)
tree.place(x=300, y=100, width=1000, height=600)

# Configuration des
tree.heading("id_cellule", text="id")
tree.heading("numero", text="Numéro")
tree.heading("capacite", text="Capacité (m²)")
tree.heading("type", text="Type")
tree.heading("occupants", text="Occupants")

tree.column("numero", width=100, anchor=CENTER)
tree.column("capacite", width=150, anchor=CENTER)
tree.column("type", width=200, anchor=CENTER)
tree.column("occupants", width=100, anchor=CENTER)


# Fonction pour rafraîchir l'affichage des cellules
def afficher_cellules():
    try:
        # Effacer les données existantes
        for item in tree.get_children():
            tree.delete(item)

        # Connexion à la base de données
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gestion_prisonier"
        )
        curseur = conn.cursor()

        # Récupération des données
        curseur.execute("SELECT id, numero, capacite, type, occupant FROM cellules")
        cellules = curseur.fetchall()

        # Insertion dans le Treeview
        for cellule in cellules:
            tree.insert("", END, values=cellule)

        conn.close()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement : {e}")


# ... (le reste du code existant avant cette partie)

# === FONCTION POUR OUVRIRE LA FENETRE DE RECHERCHE ===
def ouvrir_recherche_cellule():
    fen_recherche = Toplevel(fenetre)
    fen_recherche.title("Rechercher une cellule")
    fen_recherche.geometry("500x300+400+200")
    fen_recherche.config(bg=COLOR_BACKGROUND_MAIN)
    fen_recherche.resizable(False, False)
    fen_recherche.grab_set()  # Rend la fenêtre modale

    # Titre
    Label(fen_recherche, text="Rechercher une cellule", font=("Arial", 14, "bold"),
          bg=COLOR_BACKGROUND_MAIN, fg=COLOR_BLUE_PRIMARY).pack(pady=10)

    # Frame pour les critères
    criteres_frame = Frame(fen_recherche, bg=COLOR_BACKGROUND_MAIN)
    criteres_frame.pack(pady=10)

    # Critère de recherche
    Label(criteres_frame, text="Rechercher par:", bg=COLOR_BACKGROUND_MAIN).grid(row=0, column=0, padx=5)
    critere_combo = ttk.Combobox(criteres_frame,
                                 values=["Numéro", "Type", "Capacité", "Occupants"],
                                 width=15)
    critere_combo.grid(row=0, column=1, padx=5)
    critere_combo.current(0)

    # Valeur à rechercher
    Label(criteres_frame, text="Valeur:", bg=COLOR_BACKGROUND_MAIN).grid(row=1, column=0, padx=5)
    valeur_entry = Entry(criteres_frame, width=30)
    valeur_entry.grid(row=1, column=1, padx=5)
    valeur_entry.focus()

    # Boutons
    btn_frame = Frame(fen_recherche, bg=COLOR_BACKGROUND_MAIN)
    btn_frame.pack(pady=20)

    btn_rechercher = Button(btn_frame, text="Rechercher", width=15,
                            command=lambda: executer_recherche_cellule(
                                critere_combo.get(),
                                valeur_entry.get(),
                                fen_recherche
                            ))
    btn_rechercher.grid(row=0, column=0, padx=10)

    btn_annuler = Button(btn_frame, text="Annuler", width=15, command=fen_recherche.destroy)
    btn_annuler.grid(row=0, column=1, padx=10)


# === FONCTION DE RECHERCHE ===
def executer_recherche_cellule(critere, valeur, fen_recherche):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gestion_prisonier"
        )
        curseur = conn.cursor()

        # Construction de la requête en fonction du critère
        if critere == "Numéro":
            requete = "SELECT id, numero, capacite, type, occupant FROM cellules WHERE numero LIKE %s"
            parametres = (f"%{valeur}%",)
        elif critere == "Type":
            requete = "SELECT id, numero, capacite, type, occupant FROM cellules WHERE type LIKE %s"
            parametres = (f"%{valeur}%",)
        elif critere == "Capacité":
            requete = "SELECT id, numero, capacite, type, occupant FROM cellules WHERE capacite = %s"
            parametres = (valeur.replace("m²", ""),)
        else:  # Occupants
            requete = "SELECT id, numero, capacite, type, occupant FROM cellules WHERE occupant = %s"
            parametres = (valeur,)

        curseur.execute(requete, parametres)
        cellules = curseur.fetchall()
        conn.close()

        if not cellules:
            messagebox.showinfo("Information", "Aucune cellule trouvée")
            return

        # Effacer les anciens résultats
        for item in tree.get_children():
            tree.delete(item)

        # Afficher les résultats
        for cellule in cellules:
            tree.insert("", END, values=cellule)

        # Fermer la fenêtre de recherche
        fen_recherche.destroy()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur recherche cellules: {e}")


# ... (le reste du code existant)

# Modifier la création du bouton recherche pour utiliser la nouvelle fonction
icon_recherche = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tel1.png")
bouton_recherche = Button(titre,
                          image=icon_recherche,
                          bg=COLOR_BACKGROUND_MAIN,
                          command=ouvrir_recherche_cellule,
                          borderwidth=0)
bouton_recherche.image = icon_recherche
bouton_recherche.place(x=1000, y=5)


# ... (le reste du code existant)

# Fonction pour enregistrer une nouvelle cellule
def enregistrer_prisonnier():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gestion_prisonier"
        )
        curseur = conn.cursor()

        num = numerocelluleentre.get()
        capacite = capaciteentre.get().replace("m²", "")
        type_cellule = typeentre.get()
        occupants = occupants_entre.get()

        requete = """
        INSERT INTO cellules (numero, capacite, type, occupant)
        VALUES (%s, %s, %s, %s)
        """
        valeurs = (num, capacite, type_cellule, occupants)

        curseur.execute(requete, valeurs)
        conn.commit()
        messagebox.showinfo("Succès", "Cellule enregistrée avec succès.")
        conn.close()
        afficher_cellules()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur : {e}")


# Fonction pour modifier une cellule existante
def modifier_cellule():
    try:
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une cellule à modifier")
            return

        valeurs = tree.item(selected_item, 'values')

        # Pré-remplir les champs avec les valeurs sélectionnées
        numerocelluleentre.delete(0, END)
        numerocelluleentre.insert(0, valeurs[0])

        capaciteentre.delete(0, END)
        capaciteentre.insert(0, f"{valeurs[1]}m²")

        typeentre.delete(0, END)
        typeentre.insert(0, valeurs[2])

        occupants_entre.delete(0, END)
        occupants_entre.insert(0, valeurs[3])

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la sélection : {e}")


# Fonction pour supprimer une cellule
def supprimer_cellule():
    try:
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une cellule à supprimer")
            return

        reponse = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette cellule?")
        if reponse:
            numero_cellule = tree.item(selected_item, 'values')[0]

            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="gestion_prisonier"
            )
            curseur = conn.cursor()

            curseur.execute("DELETE FROM cellules WHERE id = %s", (numero_cellule,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Cellule supprimée avec succès")
            afficher_cellules()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")


# Barre de recherche


# Boutons avec icônes
icon = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tabs.png")
gen = photo.icon(panel=fenetre, position='top', texte='ajouter', icon=icon, com=enregistrer_prisonnier)
gen.place(x=30, y=610)

icon2 = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0035.jpg")
gen2 = photo.icon(panel=fenetre, position='top', texte='modifier', icon=icon2, com=modifier_cellule)
gen2.place(x=110, y=610)

icon3 = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0041.jpg")
gen3 = photo.icon(panel=fenetre, position='top', texte='supprimer', icon=icon3, com=supprimer_cellule)
gen3.place(x=200, y=610)

icon4 = photo.generer_image(taille=(150, 80), chemin=r"C:/Users/HP/gestion des prisoniers/i.png")
gen4 = photo.icon(panel=fenetre, position='top', texte='', icon=icon4, com='')
gen4.place(x=10, y=10)

icon_recherche = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tel1.png")
photo.icon(panel=fenetre, position='top', texte='Rechercher', icon=icon_recherche, com=ouvrir_recherche_cellule).place(x=1000,
                                                                                                                y=5)

icon6 = photo.generer_image(taille=(40, 40), chemin=r"C:/Users/HP/gestion des prisoniers/m.jpg")
gen6 = photo.icon(panel=fenetre, position='top', texte='', icon=icon6, com= lambda : alternance(val = ("accueil.py")))
gen6.place(x=250, y=5)

# Afficher les cellules au démarrage
afficher_cellules()
def alternance(val):
    fenetre.destroy()
    subprocess.run(["python", val])

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

from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import mysql.connector
import hashlib
import photo
import subprocess

# === Récupération du rôle utilisateur ===
try:
    with open("session_role.txt", "r") as fichier:
        user_role = fichier.read().strip()
except FileNotFoundError:
    user_role = None

# === Couleurs ===
COLOR_BACKGROUND_MAIN = "#F8F9FA"
COLOR_BORDER_SUBTLE = "#E9ECEF"
COLOR_TEXT_PRIMARY = "#343A40"
COLOR_BLUE_PRIMARY = "#007BFF"
COLOR_RED_ERROR = "#DC3545"

# === Fenêtre principale ===
fenetre = Tk()
fenetre.title("Gestion de prisonniers")
fenetre.geometry("1300x700")
fenetre.config(background=COLOR_BORDER_SUBTLE)
fenetre.resizable(False, False)

# === Onglet Visites ===
frame_visite = Frame(fenetre, bg=COLOR_BACKGROUND_MAIN)
frame_visite.place(x=0, y=0, width=310, height=690)

titre = Frame(fenetre, bd=20, bg=COLOR_BACKGROUND_MAIN)
titre.place(x=300, y=0, width=1000, height=200)

labels_visite = ["ID Prisonnier", "Nom visiteur", "Nom prisonnier", "Date visite", "Lien avec détenu"]
entries_visite = {}

# Position de départ
start_y = 100  # Position Y initiale
y_step = 50  # Espacement vertical entre les champs

# ID Prisonnier
Label(frame_visite, text="ID Prisonnier", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=start_y)
combo_id_prisonnier = ttk.Combobox(frame_visite, width=20)
combo_id_prisonnier.place(x=150, y=start_y)
entries_visite["ID Prisonnier"] = combo_id_prisonnier

# Nom visiteur
Label(frame_visite, text="Nom visiteur", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=start_y + y_step)
entry_nom_visiteur = Entry(frame_visite, width=20)
entry_nom_visiteur.place(x=150, y=start_y + y_step)
entries_visite["Nom visiteur"] = entry_nom_visiteur

# Nom prisonnier
Label(frame_visite, text="Nom prisonnier", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=start_y + 2 * y_step)
entry_nom_prisonnier = Entry(frame_visite, width=20, state="readonly")
entry_nom_prisonnier.place(x=150, y=start_y + 2 * y_step)
entries_visite["Nom prisonnier"] = entry_nom_prisonnier

# Date visite
Label(frame_visite, text="Date visite", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=start_y + 3 * y_step)
entry_date_visite = DateEntry(frame_visite, width=20, date_pattern="yyyy-mm-dd")
entry_date_visite.place(x=150, y=start_y + 3 * y_step)
entries_visite["Date visite"] = entry_date_visite

# Lien avec détenu
Label(frame_visite, text="Lien avec détenu", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=start_y + 4 * y_step)
entry_lien = Entry(frame_visite, width=20)
entry_lien.place(x=150, y=start_y + 4 * y_step)
entries_visite["Lien avec détenu"] = entry_lien

try:
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
    curseur = conn.cursor()
    curseur.execute("SELECT id, nom FROM prisonniers")
    prisonnier_data = curseur.fetchall()
    conn.close()
    combo_id_prisonnier["values"] = [str(pid) for pid, _ in prisonnier_data]

    # Associer ID et nom dans un dictionnaire
    id_to_nom = {str(pid): nom for pid, nom in prisonnier_data}


    def update_nom_prisonnier(event):
        selected_id = combo_id_prisonnier.get()
        nom = id_to_nom.get(selected_id, "")
        entry_nom_prisonnier.config(state="normal")
        entry_nom_prisonnier.delete(0, END)
        entry_nom_prisonnier.insert(0, nom)
        entry_nom_prisonnier.config(state="readonly")


    combo_id_prisonnier.bind("<<ComboboxSelected>>", update_nom_prisonnier)

except Exception as e:
    messagebox.showerror("Erreur", f"Chargement ID prisonniers : {e}")

# === Table Visites ===
frame_table_visite = Frame(fenetre, bg="white", bd=2, relief=RIDGE)
frame_table_visite.place(x=320, y=100, width=950, height=600)

scroll_y_v = Scrollbar(frame_table_visite, orient=VERTICAL)
scroll_x_v = Scrollbar(frame_table_visite, orient=HORIZONTAL)

colonnes_visite = ("ID", "Prisonnier ID", "Nom visiteur", "Nom prisonnier", "Date visite", "Lien avec détenu")
table_visite = ttk.Treeview(frame_table_visite, columns=colonnes_visite, yscrollcommand=scroll_y_v.set,
                            xscrollcommand=scroll_x_v.set)
scroll_y_v.pack(side=RIGHT, fill=Y)
scroll_x_v.pack(side=BOTTOM, fill=X)
scroll_y_v.config(command=table_visite.yview)
scroll_x_v.config(command=table_visite.xview)
table_visite.pack(fill=BOTH, expand=True)

for col in colonnes_visite:
    table_visite.heading(col, text=col)
    table_visite.column(col, width=120)
table_visite["show"] = "headings"


# === Fonctions CRUD ===
def charger_visites():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("SELECT * FROM visites")
        lignes = curseur.fetchall()
        conn.close()

        table_visite.delete(*table_visite.get_children())
        for ligne in lignes:
            table_visite.insert("", END, values=ligne)

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur chargement visites : {e}")


def rechercher_visite():
    critere = simpledialog.askstring("Recherche", "Entrez un nom (visiteur ou prisonnier) ou date :")
    if not critere:
        return
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        query = """
            SELECT * FROM visites
            WHERE nom_visiteur LIKE %s OR nom_prisonier LIKE %s OR date_visite = %s
        """
        curseur.execute(query, (f"%{critere}%", f"%{critere}%", critere))
        resultats = curseur.fetchall()
        conn.close()

        table_visite.delete(*table_visite.get_children())
        for ligne in resultats:
            table_visite.insert("", END, values=ligne)

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur recherche : {e}")


def ajouter_visite():
    data = [entries_visite[label].get() for label in labels_visite]
    if any(d == '' for d in data):
        messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
        return
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute(
            "INSERT INTO visites (prisonnier_id, nom_visiteur, nom_prisonier, date_visite, lien_avec_detenu) VALUES (%s, %s, %s, %s, %s)",
            tuple(data))
        conn.commit()
        conn.close()
        charger_visites()
        messagebox.showinfo("Succès", "Visite enregistrée.")
        vider_champs_visite()  # Vider les champs après ajout
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur ajout : {e}")


def modifier_visite():
    selected = table_visite.focus()
    if not selected:
        messagebox.showwarning("Sélection", "Veuillez sélectionner une visite.")
        return
    id_visite = table_visite.item(selected)['values'][0]
    data = [entries_visite[label].get() for label in labels_visite]
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute(
            "UPDATE visites SET prisonnier_id=%s, nom_visiteur=%s, nom_prisonier=%s, date_visite=%s, lien_avec_detenu=%s WHERE id=%s",
            tuple(data + [id_visite]))
        conn.commit()
        conn.close()
        charger_visites()
        messagebox.showinfo("Succès", "Visite modifiée.")
        vider_champs_visite()  # Vider les champs après modification
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur modif : {e}")


def supprimer_visite():
    selected = table_visite.focus()
    if not selected:
        messagebox.showwarning("Sélection", "Veuillez sélectionner une visite.")
        return
    id_visite = table_visite.item(selected)['values'][0]
    confirm = messagebox.askyesno("Confirmer", "Supprimer cette visite ?")
    if not confirm:
        return
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("DELETE FROM visites WHERE id=%s", (id_visite,))
        conn.commit()
        conn.close()
        charger_visites()
        messagebox.showinfo("Succès", "Visite supprimée.")
        vider_champs_visite()  # Vider les champs après suppression
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur suppression : {e}")


def selectionner_visite(event):
    selected = table_visite.focus()
    if not selected:
        return
    valeurs = table_visite.item(selected, 'values')
    if not valeurs:
        return

    try:
        # ID Prisonnier
        combo_id_prisonnier.set(valeurs[1])

        # Mise à jour manuelle du nom prisonnier
        entry_nom_prisonnier.config(state="normal")
        entry_nom_prisonnier.delete(0, END)
        entry_nom_prisonnier.insert(0, valeurs[3])
        entry_nom_prisonnier.config(state="readonly")

        # Autres champs
        entry_nom_visiteur.delete(0, END)
        entry_nom_visiteur.insert(0, valeurs[2])

        # Gestion de la date
        if valeurs[4]:  # Si la date existe
            entry_date_visite.set_date(valeurs[4])
        else:
            entry_date_visite.set_date(None)

        entry_lien.delete(0, END)
        entry_lien.insert(0, valeurs[5])

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la sélection: {e}")


def vider_champs_visite():
    combo_id_prisonnier.set('')
    entry_nom_visiteur.delete(0, END)

    entry_nom_prisonnier.config(state="normal")
    entry_nom_prisonnier.delete(0, END)
    entry_nom_prisonnier.config(state="readonly")

    entry_date_visite.set_date(None)
    entry_lien.delete(0, END)


def alternance(val):
    fenetre.destroy()
    subprocess.run(["python", val])


# === Boutons avec icones ===
icon_ajouter = photo.generer_image(taille=(20, 20), chemin="C:/Users/HP/gestion des prisoniers/tabs.png")
photo.icon(panel=frame_visite, position='top', texte='Ajouter', icon=icon_ajouter, com=ajouter_visite).place(x=10,
                                                                                                             y=600)

icon_modifier = photo.generer_image(taille=(20, 20),
                                    chemin="C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0035.jpg")
photo.icon(panel=frame_visite, position='top', texte='Modifier', icon=icon_modifier, com=modifier_visite).place(x=110,
                                                                                                                y=600)

icon_supprimer = photo.generer_image(taille=(20, 20),
                                     chemin="C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0041.jpg")
photo.icon(panel=frame_visite, position='top', texte='Supprimer', icon=icon_supprimer, com=supprimer_visite).place(
    x=210, y=600)

icon_recherche = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tel1.png")
photo.icon(panel=fenetre, position='top', texte='Rechercher', icon=icon_recherche, com=rechercher_visite).place(x=1000,
                                                                                                                y=5)

icon6 = photo.generer_image(taille=(40, 40), chemin=r"C:/Users/HP/gestion des prisoniers/m.jpg")
gen6 = Button(fenetre, image=icon6, command=lambda: alternance("accueil.py"))
gen6.image = icon6
gen6.place(x=250, y=5)

icon4 = photo.generer_image(taille=(150, 80), chemin=r"C:/Users/HP/gestion des prisoniers/i.png")
gen4 = Label(fenetre, image=icon4)
gen4.image = icon4
gen4.place(x=10, y=10)

# === Lier l'événement de sélection ===
table_visite.bind('<<TreeviewSelect>>', selectionner_visite)

# === Chargement initial ===
charger_visites()

Label(titre, text="GESTION DES VISITES", font=("Arial", 16, "bold"), bg=COLOR_BACKGROUND_MAIN).pack(side=TOP,
                                                                                                    fill=X)

# === Lancer l'app principale ===
fenetre.after(100, lambda: None)
fenetre.mainloop()
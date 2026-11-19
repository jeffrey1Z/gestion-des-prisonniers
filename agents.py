from tkinter import *
from tkinter import ttk, messagebox, simpledialog

from patsy.state import center
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import mysql.connector
import hashlib
import photo
import subprocess
import os

# === Récupération du rôle utilisateur et email ===
try:
    with open("session_role.txt", "r") as fichier:
        session_data = fichier.readlines()
        user_role = session_data[0].strip()
        user_email = session_data[1].strip()
except FileNotFoundError:
    user_role = None
    user_email = None


# === Fonction de vérification de l'ancien mot de passe ===
def verifier_ancien_mot_de_passe(mot_de_passe_en_base):
    ancien_mdp = simpledialog.askstring("Vérification", "Entrez votre ancien mot de passe :", show='*')
    if ancien_mdp is None:
        return False
    if hashlib.sha256(ancien_mdp.encode()).hexdigest() != mot_de_passe_en_base:
        messagebox.showerror("Erreur", "Mot de passe incorrect !")
        return False
    return True


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

form_frame = Frame(fenetre, bg=COLOR_BACKGROUND_MAIN)
form_frame.place(x=0, y=0, width=300, height=700)
titre = Frame(fenetre, bd=20, bg=COLOR_BACKGROUND_MAIN)
titre.place(x=300, y=0, width=1000, height=200)


# === Fonctions ===
def hash_mot_de_passe(mot_de_passe):
    return hashlib.sha256(mot_de_passe.encode()).hexdigest()


def charger_donnees_table():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute(
            "SELECT id_admin, nom, postnom, date_naissance, lieu_de_naissance, adress, telephone, etat_civil, sexe, mail, role, description FROM admin ORDER BY id_admin DESC")
        lignes = curseur.fetchall()
        conn.close()

        table_admin.delete(*table_admin.get_children())
        for ligne in lignes:
            table_admin.insert("", END, values=ligne)

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement des données : {e}")


# === Tableau Admins ===
table_frame = Frame(fenetre, bg="white", bd=2, relief=RIDGE)
table_frame.place(x=300, y=100, width=980, height=580)

scroll_y = Scrollbar(table_frame, orient=VERTICAL)
scroll_x = Scrollbar(table_frame, orient=HORIZONTAL)

colonnes = (
    "ID", "Nom", "Postnom", "Date de naissance", "Lieu de naissance", "Adresse", "Téléphone", "État civil", "Sexe",
    "Email",
    "Rôle", "Description")
table_admin = ttk.Treeview(table_frame, columns=colonnes, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_x.pack(side=BOTTOM, fill=X)
scroll_y.config(command=table_admin.yview)
scroll_x.config(command=table_admin.xview)
table_admin.pack(fill=BOTH, expand=True)

for col in colonnes:
    table_admin.heading(col, text=col)
    table_admin.column(col, width=100)
table_admin["show"] = "headings"

# === Champs de saisie (pour ajout et modif) ===
frame_form = Frame(fenetre, bg=COLOR_BACKGROUND_MAIN)
frame_form.place(x=10, y=100, width=280, height=500)

labels = ["Nom", "Postnom", "Date de naissance", "Lieu de naissance", "Adresse", "Téléphone", "État civil", "Sexe",
          "Email", "Rôle", "Description"]
entries = {}

# Position de départ
start_y = 20  # Position Y initiale
y_step = 30  # Espacement vertical entre les champs

for idx, label_text in enumerate(labels):
    # Label
    Label(frame_form, text=label_text, bg=COLOR_BACKGROUND_MAIN).place(x=10, y=start_y + idx * y_step)

    # Champ correspondant
    if label_text == "Date de naissance":
        entry = DateEntry(frame_form, width=20, date_pattern="yyyy-mm-dd")
    elif label_text == "Sexe":
        entry = ttk.Combobox(frame_form, values=["M", "F"], width=20)
    elif label_text == "Rôle":
        entry = ttk.Combobox(frame_form, values=["Agent", "Administrateur", "Directeur"], width=20)
    else:
        entry = Entry(frame_form, width=20)

    entry.place(x=150, y=start_y + idx * y_step)
    entries[label_text] = entry
# === Fonction pour remplir les champs lors de la sélection ===
def remplir_champs(event):
    item_selectionne = table_admin.focus()
    if not item_selectionne:
        return

    valeurs = table_admin.item(item_selectionne)['values']
    for i, label in enumerate(labels):
        entries[label].delete(0, END)
        entries[label].insert(0, valeurs[i + 1])  # +1 pour sauter l'ID


table_admin.bind("<ButtonRelease-1>", remplir_champs)


# === Fonctions CRUD ===
def ajouter_admin():
    valeurs = [entries[label].get() for label in labels]

    # Vérification des champs obligatoires
    if not valeurs[0] or not valeurs[1] or not valeurs[8]:
        messagebox.showerror("Erreur", "Nom, Postnom et Email sont obligatoires!")
        return

    # Demander le mot de passe initial
    mdp = simpledialog.askstring("Mot de passe", "Définir le mot de passe:", show='*')
    if not mdp:
        return

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()

        # Hacher le mot de passe
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()

        # Insertion des données avec mot de passe
        curseur.execute("""
            INSERT INTO admin (nom, postnom, date_naissance, lieu_de_naissance, adress, 
            telephone, etat_civil, sexe, mail, role, description, mdp) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, valeurs + [mdp_hash])

        conn.commit()
        conn.close()

        messagebox.showinfo("Succès", "Administrateur ajouté avec succès!")
        charger_donnees_table()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {e}")


# ... (le reste du code existant avant cette partie)

# === FONCTION POUR OUVRIRE LA FENETRE DE RECHERCHE ===
def ouvrir_recherche_admin():
    fen_recherche = Toplevel(fenetre)
    fen_recherche.title("Rechercher un administrateur")
    fen_recherche.geometry("500x300+400+200")
    fen_recherche.config(bg=COLOR_BACKGROUND_MAIN)
    fen_recherche.resizable(False, False)
    fen_recherche.grab_set()  # Rend la fenêtre modale

    # Titre
    Label(fen_recherche, text="Rechercher un administrateur", font=("Arial", 14, "bold"),
          bg=COLOR_BACKGROUND_MAIN, fg=COLOR_BLUE_PRIMARY).pack(pady=10)

    # Frame pour les critères
    criteres_frame = Frame(fen_recherche, bg=COLOR_BACKGROUND_MAIN)
    criteres_frame.pack(pady=10)

    # Critère de recherche
    Label(criteres_frame, text="Rechercher par:", bg=COLOR_BACKGROUND_MAIN).grid(row=0, column=0, padx=5)
    critere_combo = ttk.Combobox(criteres_frame, values=["ID", "Nom", "Postnom", "Email", "Rôle"], width=15)
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
                            command=lambda: executer_recherche_admin(
                                critere_combo.get(),
                                valeur_entry.get(),
                                fen_recherche
                            ))
    btn_rechercher.grid(row=0, column=0, padx=10)

    btn_annuler = Button(btn_frame, text="Annuler", width=15, command=fen_recherche.destroy)
    btn_annuler.grid(row=0, column=1, padx=10)


# === FONCTION DE RECHERCHE ===
def executer_recherche_admin(critere, valeur, fen_recherche):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()

        # Construction de la requête en fonction du critère
        if critere == "ID":
            requete = "SELECT id_admin, nom, postnom, date_naissance, lieu_de_naissance, adress, telephone, etat_civil, sexe, mail, role, description FROM admin WHERE id_admin = %s"
            parametres = (valeur,)
        elif critere == "Nom":
            requete = "SELECT id_admin, nom, postnom, date_naissance, lieu_de_naissance, adress, telephone, etat_civil, sexe, mail, role, description FROM admin WHERE nom LIKE %s"
            parametres = (f"%{valeur}%",)
        elif critere == "Postnom":
            requete = "SELECT id_admin, nom, postnom, date_naissance, lieu_de_naissance, adress, telephone, etat_civil, sexe, mail, role, description FROM admin WHERE postnom LIKE %s"
            parametres = (f"%{valeur}%",)
        elif critere == "Email":
            requete = "SELECT id_admin, nom, postnom, date_naissance, lieu_de_naissance, adress, telephone, etat_civil, sexe, mail, role, description FROM admin WHERE mail LIKE %s"
            parametres = (f"%{valeur}%",)
        else:  # Rôle
            requete = "SELECT id_admin, nom, postnom, date_naissance, lieu_de_naissance, adress, telephone, etat_civil, sexe, mail, role, description FROM admin WHERE role = %s"
            parametres = (valeur,)

        curseur.execute(requete, parametres)
        lignes = curseur.fetchall()
        conn.close()

        if not lignes:
            messagebox.showinfo("Information", "Aucun administrateur trouvé")
            return

        # Mettre à jour le tableau principal
        table_admin.delete(*table_admin.get_children())
        for ligne in lignes:
            table_admin.insert("", END, values=ligne)

        # Fermer la fenêtre de recherche
        fen_recherche.destroy()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur recherche administrateurs: {e}")


# ... (le reste du code existant)

# Modifier la création du bouton recherche pour utiliser la nouvelle fonction
icon_recherche = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tel1.png")
bouton_recherche = Button(titre, image=icon_recherche, bg=COLOR_BACKGROUND_MAIN,
                          command=ouvrir_recherche_admin, borderwidth=0)
bouton_recherche.image = icon_recherche
bouton_recherche.place(x=1000, y=5)


# ... (le reste du code existant)
def modifier_admin():
    item_selectionne = table_admin.focus()
    if not item_selectionne:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un administrateur à modifier")
        return

    id_admin = table_admin.item(item_selectionne)['values'][0]
    nouvelles_valeurs = [entries[label].get() for label in labels]

    # Vérification des champs obligatoires
    if not nouvelles_valeurs[0] or not nouvelles_valeurs[1] or not nouvelles_valeurs[8]:
        messagebox.showerror("Erreur", "Nom, Postnom et Email sont obligatoires!")
        return

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()

        # Mise à jour des données
        curseur.execute("""
            UPDATE admin SET 
            nom=%s, postnom=%s, date_naissance=%s, lieu_de_naissance=%s, adress=%s, 
            telephone=%s, etat_civil=%s, sexe=%s, mail=%s, role=%s, description=%s 
            WHERE id_admin=%s
        """, nouvelles_valeurs + [id_admin])

        conn.commit()
        conn.close()

        messagebox.showinfo("Succès", "Administrateur modifié avec succès!")
        charger_donnees_table()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la modification: {e}")


def supprimer_admin():
    item_selectionne = table_admin.focus()
    if not item_selectionne:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un administrateur à supprimer")
        return

    id_admin = table_admin.item(item_selectionne)['values'][0]

    if not messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet administrateur?"):
        return

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("DELETE FROM admin WHERE id_admin=%s", (id_admin,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Succès", "Administrateur supprimé avec succès!")
        charger_donnees_table()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")


# === Modification mot de passe (pour agents/administrateurs uniquement) ===
def modifier_mot_de_passe():
    top = Toplevel(fenetre)
    top.title("Modifier mot de passe")
    top.geometry("350x300")
    top.resizable(False, False)
    top.grab_set()  # Bloque l'interaction avec la fenêtre principale

    Label(top, text=f"Email: {user_email}", font=("Arial", 10)).pack(pady=10)

    Label(top, text="Ancien mot de passe:", font=("Arial", 10)).pack(pady=5)
    ancien_mdp_entry = Entry(top, show="*", width=30)
    ancien_mdp_entry.pack(pady=5)

    Label(top, text="Nouveau mot de passe:", font=("Arial", 10)).pack(pady=5)
    nouveau_mdp_entry = Entry(top, show="*", width=30)
    nouveau_mdp_entry.pack(pady=5)

    Label(top, text="Confirmer le mot de passe:", font=("Arial", 10)).pack(pady=5)
    confirm_mdp_entry = Entry(top, show="*", width=30)
    confirm_mdp_entry.pack(pady=5)

    def changer_mdp():
        email = user_email
        ancien_mdp = ancien_mdp_entry.get()
        nouveau_mdp = nouveau_mdp_entry.get()
        confirm_mdp = confirm_mdp_entry.get()

        if not ancien_mdp or not nouveau_mdp or not confirm_mdp:
            messagebox.showwarning("Erreur", "Tous les champs sont requis.", parent=top)
            return

        if nouveau_mdp != confirm_mdp:
            messagebox.showwarning("Erreur", "Les mots de passe ne correspondent pas.", parent=top)
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
            curseur = conn.cursor()
            curseur.execute("SELECT mdp FROM admin WHERE mail = %s", (email,))
            result = curseur.fetchone()

            if not result:
                messagebox.showerror("Erreur", "Email introuvable.", parent=top)
                return

            mot_de_passe_en_base = result[0]
            ancien_mdp_hash = hashlib.sha256(ancien_mdp.encode()).hexdigest()

            if ancien_mdp_hash != mot_de_passe_en_base:
                messagebox.showerror("Erreur", "Ancien mot de passe incorrect!", parent=top)
                return

            nouveau_mdp_hash = hashlib.sha256(nouveau_mdp.encode()).hexdigest()
            curseur.execute("UPDATE admin SET mdp = %s WHERE mail = %s", (nouveau_mdp_hash, email))
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Mot de passe modifié avec succès!", parent=top)
            top.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du changement : {e}", parent=top)

    Button(top, text="Modifier", command=changer_mdp, bg="", fg="white", width=10).pack(pady=10)


# === Boutons d'action ===
if user_role == "Directeur":
    # Boutons pour le directeur (pleins droits)
    icon_ajouter = photo.generer_image(taille=(20, 20),
                                       chemin=r"C:/Users/HP/gestion des prisoniers/tabs.png")
    btn_ajouter = Button(fenetre, text="Ajouter", image=icon_ajouter, compound=TOP, command=ajouter_admin,
                        fg="black")
    btn_ajouter.image = icon_ajouter
    btn_ajouter.place(x=30, y=610)

    icon_modifier = photo.generer_image(taille=(20, 20),
                                        chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0035.jpg")
    btn_modifier = Button(fenetre, text="Modifier", image=icon_modifier, compound=TOP, command=modifier_admin,
                           fg="black")
    btn_modifier.image = icon_modifier
    btn_modifier.place(x=110, y=610)

    icon_supprimer = photo.generer_image(taille=(20, 20),
                                         chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0041.jpg")
    btn_supprimer = Button(fenetre, text="Supprimer", image=icon_supprimer, compound=TOP, command=supprimer_admin,
                            fg="black")
    btn_supprimer.image = icon_supprimer
    btn_supprimer.place(x=200, y=610)
else:
    # Bouton "Modifier MDP" pour les agents/administrateurs
    icon_pwd = photo.generer_image(taille=(20, 20),
                                   chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0035.jpg")
    btn_mdp = Button(fenetre, text="Modifier MDP", image=icon_pwd, compound=LEFT, command=modifier_mot_de_passe,
                      fg="black")
    btn_mdp.image = icon_pwd
    btn_mdp.place(x=100, y=610)


# === Navigation ===
def alternance(val):
    fenetre.destroy()
    subprocess.run(["python", val])


# === Déconnexion automatique ===
TEMPS_INACTIVITE = 60000  # 60 secondes
timer_inactivite = None


def deconnexion_automatique():
    messagebox.showwarning("Inactivité", "Vous avez été déconnecté pour inactivité.")
    try:
        os.remove("session.txt")
    except:
        pass
    fenetre.destroy()
    subprocess.run(["python", "connexion.py"])


def reinitialiser_inactivite(event=None):
    global timer_inactivite
    if timer_inactivite:
        fenetre.after_cancel(timer_inactivite)
    timer_inactivite = fenetre.after(TEMPS_INACTIVITE, deconnexion_automatique)


evenements_utilisateur = ["<Motion>", "<Key>", "<Button>"]
for event in evenements_utilisateur:
    fenetre.bind_all(event, reinitialiser_inactivite)

reinitialiser_inactivite()

# === Interface graphique ===
icon4 = photo.generer_image(taille=(150, 80), chemin=r"C:/Users/HP/gestion des prisoniers/i.png")
gen4 = Label(fenetre, image=icon4)
gen4.image = icon4
gen4.place(x=10, y=10)

icon_recherche = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tel1.png")
photo.icon(panel=fenetre, position='top', texte='Rechercher', icon=icon_recherche, com=ouvrir_recherche_admin).place(x=1000,y=5)


icon6 = photo.generer_image(taille=(40, 40), chemin=r"C:/Users/HP/gestion des prisoniers/m.jpg")
gen6 = Button(fenetre, image=icon6, command=lambda: alternance("accueil.py"))
gen6.image = icon6
gen6.place(x=250, y=5)

# === Titre ===
Label(titre, text="GESTION DES ADMINISTRATEURS", font=("Arial", 16, "bold"), bg=COLOR_BACKGROUND_MAIN).pack(side=TOP,
                                                                                                            fill=X)

# === Chargement initial des données ===
fenetre.after(100, charger_donnees_table)

fenetre.mainloop()
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
import crud
import photo
from PIL import Image, ImageTk, ImageDraw
from reportlab.pdfgen import canvas
import os
import subprocess
import shutil

# Créer le dossier photos s'il n'existe pas
DOSSIER_PHOTOS = "photos_prisonniers"
if not os.path.exists(DOSSIER_PHOTOS):
    os.makedirs(DOSSIER_PHOTOS)

try:
    with open("session_role.txt", "r") as fichier:
        user_role = fichier.read().strip()
except FileNotFoundError:
    user_role = None

COLOR_BACKGROUND_MAIN = "#F8F9FA"
COLOR_BORDER_SUBTLE = "#E9ECEF"
COLOR_TEXT_PRIMARY = "#343A40"
COLOR_BLUE_PRIMARY = "#007BFF"

fenetre = Tk()
fenetre.title("Gestion de prisonniers")
fenetre.geometry("1300x700")
fenetre.config(background=COLOR_BORDER_SUBTLE)
fenetre.resizable(False, False)

# --- VARIABLES GLOBALES ---
id_modif = StringVar()
photo_chemin = ""

# --- FORMULAIRE ---
form_frame = Frame(fenetre, bg=COLOR_BACKGROUND_MAIN)
form_frame.place(x=0, y=0, width=300, height=700)
titre = Frame(fenetre, bd=20, bg=COLOR_BACKGROUND_MAIN)
titre.place(x=300, y=0, width=1000, height=200)
champ_y = 100
champ_espacement = 35


def reset_form():
    id_modif.set("")
    nom_entry.delete(0, END)
    postnom_entry.delete(0, END)
    naissance_entry.set_date("")
    sexe_combo.set("")
    entree_entry.set_date("")
    sortie_entry.set_date("")
    cellule_combo.set("")
    statut_combo.set("")
    lieu_entry.delete(0, END)
    adress_entry.delete(0, END)
    comdanation_entry.delete(0, END)
    description_entry.delete(0, END)

    photo_label.config(text="Aucune photo")
    global photo_chemin
    photo_chemin = ""


Label(form_frame, text="Nom", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
nom_entry = Entry(form_frame, width=20)
nom_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Postnom", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
postnom_entry = Entry(form_frame, width=20)
postnom_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Date de naissance", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
naissance_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=20)
naissance_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Sexe", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
sexe_combo = ttk.Combobox(form_frame, values=["M", "F"], width=20)
sexe_combo.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Date entrée", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
entree_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=20)
entree_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Date sortie", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
sortie_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=20)
sortie_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Numéro cellule", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
cellule_combo = ttk.Combobox(form_frame, values=[], width=20)
cellule_combo.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Statut", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
statut_combo = ttk.Combobox(form_frame, values=["Detenu", "Livre", "Transferer"], width=20)
statut_combo.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Lieu de naissance", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
lieu_entry = Entry(form_frame, width=25)
lieu_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Adresse", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
adress_entry = Entry(form_frame, width=25)
adress_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Condamnation", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
comdanation_entry = Entry(form_frame, width=25)
comdanation_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
Label(form_frame, text="Description du délit", bg=COLOR_BACKGROUND_MAIN).place(x=10, y=champ_y)
description_entry = Entry(form_frame, width=25)
description_entry.place(x=120, y=champ_y)

champ_y += champ_espacement
photo_label = Label(form_frame, text="Aucune photo", bg=COLOR_BACKGROUND_MAIN)
photo_label.place(x=100, y=champ_y)

champ_y += champ_espacement
photo_btn = Button(form_frame, text="Choisir photo", command=lambda: choisir_photo())
photo_btn.place(x=90, y=champ_y)


# --- FONCTION POUR CHOISIR LA PHOTO ---
def choisir_photo():
    global photo_chemin
    try:
        # Appelle la fonction du module crud
        chemin_selectionne = crud.choisir_image(label=photo_label)

        # Vérifie si le module crud a bien défini un chemin
        if hasattr(crud, "chemin_image_selectionnee") and crud.chemin_image_selectionnee:
            photo_chemin = crud.chemin_image_selectionnee

            # Affiche dans le label le nom du fichier
            nom_fichier = os.path.basename(photo_chemin)
            photo_label.config(text=nom_fichier)

            # Affiche dans la console pour débogage
            print("✅ Image sélectionnée :", photo_chemin)
        else:
            photo_chemin = ""
            photo_label.config(text="Aucune photo")
            print("⚠️ Aucun chemin d'image récupéré depuis crud.")
            messagebox.showwarning("Attention", "Aucune photo sélectionnée.")
    except Exception as e:
        print("❌ Erreur lors du choix de la photo :", e)
        messagebox.showerror("Erreur", f"Erreur lors de la sélection de la photo : {e}")


# ... (conservez tout le code existant avant cette partie)

# --- FONCTION POUR OUVRIRE LA FENETRE DE RECHERCHE ---
def ouvrir_recherche_prisonnier():
    fen_recherche = Toplevel(fenetre)
    fen_recherche.title("Rechercher un prisonnier")
    fen_recherche.geometry("500x300+400+200")
    fen_recherche.config(bg=COLOR_BACKGROUND_MAIN)
    fen_recherche.resizable(False, False)

    # Titre
    Label(fen_recherche, text="Rechercher un prisonnier", font=("Arial", 14, "bold"),
          bg=COLOR_BACKGROUND_MAIN, fg=COLOR_BLUE_PRIMARY).pack(pady=10)

    # Frame pour les critères
    criteres_frame = Frame(fen_recherche, bg=COLOR_BACKGROUND_MAIN)
    criteres_frame.pack(pady=10)

    # Critère de recherche
    Label(criteres_frame, text="Rechercher par:", bg=COLOR_BACKGROUND_MAIN).grid(row=0, column=0, padx=5)
    critere_combo = ttk.Combobox(criteres_frame, values=["ID", "Nom", "Postnom", "Cellule"], width=15)
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
                            command=lambda: rechercher_prisonnier(
                                critere_combo.get(),
                                valeur_entry.get(),
                                fen_recherche
                            ))
    btn_rechercher.grid(row=0, column=0, padx=10)

    btn_annuler = Button(btn_frame, text="Annuler", width=15, command=fen_recherche.destroy)
    btn_annuler.grid(row=0, column=1, padx=10)


# --- FONCTION DE RECHERCHE ---
def rechercher_prisonnier(critere, valeur, fen_recherche):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()

        if critere == "ID":
            requete = "SELECT * FROM prisonniers WHERE id = %s"
            parametres = (valeur,)
        elif critere == "Nom":
            requete = "SELECT * FROM prisonniers WHERE nom LIKE %s"
            parametres = (f"%{valeur}%",)
        elif critere == "Postnom":
            requete = "SELECT * FROM prisonniers WHERE postnom LIKE %s"
            parametres = (f"%{valeur}%",)
        else:  # Cellule
            requete = "SELECT * FROM prisonniers WHERE cellule = %s"
            parametres = (valeur,)

        curseur.execute(requete, parametres)
        lignes = curseur.fetchall()
        conn.close()

        if not lignes:
            messagebox.showinfo("Information", "Aucun prisonnier trouvé")
            return

        # Mettre à jour le tableau principal
        table_prisonniers.delete(*table_prisonniers.get_children())
        for ligne in lignes:
            table_prisonniers.insert("", END, values=ligne)

        # Fermer la fenêtre de recherche
        fen_recherche.destroy()

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur recherche prisonniers: {e}")


# ... (conservez tout le code existant après cette partie)

# Modifiez seulement la création du bouton recherche pour utiliser la nouvelle fonction
icon_recherche = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tel1.png")
bouton_recherche = Button(titre, image=icon_recherche, bg=COLOR_BACKGROUND_MAIN,
                          command=ouvrir_recherche_prisonnier, borderwidth=0)
bouton_recherche.image = icon_recherche
bouton_recherche.place(x=1000, y=5)
# --- FONCTION POUR CHARGER CELLULES ---
def charger_cellules():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("SELECT id, numero FROM cellules")
        resultats = curseur.fetchall()
        conn.close()
        cellules = [str(row[0]) for row in resultats]
        cellule_combo['values'] = cellules
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur chargement cellules: {e}")


charger_cellules()

# --- TABLEAU ---
table_frame = Frame(fenetre, bg="white", bd=2, relief=RIDGE)
table_frame.place(x=300, y=100, width=980, height=600)

scroll_y = Scrollbar(table_frame, orient=VERTICAL)
scroll_x = Scrollbar(table_frame, orient=HORIZONTAL)

table_prisonniers = ttk.Treeview(
    table_frame,
    columns=(
        "ID", "Nom", "Postnom", "Naissance", "Sexe", "Entrée", "Sortie", "Cellule", "Statut",
        "Lieu de naissance", "Adresse", "Condamnation", "Description"),
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_x.pack(side=BOTTOM, fill=X)
scroll_y.config(command=table_prisonniers.yview)
scroll_x.config(command=table_prisonniers.xview)
table_prisonniers.pack(fill=BOTH, expand=True)

for col in table_prisonniers["columns"]:
    table_prisonniers.heading(col, text=col)
    table_prisonniers.column(col, width=100)
table_prisonniers["show"] = "headings"


# --- FONCTIONS CRUD ---
def verifier_doublon(nom, postnom, naissance):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("""
            SELECT COUNT(*) FROM prisonniers 
            WHERE nom = %s AND postnom = %s AND date_naissance = %s
        """, (nom, postnom, naissance))
        count = curseur.fetchone()[0]
        conn.close()
        return count > 0
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur vérification doublon: {e}")
        return False


def enregistrer_prisonnier():
    try:
        nom = nom_entry.get()
        postnom = postnom_entry.get()
        naissance = naissance_entry.get_date().strftime("%Y-%m-%d")
        sexe = sexe_combo.get()
        entree = entree_entry.get_date().strftime("%Y-%m-%d")
        sortie = sortie_entry.get_date().strftime("%Y-%m-%d")
        cellule = cellule_combo.get()
        statut = statut_combo.get()
        adress = adress_entry.get()
        comdanation = comdanation_entry.get()
        description = description_entry.get()
        lieu = lieu_entry.get()
        global photo_chemin

        if not nom or not postnom or not sexe or not cellule or not statut:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs obligatoires.")
            return

        # Vérification des doublons
        if verifier_doublon(nom, postnom, naissance):
            messagebox.showerror("Erreur", "Ce prisonnier existe déjà dans la base de données.")
            return

        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()

        # Gestion de la photo
        chemin_photo_final = None
        if photo_chemin and os.path.exists(photo_chemin):
            # Créer un nom unique pour la photo
            nom_fichier = f"{nom}_{postnom}_{naissance.replace('-', '')}.jpg"
            chemin_photo_final = os.path.join(DOSSIER_PHOTOS, nom_fichier)

            # Copier la photo dans le dossier dédié
            shutil.copy(photo_chemin, chemin_photo_final)

        requete = """INSERT INTO prisonniers
        (nom, postnom, date_naissance, sexe, date_entree, date_sortie, cellule, statut,
        lieu_de_naissance, adress_prisonier, comdanation, description_delit, photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        valeurs = (
            nom, postnom, naissance, sexe, entree, sortie, cellule, statut,
            lieu, adress, comdanation, description, chemin_photo_final
        )
        curseur.execute(requete, valeurs)
        conn.commit()
        conn.close()

        messagebox.showinfo("Succès", "Prisonnier enregistré.")
        charger_donnees_table()
        reset_form()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur enregistrement : {e}")


def modifier_prisonnier():
    try:
        id_prisonnier = id_modif.get()
        if not id_prisonnier:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un prisonnier à modifier.")
            return

        nom = nom_entry.get()
        postnom = postnom_entry.get()
        naissance = naissance_entry.get_date().strftime("%Y-%m-%d")
        sexe = sexe_combo.get()
        entree = entree_entry.get_date().strftime("%Y-%m-%d")
        sortie = sortie_entry.get_date().strftime("%Y-%m-%d")
        cellule = cellule_combo.get()
        statut = statut_combo.get()
        adress = adress_entry.get()
        comdanation = comdanation_entry.get()
        description = description_entry.get()
        lieu = lieu_entry.get()
        global photo_chemin

        if not nom or not postnom or not sexe or not cellule or not statut:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs obligatoires.")
            return

        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()

        # Gestion de la photo
        chemin_photo_final = None
        if photo_chemin and os.path.exists(photo_chemin):
            # Créer un nom unique pour la photo
            nom_fichier = f"{nom}_{postnom}_{naissance.replace('-', '')}.jpg"
            chemin_photo_final = os.path.join(DOSSIER_PHOTOS, nom_fichier)

            # Copier la photo dans le dossier dédié
            shutil.copy(photo_chemin, chemin_photo_final)

        # Récupérer l'ancien chemin de la photo pour la suppression
        curseur.execute("SELECT photo FROM prisonniers WHERE id = %s", (id_prisonnier,))
        ancienne_photo = curseur.fetchone()[0]

        requete = """UPDATE prisonniers SET
        nom=%s, postnom=%s, date_naissance=%s, sexe=%s, date_entree=%s,
        date_sortie=%s, cellule=%s, statut=%s, lieu_de_naissance=%s,
        adress_prisonier=%s, comdanation=%s, description_delit=%s, photo=%s WHERE id=%s"""
        valeurs = (
            nom, postnom, naissance, sexe, entree, sortie, cellule, statut,
            lieu, adress, comdanation, description, chemin_photo_final, id_prisonnier
        )
        curseur.execute(requete, valeurs)
        conn.commit()

        # Supprimer l'ancienne photo si elle existe et est différente de la nouvelle
        if ancienne_photo and os.path.exists(ancienne_photo) and ancienne_photo != chemin_photo_final:
            try:
                os.remove(ancienne_photo)
            except Exception as e:
                print(f"Erreur suppression ancienne photo: {e}")

        conn.close()

        messagebox.showinfo("Succès", "Prisonnier modifié.")
        charger_donnees_table()
        reset_form()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur modification : {e}")


def supprimer_prisonnier():
    try:
        item = table_prisonniers.focus()
        if not item:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un prisonnier à supprimer.")
            return
        if user_role != "Directeur":
            messagebox.showerror("Accès refusé", "Vous n'avez pas le droit de supprimer un prisonnier.")
            return

        valeurs = table_prisonniers.item(item, "values")
        id_prisonnier = valeurs[0]

        confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce prisonnier ?")
        if not confirm:
            return

        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()

        # Récupérer le chemin de la photo pour la supprimer
        curseur.execute("SELECT photo FROM prisonniers WHERE id = %s", (id_prisonnier,))
        photo_path = curseur.fetchone()[0]

        # Supprimer l'enregistrement
        curseur.execute("DELETE FROM prisonniers WHERE id = %s", (id_prisonnier,))
        conn.commit()
        conn.close()

        # Supprimer la photo associée si elle existe
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except Exception as e:
                print(f"Erreur suppression photo: {e}")

        messagebox.showinfo("Succès", "Prisonnier supprimé.")
        charger_donnees_table()
        reset_form()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur suppression : {e}")


def charger_donnees_table():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("""
            SELECT id, nom, postnom, date_naissance, sexe, date_entree, date_sortie, cellule, statut,
                   lieu_de_naissance, adress_prisonier, comdanation, description_delit
            FROM prisonniers ORDER BY id DESC
        """)
        lignes = curseur.fetchall()
        conn.close()

        table_prisonniers.delete(*table_prisonniers.get_children())
        for ligne in lignes:
            table_prisonniers.insert("", END, values=ligne)

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur chargement table: {e}")


def remplir_form_avec_selection(event):
    item = table_prisonniers.focus()
    if not item:
        return
    valeurs = table_prisonniers.item(item, "values")
    id_modif.set(valeurs[0])
    nom_entry.delete(0, END)
    nom_entry.insert(0, valeurs[1])
    postnom_entry.delete(0, END)
    postnom_entry.insert(0, valeurs[2])
    naissance_entry.set_date(valeurs[3])
    sexe_combo.set(valeurs[4])
    entree_entry.set_date(valeurs[5])
    sortie_entry.set_date(valeurs[6])
    cellule_combo.set(valeurs[7])
    statut_combo.set(valeurs[8])
    lieu_entry.delete(0, END)
    lieu_entry.insert(0, valeurs[9])
    adress_entry.delete(0, END)
    adress_entry.insert(0, valeurs[10])
    comdanation_entry.delete(0, END)
    comdanation_entry.insert(0, valeurs[11])
    description_entry.delete(0, END)
    description_entry.insert(0, valeurs[12])

    # Charger la photo si elle existe
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("SELECT photo FROM prisonniers WHERE id = %s", (valeurs[0],))
        photo_path = curseur.fetchone()[0]
        conn.close()

        global photo_chemin
        photo_chemin = photo_path if photo_path else ""
        photo_label.config(text=os.path.basename(photo_path) if photo_path else "Aucune photo")
    except:
        photo_label.config(text="Aucune photo")
        photo_chemin = ""


def afficher_details_prisonnier():
    item = table_prisonniers.focus()
    if not item:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un prisonnier.")
        return

    valeurs = table_prisonniers.item(item, 'values')

    fen_detail = Toplevel()
    fen_detail.title("Détails du prisonnier")
    fen_detail.geometry("600x500+300+200")  # Augmenté la taille pour plus d'espace
    fen_detail.config(bg="#f4f4f4")
    fen_detail.resizable(False, False)

    main_frame = Frame(fen_detail, bg="white", bd=2, relief=RIDGE)
    main_frame.place(x=10, y=10, width=580, height=480)

    Label(main_frame, text="DÉTAILS DU PRISONNIER", font=("Helvetica", 14, "bold"), fg="#007BFF",
          bg="white").place(x=170, y=10)

    photo_frame = Frame(main_frame, bg="white", bd=1, relief=GROOVE)
    photo_frame.place(x=10, y=50, width=150, height=150)

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
        curseur = conn.cursor()
        curseur.execute("SELECT photo FROM prisonniers WHERE id = %s", (valeurs[0],))
        photo_path = curseur.fetchone()[0]
        conn.close()

        if photo_path and os.path.exists(photo_path):
            img = Image.open(photo_path)
            img = img.resize((140, 140))

            # Créer un masque pour les coins arrondis
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius=20, fill=255)

            # Appliquer le masque
            img.putalpha(mask)
            img = img.convert("RGB")
            photo_img = ImageTk.PhotoImage(img)

            label_photo = Label(photo_frame, image=photo_img, bg="white")
            label_photo.image = photo_img
            label_photo.pack()
        else:
            Label(photo_frame, text="Aucune photo", bg="white").pack()
    except Exception as e:
        print(f"Erreur chargement photo: {e}")
        Label(photo_frame, text="Erreur chargement photo", bg="white").pack()

    x_info = 180
    y_base = 50
    y_step = 23
    champs = [
        ("ID", valeurs[0]),
        ("Nom", valeurs[1]),
        ("Postnom", valeurs[2]),
        ("Naissance", valeurs[3]),
        ("Sexe", valeurs[4]),
        ("Entrée", valeurs[5]),
        ("Sortie", valeurs[6]),
        ("Cellule", valeurs[7]),
        ("Statut", valeurs[8]),
        ("Lieu de naissance", valeurs[9]),
        ("Adresse", valeurs[10]),
        ("Condamnation", valeurs[11].replace("|", "\n• ") if valeurs[11] else ""),
        ("Description du délit", valeurs[12].replace("|", "\n• ") if valeurs[12] else ""),
    ]

    for i, (titre, valeur) in enumerate(champs):
        Label(main_frame, text=f"{titre} :", anchor="w", font=("Arial", 9, "bold"), bg="white").place(x=x_info,
                                                                                                      y=y_base + i * y_step)
        Label(main_frame, text=valeur, anchor="w", font=("Arial", 9), bg="white", fg="#333", justify=LEFT).place(
            x=x_info + 120,
            y=y_base + i * y_step)

    def imprimer_pdf():
        fichier = f"fiche_prisonnier_{valeurs[0]}.pdf"
        c = canvas.Canvas(fichier)
        c.setFont("Helvetica", 12)
        c.drawString(100, 800, f"Fiche détaillée du prisonnier ID {valeurs[0]}")
        y = 770
        for champ, val in champs:
            if champ in ["Condamnation", "Description du délit"]:
                # Pour les champs multilignes
                lines = val.split('\n')
                c.drawString(100, y, f"{champ}:")
                y -= 15
                for line in lines:
                    c.drawString(120, y, f"• {line}")
                    y -= 15
            else:
                c.drawString(100, y, f"{champ}: {val}")
                y -= 20

        # Ajouter la photo si elle existe
        if photo_path and os.path.exists(photo_path):
            try:
                c.drawImage(photo_path, 400, 650, width=100, height=100)
            except:
                pass

        c.save()
        try:
            os.startfile(fichier)
        except:
            subprocess.run(["xdg-open", fichier])

    icon_imprimer = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/dow.JPG")
    bouton_imprimer = Button(main_frame, text="Imprimer", image=icon_imprimer, compound=LEFT, command=imprimer_pdf)
    bouton_imprimer.image = icon_imprimer
    bouton_imprimer.place(x=220, y=430)

    icon_fermer = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tabs.PNG")
    bouton_fermer = Button(main_frame, text="Fermer", image=icon_fermer, compound=LEFT, command=fen_detail.destroy)
    bouton_fermer.image = icon_fermer
    bouton_fermer.place(x=340, y=430)


# --- NOUVELLE FONCTION POUR AJOUTER DES INFORMATIONS ---
def ajouter_information_prisonnier():
    try:
        item = table_prisonniers.focus()
        if not item:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un prisonnier.")
            return

        valeurs = table_prisonniers.item(item, "values")
        id_prisonnier = valeurs[0]

        # Créer une fenêtre pour ajouter des informations
        fen_ajout = Toplevel()
        fen_ajout.title("Ajouter des informations")
        fen_ajout.geometry("400x300")
        fen_ajout.resizable(False, False)

        # Variables pour les nouveaux champs
        nouvelle_condamnation = StringVar()
        nouvelle_description = StringVar()
        nouvelle_date_sortie = StringVar()

        Label(fen_ajout, text="Nouvelle condamnation:").pack(pady=5)
        Entry(fen_ajout, textvariable=nouvelle_condamnation, width=40).pack()

        Label(fen_ajout, text="Nouvelle description du délit:").pack(pady=5)
        Entry(fen_ajout, textvariable=nouvelle_description, width=40).pack()

        Label(fen_ajout, text="Nouvelle date de sortie:").pack(pady=5)
        date_sortie_entry = DateEntry(fen_ajout, date_pattern="yyyy-mm-dd", width=37,textvariable=nouvelle_date_sortie)
        date_sortie_entry.pack()

        def valider_ajout():
            try:
                nouvelle_date = date_sortie_entry.get_date().strftime("%Y-%m-%d")

                conn = mysql.connector.connect(host="localhost", user="root", password="", database="gestion_prisonier")
                curseur = conn.cursor()

                # Récupérer les anciennes valeurs
                curseur.execute("SELECT comdanation, description_delit FROM prisonniers WHERE id = %s",
                                (id_prisonnier,))
                anciennes_valeurs = curseur.fetchone()

                # Concaténer les nouvelles informations avec les anciennes
                condamnation_finale = (anciennes_valeurs[0] + " | " + nouvelle_condamnation.get()) if anciennes_valeurs[
                    0] else nouvelle_condamnation.get()
                description_finale = (anciennes_valeurs[1] + " | " + nouvelle_description.get()) if anciennes_valeurs[
                    1] else nouvelle_description.get()

                # Mettre à jour la base de données
                curseur.execute("""
                    UPDATE prisonniers SET 
                    comdanation = %s, 
                    description_delit = %s,
                    date_sortie = %s
                    WHERE id = %s
                """, (
                    condamnation_finale,
                    description_finale,
                    nouvelle_date,
                    id_prisonnier
                ))

                conn.commit()
                conn.close()
                messagebox.showinfo("Succès", "Informations ajoutées avec succès.")
                fen_ajout.destroy()
                charger_donnees_table()

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ajout d'informations: {e}")

        Button(fen_ajout, text="Valider", command=valider_ajout).pack(pady=20)

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout d'informations: {e}")


# Bind sélection tableau pour remplir formulaire
table_prisonniers.bind("<<TreeviewSelect>>", remplir_form_avec_selection)
table_prisonniers.bind("<Double-1>", lambda e: afficher_details_prisonnier())

# Chargement initial
charger_cellules()
charger_donnees_table()

icon6 = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tabs.png")
gen6 = Button(fenetre, text="Ajouter", image=icon6, compound=LEFT, command=enregistrer_prisonnier)
gen6.image = icon6
gen6.place(x=30, y=610)

icon2 = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0035.jpg")
gen2 = Button(fenetre, text="Modifier", image=icon2, compound=LEFT, command=modifier_prisonnier)
gen2.image = icon2
gen2.place(x=110, y=610)

'''icon3 = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0041.jpg")
gen3 = Button(fenetre, text="Supprimer", image=icon3, compound=LEFT, command=supprimer_prisonnier)
gen3.image = icon3
gen3.place(x=200, y=610)'''

# Ajout du nouveau bouton pour ajouter des informations
icon7 = photo.generer_image(taille=(20, 20),
                            chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0026.jpg")  # Remplacez par votre icône
gen7 = Button(fenetre, text="Ajouter Info", image=icon7, compound=LEFT, command=ajouter_information_prisonnier)
gen7.image = icon7
gen7.place(x=200, y=610)

icon4 = photo.generer_image(taille=(150, 80), chemin=r"C:/Users/HP/gestion des prisoniers/i.png")
gen4 = Label(fenetre, image=icon4)
gen4.image = icon4
gen4.place(x=10, y=10)

icon_recherche = photo.generer_image(taille=(20, 20), chemin=r"C:/Users/HP/gestion des prisoniers/tel1.png")
photo.icon(panel=fenetre, position='top', texte='Rechercher', icon=icon_recherche, com=ouvrir_recherche_prisonnier).place(x=1000,
                                                                                                                y=5)


icon6 = photo.generer_image(taille=(40, 40), chemin=r"C:/Users/HP/gestion des prisoniers/m.jpg")
gen6 = Button(fenetre, image=icon6, command=lambda: alternance("accueil.py"))
gen6.image = icon6
gen6.place(x=250, y=5)


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


# Bind tous les événements d'activité utilisateur
evenements_utilisateur = ["<Motion>", "<Key>", "<Button>"]
for event in evenements_utilisateur:
    fenetre.bind_all(event, reinitialiser_inactivite)

Label(titre, text="GESTION DES PRISONNIERS", font=("Arial", 16, "bold"), bg=COLOR_BACKGROUND_MAIN).pack(side=TOP,
                                                                                                            fill=X)

# Démarrer le timer d'inactivité au lancement
reinitialiser_inactivite()

fenetre.mainloop()
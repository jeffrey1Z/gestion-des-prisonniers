from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from PIL import Image, ImageTk
from photo import lancer_interface
import photo
import subprocess  # Pour ouvrir un autre script Python (comme "chargement.py")



# === Couleurs ===
COLOR_BACKGROUND_MAIN = "#F8F9FA"
COLOR_BORDER_SUBTLE = "#E9ECEF"
COLOR_TEXT_SECONDARY = "#6C757D"
COLOR_TEXT_PRIMARY = "#343A40"
COLOR_BLUE_PRIMARY = "#007BFF"
COLOR_BLUE_HOVER = "#0056B3"
COLOR_GREEN_SUCCESS = "#28A745"
COLOR_RED_ERROR = "#DC3545"
COLOR_ORANGE_WARNING = "#FFC107"
user_role=None
# === Fenêtre principale ===
fenetre = Tk()
fenetre.title("connexion")
fenetre.geometry("900x550")
fenetre.resizable(False, False)

# === Interface Gauche ===
panel1 = Frame(fenetre, bd=20, bg=COLOR_BACKGROUND_MAIN)
panel1.place(x=0, y=0, width=450, height=550)

titre = Label(panel1, text='Connexion', font=('times new roman', 30), bg=COLOR_BACKGROUND_MAIN)
titre.place(x=100, y=50)

# === Interface Droite ===
panel2 = Frame(fenetre, bd=20, bg="white")
panel2.place(x=450, y=0, width=450, height=550)

# === Icônes ===
icon = photo.generer_image(taille=(30, 30), chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0026.jpg")
gen = photo.icon(panel=fenetre, position='top', texte='', icon=icon,com='')
gen.place(x=15, y=165)

icon2 = photo.generer_image(taille=(30, 30), chemin=r"C:/Users/HP/gestion des prisoniers/IMG-20250604-WA0025.jpg")
gen2 = photo.icon(panel=fenetre, position='top', texte='', icon=icon2,com='')
gen2.place(x=15, y=265)

# === Champs de Connexion ===
Label(panel1, text='Entrer votre identifiant', bg='white').place(x=50, y=120)
entrerlabel1 = Entry(panel1, width=50, bd=5)
entrerlabel1.place(x=50, y=150)

Label(panel1, text='Entrer votre mot de passe', bg='white').place(x=50, y=220)
entrerlabel2 = Entry(panel1, width=50, bd=5, show='*')  # Masquer mot de passe
entrerlabel2.place(x=50, y=250)

Label(panel1, text='Rôle', bg='white').place(x=50, y=290)
value = ("Agent", "Administrateur", "Directeur")
combobox1 = ttk.Combobox(panel1, values=value, width=47, state="readonly")
combobox1.place(x=50, y=320)

# === Fonction de Connexion ===
def verifier_connexion():
    identifiant = entrerlabel1.get()
    mot_de_passe = entrerlabel2.get()
    role = combobox1.get()

    if not identifiant or not mot_de_passe or not role:
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gestion_prisonier"
        )
        cursor = conn.cursor()

        if role == "Directeur":
            cursor.execute("SELECT * FROM directeur WHERE email = %s AND mdp = %s", (identifiant, mot_de_passe))
        elif role == "Agent" or role =="Administrateur":
            cursor.execute("SELECT * FROM admin WHERE mail = %s AND mdp = %s", (identifiant, mot_de_passe))
        else:
            messagebox.showwarning("Rôle non pris en charge", "Ce rôle n'est pas encore implémenté.")
            return

        resultat = cursor.fetchone()


                # ... ton code de vérification ...
        if resultat:
            con = role + '\n' + identifiant
            messagebox.showinfo("Succès", f"Connexion réussie en tant que {role}.")
            with open("session_role.txt", "w") as fichier:
                fichier.write(con)
            # 🟢 Stocke le rôle de l’utilisateur
            fenetre.destroy()
            subprocess.run(["python", "chargement.py"])

        else:
            messagebox.showerror("Erreur", "Identifiant ou mot de passe incorrect.")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur", f"Erreur de connexion à la base de données : {err}")

# === Bouton de Connexion ===
button = Button(panel1, text='Se Connecter', bg=COLOR_BLUE_PRIMARY, fg="white", command=verifier_connexion)
button.place(x=150, y=360)

# === Image à droite ===
lancer_interface(
    chemin=r"c:/Users/HP/gestion des prisoniers/gros-plan-sur-la-main-portant-des-menottes-en-prison.jpg",
    taille=(500, 500),
    panel=panel2
)


if __name__ == "__main__":
    fenetre.mainloop()

from tkinter import filedialog
from tkinter import messagebox
import os

# Variable globale pour stocker le chemin de l'image sélectionnée
chemin_image_selectionnee = ""

def choisir_image(label=None):
    global chemin_image_selectionnee

    try:
        # Filtre uniquement les fichiers image
        fichier = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Tous les fichiers", "*.*")
            ]
        )

        # Si aucun fichier sélectionné, on annule
        if not fichier:
            chemin_image_selectionnee = ""
            if label:
                label.config(text="Aucune photo")
            return None

        # Si le fichier existe bien
        if os.path.exists(fichier):
            chemin_image_selectionnee = fichier

            # Mise à jour du label s'il est passé
            if label:
                label.config(text=os.path.basename(fichier))

            print("✅ Fichier image sélectionné :", fichier)
            return fichier
        else:
            chemin_image_selectionnee = ""
            messagebox.showerror("Erreur", "Le fichier sélectionné n'existe pas.")
            return None

    except Exception as e:
        chemin_image_selectionnee = ""
        messagebox.showerror("Erreur", f"Erreur lors du choix de l'image : {e}")
        print("❌ Erreur choisir_image:", e)
        return None

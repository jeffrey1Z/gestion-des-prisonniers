from tkinter import *
from PIL import Image, ImageTk
def lancer_interface(chemin,taille,panel):


    # Garde les objets globalement
    lancer_interface.bg_image = Image.open(chemin)
    lancer_interface.bg_image = lancer_interface.bg_image.resize((taille), Image.LANCZOS)
    lancer_interface.bg_photo = ImageTk.PhotoImage(lancer_interface.bg_image)

    label_bg = Label(panel, image=lancer_interface.bg_photo)
    label_bg.image = lancer_interface.bg_photo
    label_bg.pack(fill=BOTH, expand=True)


def icon(panel,position,texte,icon,com):
    button_icon = (Button(panel,
                        text=texte,
                         image=icon,

                         compound=position,  # place l'image à gauche du texte
                         font=("Bell MT", 10),
                         bg="#E0E0E0",  # couleur de fond normale
                         fg="black",  # couleur du texte
                         bd=0,  # épaisseur de bordure
                         relief="raised",  # effet en relief
                         padx=10,
                         pady=5,
                         activebackground="#D0D0D0",  # Couleur lorsque cliqué
                         activeforeground="black" ,command=com))

    #button_icon.place(taille)
      # <-- Ceci garde l’image en mémoire

    return button_icon


def generer_image(chemin,taille):
    image_normal = Image.open(chemin)
    image_normal = image_normal.resize((taille), Image.LANCZOS)

    icon_normal = ImageTk.PhotoImage(image_normal)
    return  icon_normal

def choisir_image(label):
    chemin = filedialog.askopenfilename(title="Choisir une image", filetypes=[("Images", "*.jpg *.png *.jpeg *.gif")])
    if chemin:
        image = Image.open(chemin)
        image = image.resize((80, 50))  # Redimensionner si nécessaire
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo  # Important pour garder l’image visible





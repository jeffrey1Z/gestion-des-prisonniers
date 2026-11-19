
import tkinter as tk
from tkinter import messagebox
import mysql.connector
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime


# Connexion à MySQL
def get_connexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion_prisonier"
    )


#  Analyse par commune
def analyser_par_commune():
    try:
        conn = get_connexion()
        cursor = conn.cursor()
        cursor.execute("SELECT adress_prisonier FROM prisonniers")
        communes = [row[0].split("c/")[0].strip().capitalize() for row in cursor.fetchall()]
        compteur = Counter(communes)

        afficher_graphique(
            labels=list(compteur.keys()),
            valeurs=list(compteur.values()),
            titre="Répartition des prisonniers par commune",
            xlabel="Commune",
            ylabel="Nombre de prisonniers"
        )
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


# Analyse par tranche d'âge
def analyser_par_age():
    try:
        conn = get_connexion()
        cursor = conn.cursor()
        cursor.execute("SELECT date_naissance FROM prisonniers")
        tranches = {
            "Moins de 18 ans": 0,
            "18-25 ans": 0,
            "26-40 ans": 0,
            "41-60 ans": 0,
            "Plus de 60 ans": 0
        }

        for (date_naissance,) in cursor.fetchall():
            if date_naissance:
                age = datetime.now().year - date_naissance.year
                if age < 18:
                    tranches["Moins de 18 ans"] += 1
                elif age <= 25:
                    tranches["18-25 ans"] += 1
                elif age <= 40:
                    tranches["26-40 ans"] += 1
                elif age <= 60:
                    tranches["41-60 ans"] += 1
                else:
                    tranches["Plus de 60 ans"] += 1

        afficher_graphique(
            labels=list(tranches.keys()),
            valeurs=list(tranches.values()),
            titre="Répartition des prisonniers par tranche d'âge",
            xlabel="Tranche d'âge",
            ylabel="Nombre de prisonniers"
        )
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


#  Analyse par sexe
def analyser_par_sexe():
    try:
        conn = get_connexion()
        cursor = conn.cursor()
        cursor.execute("SELECT sexe FROM prisonniers")
        sexes = [row[0].capitalize() for row in cursor.fetchall()]
        compteur = Counter(sexes)

        afficher_graphique(
            labels=list(compteur.keys()),
            valeurs=list(compteur.values()),
            titre="Répartition des prisonniers par sexe",
            xlabel="Sexe",
            ylabel="Nombre de prisonniers"
        )
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


#  Analyse par condamnation
def analyser_par_condamnation():
    try:
        conn = get_connexion()
        cursor = conn.cursor()
        cursor.execute("SELECT comdanation FROM prisonniers")
        peines = [row[0].capitalize() for row in cursor.fetchall()]
        compteur = Counter(peines)

        afficher_graphique(
            labels=list(compteur.keys()),
            valeurs=list(compteur.values()),
            titre="Répartition des condamnations",
            xlabel="Durée de condamnation",
            ylabel="Nombre de prisonniers"
        )
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


#  Analyse par type de délit
def analyser_par_delit():
    try:
        conn = get_connexion()
        cursor = conn.cursor()
        cursor.execute("SELECT description_delit FROM prisonniers")
        delits = [row[0].capitalize() for row in cursor.fetchall()]
        compteur = Counter(delits)

        afficher_graphique(
            labels=list(compteur.keys()),
            valeurs=list(compteur.values()),
            titre="Répartition des prisonniers par type de délit",
            xlabel="Délit",
            ylabel="Nombre de prisonniers"
        )
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


#  Fonction utilitaire pour afficher un graphique
def afficher_graphique(labels, valeurs, titre, xlabel, ylabel):
    plt.figure(figsize=(10, 5))
    plt.bar(labels, valeurs, color='teal')
    plt.title(titre)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# === INTERFACE PRINCIPALE ===
root = tk.Tk()
root.title("Analyse des données des prisonniers")
root.geometry("450x400")
root.configure(bg="#f4f4f4")

tk.Label(root, text="Analyse des données", font=("Arial", 18, "bold"), bg="#f4f4f4", fg="#333").pack(pady=20)

tk.Button(root, text="📊 Par commune", command=analyser_par_commune, width=30).pack(pady=5)
tk.Button(root, text="📈 Par tranche d'âge", command=analyser_par_age, width=30).pack(pady=5)
tk.Button(root, text="👤 Par sexe", command=analyser_par_sexe, width=30).pack(pady=5)
tk.Button(root, text="⚖️ Par condamnation", command=analyser_par_condamnation, width=30).pack(pady=5)
tk.Button(root, text="🚨 Par type de délit", command=analyser_par_delit, width=30).pack(pady=5)

root.mainloop()

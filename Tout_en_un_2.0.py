import time
import ollama
import os
import pyaudio
import pyttsx3
import requests
import subprocess
import tkinter as tk
import webbrowser
from datetime import datetime
from googleapiclient.discovery import build
from tkinter import scrolledtext
from vosk import Model, KaldiRecognizer

index_date_heure = ["quelle heure est-il", "quelle heure est il", "donnes-moi l'heure", "donnes-moi l'heure", "donne-moi l'heure", "quel jour on est", "quel jour est on", "quel jour sommes-nous", "quel jour sommes nous", "date d'aujourd'hui", "date d aujourd hui"]
index_explore_launch = ["lance"]
index_internet = ["cherche", "sur youtube"]
index_os = index_explore_launch + index_date_heure

def trouver_mot_cle(phrase, liste_de_mots):
    mots_trouve = [mot for mot in liste_de_mots if phrase.find(mot) != -1]
    if mots_trouve:
        return mots_trouve

def rechercher_fichiers(dossier, mots_cles):
    fichiers_trouves = []
    for nom_fichier in os.listdir(dossier):
        if all(mot.lower() in nom_fichier.lower() for mot in mots_cles):
            fichiers_trouves.append(nom_fichier)
    return fichiers_trouves

def ouvrir_fichier(dossier, nom_fichier):
    chemin_fichier = os.path.join(dossier, nom_fichier)
    if os.path.isfile(chemin_fichier):
        try:
            subprocess.run(["cmd", "/c", "start", "", chemin_fichier], shell=True)
            console = (f"{nom_fichier} ouvert avec succès.")
            afficher_message(console)
        except Exception as e:
            console  = (f"Erreur lors de l'ouverture du fichier : {e}")
            afficher_message(console)

def explore_launch(requete):
    dossier = 'C:/Users/XXXXXXX/Music'
    if requete.strip() == "":  # Vérifie si la requête est vide ou composée uniquement d'espaces
        console = "Aucune requête fournie."
        afficher_message(console)
        return  # Quitte la fonction si la requête est vide

    mots_cles = requete.split()
    fichiers_correspondants = rechercher_fichiers(dossier, mots_cles)

    if len(fichiers_correspondants) == 1:
        ouvrir_fichier(dossier, fichiers_correspondants[0])
    elif len(fichiers_correspondants) > 1:
        console = ("Fichiers trouvés :")
        afficher_message(console)
        for fichier in fichiers_correspondants:
            console = (f"- {fichier}")
            afficher_message(console)
    else:
        console = ("Aucun fichier trouvé avec ces mots-clés.")
        afficher_message(console)

def date_heure(requete):
    date_actuelle = datetime.now().strftime("%d-%m-%Y")
    heure_actuelle = datetime.now().strftime("%H:%M:%S")
    if "heure" in requete.lower():
        console = (f"Il est : {heure_actuelle}")
        afficher_message(console)
    else:
        console = (f"On est le : {date_actuelle}")
        afficher_message(console)

def test_reseau(url='http://www.google.com/', timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        afficher_message("Vous n'êtes pas connécté à internet.")
        return False

def rechercher_et_lancer_premiere_video(requete):
    API_KEY = 'XXXXXXXXXXXXXXXXXXXx'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    recherche_response = youtube.search().list(q=requete, part='snippet', maxResults=1, type='video').execute()

    if recherche_response['items']:
        premiere_video = recherche_response['items'][0]
        video_id = premiere_video['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        webbrowser.open(video_url)
        console = (f"Vidéo lancée : {video_url}")
        afficher_message(console)
    else:
        console = ("Aucune vidéo trouvée pour cette requête.")
        afficher_message(console)

def ouvrir_navigateur_avec_lien(entree):
    url = f"https://www.google.com/search?q={entree}"

    try:
        webbrowser.open(url, new=2)
        console = (f"Navigateur ouvert avec succès à l'URL : {url}")
        afficher_message(console)
    except Exception as e:
        console = (f"Erreur lors de l'ouverture du navigateur : {e}")
        afficher_message(console)

def chat_loop(question):
    while True:
        reponse = ollama.chat(model="phi3", messages=[{'role': 'user', 'content': question}])
        ia_reponse = ("phi3 : " + reponse['message']['content'])
        afficher_message(ia_reponse)
        break

def afficher_message(message):
    texte_sortie.configure(state='normal')
    texte_sortie.insert(tk.END, message + '\n')
    texte_sortie.configure(state='disabled')
    texte_sortie.see(tk.END)
    print(message)
    if toggle_bouton.state:
        TTS(message)
    # return message
def afficher_message_user(message):
    texte_sortie.configure(state='normal')
    texte_sortie.insert(tk.END, message + '\n')
    texte_sortie.configure(state='disabled')
    texte_sortie.see(tk.END)

def TTS(parole):
    # Initialiser le moteur
    engine = pyttsx3.init()
    # Faire parler le moteur
    engine.say(parole)
    # Attendre que la parole soit terminée
    engine.runAndWait()

def envoyer_commande():
    entree = entree_utilisateur.get()
    afficher_message_user(entree)
    if entree.lower() == '/bye':
        root.quit()
    if trouver_mot_cle(entree, index_internet):
        word = trouver_mot_cle(entree, index_internet)
        if " ".join(word).strip() == "":
            console = "Aucune requête fournie."
            afficher_message(console)
        if test_reseau():
            if "youtube" in entree:
                mots_trouve = trouver_mot_cle(entree, index_internet)
                if mots_trouve:
                    for mot in mots_trouve:
                        entree = entree.replace(mot, "").strip()
                rechercher_et_lancer_premiere_video(entree)
            else:
                mots_trouve = trouver_mot_cle(entree, index_internet)
                if mots_trouve:
                    for mot in mots_trouve:
                        entree = entree.replace(mot, "").strip()
                ouvrir_navigateur_avec_lien(entree)
    elif trouver_mot_cle(entree, index_os):
        word = trouver_mot_cle(entree, index_os)
        if " ".join(word).strip() == "":
            console = "Aucune requête fournie."
            afficher_message(console)
        if trouver_mot_cle(entree, index_date_heure):
            date_heure(entree)
        else:
            mots_trouve = trouver_mot_cle(entree, index_explore_launch)
            if mots_trouve:
                for mot in mots_trouve:
                    entree = entree.replace(mot, "").strip()
                explore_launch(entree)
    else:

        if entree.strip() == "":
            console = "Aucune requête fournie."
            afficher_message(console)
        else:
            chat_loop(entree)
    entree_utilisateur.delete(0, tk.END)

# Interface Tkinter
def toggle_assistant(parole):
    # Sauvegarde de l'état précédent
    etat_precedent = toggle_bouton.state

    # Toggle the TTS state
    toggle_bouton.state = not toggle_bouton.state

    if toggle_bouton.state:  # If TTS is now enabled
        toggle_bouton.config(text='TTS actif 🔊', bg='green')
        afficher_message("TTS activé.")
    else:  # If TTS is now disabled
        toggle_bouton.config(text='Désactivé 🔈', bg='red')
        afficher_message("TTS désactivé.")

    # Lire le message uniquement si TTS est activé
    if toggle_bouton.state:
        TTS(parole)  # Read the current message if TTS is enabled


root = tk.Tk()
root.title("Inteligent Assistant-de Qualité")

frame = tk.Frame(root)
frame.pack(pady=10)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

texte_sortie = scrolledtext.ScrolledText(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, state='disabled', width=80, height=20)
texte_sortie.pack()
scrollbar.config(command=texte_sortie.yview)

entree_utilisateur = tk.Entry(root, width=70)
entree_utilisateur.pack(pady=10)
entree_utilisateur.bind("<Return>", lambda event: envoyer_commande())

# Frame pour les boutons
button_frame = tk.Frame(root)
button_frame.pack(pady=5)
button_frame.bind("<Button-1>", toggle_assistant)

bouton_envoyer = tk.Button(root, text="Envoyer", command=envoyer_commande)
bouton_envoyer.pack(pady=5)

# Crée le bouton avec un état initial
toggle_bouton = tk.Button(button_frame, text='Activé 🔊', command=lambda: toggle_assistant(""), bg='green')
toggle_bouton.state = True  # État initial
toggle_bouton.pack(side=tk.LEFT, padx=5)

root.mainloop()

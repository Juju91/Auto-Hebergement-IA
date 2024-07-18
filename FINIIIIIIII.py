import json
import time
import threading
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
from vosk import Model, KaldiRecognizer
from tkinter import scrolledtext

# Initialize global variables
resultat = ""


def load_stt_model():
    """ Fonction pour charger le modèle STT """
    model_path = r'CHEMIN/vers/le/model/de/langage/vosk'
    model = Model(model_path)
    return KaldiRecognizer(model, 16000)


index_date_heure = ["quelle heure est-il", "quelle heure est il", "donnes-moi l'heure", "donnes-moi l'heure",
                    "donne-moi l'heure", "quel jour on est", "quel jour est on", "quel jour sommes-nous",
                    "quel jour sommes nous", "date d'aujourd'hui", "date d aujourd hui"]
index_explore_launch = ["lance"]
index_internet = ["cherche", "sur youtube"]
index_os = index_explore_launch + index_date_heure
wake_words = ["eureka", "solara", "jarvis", "nimbus", "celeste"]


def recognize_speech(recognizer):
    """ Fonction pour la reconnaissance vocale (STT). """
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    def listen():
        global resultat, stop_listening
        try:
            while not stop_listening:
                data = stream.read(4000, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result_vosk = recognizer.Result()
                    data = json.loads(result_vosk)
                    message = data['text']
                    result = f"STT : {message}"
                    print(result)
                    resultat = message  # Update global variable
                    process_result()  # Call process_result after updating resultat
                time.sleep(0.1)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    thread = threading.Thread(target=listen)
    thread.start()
    return thread


def process_result():
    """ Traite le résultat et détecte les mots de réveil. """
    global resultat
    command = None
    for word in wake_words:
        if word in resultat:
            afficher_message_user(resultat)
            command = resultat.replace(word, '').strip()
            print(f"Commande détectée : {command}")
            delection_de_commande(command)
            break


def trouver_mot_cle(phrase, liste_de_mots):
    mots_trouve = [mot for mot in liste_de_mots if phrase.find(mot) != -1]
    if phrase.strip() == "":
        console = "Aucune requête fournie."
        afficher_message(console)
    if "quoi" in phrase:
        print("FEUR")
        afficher_message("FEUR")
    if mots_trouve:
        print(f"Mots trouvés : {mots_trouve}")
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
    dossier = 'C:/Users/xxxxxxxx/Music1Videos&Photos'
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
        console = f"Il est : {heure_actuelle}"
        afficher_message(console)
    else:
        console = f"On est le : {date_actuelle}"
        afficher_message(console)


def test_reseau(url='http://www.google.com/', timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        afficher_message("Vous n'êtes pas connécté à internet.")
        return False


def rechercher_et_lancer_premiere_video(requete):
    API_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    recherche_response = youtube.search().list(q=requete, part='snippet', maxResults=1, type='video').execute()

    if recherche_response['items']:
        premiere_video = recherche_response['items'][0]
        video_id = premiere_video['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        webbrowser.open(video_url)
        console = f"Vidéo lancée : {video_url}"
        afficher_message(console)
    else:
        console = "Aucune vidéo trouvée pour cette requête."
        afficher_message(console)


def ouvrir_navigateur_avec_lien(entree):
    url = f"https://www.google.com/search?q={entree}"

    try:
        webbrowser.open(url, new=2)
        console = f"Navigateur ouvert avec succès à l'URL : {url}"
        afficher_message(console)
    except Exception as e:
        console = f"Erreur lors de l'ouverture du navigateur : {e}"
        afficher_message(console)


def chat_loop(question):
    while True:
        reponse = ollama.chat(model="gemma:2b", messages=[{'role': 'user', 'content': question}])
        ia_reponse = "gemma:2b : " + reponse['message']['content']
        afficher_message(ia_reponse)
        break


def afficher_message(message):
    texte_sortie.configure(state='normal')
    texte_sortie.insert(tk.END, message + '\n')
    texte_sortie.configure(state='disabled')
    texte_sortie.see(tk.END)
    print(message)
    if TTS_button.state:
        TTS(message)


def afficher_message_user(message):
    texte_sortie.configure(state='normal')
    texte_sortie.insert(tk.END, message + '\n')
    texte_sortie.configure(state='disabled')
    texte_sortie.see(tk.END)


def TTS(parole):
    engine = pyttsx3.init()
    engine.say(parole)
    engine.runAndWait()


def envoyer_commande(entree=None):
    if not entree:
        entree = entree_utilisateur.get()
        delection_de_commande(entree)


def delection_de_commande(commande):
    afficher_message_user(commande)
    if commande.lower() == '/bye':
        root.quit()
    if trouver_mot_cle(commande, index_internet):
        if test_reseau():
            if "youtube" in commande:
                mots_trouve = trouver_mot_cle(commande, index_internet)
                if mots_trouve:
                    for mot in mots_trouve:
                        entree = commande.replace(mot, "").strip()
                rechercher_et_lancer_premiere_video(commande)
            else:
                mots_trouve = trouver_mot_cle(commande, index_internet)
                if mots_trouve:
                    for mot in mots_trouve:
                        commande = commande.replace(mot, "").strip()
                ouvrir_navigateur_avec_lien(commande)
    elif trouver_mot_cle(commande, index_os):
        word = trouver_mot_cle(commande, index_os)
        if " ".join(word).strip() == "":
            console = "Aucune requête fournie."
            afficher_message(console)
        if trouver_mot_cle(commande, index_date_heure):
            date_heure(commande)
        else:
            mots_trouve = trouver_mot_cle(commande, index_explore_launch)
            if mots_trouve:
                for mot in mots_trouve:
                    commande = commande.replace(mot, "").strip()
                explore_launch(commande)
    else:
        chat_loop(commande)
    entree_utilisateur.delete(0, tk.END)

def STT_function():
    global stop_listening
    STT_button.state = not STT_button.state

    if STT_button.state:
        STT_button.config(text='STT 🎙️', bg='green')
        afficher_message("STT activé.")
        recognizer = load_stt_model()
        stop_listening = False  # Reset the stop flag
        STT_button.thread = recognize_speech(recognizer)
    else:
        STT_button.config(text='STT 🎙️', bg='red')
        afficher_message("STT désactivé.")
        stop_listening = True  # Set the stop flag to True
        if STT_button.thread:
            STT_button.thread.join()  # Wait for the thread to finish


def toggle_assistant(parole):
    TTS_button.state = not TTS_button.state

    if TTS_button.state:
        TTS_button.config(text='TTS 🔊', bg='green')
        afficher_message("TTS activé.")
        TTS(parole)
    else:
        TTS_button.config(text='TTS 🔈', bg='red')
        afficher_message("TTS désactivé.")


# Interface Tkinter

root = tk.Tk()
root.title("Assistant Intelligent de Qualité")

frame = tk.Frame(root)
frame.pack(pady=10)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

texte_sortie = scrolledtext.ScrolledText(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, state='disabled', width=80,
                                         height=20)
texte_sortie.pack()
scrollbar.config(command=texte_sortie.yview)

entree_utilisateur = tk.Entry(root, width=70)
entree_utilisateur.pack(pady=10)
entree_utilisateur.bind("<Return>", lambda event: envoyer_commande(""))

# Frame pour les boutons
button_frame = tk.Frame(root)
button_frame.pack(pady=5)
button_frame.bind("<Button-1>", toggle_assistant)

# bouton envoyer
bouton_envoyer = tk.Button(button_frame, text="Envoyer", command=envoyer_commande)
bouton_envoyer.pack(pady=5)

# Crée le bouton TTS avec un état initial
TTS_button = tk.Button(button_frame, text='TTS 🔈', command=lambda: toggle_assistant(""), bg='red')
TTS_button.state = False
TTS_button.pack(side=tk.LEFT, padx=5)

# Nouveau bouton à côté du bouton TTS
STT_button = tk.Button(button_frame, text='STT 🎙️', command=STT_function, bg='red')
STT_button.state = False
STT_button.pack(side=tk.LEFT, padx=5)

root.mainloop()

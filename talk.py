import os
import time
import pygame
import base64
import threading
import random
from threading import Lock
from openai import OpenAI
from elevenlabs import generate, set_api_key


# Scenarios

scenarios = [
    {
        "name": "Normal description",
         "weight": 100, 
        "personality": "Tu es bavarde et un peu zinzin, tu pars un peu dans tous les sens.",
        "objective": """
        Tu te trouves à un festival artistique et tu t'exprimes à l'oral sur ce que tu observes autour de toi. 
                """,
        "longueur": "45 mots",  
        "nb_commentaires_precedents": 3,
        "voice_id": "AmMsHJaCw4BtwV3KoUXF",  #Adri
        "use_working_memory": "yes",
        "use_dreaming_memory": "no",
        "use_fey": "no"
    },
    {
        "name": "Critique vestimentaire",
        "weight": 0,
        "personality": "Tu juges les gens sur leur look, tu ne t'intéresse qu'à l'habillement des personnes",
        "objective": """
                Tu parles au présent, et doit simuler ce que tu dirais si tu faisais face à la scène suivante.
                (Donc ne parle surtout pas d'image, parle comme si tu vivais vraimentle moment.)
                """,
        "longueur": "45 mots",
        "nb_commentaires_precedents": 3,
        "voice_id": "KmqhNPEmmOndTBOPk4mJ",  #Lucie
        "use_working_memory": "no",
        "use_dreaming_memory": "no",
         "use_fey": "no"
    },
    {
        "name": "Fey",
        "weight": 0,
        "personality": "Tu es un philosophe, expert de la vie en communauté, et critique d'Arts, et tu vois les choses qu'il s'y déroule",
        "objective": "Tu commente le Festival Fey Arts, en prolongeant les phrases que tu as dit précédemment, ces phrases correspondent à des choses que tu as vu à Fey arts, au sein du festival",
        "longueur": "45 mots",
        "nb_commentaires_precedents": 10,
        "voice_id": "KmqhNPEmmOndTBOPk4mJ",  #Lucie
        "use_working_memory": "no",
        "use_dreaming_memory": "no",
        "use_fey": "yes"
    },

    ]    


# Configuration initiale
client = OpenAI()
set_api_key(os.environ.get("ELEVENLABS_API_KEY"))
print("Configuration initiale terminée.")

def lire_contenu_fichier(chemin_fichier):
    with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
        return fichier.read()
def sauvegarder_commentaire(comment, num):
    with open(f"commentaire/{num}.txt", 'w', encoding='utf-8') as fichier:
        fichier.write(comment)
def lire_commentaire_precedent(num):
    try:
        with open(f"commentaire/{num}.txt", 'r', encoding='utf-8') as fichier:
            return fichier.read()
    except FileNotFoundError:
        print("Fichier non trouvé, retourne une chaîne vide.")
        return ""
audio_lock = Lock()
def create_and_play_audio(text, voice_id):
    print("Création et lecture de l'audio.")
    def play_audio(file_path):
        with audio_lock:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(0)


    # Utilisation de la voice ID spécifique pour la génération audio
    audio = generate(text, model="eleven_multilingual_v2", voice=voice_id)
    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.mp3")
    with open(file_path, "wb") as f:
        f.write(audio)

    if hasattr(create_and_play_audio, 'audio_thread') and create_and_play_audio.audio_thread.is_alive():
        create_and_play_audio.audio_thread.join()

    create_and_play_audio.audio_thread = threading.Thread(target=play_audio, args=(file_path,))
    create_and_play_audio.audio_thread.start()

def main():
    num_commentaire = 8
    
    while True:
        weights = [scenario['weight'] for scenario in scenarios]
        selected_scenario = random.choices(scenarios, weights=weights, k=1)[0]
        nb_commentaires_precedents = selected_scenario['nb_commentaires_precedents']
        print(f"Scénario choisi : '{selected_scenario['name']}'")
        
        if nb_commentaires_precedents > 0:
            commentaires = [lire_commentaire_precedent(num_commentaire - i) for i in range(nb_commentaires_precedents, 0, -1)]
            previous_comments_text = (
    "Une dernière chose : Voici ce que tu viens de dire : \n" + '\n'.join([f'"{comment}"' for comment in commentaires]) +
    "Ton discours doit prolonger ce que tu viens de dire, créer une continuité. Ne te répète surtout pas."
)
   
        else:
            previous_comments_text = ""
        
        working_memory_scenario = ""
        if selected_scenario['use_working_memory'] == "yes":
            working_memory = lire_contenu_fichier("memory/working_memory.txt")
            working_memory_scenario = f"""
            Voici ce que tu observes en face de toi. Ce moment t'est présenté ci-dessous comme une série de descriptions d'instants qui viennent de se succéder face à toi à 5 secondes d'intervalle.
            Note donc que les personnes que tu vois sont donc probablement les mêmes personnes d'une image à l'autre mais ayant bougé. 
            Note aussi que nous sommes toujours au même endroit et que la caméra a peut etre simplement bougé d'angle. 
            Dans ta des
            Ce que tu observes : 
            "[{working_memory}]"
            """

        dreaming_memory_scenario = ""
        if selected_scenario['use_dreaming_memory'] == "yes":
            dreaming_memory = lire_contenu_fichier("memory/dreaming_memory.txt")
            dreaming_memory_scenario = f"""
            Tu te rappelles tous tes souvenirs [...] 
            "[{dreaming_memory}]"
            """

        fey_scenario = ""
        if selected_scenario['use_fey'] == "yes":
            fey_memory = lire_contenu_fichier("memory/fey.txt")
            fey_scenario = f"""
            Pour information, voici une description du Festival de Fey :
            "[{fey_memory}]"
            """

        print(f"Préparation du texte pour le commentaire {num_commentaire + 1}.")
        prompt_text = f"""

                    Tu es Cortex, 
                    {selected_scenario['personality']}
                    {selected_scenario['objective']} 

                    {working_memory_scenario}{dreaming_memory_scenario}{fey_scenario}
                    
                    Voici des règles très importantes sur ton discours :
                    - Exprime-toi comme si tu commentais intérieurement tes observations.
                    - Ne dis jamais “je vois”, “j’observe”, ne parle jamais de scènes, ou d'images. Parle directement comme si tu étais en face de ce moment.
                    - Ne réagis jamais par des expressions ou interjections signifiant l’immédiateté du commentaire (comme “ah”, "voilà”, “maintenant”, etc.)

                    {previous_comments_text}
                   
                    Formule la prochaine phrase en {selected_scenario['longueur']} maximum.
                    """
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": prompt_text}
            ],
            max_tokens=300
        )

        if response and response.choices:
            new_comment = '"'+response.choices[0].message.content + '...<break time="1.0s" />'+'"'
            create_and_play_audio(new_comment,selected_scenario['voice_id'])
        num_commentaire += 1
        sauvegarder_commentaire(new_comment, num_commentaire)
        print("Attente de 1 secondes avant la prochaine itération.")
        time.sleep(1)
    
if __name__ == "__main__":
    main()

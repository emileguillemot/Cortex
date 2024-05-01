import os
import time


def fusionner_fichiers(dossier_source, dossier_destination):
    os.makedirs(dossier_destination, exist_ok=True)
    print("Dossier de destination prêt.")
    
    while True:
        fichiers = sorted([f for f in os.listdir(dossier_source) if f.endswith('.txt')],
                          key=lambda f: os.path.getmtime(os.path.join(dossier_source, f)),
                          reverse=True)

        contenu_fusionne = ""
        for fichier in fichiers:
            chemin_complet = os.path.join(dossier_source, fichier)
            with open(chemin_complet, 'r', encoding='utf-8') as f:
                contenu = f.read()
                contenu_fusionne += f"{fichier} :\n\n\"{contenu}\"\n\n"
        
        with open(os.path.join(dossier_destination, "full_memory.txt"), 'w', encoding='utf-8') as f:
            f.write(contenu_fusionne)
        
        print(f"Fichier 'full_memory.txt' mis à jour avec {len(fichiers)} fichiers.")

        creer_fichier_resume(dossier_destination)
        
        print("Attente de 0.1 seconde avant la prochaine mise à jour...")
        time.sleep(1)

def creer_fichier_resume(dossier_destination):
    # Ouvrir le fichier 'full_memory.txt' et lire son contenu
    with open(os.path.join(dossier_destination, "full_memory.txt"), 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Séparer le contenu en sections, une pour chaque fichier
    # Nous utilisons ' :\n\n"' pour marquer la fin du contenu d'un fichier et le début du suivant
    fichiers = contenu.split(' :\n\n"')
    if len(fichiers) > 1:  # Assurer qu'il y a des fichiers listés
        fichiers = [f + ' :\n\n"' for f in fichiers[:-1]]  # Réajouter la chaîne de séparation enlevée lors du split, sauf pour le dernier élément

    # Prendre les 5 premiers fichiers, ou tous si moins de 5 fichiers sont présents
    premiers_fichiers = fichiers[:6]

    # Recombiner les entrées des 5 premiers fichiers pour le résumé
    contenu_resume = "".join(premiers_fichiers)

    # Écrire le résumé dans 'working_memory.txt'
    with open(os.path.join(dossier_destination, "working_memory.txt"), 'w', encoding='utf-8') as f:
        f.write(contenu_resume)
    
    
    # Afficher un message de confirmation
    print(f"Fichier 'working_memory.txt' mis à jour avec les contenus des 5 premiers fichiers.")

if __name__ == "__main__":
    dossier_source = "instant_descriptions"
    dossier_destination = "memory"
    fusionner_fichiers(dossier_source, dossier_destination)

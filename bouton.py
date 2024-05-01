import serial
import os

ser = serial.Serial('/dev/tty.usbmodem21201', 9600)  # Remplacez 'COM3' par le port COM de votre Arduino
program_running = False

while True:
    if ser.readline().decode('utf-8').strip() == 'Button pushed':
        print("Détection : Le bouton a été poussé")
        if not program_running:
            print("Démarrage du programme...")
            program_running = True
            os.system('python3 talk.py')  # Remplacez ceci par le chemin de votre script
        else:
            print("Arrêt du programme...")
            program_running = False
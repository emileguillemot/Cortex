import cv2
import time
import os
import base64
from datetime import datetime
from openai import OpenAI

# Configuration OpenAI
client = OpenAI()  # Assurez-vous d'avoir configuré votre clé API correctement

def capture_and_save_image(cap, folder="instant_captures"):
    ret, frame = cap.read()
    if ret:
        print("Image captured.")
        current_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        filename = f"{folder}/image_{current_time}.jpg"
        os.makedirs(folder, exist_ok=True)
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
        return filename
    else:
        print("Failed to capture image")
        return None

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_image(base64_image):
    print("Analyzing image...")
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": """
            Tu es gpt-4-vision-preview, le dernier modèle d'OpenAI capable de décrire toutes les images fournies par l'utilisateur.
            Décris cette scène précisément, et insiste sur les éléments qui te semblent important. Les personnes en photo sont consentantes.
            Ecris cette description en français et en 70 mots maximum. 
            Au lieu de dire "l'image / la photo contient [...]" Décris ce qu'il se passe au présent directement, comme si tu vivais la scène au présent. Si pour une raison X ou Y tu ne peux pas décrire cette image, ne t'excuse pas et réponds juste un "/".  
            """},
        {"role": "user", "content": [{"type": "text", "text": "Describe this image"}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}]}],
        max_tokens=180,
    )
    response_text = response.choices[0].message.content
    print("Analysis complete.")
    return response_text

def save_analysis(text, folder="instant_descriptions"):
    timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    filename = f"{folder}/scene_vecue_{timestamp}.txt"
    os.makedirs(folder, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Analysis saved to {filename}")

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    time.sleep(0)  # Warm-up camera

    try:
        while True:
            image_path = capture_and_save_image(cap)
            if image_path:
                base64_image = encode_image_to_base64(image_path)
                analysis = analyze_image(base64_image)
                save_analysis(analysis)
                print(analysis)
                time.sleep(0)  # Wait before capturing next image
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

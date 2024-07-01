import cv2
import os
import time

#Inladen van de pretrained face detectie
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#Directory met de gezichten & output directory voor cropped images
IMAGE_DIR = "input_images"
OUTPUT_DIR = "output_faces"

#Als "output_faces" niet bestaat maakt die de directory aan
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

#Parameters voor gezichtdetectie optimalisatie
scale_factor = 2  # Increase this value to increase detection sensitivity (may increase false positives)
min_neighbors = 3   # Increase this value to reduce false positives (may miss some faces)
min_size = (100, 100) # Adjust this value based on expected face size in the camera feed

#Controle of de input directory bestaat
if not os.path.exists(IMAGE_DIR):
    print(f"Directory '{IMAGE_DIR}' does not exist.")
    quit()

#Verwerkt elke file in de input directory
for filename in os.listdir(IMAGE_DIR):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        image_path = os.path.join(IMAGE_DIR, filename)
        print(f"Processing {image_path}")

#Laad de image
        image = cv2.imread(image_path)

        #Converteert de image naar grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Detecteerd gezichten met behulp van OpenCV face detector
        faces = face_cascade.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=min_neighbors, minSize=min_size)

        #Tekent een vierkant om het gezicht
        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        #Cropt het gezicht
        face_crop = image[y:y+h, x:x+w]

        #Hernoem de file voor het gecropt gezicht
        face_filename = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}_face_{i}.bmp")

        #Sla de nieuwe gecropte file op
        cv2.imwrite(face_filename, face_crop)
        print(f"Cropped face saved to {face_filename}")

        #Weergeeft het resultaat
        cv2.imshow('Face Detection', image)
        cv2.waitKey(0)

#Sluit de OpenCV windows
cv2.destroyAllWindows()

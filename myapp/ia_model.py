import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

model_path = "C:/Users/FERNANDO/Documents/GitHub/IA_PNEUMONIA_DETECTOR/myapp/models/85_mobileNetV2.h5"

if not os.path.exists(model_path):
    raise FileNotFoundError(f"El archivo del modelo no se encuentra en: {model_path}")

model = load_model(model_path)
print("Modelo cargado con éxito.")

# Definir las clases
class_names = ['BACTERIANA', 'NORMAL', 'VIRAL']

def predict_image_class(image_path):
    try:
        # Cargar la imagen desde el path proporcionado
        img = image.load_img(image_path, target_size=(224, 224))  # Ajustar el tamaño según la entrada del modelo
        img_array = image.img_to_array(img) / 255.0  # Normalizar la imagen (0-255 -> 0-1)
        img_array = np.expand_dims(img_array, axis=0)  # Expandir dimensiones para que coincida con la entrada del modelo

        # Realizar la predicción
        prediction = model.predict(img_array, verbose=0)
        predicted_label = np.argmax(prediction[0])  # Obtener la clase con la mayor probabilidad
        accuracy = np.max(prediction[0]) * 100  # Calcular la precisión como el valor más alto en la predicción

        return class_names[predicted_label], accuracy  # Devolver la clase predicha y la precisión
    except Exception as e:
        print(f"Error durante la predicción: {e}")
        return None, None
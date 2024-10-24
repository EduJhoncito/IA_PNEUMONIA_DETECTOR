import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Cargar el modelo preentrenado (asegúrate de tener el archivo '85_mobileNetV2.h5')
model = load_model('models/85_mobileNetV2.h5')

# Definir las clases
class_names = ['BACTERIANA', 'NORMAL', 'VIRAL']

def predict_image_class(image_path):
    # Cargar la imagen desde el path proporcionado
    img = image.load_img(image_path, target_size=(224, 224))  # Ajustar el tamaño según la entrada del modelo
    img_array = image.img_to_array(img) / 255.0  # Normalizar la imagen
    img_array = np.expand_dims(img_array, axis=0)  # Expandir dimensiones para que coincida con la entrada del modelo

    # Realizar la predicción
    prediction = model.predict(img_array, verbose=0)
    predicted_label = np.argmax(prediction[0])
    accuracy = np.max(prediction[0]) * 100

    return class_names[predicted_label], accuracy

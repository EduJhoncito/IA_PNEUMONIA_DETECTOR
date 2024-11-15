from django.shortcuts import render, redirect
from .models import Doctor, Patient, Radiograph, Analysis
from django.contrib.auth.hashers import check_password, make_password
import base64
from django.http import JsonResponse
import datetime
from django import template
from django.utils.safestring import mark_safe
from django import forms
from .ia_model import predict_image_class
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .ia_model import predict_image_class
import datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras import models
from django.shortcuts import render

model = load_model(os.path.join(settings.BASE_DIR, "myapp", "models", "85_mobileNetV2.h5"))

# Define los directorios donde se guardarán las imágenes
CARPETA_SIN_PREDICCION = 'imagenes_sin_prediccion/'
CARPETA_CON_PREDICCION = 'imagenes_con_prediccion/'

register = template.Library()

@register.filter(name='b64encode')
def b64encode(value):
    if isinstance(value, bytes):
        encoded_value = base64.b64encode(value).decode('utf-8')
        return mark_safe(encoded_value)
    return ''

#Vista principal y para iniciar sesión
def login_neumologo(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            # Busca el doctor en la base de datos usando el email
            doctor = Doctor.objects.get(email_doctor=email)
            
            # Verifica la contraseña usando `check_password`
            if check_password(password, doctor.password_doctor):
                # Aquí debes implementar la lógica para establecer la sesión manualmente
                request.session['doctor_id'] = doctor.id_doctor  # Ejemplo de cómo guardar el ID en la sesión
                return redirect('home')  # Redirige a la página de inicio si la autenticación es correcta
            else:
                # Contraseña incorrecta
                return render(request, 'index.html', {'error': 'Credenciales incorrectas'})
        except Doctor.DoesNotExist:
            # El doctor no existe
            return render(request, 'index.html', {'error': 'Credenciales incorrectas'})
    
    return render(request, 'index.html')

#Vista para registrar usuario
def registro_neumologo(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        colegiatura = request.POST['colegiatura']
        password = request.POST['password']

        # Validar colegiatura: 6 dígitos y comienza con 0
        if not (colegiatura.isdigit() and len(colegiatura) == 6 and colegiatura[0] == '0'):
            return render(request, 'index.html', {
                'error': 'La colegiatura debe tener exactamente 6 números y comenzar con 0.'
        })
        
        # Verificar si ya existe un doctor con el mismo email
        if Doctor.objects.filter(email_doctor=email).exists():
            # Si existe, muestra una alerta de JavaScript
            return render(request, 'index.html', {
                'error': 'El usuario con este correo ya está registrado.'
            })

        # Crear el nuevo doctor con la contraseña encriptada
        doctor = Doctor.objects.create(
            name_doctor=nombre,
            email_doctor=email,
            colegiatura_doctor=colegiatura,
            password_doctor=make_password(password)  # Encripta la contraseña
        )
        doctor.save()

        # Iniciar sesión manualmente estableciendo la sesión
        request.session['doctor_id'] = doctor.id_doctor  # Guardar el ID del doctor en la sesión

        # Redirigir a la página de inicio o a la página que prefieras
        return redirect('home')  # Asegúrate de que 'home' sea la URL correcta

    return render(request, 'index.html')

# Vista de recuperar contraseña
def cambiar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')

        if not email or not nueva_contrasena or not confirmar_contrasena:
            return render(request, 'password.html', {
                'error_message': 'Todos los campos son obligatorios.'
            })

        if nueva_contrasena != confirmar_contrasena:
            return render(request, 'password.html', {
                'error_message': 'Las nuevas contraseñas no coinciden.'
            })

        try:
            # Verificar si el email existe en la base de datos
            doctor = Doctor.objects.get(email_doctor=email)
            
            # Actualizar la contraseña del doctor
            doctor.password_doctor = make_password(nueva_contrasena)# Recuerda encriptar la contraseña si es necesario
            doctor.save()

            return redirect('login_neumologo')  # Redirige al login o a otra página apropiada

        except Doctor.DoesNotExist:
            return render(request, 'password.html', {
                'error_message': 'No se encontró ninguna cuenta con ese correo electrónico.'
            })

    return render(request, 'password.html')


#Vista de home, donde se ingresa al iniciar sesión
def home(request):
    return render(request,'home.html')

# Vista para agregar paciente 
def registrar_paciente(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        dni = request.POST['dni']

        # Validar DNI: debe tener exactamente 8 dígitos
        if not (dni.isdigit() and len(dni) == 8):
            return render(request, 'patient.html', {
                'error_message': 'El DNI debe tener exactamente 8 números.'
            })

        # Asumimos que doctor_id está almacenado en la sesión (o lo obtienes de alguna otra forma)
        doctor_id = request.session.get('doctor_id')  # Asegúrate de tener esto configurado correctamente

        # Validar si el paciente ya está registrado 
        if Patient.objects.filter(dni_patient=dni).exists():
            return render(request, 'patient.html', {
                'error_message': 'El paciente ya se encuentra registrado'
            })

        try:
            # Obtener el objeto del doctor con el id_doctor correcto
            doctor = Doctor.objects.get(id_doctor=doctor_id)

            # Crear un nuevo paciente asociado con el doctor
            paciente = Patient(name_patient=nombre, dni_patient=dni, doctor_id=doctor)
            paciente.save()

            return redirect('home')  # Cambiar por la vista a la que quieras redirigir
        except Doctor.DoesNotExist:
            return render(request, 'patient.html', {
                'error_message': 'No se encontró el doctor'
            })
            
    return render(request, 'patient.html')  # La vista del template principal.

def buscar_paciente(request):
    dni = request.GET.get('dni')
    paciente = Patient.objects.filter(dni_patient=dni).first()
    
    if paciente:
        # Obtener las radiografías ordenadas por fecha de manera descendente
        radiografias = Radiograph.objects.filter(patient=paciente).prefetch_related('analysis_set').order_by('-date_radiograph')
        for radiografia in radiografias:
            # Asegúrate de que cada radiografía tiene un análisis asociado
            radiografia.analysis = radiografia.analysis_set.first() if radiografia.analysis_set.exists() else None
    else:
        radiografias = []

    return render(request, 'home.html', {
        'paciente': paciente,
        'radiografias': radiografias,
        'error_message': 'No se encontró al paciente' if not paciente else '',
        'MEDIA_URL': settings.MEDIA_URL,  # Pasar la URL base de los archivos multimedia
    })

def agregar_radiografia(request, paciente_id):
    if request.method == 'POST':
        image_file = request.FILES.get('radiograph_image')
        paciente = get_object_or_404(Patient, id_patient=paciente_id)

        # Obtener la última radiografía registrada del paciente
        ultima_radiografia = Radiograph.objects.filter(patient=paciente).order_by('-date_radiograph').first()

        # Verificar si han pasado al menos 10 días desde la última radiografía
        if ultima_radiografia:
            dias_diferencia = (timezone.now().date() - ultima_radiografia.date_radiograph).days

            if dias_diferencia < 10:
                return JsonResponse({
                    'success': False,
                    'mensaje': f'No han pasado 10 días desde la última radiografía. Debes esperar {10 - dias_diferencia} días más.'
                })

        # Guardar la imagen en la carpeta "sin predicción"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, CARPETA_SIN_PREDICCION))
        filename = fs.save(image_file.name, image_file)
        path_imagen_sin_prediccion = fs.path(filename)

        # Guardar la radiografía en la base de datos
        nueva_radiografia = Radiograph(
            date_radiograph=datetime.date.today(),
            image_radiograph=os.path.join(CARPETA_SIN_PREDICCION, filename),
            patient=paciente
        )
        nueva_radiografia.save()

        # Realizar la predicción utilizando la imagen subida
        predicted_class, accuracy = predict_image_class(path_imagen_sin_prediccion)

        # Mapear la clase a un resultado de detección amigable
        deteccion = {
            'BACTERIANA': 'Neumonía bacteriana',
            'NORMAL': 'Sano',
            'VIRAL': 'Neumonía vírica',
        }.get(predicted_class, 'Sano')

        # Mover la imagen a la carpeta con predicción
        path_imagen_con_prediccion = os.path.join(settings.MEDIA_ROOT, CARPETA_CON_PREDICCION, filename)
        if os.path.exists(path_imagen_con_prediccion):
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            path_imagen_con_prediccion = os.path.join(settings.MEDIA_ROOT, CARPETA_CON_PREDICCION, filename)

        os.rename(path_imagen_sin_prediccion, path_imagen_con_prediccion)

        # Actualizar la base de datos con la nueva imagen
        nueva_radiografia.image_radiograph = os.path.join(CARPETA_CON_PREDICCION, filename)
        nueva_radiografia.save()

        # Crear un análisis de la radiografía
        nuevo_analisis = Analysis(
            radiograph=nueva_radiografia,
            detection_radiograph=deteccion,
            prediction_radiograph=f"Precisión: {accuracy:.2f}%"
        )
        nuevo_analisis.save()

        # Devolver una respuesta con la nueva radiografía
        return JsonResponse({
            'success': True,
            'fecha': nueva_radiografia.date_radiograph.strftime("%d-%m-%Y"),
            'imagen': os.path.join(settings.MEDIA_URL, nueva_radiografia.image_radiograph),
            'deteccion': nuevo_analisis.detection_radiograph,
            'radiografia_id': nueva_radiografia.id,
        })

    return JsonResponse({'success': False})

# def ver_heatmap(request, paciente_id, radiografia_id):
#     try:
#         paciente = Patient.objects.get(id_patient=paciente_id)
#         radiografia = Radiograph.objects.get(id=radiografia_id, patient=paciente)
#         radiografia.analysis = radiografia.analysis_set.first() if radiografia.analysis_set.exists() else None

#         return render(request, 'heatMap.html', {
#             'paciente': paciente,
#             'radiografia': radiografia,
#             'MEDIA_URL': settings.MEDIA_URL,
#         })
#     except Patient.DoesNotExist:
#         return render(request, 'heatMap.html', {'error_message': 'Paciente no encontrado'})
#     except Radiograph.DoesNotExist:
#         return render(request, 'heatMap.html', {'error_message': 'Radiografía no encontrada'})
    
def grad_cam(input_model, img_array, layer_name):
    # Crear el modelo intermedio basado en las capas necesarias para Grad-CAM
    grad_model = tf.keras.models.Model(
        inputs=[input_model.input], 
        outputs=[input_model.get_layer(layer_name).output, input_model.output]
    )
    
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, np.argmax(predictions[0])]
        
    grads = tape.gradient(loss, conv_outputs)[0]
    guided_grads = grads * tf.cast(grads > 0, grads.dtype)
    conv_outputs = conv_outputs[0]
    weights = np.mean(guided_grads, axis=(0, 1))
    cam = np.dot(conv_outputs, weights)
    
    # Redimensionar y normalizar el mapa de calor
    cam = cv2.resize(cam, (img_array.shape[1], img_array.shape[2]))
    cam = np.maximum(cam, 0)
    heatmap = cam / cam.max() if cam.max() != 0 else cam
    return heatmap

def generate_and_save_heatmap(radiograph):
    img_path = os.path.join(settings.MEDIA_ROOT, radiograph.image_radiograph)
    print("Ruta de la imagen:", img_path)

    try:
        # Verifica si el archivo existe
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"El archivo no se encontró en la ruta: {img_path}")

        # Abre la imagen con PIL y cambia el tamaño
        with Image.open(img_path) as pil_img:
            pil_img = pil_img.resize((224, 224))
            original_img = np.array(pil_img)

        # Asegúrate de que la imagen tiene 3 canales
        if len(original_img.shape) == 2:  # Imagen en escala de grises
            original_img = np.stack((original_img,) * 3, axis=-1)

        # Procesa la imagen para el modelo
        img_array = np.expand_dims(original_img, axis=0) / 255.0
        print("Tamaño de img_array:", img_array.shape)

        # Genera el heatmap
        heatmap = grad_cam(model, img_array, layer_name="out_relu")

        # Verifica si el directorio existe o créalo
        heatmap_dir = os.path.join(settings.MEDIA_ROOT, 'heatmaps')
        if not os.path.exists(heatmap_dir):
            os.makedirs(heatmap_dir)
            print(f"Carpeta {heatmap_dir} creada para almacenar heatmaps.")

        heatmap_path = os.path.join(heatmap_dir, f"heatmap_{radiograph.id}.png")
        print(f"Guardando el heatmap en: {heatmap_path}")

        # Aplica el colormap y superpone la imagen original
        heatmap_img = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
        superimposed_img = cv2.addWeighted(heatmap_img, 0.5, original_img, 0.5, 0)

        # Convierte la imagen resultante a PIL antes de guardarla
        superimposed_img_pil = Image.fromarray(cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB))
        superimposed_img_pil.save(heatmap_path, format='PNG')
        
        print("Heatmap guardado exitosamente en:", heatmap_path)
        return heatmap_path

    except Exception as e:
        print(f"Error al generar el heatmap: {e}")
        return None
    
# Vista para mostrar el heatmap y análisis
def ver_heatmap(request, paciente_id, radiografia_id):
    paciente = get_object_or_404(Patient, id_patient=paciente_id)
    radiografia = get_object_or_404(Radiograph, id=radiografia_id)
    
    # Genera el heatmap si no existe
    heatmap_path = generate_and_save_heatmap(radiografia)
    heatmap_url = os.path.join(settings.MEDIA_URL, 'heatmaps', f"heatmap_{radiografia.id}.png") if heatmap_path else None

    # Verifica si existe el análisis
    analysis = radiografia.analysis_set.first()

    context = {
        'paciente': paciente,
        'radiografia': radiografia,
        'heatmap_url': heatmap_url,
        'analysis': analysis
    }
    return render(request, 'heatMap.html', context)
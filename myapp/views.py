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
        # Aquí reemplazas select_related con prefetch_related para optimizar
        radiografias = Radiograph.objects.filter(patient=paciente).prefetch_related('analysis_set')
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
        image_file = request.FILES['radiograph_image']
        paciente = Patient.objects.get(id_patient=paciente_id)

        # Guardar la imagen en la carpeta "sin predicción"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, CARPETA_SIN_PREDICCION))
        filename = fs.save(image_file.name, image_file)
        path_imagen_sin_prediccion = fs.path(filename)

        # Guardar el path de la imagen en la base de datos (directorio sin predicción)
        nueva_radiografia = Radiograph(
            date_radiograph=datetime.date.today(),  # Formateo correcto de la fecha
            image_radiograph=os.path.join(CARPETA_SIN_PREDICCION, filename),
            patient=paciente
        )
        nueva_radiografia.save()

        # Realizar la predicción utilizando el path de la imagen
        predicted_class, accuracy = predict_image_class(path_imagen_sin_prediccion)

        # Mapear la clase a un resultado de detección amigable
        deteccion = {
            'BACTERIANA': 'Neumonía bacteriana',
            'NORMAL': 'Sano',
            'VIRAL': 'Neumonía vírica',
        }.get(predicted_class, 'Sano')

        # Mover la imagen a la carpeta "con predicción"
        path_imagen_con_prediccion = os.path.join(settings.MEDIA_ROOT, CARPETA_CON_PREDICCION, filename)
        
        # Comprobar que la imagen existe antes de moverla
        if os.path.exists(path_imagen_sin_prediccion):
            os.rename(path_imagen_sin_prediccion, path_imagen_con_prediccion)
        else:
            return JsonResponse({'success': False, 'error': 'No se encontró la imagen sin predicción.'})

        # Actualizar la ruta de la imagen en la base de datos (directorio con predicción)
        nueva_radiografia.image_radiograph = os.path.join(CARPETA_CON_PREDICCION, filename)
        nueva_radiografia.save()

        # Guardar el análisis en la base de datos
        nuevo_analisis = Analysis(
            radiograph=nueva_radiografia,
            detection_radiograph=deteccion,
            prediction_radiograph=f"Precisión: {accuracy:.2f}%"
        )
        nuevo_analisis.save()

        # Retornar los datos para actualizar la tabla en el frontend
        return JsonResponse({
            'success': True,
            'fecha': nueva_radiografia.date_radiograph.strftime("%d-%m-%Y"),  # Formato D-M-Y
            'imagen': os.path.join(settings.MEDIA_URL, nueva_radiografia.image_radiograph),
            'deteccion': nuevo_analisis.detection_radiograph,
        })

    return JsonResponse({'success': False})

def ver_heatmap(request, paciente_id, radiografia_id):
    try:
        paciente = Patient.objects.get(id_patient=paciente_id)
        radiografia = Radiograph.objects.get(id=radiografia_id, patient=paciente)
        radiografia.analysis = radiografia.analysis_set.first() if radiografia.analysis_set.exists() else None

        return render(request, 'heatMap.html', {
            'paciente': paciente,
            'radiografia': radiografia,
            'MEDIA_URL': settings.MEDIA_URL,
        })
    except Patient.DoesNotExist:
        return render(request, 'heatMap.html', {'error_message': 'Paciente no encontrado'})
    except Radiograph.DoesNotExist:
        return render(request, 'heatMap.html', {'error_message': 'Radiografía no encontrada'})
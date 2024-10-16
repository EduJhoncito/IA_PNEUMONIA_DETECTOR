from django.shortcuts import render, redirect
from .models import Doctor, Patient, Radiograph, Analysis
from django.contrib.auth.hashers import check_password, make_password
import base64
from django.http import JsonResponse
import datetime
from django import template
from django.utils.safestring import mark_safe
from django import forms

register = template.Library()

@register.filter(name='b64encode')
def b64encode(value):
    # Asegúrate de que el valor sea un objeto de bytes
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
        radiografias = Radiograph.objects.filter(patient=paciente).select_related('analisis')
    else:
        radiografias = []

    return render(request, 'home.html', {
        'paciente': paciente,
        'radiografias': radiografias,
        'error_message': 'No se encontró al paciente' if not paciente else ''
    })

def agregar_radiografia(request, paciente_id):
    if request.method == 'POST':
        image_file = request.FILES['radiograph_image']
        paciente = Patient.objects.get(id_patient=paciente_id)

        # Guardar la radiografía en la base de datos
        nueva_radiografia = Radiograph(
            date_radiograph=datetime.date.today(),
            image_radiograph=image_file.read(),
            patient=paciente
        )
        nueva_radiografia.save()

        # Simular el análisis de detección de neumonía (aquí podrías llamar a tu IA)
        nuevo_analisis = Analysis(
            radiograph=nueva_radiografia,
            detection_radiograph="No se detecta neumonía",  # Resultado simulado
            prediction_radiograph="Predicción no disponible"  # Predicción simulada
        )
        nuevo_analisis.save()

        # Retorna la respuesta JSON con la información para agregar la fila en la tabla
        imagen_base64 = base64.b64encode(nueva_radiografia.image_radiograph).decode('utf-8')
        return JsonResponse({
            'success': True,
            'fecha': nueva_radiografia.date_radiograph,
            'imagen': imagen_base64,
            'deteccion': nuevo_analisis.detection_radiograph,
        })
    return JsonResponse({'success': False})
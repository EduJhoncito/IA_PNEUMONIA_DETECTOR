from django.shortcuts import render, redirect
from .models import Doctor
from django.contrib.auth.hashers import check_password, make_password

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
        
        # Verificar si ya existe un doctor con el mismo email
        if Doctor.objects.filter(email_doctor=email).exists():
            # Si existe, muestra una alerta de JavaScript
            return render(request, 'index.html', {
                'error_message': 'El usuario con este correo ya está registrado.'
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

#Vista de home, donde se ingresa al iniciar sesión
def home(request):
    return render(request,'home.html')
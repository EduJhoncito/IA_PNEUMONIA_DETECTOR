import pytest
from django.contrib.auth.hashers import check_password, make_password
from myapp.models import Doctor, Patient

# Test para registrar un nuevo doctor (neumólogo)
@pytest.mark.django_db
def test_registro_neumologo(client):
    # Test de registro exitoso
    response = client.post('/registrar/', {
        'nombre': 'Doctor Test',
        'email': 'test@example.com',
        'colegiatura': '1234567',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirige a 'home'

    # Verifica si el doctor se creó correctamente
    doctor = Doctor.objects.get(email_doctor='test@example.com')
    assert doctor.name_doctor == 'Doctor Test'
    assert check_password('password123', doctor.password_doctor)

# Test para iniciar sesión (login)
@pytest.mark.django_db
def test_login_neumologo(client):
    # Crea un doctor para la prueba de login
    doctor = Doctor.objects.create(
        name_doctor='Doctor Test',
        email_doctor='test@example.com',
        colegiatura_doctor='1234567',
        password_doctor=make_password('password123')  # Encripta la contraseña
    )

    # Test de login exitoso
    response = client.post('/', {
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirige a 'home'
    assert client.session['doctor_id'] == doctor.id_doctor

# Test para cambiar contraseña
@pytest.mark.django_db
def test_cambiar_contrasena(client):
    # Crea un doctor para la prueba de cambio de contraseña
    doctor = Doctor.objects.create(
        name_doctor='Doctor Test',
        email_doctor='test@example.com',
        colegiatura_doctor='1234567',
        password_doctor=make_password('oldpassword123')
    )

    # Cambio de contraseña exitoso
    response = client.post('/recuperar/', {
        'email': 'test@example.com',
        'nueva_contrasena': 'newpassword123',
        'confirmar_contrasena': 'newpassword123'
    })
    assert response.status_code == 302  # Redirige a 'login'
    doctor.refresh_from_db()  # Refresca el objeto para obtener la nueva contraseña
    assert check_password('newpassword123', doctor.password_doctor)

# Test para registrar un paciente
@pytest.mark.django_db
def test_registrar_paciente(client):
    # Crea un doctor para asociar con el paciente
    doctor = Doctor.objects.create(
        name_doctor='Doctor Test',
        email_doctor='test@example.com',
        colegiatura_doctor='1234567',
        password_doctor=make_password('password123')
    )
    client.session['doctor_id'] = doctor.id_doctor  # Simula que el doctor está logueado

    # Registro exitoso de un paciente
    response = client.post('/registrar_paciente/', {
        'nombre': 'Paciente Test',
        'dni': '12345678'
    })
    assert response.status_code == 302  # Redirige a 'home'
    assert Patient.objects.filter(name_patient='Paciente Test').exists()

# Test para acceder a la página principal (home)
@pytest.mark.django_db
def test_acceso_home(client):
    # Crea un doctor
    doctor = Doctor.objects.create(
        name_doctor='Doctor Test',
        email_doctor='test@example.com',
        colegiatura_doctor='1234567',
        password_doctor=make_password('password123')
    )
    client.session['doctor_id'] = doctor.id_doctor  # Simula que el doctor está logueado

    # Accede a la página principal
    response = client.get('/home/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_registro_neumologo_email_existente(client):
    # Registra un doctor
    client.post('/registrar/', {
        'nombre': 'Doctor Test',
        'email': 'test@example.com',
        'colegiatura': '1234567',
        'password': 'password123'
    })

    # Intenta registrar otro doctor con el mismo email
    response = client.post('/registrar/', {
        'nombre': 'Otro Doctor',
        'email': 'test@example.com',
        'colegiatura': '7654321',
        'password': 'password456'
    })

    assert response.status_code == 200  # Debe retornar un error
    assert 'El usuario con este correo ya está registrado.' in response.content.decode()

@pytest.mark.django_db
def test_acceso_home_no_autenticado(client):
    response = client.get('/home/')
    assert response.status_code == 302  # Debe redirigir al login

@pytest.mark.django_db
def test_cambiar_contrasena_exitoso(client):
    # Crea un doctor
    doctor = Doctor.objects.create(
        name_doctor='Doctor Test',
        email_doctor='test@example.com',
        colegiatura_doctor='1234567',
        password_doctor=make_password('oldpassword')
    )

    # Intenta cambiar la contraseña
    response = client.post('/recuperar/', {
        'email': 'test@example.com',
        'nueva_contrasena': 'newpassword123',
        'confirmar_contrasena': 'newpassword123'
    })

    assert response.status_code == 302  # Debe redirigir al login
    doctor.refresh_from_db()  # Refresca el objeto
    assert check_password('newpassword123', doctor.password_doctor)

@pytest.mark.django_db
def test_registrar_paciente_exitoso(client):
    # Crea un doctor
    doctor = Doctor.objects.create(
        name_doctor='Doctor Test',
        email_doctor='test@example.com',
        colegiatura_doctor='1234567',
        password_doctor=make_password('password123')
    )
    client.session['doctor_id'] = doctor.id_doctor  # Simula que el doctor está logueado

    # Registro exitoso de un paciente
    response = client.post('/registrar_paciente/', {
        'nombre': 'Paciente Test',
        'dni': '12345678'
    })
    assert response.status_code == 302  # Debe redirigir a 'home'
    assert Patient.objects.filter(name_patient='Paciente Test').exists()

@pytest.mark.django_db
def test_acceso_recuperar_contrasena(client):
    response = client.get('/recuperar/')
    assert response.status_code == 200  # Debe cargar la página


from django.db import models

# Modelo para la tabla de Doctor 
class Doctor(models.Model):
    id_doctor = models.AutoField(primary_key=True)
    name_doctor = models.CharField(max_length=255)
    email_doctor = models.EmailField(max_length=255, unique=True)
    colegiatura_doctor = models.CharField(max_length=255)
    password_doctor = models.CharField(max_length=255)

    def __str__(self):
        return self.name_doctor
    
# Modelo para la tabla de Paciente 
class Patient(models.Model):
    id_patient = models.AutoField(primary_key=True)
    name_patient = models.CharField(max_length=255)
    dni_patient = models.IntegerField(unique=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_patient  

class Radiograph(models.Model):
    date_radiograph = models.DateField()
    image_radiograph = models.CharField(max_length=255)  # Guardaremos el path en este campo
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

class Analysis(models.Model):
    radiograph = models.ForeignKey(Radiograph, on_delete=models.CASCADE)
    detection_radiograph = models.CharField(max_length=255)
    prediction_radiograph = models.CharField(max_length=255)
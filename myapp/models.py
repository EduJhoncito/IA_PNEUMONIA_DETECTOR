from django.db import models

class Doctor(models.Model):
    id_doctor = models.AutoField(primary_key=True)
    name_doctor = models.CharField(max_length=255)
    email_doctor = models.EmailField(max_length=255, unique=True)
    colegiatura_doctor = models.CharField(max_length=255)
    password_doctor = models.CharField(max_length=255)

    def __str__(self):
        return self.name_doctor
    
class Patient(models.Model):
    id_patient = models.AutoField(primary_key=True)
    name_patient = models.CharField(max_length=255)
    dni_patient = models.IntegerField(unique=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_patient
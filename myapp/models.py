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

# Modelo para la tabla de Radiografías 
class Radiograph(models.Model):
    id_radiograph = models.AutoField(primary_key=True)
    date_radiograph = models.DateField()  # Fecha de la radiografía
    image_radiograph = models.BinaryField()  # Imagen de la radiografía almacenada como BLOB
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)  # Relación con el paciente (FK)

    def __str__(self):
        return f"Radiografía {self.id_radiograph} - Paciente {self.patient}"

# Modelo para la tabla de Análisis 
class Analysis(models.Model):
    id_analysis = models.AutoField(primary_key=True)
    radiograph = models.ForeignKey(Radiograph, on_delete=models.CASCADE)  # Relación con la radiografía (FK)
    detection_radiograph = models.TextField()  # Resultado de la detección (Texto)
    heat_image_radiograph = models.BinaryField(blank=True, null=True)  # Imagen de calor (BLOB), opcional
    prediction_radiograph = models.TextField()  # Resultado de la predicción (Texto)

    def __str__(self):
        return f"Análisis {self.id_analysis} - Radiografía {self.radiograph.id_radiograph}"
# Generated by Django 5.1.1 on 2024-10-05 16:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_rename_doctor_patient_doctor_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Radiograph',
            fields=[
                ('id_radiograph', models.AutoField(primary_key=True, serialize=False)),
                ('date_radiograph', models.DateField()),
                ('image_radiograph', models.BinaryField()),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id_analysis', models.AutoField(primary_key=True, serialize=False)),
                ('detection_radiograph', models.TextField()),
                ('heat_image_radiograph', models.BinaryField(blank=True, null=True)),
                ('prediction_radiograph', models.TextField()),
                ('radiograph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.radiograph')),
            ],
        ),
    ]

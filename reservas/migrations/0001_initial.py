# Generated by Django 5.2.3 on 2025-06-26 06:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duracion_minutos', models.IntegerField(help_text='Duración del servicio en minutos')),
            ],
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField()),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('completada', 'Completada')], default='pendiente', max_length=10)),
                ('clienta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to=settings.AUTH_USER_MODEL)),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.servicio')),
            ],
            options={
                'ordering': ['-fecha_hora'],
            },
        ),
    ]

# Generated by Django 4.2.4 on 2024-05-08 09:05

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ControllerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemName', models.CharField(max_length=64)),
                ('controllerID', models.CharField(max_length=64)),
                ('controllerKey', models.CharField(max_length=32)),
                ('electricity', models.FloatField(default=100)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
            ],
            options={
                'db_table': 'controllerTable',
            },
        ),
        migrations.CreateModel(
            name='ControllerSettingHistoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('isCurrent', models.BooleanField(default=True)),
                ('on', models.BooleanField()),
                ('manualControl', models.BooleanField(default=False)),
                ('openTemp', models.FloatField(null=True)),
                ('closeTemp', models.FloatField(null=True)),
                ('cutHumidity', models.FloatField(null=True)),
                ('controller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='controllerHistory', to='greenhouse_data.controllermodel')),
            ],
            options={
                'db_table': 'controllerHistoryTable',
                'ordering': ['controller', 'timestamp'],
            },
        ),
        migrations.CreateModel(
            name='GreenhouseModel',
            fields=[
                ('greenhouseUID', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('address', models.CharField(max_length=128)),
                ('beginDate', models.DateField()),
                ('photo', models.ImageField(null=True, upload_to='image/greenhouse_photo', verbose_name='Greenhouse Avatar')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='greenhouses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'greenhouseTable',
                'ordering': ['owner', '-beginDate'],
            },
        ),
        migrations.CreateModel(
            name='RealSensorModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemName', models.CharField(max_length=64)),
                ('realSensorID', models.CharField(max_length=32)),
                ('realSensorKey', models.CharField(max_length=32)),
                ('electricity', models.FloatField(default=100)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('greenhouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='realSensors', to='greenhouse_data.greenhousemodel')),
            ],
            options={
                'db_table': 'realSensorTable',
            },
        ),
        migrations.CreateModel(
            name='SensorModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemName', models.CharField(max_length=64)),
                ('sensorKey', models.CharField(max_length=32)),
                ('realSensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='greenhouse_data.realsensormodel')),
            ],
            options={
                'db_table': 'sensorTable',
            },
        ),
        migrations.CreateModel(
            name='SensorValueHistoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('isCurrent', models.BooleanField(default=True)),
                ('value', models.FloatField()),
                ('sensor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sensorHistory', to='greenhouse_data.sensormodel')),
            ],
            options={
                'db_table': 'sensorHistoryTable',
                'ordering': ['sensor', 'timestamp'],
            },
        ),
        migrations.CreateModel(
            name='EvalveScheduleModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('startTime', models.TimeField(default=datetime.time(16, 0))),
                ('controllerSetting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evalveSchedules', to='greenhouse_data.controllersettinghistorymodel')),
            ],
            options={
                'db_table': 'evalveScheduleTable',
            },
        ),
        migrations.AddField(
            model_name='controllermodel',
            name='greenhouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='controllers', to='greenhouse_data.greenhousemodel'),
        ),
    ]

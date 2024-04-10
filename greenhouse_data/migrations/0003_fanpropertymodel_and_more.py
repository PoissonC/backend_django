# Generated by Django 4.2.4 on 2024-04-10 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('greenhouse_data', '0002_alter_controllermodel_uid_alter_greenhousemodel_uid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FanPropertyModel',
            fields=[
                ('controller', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='fanProperty', serialize=False, to='greenhouse_data.controllermodel')),
                ('openTemp', models.FloatField()),
                ('closeTemp', models.FloatField()),
            ],
            options={
                'db_table': 'fanPropertyTable',
            },
        ),
        migrations.RemoveField(
            model_name='evalvepropertymodel',
            name='cutHumidity',
        ),
        migrations.RemoveField(
            model_name='evalvepropertymodel',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='evalvepropertymodel',
            name='startTime',
        ),
        migrations.AlterField(
            model_name='evalveschedulemodel',
            name='evalveProperty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evalveSchedule', to='greenhouse_data.evalvepropertymodel'),
        ),
    ]

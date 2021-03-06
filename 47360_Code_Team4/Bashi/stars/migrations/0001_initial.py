# Generated by Django 2.0.7 on 2018-07-26 20:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Shape',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shape_id', models.CharField(max_length=20)),
                ('shape_pt_lat', models.CharField(max_length=20)),
                ('shape_pt_lon', models.CharField(max_length=20)),
                ('shape_pt_sequence', models.IntegerField()),
                ('prog_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['shape_id'],
            },
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('stop_name', models.CharField(max_length=50)),
                ('stop_lat', models.CharField(max_length=20)),
                ('stop_lon', models.CharField(max_length=20)),
                ('stop_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ['stop_id'],
            },
        ),
        migrations.CreateModel(
            name='Timetable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_id', models.CharField(max_length=50)),
                ('departure_time', models.IntegerField()),
                ('prog_number', models.IntegerField()),
                ('line_ID', models.CharField(max_length=5)),
                ('route_start_time', models.IntegerField()),
                ('route_end_time', models.IntegerField()),
                ('weekday', models.CharField(choices=[('y102m', 'from Monday to Friday'), ('y102n', 'sunday and monday'), ('y102o', 'saturday')], max_length=5)),
                ('shape_id', models.CharField(max_length=20)),
                ('previous_stopID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous_stopID', to='stars.Stop')),
                ('route_end_stop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='route_end_stop', to='stars.Stop')),
                ('route_start_stop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='route_start_stop', to='stars.Stop')),
                ('stop_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stars.Stop')),
            ],
            options={
                'ordering': ['trip_id'],
            },
        ),
        migrations.AddField(
            model_name='shape',
            name='stop_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stars.Stop'),
        ),
    ]

# Generated by Django 3.0.8 on 2020-07-14 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EKD_Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EKD_Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('ISIN', models.CharField(max_length=255)),
                ('Ticker', models.CharField(max_length=255)),
                ('Bloomberg', models.CharField(max_length=255)),
                ('EKD_ClassID', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='import.EKD_Class')),
                ('EKD_SectionID', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='import.EKD_Section')),
            ],
        ),
    ]

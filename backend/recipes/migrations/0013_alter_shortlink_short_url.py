# Generated by Django 4.2.14 on 2024-08-12 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_shortlink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortlink',
            name='short_url',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
    ]
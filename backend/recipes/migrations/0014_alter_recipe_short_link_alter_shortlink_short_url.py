# Generated by Django 4.2.14 on 2024-08-12 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_alter_shortlink_short_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='shortlink',
            name='short_url',
            field=models.CharField(blank=True, max_length=6, unique=True),
        ),
    ]

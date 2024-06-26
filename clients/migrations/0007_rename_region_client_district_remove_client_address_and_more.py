# Generated by Django 5.0.2 on 2024-05-21 12:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0006_rename_about_client_bio'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='region',
            new_name='district',
        ),
        migrations.RemoveField(
            model_name='client',
            name='address',
        ),
        migrations.AddField(
            model_name='client',
            name='industry',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='client',
            name='state',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='client',
            name='website',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='review',
            name='deleted',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='rating',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='review',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewer', to=settings.AUTH_USER_MODEL),
        ),
    ]

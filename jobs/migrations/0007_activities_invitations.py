# Generated by Django 5.0.2 on 2024-05-19 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_activities_client_last_visit_activities_deleted_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activities',
            name='invitations',
            field=models.ManyToManyField(related_name='activity', to='jobs.invitation'),
        ),
    ]

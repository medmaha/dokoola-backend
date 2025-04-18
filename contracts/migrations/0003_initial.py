# Generated by Django 5.0.2 on 2025-04-11 19:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contracts", "0002_initial"),
        ("proposals", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contract",
            name="proposal",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contract",
                to="proposals.proposal",
            ),
        ),
    ]

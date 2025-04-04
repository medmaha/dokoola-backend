# Generated by Django 5.0.2 on 2025-04-03 23:28

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0002_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="JobAgentProxy",
        ),
        migrations.AlterField(
            model_name="job",
            name="additional_payment_terms",
            field=models.CharField(blank=True, default="", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="job",
            name="bits_amount",
            field=models.IntegerField(blank=True, default=16),
        ),
        migrations.AlterField(
            model_name="job",
            name="metadata",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]

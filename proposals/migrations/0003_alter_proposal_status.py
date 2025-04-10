# Generated by Django 5.0.2 on 2025-04-06 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proposals", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="status",
            field=models.CharField(
                choices=[
                    ("REVIEW", "Review"),
                    ("PENDING", "Pending"),
                    ("ACCEPTED", "Accepted"),
                    ("EXTERNAL", "External"),
                    ("CONTRACTED", "Contracted"),
                    ("DECLINED", "Declined"),
                    ("WITHDRAWN", "Withdrawn"),
                    ("TERMINATED", "Terminated"),
                ],
                default="PENDING",
                max_length=200,
            ),
        ),
    ]

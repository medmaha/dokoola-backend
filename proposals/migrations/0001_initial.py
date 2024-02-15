# Generated by Django 4.2.2 on 2023-07-31 19:56

from django.db import migrations, models
import django.db.models.deletion
import utilities.generator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("jobs", "0001_initial"),
        ("freelancers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("file_url", models.CharField(max_length=1500)),
            ],
        ),
        migrations.CreateModel(
            name="Proposal",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=utilities.generator.hex_generator,
                        editable=False,
                        max_length=64,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("cover_letter", models.TextField(max_length=1500)),
                ("bits_amount", models.IntegerField(blank=True, default=12)),
                ("is_proposed", models.BooleanField(default=False)),
                ("budget", models.FloatField(blank=True, default=0)),
                ("discount", models.FloatField(default=0.06)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attachments",
                    models.ManyToManyField(
                        related_name="proposal", to="proposals.attachment"
                    ),
                ),
                (
                    "freelancer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="proposals",
                        to="freelancers.freelancer",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="proposals",
                        to="jobs.job",
                    ),
                ),
            ],
        ),
    ]
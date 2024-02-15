# Generated by Django 4.2.2 on 2023-07-31 19:56

from django.db import migrations, models
import django.db.models.deletion
import utilities.generator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("clients", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Activities",
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
            ],
        ),
        migrations.CreateModel(
            name="Pricing",
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
                ("fixed_price", models.BooleanField(blank=True, default=True)),
                ("negotiable_price", models.BooleanField(blank=True, default=False)),
                ("will_pay_more", models.BooleanField(blank=True, default=False)),
                ("addition", models.CharField(max_length=100)),
                ("payment_type", models.CharField(default="PROJECT", max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Job",
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
                ("slug", models.SlugField(blank=True, default="", max_length=200)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("location", models.CharField(max_length=200)),
                ("active_state", models.BooleanField(blank=True, default=True)),
                ("budget", models.DecimalField(decimal_places=2, max_digits=10)),
                ("job_type", models.CharField(blank=True, default="", max_length=1000)),
                (
                    "required_skills",
                    models.CharField(blank=True, default="", max_length=1000),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "activities",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job",
                        to="jobs.activities",
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="jobs",
                        to="clients.client",
                    ),
                ),
                (
                    "pricing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_pricing",
                        to="jobs.pricing",
                    ),
                ),
            ],
        ),
    ]
# Generated by Django 5.0.2 on 2024-05-18 21:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0004_remove_proposal_hourly_rate_proposal_is_decline_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposal',
            old_name='discount',
            new_name='service_fee',
        ),
    ]
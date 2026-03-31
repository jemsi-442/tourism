from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_booking_created_at_booking_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="contactinquiry",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

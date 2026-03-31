from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_booking_archived_at_contactinquiry_archived_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="hotel",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="main.hotel"),
        ),
        migrations.AlterField(
            model_name="booking",
            name="package",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="main.package"),
        ),
        migrations.AlterField(
            model_name="booking",
            name="safari",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="main.safari"),
        ),
        migrations.AlterField(
            model_name="booking",
            name="transport",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="main.transport"),
        ),
    ]

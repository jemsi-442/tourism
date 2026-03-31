from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

# ======================
# Admin Posts
# ======================
class AdminPost(models.Model):
    target_page = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} ({self.target_page})"

# ======================
# Packages (Tours)
# ======================
class Package(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0)],
    )
    archived_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

# ======================
# Hotels
# ======================
class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0)],
    )
    archived_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

# ======================
# Safari Options
# ======================
class Safari(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0)],
    )
    archived_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

# ======================
# Transport Options
# ======================
class Transport(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100, help_text="Vehicle type e.g. Land Cruiser, Minivan")
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0)],
    )
    archived_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.type})"

# ======================
# Bookings (User does NOT need login)
# ======================
class Booking(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, blank=True, null=True)
    safari = models.ForeignKey(Safari, on_delete=models.SET_NULL, blank=True, null=True)
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, blank=True, null=True)
    booking_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False, db_index=True)
    archived_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ("-booking_date", "-created_at")

    def __str__(self):
        return f"{self.full_name} - {self.booking_date}"

    def clean(self):
        selected_services = {
            "package": self.package,
            "hotel": self.hotel,
            "safari": self.safari,
            "transport": self.transport,
        }

        if self.booking_date and self.booking_date < timezone.localdate():
            raise ValidationError({"booking_date": "Booking date cannot be in the past."})

        if not any(selected_services.values()):
            raise ValidationError(
                "Choose at least one service: package, hotel, safari, or transport."
            )

        archived_errors = {}
        for field_name, service in selected_services.items():
            if service is not None and getattr(service, "archived_at", None):
                archived_errors[field_name] = "This option is no longer available for new bookings."
        if archived_errors:
            raise ValidationError(archived_errors)


class ContactInquiry(models.Model):
    PREFERRED_CHANNEL_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
    ]
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("resolved", "Resolved"),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    message = models.TextField()
    preferred_channel = models.CharField(
        max_length=20,
        choices=PREFERRED_CHANNEL_CHOICES,
        default="whatsapp",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    archived_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.full_name} ({self.get_preferred_channel_display()})"

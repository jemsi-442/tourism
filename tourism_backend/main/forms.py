from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils import timezone

from .models import AdminPost, Booking, ContactInquiry, Hotel, Package, Safari, Transport


ADMIN_POST_TARGET_CHOICES = [
    ("home.html", "Home"),
    ("aboutus.html", "About Us"),
    ("aboutzanzibar.html", "About Zanzibar"),
    ("book.html", "Booking"),
    ("packages.html", "Packages"),
    ("gallery.html", "Gallery"),
    ("hotel.html", "Hotel"),
    ("safari.html", "Safari"),
    ("transport.html", "Transport"),
    ("contact.html", "Contact"),
    ("admin-login.html", "Admin Login"),
]


class AdminPostForm(forms.ModelForm):
    target_page = forms.ChoiceField(choices=ADMIN_POST_TARGET_CHOICES)

    class Meta:
        model = AdminPost
        fields = ["target_page", "title", "description", "photo"]

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "full_name",
            "email",
            "phone",
            "package",
            "hotel",
            "safari",
            "transport",
            "booking_date",
        ]
        widgets = {
            "booking_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["package"].queryset = Package.objects.filter(archived_at__isnull=True).order_by("name")
        self.fields["hotel"].queryset = Hotel.objects.filter(archived_at__isnull=True).order_by("name")
        self.fields["safari"].queryset = Safari.objects.filter(archived_at__isnull=True).order_by("name")
        self.fields["transport"].queryset = Transport.objects.filter(archived_at__isnull=True).order_by("name")
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

        self.fields["full_name"].widget.attrs.update(
            {"placeholder": "Your full name", "autocomplete": "name"}
        )
        self.fields["email"].widget.attrs.update(
            {"placeholder": "you@example.com", "autocomplete": "email"}
        )
        self.fields["phone"].widget.attrs.update(
            {"placeholder": "07XXXXXXXX", "autocomplete": "tel"}
        )
        self.fields["booking_date"].widget.attrs.update(
            {"min": timezone.localdate().isoformat()}
        )
        self.fields["booking_date"].help_text = "Choose your planned arrival or travel date."

        optional_labels = {
            "package": "Select a package",
            "hotel": "Select a hotel",
            "safari": "Select a safari",
            "transport": "Select transport",
        }

        for field_name, empty_label in optional_labels.items():
            self.fields[field_name].required = False
            self.fields[field_name].empty_label = empty_label
            self.fields[field_name].help_text = (
                "Optional on its own, but at least one travel service must be selected."
            )

    def clean_booking_date(self):
        booking_date = self.cleaned_data["booking_date"]
        if booking_date < timezone.localdate():
            raise forms.ValidationError("Booking date cannot be in the past.")
        return booking_date

    def clean(self):
        cleaned_data = super().clean()
        selected_services = [
            cleaned_data.get("package"),
            cleaned_data.get("hotel"),
            cleaned_data.get("safari"),
            cleaned_data.get("transport"),
        ]
        if not any(selected_services):
            raise forms.ValidationError(
                "Choose at least one service: package, hotel, safari, or transport."
            )
        return cleaned_data


class ContactInquiryForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ["full_name", "email", "phone", "message", "preferred_channel"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update(
            {
                "class": "contact-form-input",
                "placeholder": "Your full name",
                "autocomplete": "name",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "class": "contact-form-input",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        )
        self.fields["phone"].widget.attrs.update(
            {
                "class": "contact-form-input",
                "placeholder": "07XXXXXXXX",
                "autocomplete": "tel",
            }
        )
        self.fields["message"].widget.attrs.update(
            {
                "class": "contact-form-textarea",
                "placeholder": "Tell us the trip you want, dates, group size, or any special request.",
            }
        )
        self.fields["preferred_channel"].widget = forms.RadioSelect(
            choices=ContactInquiry.PREFERRED_CHANNEL_CHOICES
        )
        self.fields["preferred_channel"].initial = "whatsapp"
        self.fields["preferred_channel"].help_text = (
            "Choose the easiest way you want us to reply."
        )

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ["name", "description", "photo", "price"]


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ["name", "location", "description", "photo", "price_per_night"]


class SafariForm(forms.ModelForm):
    class Meta:
        model = Safari
        fields = ["name", "location", "description", "photo", "price_per_person"]


class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = ["name", "type", "description", "photo", "price_per_day"]


class AdminSignupForm(UserCreationForm):
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Choose a simple username for this login."
        self.fields["email"].help_text = "Use the email that should receive account communication."
        self.fields["password1"].help_text = (
            "Use 8+ characters and avoid common or personal passwords."
        )
        self.fields["password2"].help_text = "Enter the same password again to confirm."

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user


class DashboardUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Choose a simple login name for this user."
        self.fields["email"].help_text = "Used for account contact."
        self.fields["password1"].help_text = (
            "Use 8+ characters and avoid common or personal passwords."
        )
        self.fields["password2"].help_text = "Enter the same password again to confirm."

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_staff = True
        if commit:
            user.save()
        return user

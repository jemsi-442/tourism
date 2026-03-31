from django.contrib import admin
from .models import AdminPost, Booking, ContactInquiry, Hotel, Package, Safari, Transport

# ======================
# AdminPost
# ======================
@admin.register(AdminPost)
class AdminPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_page', 'created_at')
    list_filter = ('target_page', 'created_at')
    search_fields = ('title', 'description')

# ======================
# Package
# ======================
@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'archived_at')
    list_filter = ('archived_at',)
    search_fields = ('name', 'description')

# ======================
# Hotel
# ======================
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price_per_night', 'archived_at')
    list_filter = ('location', 'archived_at')
    search_fields = ('name', 'location', 'description')

# ======================
# Safari
# ======================
@admin.register(Safari)
class SafariAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price_per_person', 'archived_at')
    list_filter = ('location', 'archived_at')
    search_fields = ('name', 'location', 'description')

# ======================
# Transport
# ======================
@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price_per_day', 'archived_at')
    list_filter = ('type', 'archived_at')
    search_fields = ('name', 'type', 'description')

# ======================
# Booking
# ======================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'booking_date', 'status', 'archived_at', 'package', 'hotel', 'safari', 'transport')
    list_filter = ('booking_date', 'status', 'archived_at')
    search_fields = ('full_name', 'email', 'phone')


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "preferred_channel", "status", "created_at", "archived_at")
    list_filter = ("preferred_channel", "status", "created_at", "archived_at")
    search_fields = ("full_name", "email", "phone", "message")

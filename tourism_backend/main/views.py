import csv

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlencode

from .models import AdminPost, Booking, ContactInquiry, Hotel, Package, Safari, Transport
from .forms import (
    AdminPostForm,
    AdminSignupForm,
    BookingForm,
    ContactInquiryForm,
    DashboardUserCreationForm,
    HotelForm,
    PackageForm,
    SafariForm,
    TransportForm,
)


PAGE_TARGETS = {
    "home": ("home.html", "index.html"),
    "aboutus": ("aboutus", "aboutus.html"),
    "aboutzanzibar": ("aboutzanzibar", "aboutzanzibar.html"),
    "admin_login": ("admin-login.html",),
    "book": ("book.html",),
    "contact": ("contact", "contact.html"),
    "gallery": ("gallery", "gallery.html"),
    "hotel": ("hotel", "hotel.html"),
    "packages": ("packages", "packages.html"),
    "safari": ("safari", "safari.html"),
    "transport": ("transport", "transport.html"),
}

admin_staff_required = staff_member_required(login_url="admin_login")


BOOKING_STATUS_VALUES = {choice[0] for choice in Booking.STATUS_CHOICES}
INQUIRY_STATUS_VALUES = {choice[0] for choice in ContactInquiry.STATUS_CHOICES}
ADMIN_DASHBOARD_PAGE_SIZE = 10
BOOKING_DELETABLE_STATUSES = {"completed", "cancelled"}
INQUIRY_DELETABLE_STATUSES = {"resolved"}
BOOKING_VISIBILITY_VALUES = {"active", "archived"}
INQUIRY_VISIBILITY_VALUES = {"active", "archived"}


def active_inventory_queryset(model):
    return model.objects.filter(archived_at__isnull=True)


def render_marketing_page(request, template_name, page_key, extra_context=None):
    admin_posts = AdminPost.objects.filter(
        target_page__in=PAGE_TARGETS.get(page_key, (page_key,))
    ).order_by("-created_at")
    context = {"admin_posts": admin_posts}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def apply_booking_filters(queryset, status_filter="", query=""):
    if status_filter in BOOKING_STATUS_VALUES:
        queryset = queryset.filter(status=status_filter)
    else:
        status_filter = ""
    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    return queryset, status_filter, query


def apply_inquiry_filters(queryset, status_filter="", query=""):
    if status_filter in INQUIRY_STATUS_VALUES:
        queryset = queryset.filter(status=status_filter)
    else:
        status_filter = ""
    if query:
        queryset = queryset.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
    return queryset, status_filter, query


def apply_booking_visibility(queryset, visibility="active"):
    if visibility == "archived":
        return queryset.filter(archived_at__isnull=False), visibility
    return queryset.filter(archived_at__isnull=True), "active"


def apply_inquiry_visibility(queryset, visibility="active"):
    if visibility == "archived":
        return queryset.filter(archived_at__isnull=False), visibility
    return queryset.filter(archived_at__isnull=True), "active"


def build_status_chart_data(choices, counts):
    max_count = max(counts.values(), default=0)
    rows = []
    for value, label in choices:
        count = counts.get(value, 0)
        width = 0 if max_count == 0 else max(8, round((count / max_count) * 100))
        rows.append(
            {
                "value": value,
                "label": label,
                "count": count,
                "width": width if count else 0,
            }
        )
    return rows


def build_recent_activity(posts, bookings, inquiries, limit=8):
    activity = []

    for post in list(posts)[:4]:
        activity.append(
            {
                "kind": "post",
                "kind_label": "Post",
                "title": post.title,
                "detail": f"Published to {post.target_page}.",
                "timestamp": post.created_at,
            }
        )

    for booking in list(bookings)[:4]:
        selected_services = [
            service_name
            for service_name, service in (
                ("package", booking.package),
                ("hotel", booking.hotel),
                ("safari", booking.safari),
                ("transport", booking.transport),
            )
            if service
        ]
        service_summary = ", ".join(selected_services) if selected_services else "custom trip"
        activity.append(
            {
                "kind": "booking",
                "kind_label": "Booking",
                "title": booking.full_name,
                "detail": f"Requested {service_summary} for {booking.booking_date}.",
                "timestamp": booking.created_at,
            }
        )

    for inquiry in list(inquiries)[:4]:
        activity.append(
            {
                "kind": "inquiry",
                "kind_label": "Inquiry",
                "title": inquiry.full_name,
                "detail": f"Sent a {inquiry.get_preferred_channel_display()} inquiry.",
                "timestamp": inquiry.created_at,
            }
        )

    activity.sort(key=lambda item: item["timestamp"], reverse=True)
    return activity[:limit]


def redirect_to_dashboard(request, fallback_path=None):
    next_path = request.POST.get("next", "").strip()
    if next_path and url_has_allowed_host_and_scheme(
        next_path,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_path)
    return redirect(fallback_path or "admin_dashboard")


def get_admin_dashboard_context(request=None, form_overrides=None):
    form_overrides = form_overrides or {}
    booking_status_filter = ""
    inquiry_status_filter = ""
    booking_query = ""
    inquiry_query = ""
    booking_visibility = "active"
    inquiry_visibility = "active"
    if request is not None:
        booking_status_filter = request.GET.get("booking_status", "").strip()
        inquiry_status_filter = request.GET.get("inquiry_status", "").strip()
        booking_query = request.GET.get("booking_query", "").strip()
        inquiry_query = request.GET.get("inquiry_query", "").strip()
        booking_visibility = request.GET.get("booking_visibility", "active").strip()
        inquiry_visibility = request.GET.get("inquiry_visibility", "active").strip()

    users = get_user_model().objects.filter(is_staff=True).order_by("username")
    posts = AdminPost.objects.all().order_by("-created_at")
    can_manage_users = bool(
        request is not None
        and request.user.is_authenticated
        and request.user.is_superuser
    )
    bookings = Booking.objects.select_related(
        "package", "hotel", "safari", "transport"
    ).all()
    inquiries = ContactInquiry.objects.all().order_by("-created_at")
    recent_posts = AdminPost.objects.all().order_by("-created_at")
    recent_bookings = Booking.objects.select_related(
        "package", "hotel", "safari", "transport"
    ).filter(archived_at__isnull=True).order_by("-created_at")
    recent_inquiries = ContactInquiry.objects.filter(archived_at__isnull=True).order_by("-created_at")
    bookings, booking_visibility = apply_booking_visibility(bookings, booking_visibility)
    inquiries, inquiry_visibility = apply_inquiry_visibility(inquiries, inquiry_visibility)
    bookings, booking_status_filter, booking_query = apply_booking_filters(
        bookings, booking_status_filter, booking_query
    )
    inquiries, inquiry_status_filter, inquiry_query = apply_inquiry_filters(
        inquiries, inquiry_status_filter, inquiry_query
    )
    booking_total = Booking.objects.filter(archived_at__isnull=True).count()
    inquiry_total = ContactInquiry.objects.filter(archived_at__isnull=True).count()
    archived_booking_total = Booking.objects.filter(archived_at__isnull=False).count()
    archived_inquiry_total = ContactInquiry.objects.filter(archived_at__isnull=False).count()
    filtered_booking_count = bookings.count()
    filtered_inquiry_count = inquiries.count()
    booking_page_number = request.GET.get("booking_page", "1") if request is not None else "1"
    inquiry_page_number = request.GET.get("inquiry_page", "1") if request is not None else "1"
    bookings = Paginator(bookings, ADMIN_DASHBOARD_PAGE_SIZE).get_page(booking_page_number)
    inquiries = Paginator(inquiries, ADMIN_DASHBOARD_PAGE_SIZE).get_page(inquiry_page_number)
    recent_activity = build_recent_activity(recent_posts, recent_bookings, recent_inquiries)
    packages = active_inventory_queryset(Package).order_by("name")
    hotels = active_inventory_queryset(Hotel).order_by("name")
    safaris = active_inventory_queryset(Safari).order_by("name")
    transports = active_inventory_queryset(Transport).order_by("name")
    active_bookings = Booking.objects.filter(archived_at__isnull=True)
    active_inquiries = ContactInquiry.objects.filter(archived_at__isnull=True)
    new_booking_total = active_bookings.filter(status="new").count()
    confirmed_booking_total = active_bookings.filter(status="confirmed").count()
    new_inquiry_total = active_inquiries.filter(status="new").count()
    resolved_inquiry_total = active_inquiries.filter(status="resolved").count()
    booking_status_counts = {
        value: active_bookings.filter(status=value).count()
        for value, _ in Booking.STATUS_CHOICES
    }
    inquiry_status_counts = {
        value: active_inquiries.filter(status=value).count()
        for value, _ in ContactInquiry.STATUS_CHOICES
    }

    return {
        "users": users,
        "can_manage_users": can_manage_users,
        "posts": posts,
        "bookings": bookings,
        "inquiries": inquiries,
        "packages": packages,
        "hotels": hotels,
        "safaris": safaris,
        "transports": transports,
        "user_total": users.count(),
        "inventory_total": hotels.count() + safaris.count() + transports.count(),
        "booking_total": booking_total,
        "inquiry_total": inquiry_total,
        "archived_booking_total": archived_booking_total,
        "archived_inquiry_total": archived_inquiry_total,
        "new_booking_total": new_booking_total,
        "confirmed_booking_total": confirmed_booking_total,
        "new_inquiry_total": new_inquiry_total,
        "resolved_inquiry_total": resolved_inquiry_total,
        "booking_status_chart": build_status_chart_data(
            Booking.STATUS_CHOICES, booking_status_counts
        ),
        "inquiry_status_chart": build_status_chart_data(
            ContactInquiry.STATUS_CHOICES, inquiry_status_counts
        ),
        "recent_activity": recent_activity,
        "filtered_booking_count": filtered_booking_count,
        "filtered_inquiry_count": filtered_inquiry_count,
        "booking_status_filter": booking_status_filter,
        "inquiry_status_filter": inquiry_status_filter,
        "booking_query": booking_query,
        "inquiry_query": inquiry_query,
        "booking_visibility": booking_visibility,
        "inquiry_visibility": inquiry_visibility,
        "booking_status_choices": Booking.STATUS_CHOICES,
        "inquiry_status_choices": ContactInquiry.STATUS_CHOICES,
        "booking_query_suffix": f"&{urlencode({'booking_query': booking_query})}" if booking_query else "",
        "inquiry_query_suffix": f"&{urlencode({'inquiry_query': inquiry_query})}" if inquiry_query else "",
        "booking_filter_query": urlencode(
            {
                key: value
                for key, value in {
                    "booking_visibility": booking_visibility if booking_visibility != "active" else "",
                    "booking_status": booking_status_filter,
                    "booking_query": booking_query,
                }.items()
                if value
            }
        ),
        "inquiry_filter_query": urlencode(
            {
                key: value
                for key, value in {
                    "inquiry_visibility": inquiry_visibility if inquiry_visibility != "active" else "",
                    "inquiry_status": inquiry_status_filter,
                    "inquiry_query": inquiry_query,
                }.items()
                if value
            }
        ),
        "current_dashboard_path": (
            request.get_full_path() if request is not None else reverse("admin_dashboard")
        ),
        "user_form": form_overrides.get("user_form", DashboardUserCreationForm()),
        "post_form": form_overrides.get("post_form", AdminPostForm()),
        "package_form": form_overrides.get("package_form", PackageForm()),
        "hotel_form": form_overrides.get("hotel_form", HotelForm()),
        "safari_form": form_overrides.get("safari_form", SafariForm()),
        "transport_form": form_overrides.get("transport_form", TransportForm()),
    }


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    allow_signup = not get_user_model().objects.filter(is_staff=True).exists()
    admin_posts = AdminPost.objects.filter(target_page="admin-login.html").order_by(
        "-created_at"
    )
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.is_staff:
            return redirect("admin_dashboard")
        messages.error(request, "This account does not have admin dashboard access.")
        logout(request)
    return render(
        request,
        "admin-login.html",
        {"form": form, "admin_posts": admin_posts, "allow_signup": allow_signup},
    )


def admin_signup_view(request):
    has_staff_user = get_user_model().objects.filter(is_staff=True).exists()

    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    if has_staff_user:
        messages.error(
            request,
            "Admin signup is closed. Please log in with an existing admin account.",
        )
        return redirect("admin_login")

    form = AdminSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Admin account created successfully. Please log in.")
        return redirect("admin_login")
    return render(
        request,
        "admin-signup.html",
        {"form": form, "bootstrap_mode": not has_staff_user},
    )


def admin_logout_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("admin_login")

# Homepage
def home_view(request):
    return render_marketing_page(request, "index.html", "home")

# About pages
def aboutus_view(request):
    return render_marketing_page(request, "aboutus.html", "aboutus")

def aboutzanzibar_view(request):
    return render_marketing_page(request, "aboutzanzibar.html", "aboutzanzibar")

# Contact
def contact_view(request):
    success = request.GET.get("success") == "1"
    form = ContactInquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"{reverse('contact')}?success=1")
    return render_marketing_page(
        request,
        "contact.html",
        "contact",
        {"form": form, "success": success},
    )

# Packages
def packages_view(request):
    return render_marketing_page(
        request,
        "packages.html",
        "packages",
        {"packages": active_inventory_queryset(Package)},
    )

# Gallery
def gallery_view(request):
    return render_marketing_page(request, "gallery.html", "gallery")

# Hotel
def hotel_view(request):
    return render_marketing_page(
        request,
        "hotel.html",
        "hotel",
        {"hotels": active_inventory_queryset(Hotel)},
    )

# Safari
def safari_view(request):
    return render_marketing_page(
        request,
        "safari.html",
        "safari",
        {"safaris": active_inventory_queryset(Safari)},
    )

# Transport
def transport_view(request):
    return render_marketing_page(
        request,
        "transport.html",
        "transport",
        {"transports": active_inventory_queryset(Transport)},
    )

# Booking form
def book_view(request):
    success = request.GET.get("success") == "1"
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('book')}?success=1")
    else:
        initial = {}
        package_id = request.GET.get("package")
        if package_id and active_inventory_queryset(Package).filter(id=package_id).exists():
            initial["package"] = package_id
        form = BookingForm(initial=initial)
    return render_marketing_page(
        request,
        "book.html",
        "book",
        {"form": form, "success": success},
    )


# Admin dashboard CRUD
@admin_staff_required
def admin_dashboard(request):
    return render(request, "admin-dashboard.html", get_admin_dashboard_context(request))


@admin_staff_required
def export_bookings_csv(request):
    booking_visibility = request.GET.get("booking_visibility", "active").strip()
    booking_status_filter = request.GET.get("booking_status", "").strip()
    booking_query = request.GET.get("booking_query", "").strip()
    bookings, _ = apply_booking_visibility(
        Booking.objects.select_related(
            "package", "hotel", "safari", "transport"
        ).all(),
        booking_visibility,
    )
    bookings, _, _ = apply_booking_filters(
        bookings,
        booking_status_filter,
        booking_query,
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="tourism-bookings.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Full Name",
            "Email",
            "Phone",
            "Package",
            "Hotel",
            "Safari",
            "Transport",
            "Booking Date",
            "Status",
            "Created At",
        ]
    )
    for booking in bookings:
        writer.writerow(
            [
                booking.full_name,
                booking.email,
                booking.phone,
                booking.package.name if booking.package else "",
                booking.hotel.name if booking.hotel else "",
                booking.safari.name if booking.safari else "",
                booking.transport.name if booking.transport else "",
                booking.booking_date,
                booking.get_status_display(),
                booking.created_at,
            ]
        )
    return response


@admin_staff_required
def export_inquiries_csv(request):
    inquiry_visibility = request.GET.get("inquiry_visibility", "active").strip()
    inquiry_status_filter = request.GET.get("inquiry_status", "").strip()
    inquiry_query = request.GET.get("inquiry_query", "").strip()
    inquiries, _ = apply_inquiry_visibility(
        ContactInquiry.objects.all().order_by("-created_at"),
        inquiry_visibility,
    )
    inquiries, _, _ = apply_inquiry_filters(
        inquiries,
        inquiry_status_filter,
        inquiry_query,
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="tourism-inquiries.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Full Name",
            "Email",
            "Phone",
            "Preferred Reply",
            "Status",
            "Message",
            "Created At",
        ]
    )
    for inquiry in inquiries:
        writer.writerow(
            [
                inquiry.full_name,
                inquiry.email,
                inquiry.phone,
                inquiry.get_preferred_channel_display(),
                inquiry.get_status_display(),
                inquiry.message,
                inquiry.created_at,
            ]
        )
    return response


@admin_staff_required
def add_dashboard_user(request):
    if not request.user.is_superuser:
        messages.error(request, "Only the account owner can create new dashboard logins.")
        return redirect_to_dashboard(request)
    if request.method == "POST":
        form = DashboardUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User account created successfully.")
            return redirect("admin_dashboard")
        messages.error(
            request,
            "User account could not be created. Please correct the highlighted fields.",
        )
        return render(
            request,
            "admin-dashboard.html",
            get_admin_dashboard_context(request, {"user_form": form}),
        )
    return redirect("admin_dashboard")

# CRUD Actions
@admin_staff_required
def add_post(request):
    if request.method == "POST":
        form = AdminPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Post created successfully.")
            return redirect('admin_dashboard')
        else:
            messages.error(
                request,
                "Post could not be created. Please correct the highlighted fields.",
            )
            return render(
                request,
                "admin-dashboard.html",
                get_admin_dashboard_context(request, {"post_form": form}),
            )
    return redirect('admin_dashboard')

@admin_staff_required
def edit_post(request, post_id):
    post = get_object_or_404(AdminPost, id=post_id)
    if request.method == "POST":
        form = AdminPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect('admin_dashboard')
        messages.error(
            request,
            "Post could not be updated. Please correct the highlighted fields.",
        )
    else:
        form = AdminPostForm(instance=post)
    return render(request, "edit_post.html", {"form": form})

@admin_staff_required
def delete_post(request, post_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    post = get_object_or_404(AdminPost, id=post_id)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('admin_dashboard')

# Package CRUD
@admin_staff_required
def add_package(request):
    if request.method == "POST":
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Package created successfully.")
            return redirect('admin_dashboard')
        else:
            messages.error(
                request,
                "Package could not be created. Please correct the highlighted fields.",
            )
            return render(
                request,
                "admin-dashboard.html",
                get_admin_dashboard_context(request, {"package_form": form}),
            )
    return redirect('admin_dashboard')

@admin_staff_required
def edit_package(request, package_id):
    package = get_object_or_404(Package, id=package_id, archived_at__isnull=True)
    if request.method == "POST":
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, "Package updated successfully.")
            return redirect('admin_dashboard')
        messages.error(
            request,
            "Package could not be updated. Please correct the highlighted fields.",
        )
    else:
        form = PackageForm(instance=package)
    return render(request, "edit_package.html", {"form": form})

@admin_staff_required
def delete_package(request, package_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    package = get_object_or_404(Package, id=package_id, archived_at__isnull=True)
    package.archived_at = timezone.now()
    package.save(update_fields=["archived_at"])
    messages.success(request, "Package archived successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def add_hotel(request):
    if request.method == "POST":
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel created successfully.")
            return redirect("admin_dashboard")
        else:
            messages.error(
                request,
                "Hotel could not be created. Please correct the highlighted fields.",
            )
            return render(
                request,
                "admin-dashboard.html",
                get_admin_dashboard_context(request, {"hotel_form": form}),
            )
    return redirect("admin_dashboard")


@admin_staff_required
def edit_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, archived_at__isnull=True)
    if request.method == "POST":
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel updated successfully.")
            return redirect("admin_dashboard")
        messages.error(
            request,
            "Hotel could not be updated. Please correct the highlighted fields.",
        )
    else:
        form = HotelForm(instance=hotel)
    return render(request, "edit_hotel.html", {"form": form})


@admin_staff_required
def delete_hotel(request, hotel_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    hotel = get_object_or_404(Hotel, id=hotel_id, archived_at__isnull=True)
    hotel.archived_at = timezone.now()
    hotel.save(update_fields=["archived_at"])
    messages.success(request, "Hotel archived successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def add_safari(request):
    if request.method == "POST":
        form = SafariForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Safari created successfully.")
            return redirect("admin_dashboard")
        else:
            messages.error(
                request,
                "Safari could not be created. Please correct the highlighted fields.",
            )
            return render(
                request,
                "admin-dashboard.html",
                get_admin_dashboard_context(request, {"safari_form": form}),
            )
    return redirect("admin_dashboard")


@admin_staff_required
def edit_safari(request, safari_id):
    safari = get_object_or_404(Safari, id=safari_id, archived_at__isnull=True)
    if request.method == "POST":
        form = SafariForm(request.POST, request.FILES, instance=safari)
        if form.is_valid():
            form.save()
            messages.success(request, "Safari updated successfully.")
            return redirect("admin_dashboard")
        messages.error(
            request,
            "Safari could not be updated. Please correct the highlighted fields.",
        )
    else:
        form = SafariForm(instance=safari)
    return render(request, "edit_safari.html", {"form": form})


@admin_staff_required
def delete_safari(request, safari_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    safari = get_object_or_404(Safari, id=safari_id, archived_at__isnull=True)
    safari.archived_at = timezone.now()
    safari.save(update_fields=["archived_at"])
    messages.success(request, "Safari archived successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def add_transport(request):
    if request.method == "POST":
        form = TransportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Transport created successfully.")
            return redirect("admin_dashboard")
        else:
            messages.error(
                request,
                "Transport could not be created. Please correct the highlighted fields.",
            )
            return render(
                request,
                "admin-dashboard.html",
                get_admin_dashboard_context(request, {"transport_form": form}),
            )
    return redirect("admin_dashboard")


@admin_staff_required
def edit_transport(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id, archived_at__isnull=True)
    if request.method == "POST":
        form = TransportForm(request.POST, request.FILES, instance=transport)
        if form.is_valid():
            form.save()
            messages.success(request, "Transport updated successfully.")
            return redirect("admin_dashboard")
        messages.error(
            request,
            "Transport could not be updated. Please correct the highlighted fields.",
        )
    else:
        form = TransportForm(instance=transport)
    return render(request, "edit_transport.html", {"form": form})


@admin_staff_required
def delete_transport(request, transport_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    transport = get_object_or_404(Transport, id=transport_id, archived_at__isnull=True)
    transport.archived_at = timezone.now()
    transport.save(update_fields=["archived_at"])
    messages.success(request, "Transport archived successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def update_booking_status(request, booking_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    booking = get_object_or_404(Booking, id=booking_id)
    status = request.POST.get("status")
    if status not in BOOKING_STATUS_VALUES:
        messages.error(request, "Invalid booking status selected.")
        return redirect_to_dashboard(request)
    booking.status = status
    booking.save(update_fields=["status"])
    messages.success(request, "Booking status updated successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def update_inquiry_status(request, inquiry_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    status = request.POST.get("status")
    if status not in INQUIRY_STATUS_VALUES:
        messages.error(request, "Invalid inquiry status selected.")
        return redirect_to_dashboard(request)
    inquiry.status = status
    inquiry.save(update_fields=["status"])
    messages.success(request, "Inquiry status updated successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def delete_booking(request, booking_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status not in BOOKING_DELETABLE_STATUSES:
        messages.error(
            request,
            "Only completed or cancelled bookings can be archived.",
        )
        return redirect_to_dashboard(request)
    booking.archived_at = timezone.now()
    booking.save(update_fields=["archived_at"])
    messages.success(request, "Booking archived successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def delete_inquiry(request, inquiry_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    if inquiry.status not in INQUIRY_DELETABLE_STATUSES:
        messages.error(
            request,
            "Only resolved inquiries can be archived.",
        )
        return redirect_to_dashboard(request)
    inquiry.archived_at = timezone.now()
    inquiry.save(update_fields=["archived_at"])
    messages.success(request, "Inquiry archived successfully.")
    return redirect_to_dashboard(request)


@admin_staff_required
def restore_booking(request, booking_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    booking = get_object_or_404(Booking, id=booking_id)
    booking.archived_at = None
    booking.save(update_fields=["archived_at"])
    messages.success(request, "Booking restored successfully.")
    return redirect_to_dashboard(
        request,
        f"{reverse('admin_dashboard')}?booking_visibility=archived#booking-section",
    )


@admin_staff_required
def restore_inquiry(request, inquiry_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    inquiry.archived_at = None
    inquiry.save(update_fields=["archived_at"])
    messages.success(request, "Inquiry restored successfully.")
    return redirect_to_dashboard(
        request,
        f"{reverse('admin_dashboard')}?inquiry_visibility=archived#inquiry-section",
    )

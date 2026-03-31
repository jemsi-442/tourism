from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AdminPost, Booking, ContactInquiry, Hotel, Package, Safari, Transport


class BookingViewTests(TestCase):
    def setUp(self):
        self.package = Package.objects.create(
            name="Stone Town Explorer",
            description="City and culture tour",
            price="120.00",
        )

    def test_book_page_renders(self):
        response = self.client.get(reverse("book"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booking")
        self.assertContains(response, "responsive-navbar")
        self.assertContains(response, "marketing-nav.js")
        self.assertContains(response, "site-footer-default")
        self.assertContains(response, "tourism")
        self.assertNotContains(response, "Nakupenda Tours & Safaris")

    def test_contact_page_uses_configured_contact_details(self):
        response = self.client.get(reverse("contact"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "contact-form-field")
        self.assertContains(response, 'data-contact-email="jemsifredrick4@gmail.com"', html=False)
        self.assertContains(response, 'data-whatsapp-number="0683186987"', html=False)
        self.assertContains(response, 'data-whatsapp-country-code="255"', html=False)

    def test_valid_booking_is_saved_and_redirects(self):
        response = self.client.post(
            reverse("book"),
            {
                "full_name": "Asha Tourism",
                "email": "asha@example.com",
                "phone": "0712345678",
                "package": self.package.id,
                "booking_date": (timezone.localdate() + timedelta(days=10)).isoformat(),
            },
        )

        self.assertRedirects(response, f"{reverse('book')}?success=1")
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_requires_at_least_one_service(self):
        response = self.client.post(
            reverse("book"),
            {
                "full_name": "No Service",
                "email": "noservice@example.com",
                "phone": "0711111111",
                "booking_date": (timezone.localdate() + timedelta(days=5)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose at least one service")
        self.assertEqual(Booking.objects.count(), 0)

    def test_invalid_booking_keeps_values_and_field_markup_visible(self):
        response = self.client.post(
            reverse("book"),
            {
                "full_name": "Asha Form State",
                "email": "asha-form@example.com",
                "phone": "0712009999",
                "booking_date": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asha Form State")
        self.assertContains(response, "asha-form@example.com")
        self.assertContains(response, "This field is required")
        self.assertContains(response, "field-errors")
        self.assertContains(response, "required-marker")

    def test_booking_date_input_uses_today_as_minimum(self):
        response = self.client.get(reverse("book"))

        self.assertContains(
            response,
            f'min="{timezone.localdate().isoformat()}"',
            html=False,
        )

    def test_book_page_renders_matching_admin_posts(self):
        AdminPost.objects.create(
            target_page="book.html",
            title="Booking Notice",
            description="Visible on the booking page.",
        )
        AdminPost.objects.create(
            target_page="contact.html",
            title="Contact Notice",
            description="Should stay off the booking page.",
        )

        response = self.client.get(reverse("book"))

        self.assertContains(response, "Booking Notice")
        self.assertNotContains(response, "Contact Notice")

    def test_book_page_prefills_package_from_query_string(self):
        response = self.client.get(reverse("book"), {"package": self.package.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'<option value="{self.package.id}" selected>{self.package.name}</option>',
            html=True,
        )

    def test_book_page_hides_archived_services_from_form(self):
        archived_package = Package.objects.create(
            name="Archived Package",
            description="Should stay hidden",
            price="180.00",
            archived_at=timezone.now(),
        )
        Hotel.objects.create(
            name="Active Hotel",
            location="Paje",
            description="Visible hotel",
            price_per_night="150.00",
        )
        archived_hotel = Hotel.objects.create(
            name="Archived Hotel",
            location="Kendwa",
            description="Should stay hidden",
            price_per_night="190.00",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("book"), {"package": archived_package.id})

        self.assertContains(response, "Active Hotel")
        self.assertNotContains(response, "Archived Package")
        self.assertNotContains(response, "Archived Hotel")

    def test_booking_rejects_archived_package_selection(self):
        archived_package = Package.objects.create(
            name="Archived Package",
            description="Should not be bookable",
            price="180.00",
            archived_at=timezone.now(),
        )

        response = self.client.post(
            reverse("book"),
            {
                "full_name": "Hidden Service Guest",
                "email": "hidden@example.com",
                "phone": "0712111999",
                "package": archived_package.id,
                "booking_date": (timezone.localdate() + timedelta(days=12)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")
        self.assertEqual(Booking.objects.count(), 0)

    def test_valid_contact_inquiry_is_saved_and_redirects(self):
        response = self.client.post(
            reverse("contact"),
            {
                "full_name": "Mariam Inquiry",
                "email": "mariam@example.com",
                "phone": "0712345000",
                "message": "We need a family trip to Zanzibar in July.",
                "preferred_channel": "whatsapp",
            },
        )

        self.assertRedirects(response, f"{reverse('contact')}?success=1")
        inquiry = ContactInquiry.objects.get()
        self.assertEqual(inquiry.full_name, "Mariam Inquiry")
        self.assertEqual(inquiry.preferred_channel, "whatsapp")


class MarketingPageAdminPostTests(TestCase):
    def test_home_page_renders_matching_admin_posts(self):
        AdminPost.objects.create(
            target_page="home.html",
            title="Tourism Home Update",
            description="Visible on the homepage",
        )
        AdminPost.objects.create(
            target_page="contact.html",
            title="Contact Update",
            description="Should not appear on the homepage",
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tourism Home Update")
        self.assertNotContains(response, "Contact Update")

    def test_aboutus_page_renders_matching_admin_posts(self):
        AdminPost.objects.create(
            target_page="aboutus.html",
            title="About Us Update",
            description="Visible on about us page",
        )
        AdminPost.objects.create(
            target_page="contact.html",
            title="Contact Update",
            description="Should not appear here",
        )

        response = self.client.get(reverse("aboutus"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Us Update")
        self.assertNotContains(response, "Contact Update")


class MarketingInventoryPageTests(TestCase):
    def test_packages_page_renders_packages_from_database(self):
        Package.objects.create(
            name="Northern Circuit Escape",
            description="A curated safari package across Tanzania's north.",
            price="260.00",
        )

        response = self.client.get(reverse("packages"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Northern Circuit Escape")
        self.assertContains(response, "260.00")
        self.assertNotContains(response, "Serengeti Migration Adventure")

    def test_packages_page_hides_archived_packages(self):
        Package.objects.create(
            name="Visible Package",
            description="Available package",
            price="280.00",
        )
        Package.objects.create(
            name="Archived Package",
            description="Hidden package",
            price="300.00",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("packages"))

        self.assertContains(response, "Visible Package")
        self.assertNotContains(response, "Archived Package")

    def test_hotel_page_renders_hotels_from_database(self):
        Hotel.objects.create(
            name="Nungwi Breeze Resort",
            location="Nungwi",
            description="Oceanfront rooms and breakfast",
            price_per_night="220.00",
        )

        response = self.client.get(reverse("hotel"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nungwi Breeze Resort")
        self.assertContains(response, "220.00")
        self.assertNotContains(response, "Top Hotels & Lodges")

    def test_hotel_page_hides_archived_hotels(self):
        Hotel.objects.create(
            name="Visible Hotel",
            location="Nungwi",
            description="Available hotel",
            price_per_night="220.00",
        )
        Hotel.objects.create(
            name="Archived Hotel",
            location="Paje",
            description="Hidden hotel",
            price_per_night="180.00",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("hotel"))

        self.assertContains(response, "Visible Hotel")
        self.assertNotContains(response, "Archived Hotel")

    def test_safari_page_renders_safaris_from_database(self):
        Safari.objects.create(
            name="Ngorongoro Explorer",
            location="Ngorongoro",
            description="Crater game drive experience",
            price_per_person="310.00",
        )

        response = self.client.get(reverse("safari"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ngorongoro Explorer")
        self.assertContains(response, "310.00")
        self.assertNotContains(response, "Tanzania's Top National Parks")

    def test_safari_page_hides_archived_safaris(self):
        Safari.objects.create(
            name="Visible Safari",
            location="Serengeti",
            description="Available safari",
            price_per_person="350.00",
        )
        Safari.objects.create(
            name="Archived Safari",
            location="Ruaha",
            description="Hidden safari",
            price_per_person="330.00",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("safari"))

        self.assertContains(response, "Visible Safari")
        self.assertNotContains(response, "Archived Safari")

    def test_transport_page_renders_transport_options_from_database(self):
        Transport.objects.create(
            name="Luxury Transfer",
            type="SUV",
            description="Private transport with driver",
            price_per_day="140.00",
        )

        response = self.client.get(reverse("transport"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Luxury Transfer")
        self.assertContains(response, "140.00")
        self.assertNotContains(response, "transportData")

    def test_transport_page_hides_archived_transport_options(self):
        Transport.objects.create(
            name="Visible Transfer",
            type="SUV",
            description="Available transport",
            price_per_day="140.00",
        )
        Transport.objects.create(
            name="Archived Transfer",
            type="Van",
            description="Hidden transport",
            price_per_day="120.00",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("transport"))

        self.assertContains(response, "Visible Transfer")
        self.assertNotContains(response, "Archived Transfer")


class MarketingTemplateAssetTests(TestCase):
    def test_home_route_uses_landing_page_assets(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "js/index.js")
        self.assertContains(response, ">Login<", html=False)
        self.assertContains(response, "landing-menu-toggle")
        self.assertContains(response, 'aria-controls="landing-menu"', html=False)
        self.assertContains(response, "Welcome to tourism")
        self.assertContains(response, "Crafting unforgettable journeys across Tanzania and Zanzibar.")
        self.assertContains(response, "site-footer-default")
        self.assertContains(response, "© 2026 tourism. All rights reserved.")
        self.assertNotContains(response, 'id="home-attractions-data"')

    def test_about_pages_use_shared_marketing_nav_script(self):
        aboutus_response = self.client.get(reverse("aboutus"))
        aboutzanzibar_response = self.client.get(reverse("aboutzanzibar"))

        self.assertContains(aboutus_response, "js/marketing-nav.js")
        self.assertContains(aboutzanzibar_response, "js/marketing-nav.js")

    def test_about_page_shows_direct_marketing_header_links(self):
        response = self.client.get(reverse("aboutus"))

        self.assertContains(response, f'href="{reverse("packages")}"')
        self.assertContains(response, f'href="{reverse("safari")}"')
        self.assertContains(response, f'href="{reverse("hotel")}"')
        self.assertContains(response, f'href="{reverse("transport")}"')
        self.assertContains(response, "navbar-auth")
        self.assertNotContains(response, "Our Tours")

    def test_hotel_page_only_loads_fallback_script_without_database_inventory(self):
        fallback_response = self.client.get(reverse("hotel"))
        Hotel.objects.create(
            name="Ocean Escape",
            location="Paje",
            description="Boutique beach stay",
            price_per_night="175.00",
        )

        inventory_response = self.client.get(reverse("hotel"))

        self.assertContains(fallback_response, "js/hotel.js")
        self.assertContains(fallback_response, "hotel-modal")
        self.assertNotContains(inventory_response, "js/hotel.js")

    def test_safari_page_only_loads_fallback_script_without_database_inventory(self):
        fallback_response = self.client.get(reverse("safari"))
        Safari.objects.create(
            name="Ruaha Adventure",
            location="Ruaha",
            description="Remote wildlife safari",
            price_per_person="420.00",
        )

        inventory_response = self.client.get(reverse("safari"))

        self.assertContains(fallback_response, "js/safari.js")
        self.assertContains(fallback_response, "safari-modal")
        self.assertNotContains(inventory_response, "js/safari.js")


class AdminAuthTests(TestCase):
    def test_admin_signup_page_uses_short_password_guidance(self):
        response = self.client.get(reverse("admin_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Use 8+ characters and avoid common or personal passwords.",
        )
        self.assertNotContains(
            response,
            "Your password can’t be too similar to your other personal information.",
        )

    def test_admin_signup_creates_staff_user(self):
        response = self.client.post(
            reverse("admin_signup"),
            {
                "username": "manager1",
                "email": "manager1@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("admin_login"))
        user = get_user_model().objects.get(username="manager1")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_admin_login_redirects_staff_to_dashboard(self):
        user = get_user_model().objects.create_user(
            username="adminuser",
            password="StrongPass123!",
            is_staff=True,
        )

        response = self.client.post(
            reverse("admin_login"),
            {"username": user.username, "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_admin_signup_is_closed_after_first_staff_user_exists(self):
        get_user_model().objects.create_user(
            username="existingadmin",
            password="StrongPass123!",
            is_staff=True,
        )

        response = self.client.post(
            reverse("admin_signup"),
            {
                "username": "manager2",
                "email": "manager2@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("admin_login"))
        self.assertFalse(
            get_user_model().objects.filter(username="manager2").exists()
        )

    def test_login_page_hides_signup_link_after_first_staff_user_exists(self):
        get_user_model().objects.create_user(
            username="existingadmin2",
            password="StrongPass123!",
            is_staff=True,
        )

        response = self.client.get(reverse("admin_login"))

        self.assertContains(response, "Login")
        self.assertNotContains(response, "Set up the first account")
        self.assertContains(response, "Need access? Ask an existing administrator to create your login.")


class AdminLogoutTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="logoutadmin",
            password="StrongPass123!",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

    def test_logout_requires_post_request(self):
        response = self.client.get(reverse("admin_logout"))

        self.assertEqual(response.status_code, 405)

    def test_logout_post_ends_session_and_redirects(self):
        response = self.client.post(reverse("admin_logout"), follow=True)

        self.assertRedirects(response, reverse("admin_login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class AdminDashboardViewTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="dashboardadmin",
            password="StrongPass123!",
            is_staff=True,
            is_superuser=True,
        )

    def test_dashboard_requires_staff_access(self):
        regular_user = get_user_model().objects.create_user(
            username="regularuser",
            password="StrongPass123!",
            is_staff=False,
        )
        self.client.force_login(regular_user)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin_login"), response.url)

    def test_dashboard_hides_user_management_for_non_superuser_staff(self):
        staff_user = get_user_model().objects.create_user(
            username="staffonly",
            password="StrongPass123!",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="user-section"', html=False)
        self.assertNotContains(response, 'action="%s"' % reverse("add_dashboard_user"), html=False)

    def test_dashboard_renders_sections_forms_and_booking_data(self):
        AdminPost.objects.create(
            target_page="home.html",
            title="Homepage Spotlight",
            description="Fresh homepage message.",
        )
        package = Package.objects.create(
            name="Stone Town Escape",
            description="City getaway",
            price="140.00",
        )
        hotel = Hotel.objects.create(
            name="Ocean Pearl",
            location="Nungwi",
            description="Beachfront hotel",
            price_per_night="210.00",
        )
        safari = Safari.objects.create(
            name="Serengeti Discovery",
            location="Serengeti",
            description="Classic wildlife safari",
            price_per_person="330.00",
        )
        transport = Transport.objects.create(
            name="Island Transfer",
            type="Van",
            description="Private road transfer",
            price_per_day="95.00",
        )
        Booking.objects.create(
            full_name="Amina Hassan",
            email="amina@example.com",
            phone="0712000000",
            package=package,
            hotel=hotel,
            safari=safari,
            transport=transport,
            booking_date=timezone.localdate() + timedelta(days=14),
        )
        ContactInquiry.objects.create(
            full_name="Juma Contact",
            email="juma@example.com",
            phone="0711112222",
            message="Need a honeymoon package in Zanzibar.",
            preferred_channel="email",
        )
        Booking.objects.create(
            full_name="Confirmed Guest",
            email="confirmed@example.com",
            phone="0712333444",
            booking_date=timezone.localdate() + timedelta(days=20),
            status="confirmed",
        )
        ContactInquiry.objects.create(
            full_name="Resolved Contact",
            email="resolved@example.com",
            phone="0711555666",
            message="Already supported.",
            preferred_channel="whatsapp",
            status="resolved",
        )

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Dashboard")
        self.assertContains(response, "Users")
        self.assertContains(response, "© 2026 tourism. All rights reserved.")
        self.assertContains(response, "Site Content")
        self.assertContains(response, "Packages")
        self.assertContains(response, "Hotels")
        self.assertContains(response, "Safaris")
        self.assertContains(response, "Transport")
        self.assertContains(response, "All Bookings")
        self.assertContains(response, "Contact Inquiries")
        self.assertContains(response, "New Bookings")
        self.assertContains(response, "Confirmed Bookings")
        self.assertContains(response, "New Inquiries")
        self.assertContains(response, "Resolved Inquiries")
        self.assertContains(response, "New bookings")
        self.assertContains(response, "New inquiries")
        self.assertContains(response, "Quick Actions")
        self.assertContains(response, "Review New Bookings")
        self.assertContains(response, "Reply to New Inquiries")
        self.assertContains(response, "Publishing")
        self.assertContains(response, "Guests")
        self.assertContains(response, "Booking Status Overview")
        self.assertContains(response, "Inquiry Status Overview")
        self.assertContains(response, "Recent Activity")
        self.assertContains(response, "js/admin-dashboard.js")
        self.assertContains(response, 'id="admin-confirm-modal"', html=False)
        self.assertContains(response, "Homepage Spotlight")
        self.assertContains(response, "Published to home.html.")
        self.assertContains(response, "Juma Contact")
        self.assertContains(response, "Email")
        self.assertContains(response, "Amina Hassan")
        self.assertContains(response, "Stone Town Escape")
        self.assertContains(response, "Ocean Pearl")
        self.assertContains(response, "Serengeti Discovery")
        self.assertContains(response, "Island Transfer")
        self.assertContains(response, 'data-label="Name"', html=False)
        self.assertContains(response, 'data-label="Preferred Reply"', html=False)
        self.assertContains(response, 'action="%s"' % reverse("add_dashboard_user"), html=False)
        self.assertContains(response, 'action="%s"' % reverse("add_post"), html=False)
        self.assertContains(response, 'action="%s"' % reverse("add_package"), html=False)
        self.assertContains(response, 'action="%s"' % reverse("add_hotel"), html=False)
        self.assertContains(response, 'action="%s"' % reverse("add_safari"), html=False)
        self.assertContains(response, 'action="%s"' % reverse("add_transport"), html=False)
        self.assertContains(response, 'action="%s"' % reverse("update_booking_status", args=[Booking.objects.first().id]), html=False)
        self.assertContains(response, 'action="%s"' % reverse("update_inquiry_status", args=[ContactInquiry.objects.first().id]), html=False)
        self.assertContains(response, f'href="{reverse("admin_dashboard")}?booking_status=new#booking-section"', html=False)
        self.assertContains(response, f'href="{reverse("admin_dashboard")}?inquiry_status=new#inquiry-section"', html=False)

    def test_recent_activity_is_not_limited_by_dashboard_pagination(self):
        for index in range(12):
            Booking.objects.create(
                full_name=f"Older Booking {index}",
                email=f"older-booking-{index}@example.com",
                phone=f"0712999{index:03d}",
                booking_date=timezone.localdate() + timedelta(days=index + 1),
                created_at=timezone.now() - timedelta(days=20 - index),
            )
        newest_booking = Booking.objects.create(
            full_name="Newest Activity Booking",
            email="newest-activity@example.com",
            phone="0712555000",
            booking_date=timezone.localdate() + timedelta(days=30),
        )

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("admin_dashboard"), {"booking_page": 2})

        recent_titles = [item["title"] for item in response.context["recent_activity"]]
        recent_timestamps = [item["timestamp"] for item in response.context["recent_activity"]]

        self.assertIn("Newest Activity Booking", recent_titles)
        self.assertIn(newest_booking.created_at, recent_timestamps)


class AdminStatusUpdateTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="statusadmin",
            password="StrongPass123!",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(self.staff_user)

    def test_update_booking_status_requires_post(self):
        booking = Booking.objects.create(
            full_name="Status Booking",
            email="status-booking@example.com",
            phone="0711000000",
            booking_date=timezone.localdate() + timedelta(days=7),
        )

        response = self.client.get(reverse("update_booking_status", args=[booking.id]))

        self.assertEqual(response.status_code, 405)

    def test_update_booking_status_saves_value(self):
        booking = Booking.objects.create(
            full_name="Status Booking",
            email="status-booking@example.com",
            phone="0711000000",
            booking_date=timezone.localdate() + timedelta(days=7),
        )

        response = self.client.post(
            reverse("update_booking_status", args=[booking.id]),
            {"status": "confirmed"},
            follow=True,
        )

        booking.refresh_from_db()
        self.assertEqual(booking.status, "confirmed")
        self.assertContains(response, "Booking status updated successfully.")

    def test_update_booking_status_preserves_dashboard_context(self):
        booking = Booking.objects.create(
            full_name="Context Booking",
            email="context-booking@example.com",
            phone="0711000090",
            booking_date=timezone.localdate() + timedelta(days=8),
            status="new",
        )
        next_path = f"{reverse('admin_dashboard')}?booking_status=new&booking_query=Context#booking-section"

        response = self.client.post(
            reverse("update_booking_status", args=[booking.id]),
            {"status": "contacted", "next": next_path},
        )

        booking.refresh_from_db()
        self.assertEqual(booking.status, "contacted")
        self.assertRedirects(response, next_path, fetch_redirect_response=False)

    def test_update_inquiry_status_requires_post(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Status Inquiry",
            email="status-inquiry@example.com",
            phone="0711000001",
            message="Need help with safari.",
        )

        response = self.client.get(reverse("update_inquiry_status", args=[inquiry.id]))

        self.assertEqual(response.status_code, 405)

    def test_update_inquiry_status_saves_value(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Status Inquiry",
            email="status-inquiry@example.com",
            phone="0711000001",
            message="Need help with safari.",
        )

        response = self.client.post(
            reverse("update_inquiry_status", args=[inquiry.id]),
            {"status": "resolved"},
            follow=True,
        )

        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, "resolved")
        self.assertContains(response, "Inquiry status updated successfully.")

    def test_dashboard_shows_one_click_status_shortcuts(self):
        Booking.objects.create(
            full_name="Shortcut New Booking",
            email="shortcut-new-booking@example.com",
            phone="0711000010",
            booking_date=timezone.localdate() + timedelta(days=9),
            status="new",
        )
        Booking.objects.create(
            full_name="Shortcut Contacted Booking",
            email="shortcut-contacted-booking@example.com",
            phone="0711000011",
            booking_date=timezone.localdate() + timedelta(days=10),
            status="contacted",
        )
        ContactInquiry.objects.create(
            full_name="Shortcut New Inquiry",
            email="shortcut-new-inquiry@example.com",
            phone="0711000012",
            message="Need an update.",
            status="new",
        )
        ContactInquiry.objects.create(
            full_name="Shortcut Contacted Inquiry",
            email="shortcut-contacted-inquiry@example.com",
            phone="0711000013",
            message="Already reached out once.",
            status="contacted",
        )
        Booking.objects.create(
            full_name="Shortcut Completed Booking",
            email="shortcut-completed-booking@example.com",
            phone="0711000014",
            booking_date=timezone.localdate() + timedelta(days=11),
            status="completed",
        )

        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(response, "Mark Contacted")
        self.assertContains(response, "Confirm Trip")
        self.assertContains(response, "Resolve")
        self.assertContains(response, "View Archived Bookings")
        self.assertContains(response, "data-confirm-action")
        self.assertContains(response, "Archive Booking")

    def test_delete_booking_requires_post(self):
        booking = Booking.objects.create(
            full_name="Delete Booking",
            email="delete-booking@example.com",
            phone="0711000014",
            booking_date=timezone.localdate() + timedelta(days=11),
            status="completed",
        )

        response = self.client.get(reverse("delete_booking", args=[booking.id]))

        self.assertEqual(response.status_code, 405)

    def test_delete_booking_archives_terminal_record(self):
        booking = Booking.objects.create(
            full_name="Completed Booking",
            email="completed-booking@example.com",
            phone="0711000015",
            booking_date=timezone.localdate() + timedelta(days=12),
            status="completed",
        )

        response = self.client.post(reverse("delete_booking", args=[booking.id]), follow=True)

        booking.refresh_from_db()
        self.assertIsNotNone(booking.archived_at)
        self.assertContains(response, "Booking archived successfully.")

    def test_delete_booking_rejects_active_record(self):
        booking = Booking.objects.create(
            full_name="Active Booking",
            email="active-booking@example.com",
            phone="0711000016",
            booking_date=timezone.localdate() + timedelta(days=13),
            status="new",
        )

        response = self.client.post(reverse("delete_booking", args=[booking.id]), follow=True)

        self.assertTrue(Booking.objects.filter(id=booking.id).exists())
        self.assertContains(
            response,
            "Only completed or cancelled bookings can be archived.",
        )

    def test_delete_inquiry_requires_post(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Delete Inquiry",
            email="delete-inquiry@example.com",
            phone="0711000017",
            message="Finished inquiry.",
            status="resolved",
        )

        response = self.client.get(reverse("delete_inquiry", args=[inquiry.id]))

        self.assertEqual(response.status_code, 405)

    def test_delete_inquiry_archives_resolved_record(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Resolved Inquiry Delete",
            email="resolved-delete@example.com",
            phone="0711000018",
            message="This one can go.",
            status="resolved",
        )

        response = self.client.post(reverse("delete_inquiry", args=[inquiry.id]), follow=True)

        inquiry.refresh_from_db()
        self.assertIsNotNone(inquiry.archived_at)
        self.assertContains(response, "Inquiry archived successfully.")

    def test_delete_inquiry_rejects_active_record(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Active Inquiry",
            email="active-inquiry@example.com",
            phone="0711000019",
            message="Still waiting on follow-up.",
            status="new",
        )

        response = self.client.post(reverse("delete_inquiry", args=[inquiry.id]), follow=True)

        self.assertTrue(ContactInquiry.objects.filter(id=inquiry.id).exists())
        self.assertContains(
            response,
            "Only resolved inquiries can be archived.",
        )

    def test_restore_booking_requires_post(self):
        booking = Booking.objects.create(
            full_name="Restore Booking",
            email="restore-booking@example.com",
            phone="0711000020",
            booking_date=timezone.localdate() + timedelta(days=14),
            status="completed",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("restore_booking", args=[booking.id]))

        self.assertEqual(response.status_code, 405)

    def test_restore_booking_makes_record_active_again(self):
        booking = Booking.objects.create(
            full_name="Archived Booking",
            email="archived-booking@example.com",
            phone="0711000021",
            booking_date=timezone.localdate() + timedelta(days=15),
            status="completed",
            archived_at=timezone.now(),
        )

        response = self.client.post(reverse("restore_booking", args=[booking.id]), follow=True)

        booking.refresh_from_db()
        self.assertIsNone(booking.archived_at)
        self.assertContains(response, "Booking restored successfully.")

    def test_restore_booking_preserves_archived_view_context(self):
        booking = Booking.objects.create(
            full_name="Archived Context Booking",
            email="archived-context-booking@example.com",
            phone="0711000091",
            booking_date=timezone.localdate() + timedelta(days=15),
            status="completed",
            archived_at=timezone.now(),
        )
        next_path = f"{reverse('admin_dashboard')}?booking_visibility=archived&booking_query=Archived#booking-section"

        response = self.client.post(
            reverse("restore_booking", args=[booking.id]),
            {"next": next_path},
        )

        booking.refresh_from_db()
        self.assertIsNone(booking.archived_at)
        self.assertRedirects(response, next_path, fetch_redirect_response=False)

    def test_restore_inquiry_requires_post(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Restore Inquiry",
            email="restore-inquiry@example.com",
            phone="0711000022",
            message="Restore me.",
            status="resolved",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("restore_inquiry", args=[inquiry.id]))

        self.assertEqual(response.status_code, 405)

    def test_restore_inquiry_makes_record_active_again(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Archived Inquiry",
            email="archived-inquiry@example.com",
            phone="0711000023",
            message="Ready to restore.",
            status="resolved",
            archived_at=timezone.now(),
        )

        response = self.client.post(reverse("restore_inquiry", args=[inquiry.id]), follow=True)

        inquiry.refresh_from_db()
        self.assertIsNone(inquiry.archived_at)
        self.assertContains(response, "Inquiry restored successfully.")

    def test_dashboard_hides_archived_records_from_active_view(self):
        Booking.objects.create(
            full_name="Visible Booking",
            email="visible-booking@example.com",
            phone="0711000024",
            booking_date=timezone.localdate() + timedelta(days=16),
            status="new",
        )
        Booking.objects.create(
            full_name="Archived Booking Hidden",
            email="archived-hidden-booking@example.com",
            phone="0711000025",
            booking_date=timezone.localdate() + timedelta(days=17),
            status="completed",
            archived_at=timezone.now(),
        )

        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(response, "Visible Booking")
        self.assertNotContains(response, "Archived Booking Hidden")

    def test_dashboard_can_show_archived_records(self):
        Booking.objects.create(
            full_name="Archived Booking Visible",
            email="archived-visible-booking@example.com",
            phone="0711000026",
            booking_date=timezone.localdate() + timedelta(days=18),
            status="completed",
            archived_at=timezone.now(),
        )
        ContactInquiry.objects.create(
            full_name="Archived Inquiry Visible",
            email="archived-visible-inquiry@example.com",
            phone="0711000027",
            message="Archived inquiry.",
            status="resolved",
            archived_at=timezone.now(),
        )

        booking_response = self.client.get(
            reverse("admin_dashboard"),
            {"booking_visibility": "archived"},
        )
        inquiry_response = self.client.get(
            reverse("admin_dashboard"),
            {"inquiry_visibility": "archived"},
        )

        self.assertContains(booking_response, "Archived Bookings")
        self.assertContains(booking_response, "Archived Booking Visible")
        self.assertContains(booking_response, "Restore Booking")
        self.assertContains(inquiry_response, "Archived Inquiries")
        self.assertContains(inquiry_response, "Archived Inquiry Visible")
        self.assertContains(inquiry_response, "Restore Inquiry")

    def test_dashboard_filters_bookings_by_status(self):
        Booking.objects.create(
            full_name="New Booking",
            email="new-booking@example.com",
            phone="0711000100",
            booking_date=timezone.localdate() + timedelta(days=10),
            status="new",
        )
        Booking.objects.create(
            full_name="Confirmed Booking",
            email="confirmed-booking@example.com",
            phone="0711000101",
            booking_date=timezone.localdate() + timedelta(days=11),
            status="confirmed",
        )

        response = self.client.get(reverse("admin_dashboard"), {"booking_status": "confirmed"})

        self.assertContains(response, "Confirmed Booking")
        self.assertNotContains(response, "new-booking@example.com")
        self.assertContains(response, "admin-filter-chip active")

    def test_dashboard_filters_inquiries_by_status(self):
        ContactInquiry.objects.create(
            full_name="New Inquiry",
            email="new-inquiry@example.com",
            phone="0711000200",
            message="Need booking help.",
            status="new",
        )
        ContactInquiry.objects.create(
            full_name="Resolved Inquiry",
            email="resolved-inquiry@example.com",
            phone="0711000201",
            message="Already helped.",
            status="resolved",
        )

        response = self.client.get(reverse("admin_dashboard"), {"inquiry_status": "resolved"})

        inquiry_names = [inquiry.full_name for inquiry in response.context["inquiries"].object_list]
        self.assertIn("Resolved Inquiry", inquiry_names)
        self.assertNotIn("New Inquiry", inquiry_names)

    def test_dashboard_searches_bookings_by_name_email_or_phone(self):
        Booking.objects.create(
            full_name="Searchable Booking",
            email="search-booking@example.com",
            phone="0711222333",
            booking_date=timezone.localdate() + timedelta(days=12),
            status="new",
        )
        Booking.objects.create(
            full_name="Other Booking",
            email="other-booking@example.com",
            phone="0711999888",
            booking_date=timezone.localdate() + timedelta(days=13),
            status="new",
        )

        response = self.client.get(reverse("admin_dashboard"), {"booking_query": "0711222333"})

        booking_names = [booking.full_name for booking in response.context["bookings"].object_list]
        self.assertIn("Searchable Booking", booking_names)
        self.assertNotIn("Other Booking", booking_names)

    def test_dashboard_searches_inquiries_by_name_email_or_phone(self):
        ContactInquiry.objects.create(
            full_name="Searchable Inquiry",
            email="search-inquiry@example.com",
            phone="0711444555",
            message="Need airport pickup.",
            status="new",
        )
        ContactInquiry.objects.create(
            full_name="Other Inquiry",
            email="other-inquiry@example.com",
            phone="0711666777",
            message="Need hotel advice.",
            status="new",
        )

        response = self.client.get(reverse("admin_dashboard"), {"inquiry_query": "search-inquiry@example.com"})

        inquiry_names = [inquiry.full_name for inquiry in response.context["inquiries"].object_list]
        self.assertIn("Searchable Inquiry", inquiry_names)
        self.assertNotIn("Other Inquiry", inquiry_names)

    def test_dashboard_paginates_bookings(self):
        for index in range(12):
            Booking.objects.create(
                full_name=f"Paged Booking {index}",
                email=f"paged-booking-{index}@example.com",
                phone=f"0711555{index:03d}",
                booking_date=timezone.localdate() + timedelta(days=index + 1),
                status="new",
            )

        response = self.client.get(reverse("admin_dashboard"), {"booking_page": 2})

        self.assertContains(response, "Page 2 of 2")
        booking_names = [booking.full_name for booking in response.context["bookings"].object_list]
        self.assertIn("Paged Booking 1", booking_names)
        self.assertNotIn("Paged Booking 11", booking_names)

    def test_dashboard_paginates_inquiries(self):
        for index in range(12):
            ContactInquiry.objects.create(
                full_name=f"Paged Inquiry {index}",
                email=f"paged-inquiry-{index}@example.com",
                phone=f"0711666{index:03d}",
                message="Pagination test inquiry.",
                status="new",
            )

        response = self.client.get(reverse("admin_dashboard"), {"inquiry_page": 2})

        self.assertContains(response, "Page 2 of 2")
        inquiry_names = [inquiry.full_name for inquiry in response.context["inquiries"].object_list]
        self.assertIn("Paged Inquiry 1", inquiry_names)
        self.assertNotIn("Paged Inquiry 11", inquiry_names)

    def test_bookings_csv_export_respects_filters(self):
        Booking.objects.create(
            full_name="Export Booking Match",
            email="export-match@example.com",
            phone="0711777000",
            booking_date=timezone.localdate() + timedelta(days=20),
            status="confirmed",
        )
        Booking.objects.create(
            full_name="Export Booking Skip",
            email="export-skip@example.com",
            phone="0711777001",
            booking_date=timezone.localdate() + timedelta(days=21),
            status="new",
        )

        response = self.client.get(
            reverse("export_bookings_csv"),
            {"booking_status": "confirmed"},
        )

        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=\"tourism-bookings.csv\"", response["Content-Disposition"])
        self.assertIn("Export Booking Match", content)
        self.assertNotIn("Export Booking Skip", content)

    def test_inquiries_csv_export_respects_search(self):
        ContactInquiry.objects.create(
            full_name="Export Inquiry Match",
            email="export-inquiry-match@example.com",
            phone="0711888000",
            message="Need transport support.",
            status="new",
        )
        ContactInquiry.objects.create(
            full_name="Export Inquiry Skip",
            email="export-inquiry-skip@example.com",
            phone="0711888001",
            message="Need hotel support.",
            status="new",
        )

        response = self.client.get(
            reverse("export_inquiries_csv"),
            {"inquiry_query": "export-inquiry-match@example.com"},
        )

        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=\"tourism-inquiries.csv\"", response["Content-Disposition"])
        self.assertIn("Export Inquiry Match", content)
        self.assertNotIn("Export Inquiry Skip", content)

    def test_dashboard_shows_success_message_after_creating_hotel(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("add_hotel"),
            {
                "name": "Success Hotel",
                "location": "Jambiani",
                "description": "Freshly added hotel",
                "price_per_night": "190.00",
            },
            follow=True,
        )

        self.assertContains(response, "Hotel created successfully.")

    def test_dashboard_allows_superuser_to_create_another_user(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("add_dashboard_user"),
            {
                "username": "teammember",
                "email": "teammember@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        self.assertContains(response, "User account created successfully.")
        created_user = get_user_model().objects.get(username="teammember")
        self.assertTrue(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)

    def test_dashboard_blocks_non_superuser_from_creating_user(self):
        non_superuser = get_user_model().objects.create_user(
            username="contentmanager",
            password="StrongPass123!",
            is_staff=True,
        )
        self.client.force_login(non_superuser)

        response = self.client.post(
            reverse("add_dashboard_user"),
            {
                "username": "blockeduser",
                "email": "blocked@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        self.assertContains(response, "Only the account owner can create new dashboard logins.")
        self.assertFalse(get_user_model().objects.filter(username="blockeduser").exists())

    def test_dashboard_keeps_invalid_user_form_errors_visible(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("add_dashboard_user"),
            {
                "username": "",
                "email": "broken@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin-dashboard.html")
        self.assertContains(response, "User account could not be created. Please correct the highlighted fields.")
        self.assertContains(response, "This field is required")
        self.assertContains(response, "broken@example.com")

    def test_dashboard_user_form_uses_short_password_guidance(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(
            response,
            "Use 8+ characters and avoid common or personal passwords.",
        )
        self.assertNotContains(
            response,
            "Your password can’t be too similar to your other personal information.",
        )

    def test_dashboard_shows_error_message_after_invalid_transport_create(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("add_transport"),
            {
                "name": "",
                "type": "SUV",
                "description": "Broken create attempt",
                "price_per_day": "120.00",
            },
            follow=True,
        )

        self.assertContains(
            response,
            "Transport could not be created. Please correct the highlighted fields.",
        )

    def test_dashboard_keeps_invalid_transport_form_errors_visible(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("add_transport"),
            {
                "name": "",
                "type": "SUV",
                "description": "Broken create attempt",
                "price_per_day": "120.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin-dashboard.html")
        self.assertContains(response, "This field is required")
        self.assertContains(response, "Broken create attempt")
        self.assertContains(response, "admin-form-errors")
        self.assertIn("name", response.context["transport_form"].errors)

    def test_dashboard_uses_shared_admin_form_markup(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(response, "admin-form-grid")
        self.assertContains(response, "admin-form-field")


class AdminDeleteActionTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="staffmanager",
            password="StrongPass123!",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

    def test_delete_post_requires_post_request(self):
        post = AdminPost.objects.create(
            target_page="aboutus.html",
            title="Delete me",
            description="Temporary",
        )

        response = self.client.get(reverse("delete_post", args=[post.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(AdminPost.objects.filter(id=post.id).exists())

    def test_delete_post_via_post_removes_record(self):
        post = AdminPost.objects.create(
            target_page="aboutus.html",
            title="Delete me",
            description="Temporary",
        )

        response = self.client.post(reverse("delete_post", args=[post.id]))

        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertFalse(AdminPost.objects.filter(id=post.id).exists())

    def test_delete_package_requires_post_request(self):
        package = Package.objects.create(
            name="Remove Package",
            description="Temporary package",
            price="100.00",
        )

        response = self.client.get(reverse("delete_package", args=[package.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Package.objects.filter(id=package.id).exists())

    def test_delete_package_via_post_archives_record(self):
        package = Package.objects.create(
            name="Remove Package",
            description="Temporary package",
            price="100.00",
        )
        booking = Booking.objects.create(
            full_name="Package Booking",
            email="package-booking@example.com",
            phone="0712111000",
            package=package,
            booking_date=timezone.localdate() + timedelta(days=7),
        )

        response = self.client.post(
            reverse("delete_package", args=[package.id]),
            {"next": reverse("admin_dashboard")},
            follow=True,
        )

        self.assertContains(response, "Package archived successfully.")
        package.refresh_from_db()
        self.assertIsNotNone(package.archived_at)
        booking.refresh_from_db()
        self.assertEqual(booking.package_id, package.id)
        package_names = [item.name for item in response.context["packages"]]
        self.assertNotIn("Remove Package", package_names)

    def test_delete_hotel_requires_post_request(self):
        hotel = Hotel.objects.create(
            name="Remove Hotel",
            location="Kendwa",
            description="Temporary hotel",
            price_per_night="150.00",
        )

        response = self.client.get(reverse("delete_hotel", args=[hotel.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Hotel.objects.filter(id=hotel.id).exists())

    def test_delete_hotel_via_post_archives_record(self):
        hotel = Hotel.objects.create(
            name="Remove Hotel",
            location="Kendwa",
            description="Temporary hotel",
            price_per_night="150.00",
        )
        booking = Booking.objects.create(
            full_name="Hotel Booking",
            email="hotel-booking@example.com",
            phone="0712111001",
            hotel=hotel,
            booking_date=timezone.localdate() + timedelta(days=8),
        )

        response = self.client.post(
            reverse("delete_hotel", args=[hotel.id]),
            {"next": reverse("admin_dashboard")},
            follow=True,
        )

        self.assertContains(response, "Hotel archived successfully.")
        hotel.refresh_from_db()
        self.assertIsNotNone(hotel.archived_at)
        booking.refresh_from_db()
        self.assertEqual(booking.hotel_id, hotel.id)
        hotel_names = [item.name for item in response.context["hotels"]]
        self.assertNotIn("Remove Hotel", hotel_names)

    def test_delete_safari_requires_post_request(self):
        safari = Safari.objects.create(
            name="Remove Safari",
            location="Tarangire",
            description="Temporary safari",
            price_per_person="260.00",
        )

        response = self.client.get(reverse("delete_safari", args=[safari.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Safari.objects.filter(id=safari.id).exists())

    def test_delete_safari_via_post_archives_record(self):
        safari = Safari.objects.create(
            name="Remove Safari",
            location="Tarangire",
            description="Temporary safari",
            price_per_person="260.00",
        )
        booking = Booking.objects.create(
            full_name="Safari Booking",
            email="safari-booking@example.com",
            phone="0712111002",
            safari=safari,
            booking_date=timezone.localdate() + timedelta(days=9),
        )

        response = self.client.post(
            reverse("delete_safari", args=[safari.id]),
            {"next": reverse("admin_dashboard")},
            follow=True,
        )

        self.assertContains(response, "Safari archived successfully.")
        safari.refresh_from_db()
        self.assertIsNotNone(safari.archived_at)
        booking.refresh_from_db()
        self.assertEqual(booking.safari_id, safari.id)
        safari_names = [item.name for item in response.context["safaris"]]
        self.assertNotIn("Remove Safari", safari_names)

    def test_delete_transport_requires_post_request(self):
        transport = Transport.objects.create(
            name="Remove Transport",
            type="SUV",
            description="Temporary transport",
            price_per_day="110.00",
        )

        response = self.client.get(reverse("delete_transport", args=[transport.id]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Transport.objects.filter(id=transport.id).exists())

    def test_delete_transport_via_post_archives_record(self):
        transport = Transport.objects.create(
            name="Remove Transport",
            type="SUV",
            description="Temporary transport",
            price_per_day="110.00",
        )
        booking = Booking.objects.create(
            full_name="Transport Booking",
            email="transport-booking@example.com",
            phone="0712111003",
            transport=transport,
            booking_date=timezone.localdate() + timedelta(days=10),
        )

        response = self.client.post(
            reverse("delete_transport", args=[transport.id]),
            {"next": reverse("admin_dashboard")},
            follow=True,
        )

        self.assertContains(response, "Transport archived successfully.")
        transport.refresh_from_db()
        self.assertIsNotNone(transport.archived_at)
        booking.refresh_from_db()
        self.assertEqual(booking.transport_id, transport.id)
        transport_names = [item.name for item in response.context["transports"]]
        self.assertNotIn("Remove Transport", transport_names)


class AdminInventoryCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="inventoryadmin",
            password="StrongPass123!",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

    def test_add_hotel_creates_record(self):
        response = self.client.post(
            reverse("add_hotel"),
            {
                "name": "Ocean View Hotel",
                "location": "Nungwi",
                "description": "Beachfront stay",
                "price_per_night": "180.00",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertTrue(Hotel.objects.filter(name="Ocean View Hotel").exists())

    def test_add_safari_creates_record(self):
        response = self.client.post(
            reverse("add_safari"),
            {
                "name": "Serengeti Drive",
                "location": "Serengeti",
                "description": "Wildlife safari",
                "price_per_person": "250.00",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertTrue(Safari.objects.filter(name="Serengeti Drive").exists())

    def test_add_transport_creates_record(self):
        response = self.client.post(
            reverse("add_transport"),
            {
                "name": "Airport Transfer",
                "type": "Minivan",
                "description": "Private pickup service",
                "price_per_day": "90.00",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertTrue(Transport.objects.filter(name="Airport Transfer").exists())

    def test_edit_hotel_updates_record(self):
        hotel = Hotel.objects.create(
            name="Ocean View Hotel",
            location="Nungwi",
            description="Beachfront stay",
            price_per_night="180.00",
        )

        response = self.client.post(
            reverse("edit_hotel", args=[hotel.id]),
            {
                "name": "Ocean View Resort",
                "location": "Paje",
                "description": "Updated beachfront stay",
                "price_per_night": "210.00",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        hotel.refresh_from_db()
        self.assertEqual(hotel.name, "Ocean View Resort")
        self.assertEqual(hotel.location, "Paje")

    def test_edit_hotel_page_renders_existing_record(self):
        hotel = Hotel.objects.create(
            name="Ocean View Hotel",
            location="Nungwi",
            description="Beachfront stay",
            price_per_night="180.00",
        )

        response = self.client.get(reverse("edit_hotel", args=[hotel.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Hotel")
        self.assertContains(response, "Ocean View Hotel")

    def test_edit_hotel_with_invalid_data_keeps_original_record(self):
        hotel = Hotel.objects.create(
            name="Ocean View Hotel",
            location="Nungwi",
            description="Beachfront stay",
            price_per_night="180.00",
        )

        response = self.client.post(
            reverse("edit_hotel", args=[hotel.id]),
            {
                "name": "",
                "location": "Paje",
                "description": "Updated beachfront stay",
                "price_per_night": "210.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        hotel.refresh_from_db()
        self.assertEqual(hotel.name, "Ocean View Hotel")

    def test_edit_safari_updates_record(self):
        safari = Safari.objects.create(
            name="Serengeti Drive",
            location="Serengeti",
            description="Wildlife safari",
            price_per_person="250.00",
        )

        response = self.client.post(
            reverse("edit_safari", args=[safari.id]),
            {
                "name": "Serengeti Premium Drive",
                "location": "Ngorongoro",
                "description": "Updated wildlife safari",
                "price_per_person": "320.00",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        safari.refresh_from_db()
        self.assertEqual(safari.name, "Serengeti Premium Drive")
        self.assertEqual(safari.location, "Ngorongoro")

    def test_edit_safari_page_renders_existing_record(self):
        safari = Safari.objects.create(
            name="Serengeti Drive",
            location="Serengeti",
            description="Wildlife safari",
            price_per_person="250.00",
        )

        response = self.client.get(reverse("edit_safari", args=[safari.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Safari")
        self.assertContains(response, "Serengeti Drive")

    def test_edit_safari_with_invalid_data_keeps_original_record(self):
        safari = Safari.objects.create(
            name="Serengeti Drive",
            location="Serengeti",
            description="Wildlife safari",
            price_per_person="250.00",
        )

        response = self.client.post(
            reverse("edit_safari", args=[safari.id]),
            {
                "name": "",
                "location": "Ngorongoro",
                "description": "Updated wildlife safari",
                "price_per_person": "320.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        safari.refresh_from_db()
        self.assertEqual(safari.name, "Serengeti Drive")

    def test_edit_transport_updates_record(self):
        transport = Transport.objects.create(
            name="Airport Transfer",
            type="Minivan",
            description="Private pickup service",
            price_per_day="90.00",
        )

        response = self.client.post(
            reverse("edit_transport", args=[transport.id]),
            {
                "name": "VIP Airport Transfer",
                "type": "Luxury SUV",
                "description": "Premium pickup service",
                "price_per_day": "140.00",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        transport.refresh_from_db()
        self.assertEqual(transport.name, "VIP Airport Transfer")
        self.assertEqual(transport.type, "Luxury SUV")

    def test_edit_transport_page_renders_existing_record(self):
        transport = Transport.objects.create(
            name="Airport Transfer",
            type="Minivan",
            description="Private pickup service",
            price_per_day="90.00",
        )

        response = self.client.get(reverse("edit_transport", args=[transport.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Transport")
        self.assertContains(response, "Airport Transfer")

    def test_edit_transport_with_invalid_data_keeps_original_record(self):
        transport = Transport.objects.create(
            name="Airport Transfer",
            type="Minivan",
            description="Private pickup service",
            price_per_day="90.00",
        )

        response = self.client.post(
            reverse("edit_transport", args=[transport.id]),
            {
                "name": "",
                "type": "Luxury SUV",
                "description": "Premium pickup service",
                "price_per_day": "140.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        transport.refresh_from_db()
        self.assertEqual(transport.name, "Airport Transfer")


class AdminPostAndPackageEditTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="editoradmin",
            password="StrongPass123!",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

    def test_edit_post_page_renders_existing_record(self):
        post = AdminPost.objects.create(
            target_page="aboutus.html",
            title="Original Post",
            description="Original description",
        )

        response = self.client.get(reverse("edit_post", args=[post.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Post")
        self.assertContains(response, "Original Post")
        self.assertContains(response, "admin-form-grid")

    def test_edit_post_updates_record(self):
        post = AdminPost.objects.create(
            target_page="aboutus.html",
            title="Original Post",
            description="Original description",
        )

        response = self.client.post(
            reverse("edit_post", args=[post.id]),
            {
                "target_page": "contact.html",
                "title": "Updated Post",
                "description": "Updated description",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        post.refresh_from_db()
        self.assertEqual(post.title, "Updated Post")
        self.assertEqual(post.target_page, "contact.html")

    def test_edit_post_with_invalid_data_keeps_original_record(self):
        post = AdminPost.objects.create(
            target_page="aboutus.html",
            title="Original Post",
            description="Original description",
        )

        response = self.client.post(
            reverse("edit_post", args=[post.id]),
            {
                "target_page": "",
                "title": "",
                "description": "Updated description",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        post.refresh_from_db()
        self.assertEqual(post.title, "Original Post")
        self.assertEqual(post.target_page, "aboutus.html")

    def test_edit_post_shows_success_message_after_update(self):
        post = AdminPost.objects.create(
            target_page="aboutus.html",
            title="Original Post",
            description="Original description",
        )

        response = self.client.post(
            reverse("edit_post", args=[post.id]),
            {
                "target_page": "contact.html",
                "title": "Updated Post",
                "description": "Updated description",
            },
            follow=True,
        )

        self.assertContains(response, "Post updated successfully.")

    def test_edit_package_page_renders_existing_record(self):
        package = Package.objects.create(
            name="Original Package",
            description="Original package description",
            price="120.00",
        )

        response = self.client.get(reverse("edit_package", args=[package.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Package")
        self.assertContains(response, "Original Package")

    def test_edit_package_updates_record(self):
        package = Package.objects.create(
            name="Original Package",
            description="Original package description",
            price="120.00",
        )

        response = self.client.post(
            reverse("edit_package", args=[package.id]),
            {
                "name": "Updated Package",
                "description": "Updated package description",
                "price": "180.00",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        package.refresh_from_db()
        self.assertEqual(package.name, "Updated Package")
        self.assertEqual(str(package.price), "180.00")

    def test_edit_package_with_invalid_data_keeps_original_record(self):
        package = Package.objects.create(
            name="Original Package",
            description="Original package description",
            price="120.00",
        )

        response = self.client.post(
            reverse("edit_package", args=[package.id]),
            {
                "name": "",
                "description": "Updated package description",
                "price": "180.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertContains(
            response,
            "Package could not be updated. Please correct the highlighted fields.",
        )
        package.refresh_from_db()
        self.assertEqual(package.name, "Original Package")

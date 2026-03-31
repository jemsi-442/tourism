from django.conf import settings


def site_identity(request):
    return {
        "site_brand_name": settings.SITE_BRAND_NAME,
        "site_tagline": settings.SITE_TAGLINE,
        "site_support_email": settings.SITE_SUPPORT_EMAIL,
        "site_phone_display": settings.SITE_PHONE_DISPLAY,
        "site_whatsapp_number": settings.SITE_WHATSAPP_NUMBER,
        "site_whatsapp_country_code": settings.SITE_WHATSAPP_COUNTRY_CODE,
        "site_location": settings.SITE_LOCATION,
    }

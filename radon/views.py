import json
from datetime import timedelta

import stripe
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import City, Contractor, County, RadonLevel, SponsoredListing, ZipCode


def _active_sponsors(**filter_kwargs):
    today = timezone.now().date()
    return (
        SponsoredListing.objects.filter(
            is_approved=True,
            eff_date_start__lte=today,
            eff_date_end__gte=today,
            **filter_kwargs,
        )
        .distinct()
        .prefetch_related("service_counties")
    )


def zip_view(request, zip_code):
    zip_obj = get_object_or_404(ZipCode, zip=zip_code)
    radon = getattr(zip_obj, "radon_level", None)
    nearby_zips = (
        ZipCode.objects.filter(county=zip_obj.county)
        .exclude(zip=zip_code)
        .select_related("radon_level")
        .order_by("-radon_level__testmean")[:10]
    )
    contractors = Contractor.objects.filter(
        zip=zip_code, is_active=True
    ) | Contractor.objects.filter(county=zip_obj.county, is_active=True)
    contractors = contractors.distinct()[:20]

    sponsors = _active_sponsors().filter(
        Q(service_zip_codes=zip_obj) | Q(service_counties=zip_obj.county)
    )

    geo_data = None
    if zip_obj.geometry:
        geo_data = zip_obj.geometry.geojson  # already a JSON string

    return render(request, "radon/zip_page.html", {
        "zip": zip_obj,
        "radon": radon,
        "nearby_zips": nearby_zips,
        "contractors": contractors,
        "sponsors": sponsors,
        "geo_data": geo_data,
    })


def county_view(request, county_name):
    county = get_object_or_404(County, name__iexact=county_name.replace("-", " "))
    radon = getattr(county, "radon_level", None)
    zip_codes = (
        county.zip_codes
        .select_related("radon_level")
        .order_by("-radon_level__testmean")
    )
    cities = county.cities.order_by("-population")[:10]
    contractors = Contractor.objects.filter(county=county, is_active=True)[:20]
    sponsors = _active_sponsors().filter(
        Q(service_counties=county) | Q(service_zip_codes__county=county)
    )

    geo_data = None
    if county.geometry:
        geo_data = county.geometry.geojson  # already a JSON string

    return render(request, "radon/county_page.html", {
        "county": county,
        "radon": radon,
        "zip_codes": zip_codes,
        "cities": cities,
        "contractors": contractors,
        "sponsors": sponsors,
        "geo_data": geo_data,
    })


def county_index_view(request):
    counties = (
        County.objects.filter(state="OH")
        .select_related("radon_level")
        .order_by("name")
    )
    return render(request, "radon/county_index_page.html", {"counties": counties})


def city_view(request, city_name):
    city_name_normalized = city_name.replace("-", " ")
    city = get_object_or_404(City, name__iexact=city_name_normalized, state="OH")
    zip_codes = city.zip_codes.select_related("radon_level").order_by("-radon_level__testmean")
    contractors = Contractor.objects.filter(
        city__iexact=city_name_normalized, is_active=True
    )[:20]
    sponsors = _active_sponsors().filter(
        Q(service_cities=city)
        | Q(service_zip_codes__cities=city)
        | Q(service_counties=city.county)
    )

    return render(request, "radon/city_page.html", {
        "city": city,
        "zip_codes": zip_codes,
        "contractors": contractors,
        "sponsors": sponsors,
    })


def state_view(request, state_name):
    if state_name.lower() != "ohio":
        raise Http404
    top_counties = (
        County.objects.filter(state="OH")
        .select_related("radon_level")
        .filter(radon_level__testcount__gte=5)
        .order_by("-radon_level__testmean")[:15]
    )
    top_zips = (
        ZipCode.objects.filter(state="OH")
        .select_related("radon_level")
        .filter(radon_level__testcount__gte=5)
        .order_by("-radon_level__testmean")[:15]
    )

    # Build GeoJSON for choropleth — only counties with geometry
    county_features = []
    for c in top_counties:
        if c.geometry:
            county_features.append({
                "type": "Feature",
                "properties": {
                    "name": c.name,
                    "mean": float(c.radon_level.testmean),
                    "count": c.radon_level.testcount,
                    "url": c.get_absolute_url(),
                },
                "geometry": json.loads(c.geometry.geojson),
            })
    geo_counties = json.dumps({"type": "FeatureCollection", "features": county_features}) if county_features else None

    return render(request, "radon/state_page.html", {
        "top_counties": top_counties,
        "top_zips": top_zips,
        "geo_counties": geo_counties,
    })


def business_view(request, slug):
    # Try sponsored listing by vanity URL first
    listing = SponsoredListing.objects.filter(vanity_url_name=slug).first()
    if listing:
        if listing.is_active:
            return render(request, "radon/sponsored_business_page.html", {"listing": listing})
        # Listing exists but not active — show generic contractor if linked
        if listing.contractor:
            return render(request, "radon/business_page.html", {"contractor": listing.contractor})
        raise Http404

    # Fall back to contractor by license
    contractor = get_object_or_404(Contractor, license__iexact=slug, is_active=True)
    return render(request, "radon/business_page.html", {"contractor": contractor})


def contractors_view(request):
    sponsors = _active_sponsors().filter(
        contractor_type__in=[SponsoredListing.MITIGATOR, SponsoredListing.BOTH]
    )
    county_filter = request.GET.get("county", "").strip()
    qs = Contractor.objects.filter(
        contractor_type__in=[Contractor.MITIGATOR, Contractor.BOTH],
        is_active=True,
    ).select_related("county").order_by("county__name", "name")
    if county_filter:
        qs = qs.filter(county__name__iexact=county_filter)

    paginator = Paginator(qs, 40)
    page_obj = paginator.get_page(request.GET.get("page"))

    counties = County.objects.filter(state="OH").order_by("name")
    return render(request, "radon/contractors_page.html", {
        "contractors": page_obj,
        "page_obj": page_obj,
        "sponsors": sponsors,
        "counties": counties,
        "county_filter": county_filter,
    })


def testers_view(request):
    sponsors = _active_sponsors().filter(
        contractor_type__in=[SponsoredListing.TESTER, SponsoredListing.BOTH]
    )
    county_filter = request.GET.get("county", "").strip()
    qs = Contractor.objects.filter(
        contractor_type__in=[Contractor.TESTER, Contractor.BOTH],
        is_active=True,
    ).select_related("county").order_by("county__name", "name")
    if county_filter:
        qs = qs.filter(county__name__iexact=county_filter)

    paginator = Paginator(qs, 40)
    page_obj = paginator.get_page(request.GET.get("page"))

    counties = County.objects.filter(state="OH").order_by("name")
    return render(request, "radon/testers_page.html", {
        "testers": page_obj,
        "page_obj": page_obj,
        "sponsors": sponsors,
        "counties": counties,
        "county_filter": county_filter,
    })


# ── Advertise / Stripe ────────────────────────────────────────────────────────

def advertise_view(request):
    return render(request, "radon/advertise_page.html")


def advertise_apply_view(request):
    from .forms import SponsoredListingForm

    if request.method == "POST":
        form = SponsoredListingForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            plan = cd["plan"]

            price_map = {
                "starter": settings.STRIPE_PRICE_STARTER,
                "pro": settings.STRIPE_PRICE_PRO,
                "premier": settings.STRIPE_PRICE_PREMIER,
            }
            price_id = price_map[plan]

            listing = SponsoredListing.objects.create(
                business_name=cd["business_name"],
                contractor_type=cd["contractor_type"],
                license=cd.get("license", ""),
                owner_name=cd["owner_name"],
                email=cd["email"],
                phone=cd["phone"],
                address1=cd["address1"],
                city=cd["city"],
                state="OH",
                zip=cd["zip"],
                website=cd.get("website", ""),
                url_yelp=cd.get("url_yelp", ""),
                url_facebook=cd.get("url_facebook", ""),
                url_google=cd.get("url_google", ""),
                about=cd.get("about", ""),
                call_to_action=cd.get("call_to_action") or "Contact Us",
                hours=cd.get("hours", ""),
                vanity_url_name=cd["vanity_url_name"],
                is_approved=False,
            )

            selected_counties = cd.get("service_counties")
            if selected_counties:
                listing.service_counties.set(selected_counties)
                zips = ZipCode.objects.filter(county__in=selected_counties)
                listing.service_zip_codes.set(zips)

            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                customer_email=cd["email"],
                metadata={"listing_id": str(listing.id)},
                success_url=request.build_absolute_uri(
                    f"/advertise/success/?session_id={{CHECKOUT_SESSION_ID}}"
                ),
                cancel_url=request.build_absolute_uri("/advertise/apply/"),
            )
            return redirect(session.url, permanent=False)
    else:
        form = SponsoredListingForm()

    return render(request, "radon/advertise_apply.html", {"form": form})


def checkout_success_view(request):
    session_id = request.GET.get("session_id", "")
    return render(request, "radon/checkout_success.html", {"session_id": session_id})


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        listing_id = obj.get("metadata", {}).get("listing_id")
        if listing_id:
            try:
                listing = SponsoredListing.objects.get(id=listing_id)
                listing.stripe_customer_id = obj.get("customer", "")
                listing.stripe_subscription_id = obj.get("subscription", "")
                listing.eff_date_start = timezone.now().date()
                listing.eff_date_end = timezone.now().date() + timedelta(days=365)
                listing.is_approved = True
                listing.save()
            except SponsoredListing.DoesNotExist:
                pass

    elif event_type == "customer.subscription.deleted":
        sub_id = obj.get("id")
        if sub_id:
            SponsoredListing.objects.filter(stripe_subscription_id=sub_id).update(
                eff_date_end=timezone.now().date()
            )

    elif event_type == "invoice.payment_failed":
        sub_id = obj.get("subscription")
        if sub_id:
            SponsoredListing.objects.filter(stripe_subscription_id=sub_id).update(
                eff_date_end=timezone.now().date()
            )

    elif event_type == "customer.subscription.updated":
        sub_id = obj.get("id")
        status = obj.get("status")
        if sub_id and status == "active":
            SponsoredListing.objects.filter(stripe_subscription_id=sub_id).update(
                eff_date_end=timezone.now().date() + timedelta(days=365),
                is_approved=True,
            )

    return HttpResponse(status=200)

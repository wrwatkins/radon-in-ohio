import json

from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import City, Contractor, County, RadonLevel, ZipCode


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

    geo_data = None
    if zip_obj.geometry:
        geo_data = json.dumps(zip_obj.geometry.geojson)

    return render(request, "radon/zip_page.html", {
        "zip": zip_obj,
        "radon": radon,
        "nearby_zips": nearby_zips,
        "contractors": contractors,
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

    geo_data = None
    if county.geometry:
        geo_data = json.dumps(county.geometry.geojson)

    return render(request, "radon/county_page.html", {
        "county": county,
        "radon": radon,
        "zip_codes": zip_codes,
        "cities": cities,
        "contractors": contractors,
        "geo_data": geo_data,
    })


def city_view(request, city_name):
    city_name_normalized = city_name.replace("-", " ")
    city = get_object_or_404(City, name__iexact=city_name_normalized, state="OH")
    zip_codes = city.zip_codes.select_related("radon_level").order_by("-radon_level__testmean")
    contractors = Contractor.objects.filter(
        city__iexact=city_name_normalized, is_active=True
    )[:20]

    return render(request, "radon/city_page.html", {
        "city": city,
        "zip_codes": zip_codes,
        "contractors": contractors,
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
    return render(request, "radon/state_page.html", {
        "top_counties": top_counties,
        "top_zips": top_zips,
    })


def business_view(request, slug):
    contractor = get_object_or_404(Contractor, license__iexact=slug, is_active=True)
    return render(request, "radon/business_page.html", {"contractor": contractor})


def contractors_view(request):
    contractors = Contractor.objects.filter(
        contractor_type__in=[Contractor.MITIGATOR, Contractor.BOTH],
        is_active=True,
    ).select_related("county").order_by("county__name", "name")
    return render(request, "radon/contractors_page.html", {"contractors": contractors})


def testers_view(request):
    testers = Contractor.objects.filter(
        contractor_type__in=[Contractor.TESTER, Contractor.BOTH],
        is_active=True,
    ).select_related("county").order_by("county__name", "name")
    return render(request, "radon/testers_page.html", {"testers": testers})

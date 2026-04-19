from django.contrib.gis import admin

from .models import City, Contractor, County, RadonLevel, SponsoredListing, ZipCode


@admin.register(County)
class CountyAdmin(admin.GISModelAdmin):
    list_display = ["name", "fips", "state"]
    search_fields = ["name"]


@admin.register(ZipCode)
class ZipCodeAdmin(admin.GISModelAdmin):
    list_display = ["zip", "city", "county", "state", "population"]
    search_fields = ["zip", "city"]
    list_filter = ["county"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "county", "state", "population"]
    search_fields = ["name"]
    filter_horizontal = ["zip_codes"]


@admin.register(RadonLevel)
class RadonLevelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "testmean", "testcount", "testmax", "pubdate"]
    list_filter = ["publisher", "usepa_radon_zone"]
    search_fields = ["zip_code__zip", "county__name"]


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ["name", "business", "contractor_type", "license", "city", "phone", "is_active"]
    list_filter = ["contractor_type", "is_active", "county"]
    search_fields = ["name", "business", "license", "city"]


@admin.register(SponsoredListing)
class SponsoredListingAdmin(admin.ModelAdmin):
    list_display = [
        "business_name", "contractor_type", "city", "phone",
        "is_approved", "is_active", "eff_date_start", "eff_date_end",
        "stripe_subscription_id",
    ]
    list_filter = ["is_approved", "contractor_type"]
    search_fields = ["business_name", "email", "phone", "vanity_url_name", "stripe_customer_id"]
    readonly_fields = ["stripe_customer_id", "stripe_subscription_id", "created", "modified"]
    filter_horizontal = ["service_zip_codes", "service_counties", "service_cities"]
    fieldsets = [
        ("Identity", {"fields": ["contractor", "business_name", "contractor_type", "license", "owner_name", "vanity_url_name"]}),
        ("Contact", {"fields": ["email", "phone", "address1", "address2", "city", "state", "zip"]}),
        ("Media", {"fields": ["logo", "picture"]}),
        ("Web Presence", {"fields": ["website", "url_yelp", "url_facebook", "url_nextdoor", "url_google"]}),
        ("Profile", {"fields": ["about", "call_to_action", "hours", "ratings"]}),
        ("Service Area", {"fields": ["service_counties", "service_cities", "service_zip_codes"]}),
        ("Subscription", {"fields": ["is_approved", "eff_date_start", "eff_date_end", "stripe_customer_id", "stripe_subscription_id"]}),
        ("Timestamps", {"fields": ["created", "modified"]}),
    ]

from django.contrib.gis import admin

from .models import City, Contractor, County, RadonLevel, ZipCode


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

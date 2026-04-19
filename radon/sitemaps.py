from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import City, County, ZipCode


class ZipSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return ZipCode.objects.filter(state="OH").order_by("zip")

    def location(self, obj):
        return obj.get_absolute_url()


class CountySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9
    protocol = "https"

    def items(self):
        return County.objects.filter(state="OH").order_by("name")

    def location(self, obj):
        return obj.get_absolute_url()


class CitySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return City.objects.filter(state="OH").order_by("name")

    def location(self, obj):
        return obj.get_absolute_url()


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return [
            "state_ohio",
            "contractors",
            "testers",
            "advertise",
        ]

    def location(self, item):
        if item == "state_ohio":
            return "/state/ohio/"
        return reverse(item)

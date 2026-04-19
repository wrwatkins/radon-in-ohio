import json
import random

from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from radon.models import County, ZipCode

BACKGROUND_PHOTOS = [
    ("bridge-4096636.jpg", "Daniel Carter Beard Bridge, Cincinnati, Ohio"),
    ("cincinnati-79357.jpg", "Cincinnati, Ohio skyline at night"),
    ("cleveland-69006.jpg", "Drawbridge over the Cuyahoga River, Cleveland, Ohio"),
    ("cleveland-1936107.jpg", "Wade Park, Cleveland Museum of Art, Cleveland, Ohio"),
    ("cleveland-1936108.jpg", "The Arcade in downtown Cleveland, Ohio"),
    ("columbus-1936112.jpg", "Columbus, Ohio skyline at night"),
    ("columbus-1936114.jpg", "Columbus, Ohio skyline"),
    ("columbus-1936633.jpg", "Ohio Theater, Columbus, Ohio"),
    ("kings-island-211994.jpg", "Kings Island, Mason, Ohio"),
    ("lake-5143799.jpg", "Lake Erie, Ohio"),
    ("landscape-4096646.jpg", "Ohio farm landscape"),
    ("market-677992.jpg", "Brown's Food Market, Cleveland, OH"),
    ("ohio-114093.jpg", "Ohio farm landscape"),
    ("suspension-bridge-62930.jpg", "John A. Roebling Suspension Bridge, Cincinnati, Ohio"),
]


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Intro text below the hero search")
    hero_tagline = models.CharField(
        max_length=200,
        default="Search Radon Levels by Ohio ZIP Code or county",
    )

    content_panels = Page.content_panels + [
        FieldPanel("hero_tagline"),
        FieldPanel("intro"),
    ]

    class Meta:
        verbose_name = "Home Page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        top_counties = list(
            County.objects.filter(state="OH")
            .select_related("radon_level")
            .filter(radon_level__testcount__gte=5)
            .order_by("-radon_level__testmean")[:15]
        )
        top_zips = list(
            ZipCode.objects.filter(state="OH")
            .select_related("radon_level")
            .filter(radon_level__testcount__gte=5, geometry__isnull=False)
            .order_by("-radon_level__testmean")[:15]
        )

        # Build GeoJSON FeatureCollections for the choropleth map
        county_features = []
        for c in top_counties:
            if c.geometry:
                county_features.append({
                    "type": "Feature",
                    "properties": {
                        "county": c.name,
                        "testmean": str(c.radon_level.testmean),
                        "testcount": c.radon_level.testcount,
                        "testmax": str(c.radon_level.testmax),
                        "url": c.get_absolute_url(),
                    },
                    "geometry": json.loads(c.geometry.geojson),
                })
        zip_features = []
        for z in top_zips:
            zip_features.append({
                "type": "Feature",
                "properties": {
                    "zip": z.zip,
                    "city": z.city,
                    "testmean": str(z.radon_level.testmean),
                    "testcount": z.radon_level.testcount,
                    "testmax": str(z.radon_level.testmax),
                    "url": z.get_absolute_url(),
                },
                "geometry": json.loads(z.geometry.geojson),
            })

        context["top_counties"] = top_counties
        context["top_zips"] = top_zips
        context["geojson_counties"] = json.dumps({"type": "FeatureCollection", "features": county_features})
        context["geojson_zips"] = json.dumps({"type": "FeatureCollection", "features": zip_features})
        context["popular_zips"] = ZipCode.objects.filter(
            zip__in=["45011", "43123", "43081", "44256", "44035", "43026", "43055", "43130", "44060", "43230"]
        ).select_related("radon_level")

        # Random background photo
        photo = random.choice(BACKGROUND_PHOTOS)
        context["bg_photo"] = photo[0]
        context["bg_caption"] = photo[1]
        return context


class ContentPage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Content Page"


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["home.BlogPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["posts"] = BlogPage.objects.live().descendant_of(self).order_by("-first_published_at")
        return context


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=500, blank=True)
    body = RichTextField(blank=True)
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("date"),
            FieldPanel("intro"),
        ], heading="Article info"),
        FieldPanel("featured_image"),
        FieldPanel("body"),
    ]

    parent_page_types = ["home.BlogIndexPage"]

    class Meta:
        verbose_name = "Blog Post"

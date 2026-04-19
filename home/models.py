from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from radon.models import County, ZipCode


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
        context["top_counties"] = (
            County.objects.filter(state="OH")
            .select_related("radon_level")
            .filter(radon_level__testcount__gte=5)
            .order_by("-radon_level__testmean")[:15]
        )
        context["top_zips"] = (
            ZipCode.objects.filter(state="OH")
            .select_related("radon_level")
            .filter(radon_level__testcount__gte=5)
            .order_by("-radon_level__testmean")[:15]
        )
        context["popular_zips"] = ZipCode.objects.filter(
            zip__in=["45011", "43123", "43081", "44256", "44035", "43026", "43055", "43130", "44060", "43230"]
        ).select_related("radon_level")
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

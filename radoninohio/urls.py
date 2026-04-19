from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from radon.sitemaps import CitySitemap, CountySitemap, StaticSitemap, ZipSitemap

SITEMAPS = {
    "counties": CountySitemap,
    "zips": ZipSitemap,
    "cities": CitySitemap,
    "static": StaticSitemap,
}

ROBOTS_TXT = """\
User-agent: *
Allow: /
Disallow: /django-admin/
Disallow: /cms/
Disallow: /documents/
Disallow: /advertise/apply/
Disallow: /advertise/success/
Disallow: /stripe/

Sitemap: https://radoninohio.com/sitemap.xml
"""


def robots_txt(request):
    return HttpResponse(ROBOTS_TXT, content_type="text/plain")


def llms_txt(request):
    import os
    from django.conf import settings as _settings
    path = os.path.join(_settings.STATIC_ROOT or _settings.BASE_DIR / "static", "llms.txt")
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        content = "# Radon in Ohio\n> Radon data for every Ohio county and ZIP code.\n"
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


urlpatterns = [
    path("robots.txt", robots_txt),
    path("llms.txt", llms_txt),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="django.contrib.sitemaps.views.sitemap"),
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include("radon.urls")),
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

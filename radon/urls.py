from django.urls import path

from . import views

urlpatterns = [
    path("zip/<str:zip_code>/", views.zip_view, name="zip"),
    path("county/<str:county_name>/", views.county_view, name="county"),
    path("city/<str:city_name>/", views.city_view, name="city"),
    path("state/<str:state_name>/", views.state_view, name="state"),
    path("business/<str:slug>/", views.business_view, name="business"),
    path("contractors/", views.contractors_view, name="contractors"),
    path("testers/", views.testers_view, name="testers"),
]

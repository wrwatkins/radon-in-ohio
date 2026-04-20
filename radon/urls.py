from django.urls import path

from . import views

urlpatterns = [
    path("zip/<str:zip_code>/", views.zip_view, name="zip"),
    path("county/", views.county_index_view, name="county_index"),
    path("county/<str:county_name>/", views.county_view, name="county"),
    path("city/<str:city_name>/", views.city_view, name="city"),
    path("state/<str:state_name>/", views.state_view, name="state"),
    path("business/<str:slug>/", views.business_view, name="business"),
    path("contractors/", views.contractors_view, name="contractors"),
    path("testers/", views.testers_view, name="testers"),
    path("advertise/", views.advertise_view, name="advertise"),
    path("advertise/apply/", views.advertise_apply_view, name="advertise_apply"),
    path("advertise/success/", views.checkout_success_view, name="checkout_success"),
    path("stripe/webhook/", views.stripe_webhook_view, name="stripe_webhook"),
]

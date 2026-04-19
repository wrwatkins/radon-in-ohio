from django.contrib.gis.db import models
from django.utils import timezone


class County(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    fips = models.CharField(max_length=5, blank=True)
    state = models.CharField(max_length=2, default="OH")
    county_seat = models.CharField(max_length=100, blank=True)
    geometry = models.MultiPolygonField(srid=4326, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "counties"

    def __str__(self):
        return f"{self.name} County, OH"

    def get_absolute_url(self):
        return f"/county/{self.name.lower()}/"

    @property
    def radon_level(self):
        return getattr(self, "_radon_level", None) or self.radonlevel_set.first()


class ZipCode(models.Model):
    zip = models.CharField(max_length=5, unique=True, db_index=True)
    city = models.CharField(max_length=120)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True, related_name="zip_codes")
    state = models.CharField(max_length=2, default="OH")
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    population = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    timezone = models.CharField(max_length=120, blank=True)
    geometry = models.MultiPolygonField(srid=4326, null=True, blank=True)
    land_area = models.BigIntegerField(null=True, blank=True)
    water_area = models.BigIntegerField(null=True, blank=True)
    usepa_radon_zone = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["zip"]

    def __str__(self):
        return f"{self.zip} ({self.city}, OH)"

    def get_absolute_url(self):
        return f"/zip/{self.zip}/"


class City(models.Model):
    name = models.CharField(max_length=120, db_index=True)
    name_ascii = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=2, default="OH")
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True, related_name="cities")
    zip_codes = models.ManyToManyField(ZipCode, blank=True, related_name="cities")
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    population = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    timezone = models.CharField(max_length=120, blank=True)
    ranking = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "cities"

    def __str__(self):
        return f"{self.name}, OH"

    def get_absolute_url(self):
        return f"/city/{self.name.lower().replace(' ', '-')}/"


class RadonLevel(models.Model):
    zip_code = models.OneToOneField(
        ZipCode, on_delete=models.CASCADE, null=True, blank=True, related_name="radon_level"
    )
    county = models.OneToOneField(
        County, on_delete=models.CASCADE, null=True, blank=True, related_name="radon_level"
    )
    state = models.CharField(max_length=2, default="OH")
    testcount = models.IntegerField()
    testmin = models.DecimalField(max_digits=8, decimal_places=2)
    testmax = models.DecimalField(max_digits=8, decimal_places=2)
    testmean = models.DecimalField(max_digits=8, decimal_places=2)
    teststdev = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    testgeomean = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    usepa_radon_zone = models.IntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    pubdate = models.DateField(null=True, blank=True)
    pubsource = models.URLField(max_length=500, blank=True)
    pub_represents_period = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-testmean"]

    def __str__(self):
        label = self.zip_code or self.county
        return f"Radon data for {label} — avg {self.testmean} pCi/L"

    @property
    def risk_level(self):
        mean = float(self.testmean)
        if mean >= 8:
            return "high"
        if mean >= 4:
            return "elevated"
        return "low"


class Contractor(models.Model):
    TESTER = "tester"
    MITIGATOR = "mitigator"
    BOTH = "both"
    TYPE_CHOICES = [
        (TESTER, "Radon Tester"),
        (MITIGATOR, "Radon Mitigator"),
        (BOTH, "Tester & Mitigator"),
    ]

    contractor_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    license = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    business = models.CharField(max_length=100, blank=True)
    address1 = models.CharField(max_length=100, blank=True)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, default="OH")
    zip = models.CharField(max_length=10, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(max_length=120, blank=True)
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.license})"

    def get_absolute_url(self):
        return f"/business/{self.license.lower()}/"


class SponsoredListing(models.Model):
    MITIGATOR = "mitigator"
    TESTER = "tester"
    BOTH = "both"
    TYPE_CHOICES = [
        (MITIGATOR, "Radon Mitigator"),
        (TESTER, "Radon Tester"),
        (BOTH, "Tester & Mitigator"),
    ]

    # Identity
    contractor = models.OneToOneField(
        Contractor, on_delete=models.SET_NULL, null=True, blank=True, related_name="sponsored_listing"
    )
    license = models.CharField(max_length=10, blank=True)
    contractor_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    business_name = models.CharField(max_length=100)
    vanity_url_name = models.SlugField(max_length=150, unique=True)
    owner_name = models.CharField(max_length=100, blank=True)

    # Contact
    address1 = models.CharField(max_length=100, blank=True)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, default="OH")
    zip = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Media (uploaded to S3 in production)
    logo = models.ImageField(upload_to="sponsor-logos/", null=True, blank=True)
    picture = models.ImageField(upload_to="sponsor-photos/", null=True, blank=True)

    # Web presence
    website = models.URLField(blank=True)
    url_yelp = models.URLField(blank=True)
    url_facebook = models.URLField(blank=True)
    url_nextdoor = models.URLField(blank=True)
    url_google = models.URLField(blank=True)

    # Profile content
    about = models.TextField(max_length=1000, blank=True)
    call_to_action = models.CharField(max_length=100, blank=True, default="Contact Us")
    hours = models.CharField(max_length=150, blank=True)
    ratings = models.CharField(max_length=100, blank=True)

    # Service area targeting (M2M — the revenue differentiator)
    service_zip_codes = models.ManyToManyField(
        ZipCode, blank=True, related_name="sponsored_listings"
    )
    service_counties = models.ManyToManyField(
        County, blank=True, related_name="sponsored_listings"
    )
    service_cities = models.ManyToManyField(
        City, blank=True, related_name="sponsored_listings"
    )

    # Geo
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Stripe subscription
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    eff_date_start = models.DateField(null=True, blank=True)
    eff_date_end = models.DateField(null=True, blank=True)

    # Admin controls
    is_approved = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["business_name"]

    def __str__(self):
        return f"{self.business_name} (sponsored)"

    def get_absolute_url(self):
        return f"/business/{self.vanity_url_name}/"

    @property
    def is_active(self):
        today = timezone.now().date()
        return (
            self.is_approved
            and self.eff_date_start is not None
            and self.eff_date_end is not None
            and self.eff_date_start <= today <= self.eff_date_end
        )

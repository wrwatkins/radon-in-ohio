from django.contrib.gis.db import models


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

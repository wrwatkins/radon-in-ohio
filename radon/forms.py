from django import forms

from .models import County, SponsoredListing


class SponsoredListingForm(forms.Form):
    PLAN_CHOICES = [
        ("starter", "Starter — $49/month"),
        ("pro", "Pro — $99/month"),
        ("premier", "Premier — $199/month"),
    ]

    # Business identity
    business_name = forms.CharField(max_length=100, label="Business Name")
    contractor_type = forms.ChoiceField(choices=SponsoredListing.TYPE_CHOICES, label="Service Type")
    license = forms.CharField(max_length=10, required=False, label="Ohio Radon License # (optional)")
    owner_name = forms.CharField(max_length=100, label="Your Full Name")
    vanity_url_name = forms.SlugField(
        max_length=150,
        label="Custom Profile URL",
        help_text="Letters, numbers, and hyphens only — becomes radoninohio.com/business/YOUR-SLUG/",
    )

    # Contact
    email = forms.EmailField(label="Email Address")
    phone = forms.CharField(max_length=20, label="Phone Number")
    address1 = forms.CharField(max_length=100, label="Street Address")
    city = forms.CharField(max_length=50, label="City")
    zip = forms.CharField(max_length=10, label="ZIP Code")

    # Web presence
    website = forms.URLField(required=False, label="Website URL")
    url_yelp = forms.URLField(required=False, label="Yelp Profile URL")
    url_facebook = forms.URLField(required=False, label="Facebook Page URL")
    url_google = forms.URLField(required=False, label="Google Business URL")

    # Profile content
    about = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5}),
        max_length=1000,
        required=False,
        label="About Your Business",
        help_text="Up to 1,000 characters. Describe your services, experience, and why customers choose you.",
    )
    call_to_action = forms.CharField(
        max_length=100,
        required=False,
        initial="Contact Us",
        label="Call-to-Action Button Text",
        help_text='e.g., "Get a Free Quote", "Schedule Testing", "Contact Us"',
    )
    hours = forms.CharField(max_length=150, required=False, label="Business Hours", help_text='e.g., "Mon–Fri 8am–5pm, Sat by appointment"')

    # Service area
    service_counties = forms.ModelMultipleChoiceField(
        queryset=County.objects.filter(state="OH").order_by("name"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Counties You Serve",
        help_text="Select all Ohio counties where you accept customers. Your listing will appear on pages for each selected county and its ZIP codes.",
    )

    # Plan selection
    plan = forms.ChoiceField(
        choices=PLAN_CHOICES,
        widget=forms.RadioSelect,
        label="Listing Plan",
    )

    def clean_vanity_url_name(self):
        slug = self.cleaned_data["vanity_url_name"].lower()
        if SponsoredListing.objects.filter(vanity_url_name=slug).exists():
            raise forms.ValidationError("That URL is already taken. Please choose another.")
        return slug

    def clean_call_to_action(self):
        val = self.cleaned_data.get("call_to_action", "").strip()
        return val or "Contact Us"

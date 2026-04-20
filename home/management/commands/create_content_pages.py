from django.core.management.base import BaseCommand
from wagtail.models import Page

from home.models import ContentPage, HomePage


PAGES = [
    {
        "slug": "what-is-radon",
        "title": "What is Radon? Ohio Radon Facts and Health Risks",
        "body": """
<h2>What is Radon?</h2>
<p>Radon is a naturally occurring radioactive gas produced by the decay of uranium in soil and rock.
It is colorless, odorless, and tasteless — making it undetectable without a test.
Radon seeps up through the ground and can accumulate to dangerous levels inside homes, schools, and other buildings.</p>

<h2>Why is Radon a Problem in Ohio?</h2>
<p>Ohio has significant geological radon potential. The U.S. Environmental Protection Agency (EPA) places
most of Ohio in Zone 1 — the highest radon potential zone — with average indoor radon levels predicted
to exceed 4 pCi/L. Many Ohio counties consistently report average radon levels well above the EPA action level.
Ohio's underlying geology — including glacial deposits and limestone-rich soils — creates conditions
favorable for radon production and entry into homes.</p>

<h2>Health Risks of Radon Exposure</h2>
<p>Radon is the leading cause of lung cancer among non-smokers in the United States, responsible for approximately
21,000 lung cancer deaths each year according to the EPA. When radon decays, it releases tiny radioactive particles
that can damage lung tissue when inhaled over time.</p>
<p>The risk is cumulative: long-term exposure to elevated radon levels significantly increases lung cancer risk,
especially for smokers. The EPA recommends taking action when indoor radon levels reach 4.0 pCi/L or higher.</p>

<h2>EPA Action Levels for Radon</h2>
<ul>
<li><strong>4.0 pCi/L or higher:</strong> EPA recommends fixing your home.</li>
<li><strong>2.0–4.0 pCi/L:</strong> Consider fixing. Many homes can be reduced below 2 pCi/L.</li>
<li><strong>Below 2.0 pCi/L:</strong> Difficult to reduce further, but some risk remains.</li>
</ul>
<p>There is no safe level of radon exposure — even low levels carry some risk. The national average indoor radon
level is about 1.3 pCi/L. Ohio's average is significantly higher.</p>

<h2>How Does Radon Enter Your Home?</h2>
<p>Radon enters homes through:</p>
<ul>
<li>Cracks in foundation walls and floors</li>
<li>Construction joints</li>
<li>Gaps around service pipes</li>
<li>Crawl spaces open to the soil</li>
<li>Well water (in some regions)</li>
</ul>
<p>Homes with basements and crawl spaces are particularly susceptible, though any home can have elevated radon —
including those built on slabs.</p>

<h2>Radon Testing in Ohio</h2>
<p>Testing is the only way to know your home's radon level. Ohio has many licensed radon testers who can perform
short-term or long-term tests. You can also purchase a DIY radon test kit from a hardware store or online.</p>
<ul>
<li><strong>Short-term tests (2–90 days):</strong> Quickest way to screen your home. Closed-house conditions required.</li>
<li><strong>Long-term tests (90+ days):</strong> More accurate picture of year-round average exposure.</li>
</ul>
<p>For real estate transactions, short-term closed-house tests are typically used during the inspection period.
The Ohio Department of Health maintains a list of certified radon measurement professionals.</p>

<h2>Radon and Home Buying in Ohio</h2>
<p>Ohio law does not require sellers to disclose radon test results, but buyers can request radon testing as part
of the home inspection contingency. If a test reveals levels at or above 4.0 pCi/L, buyers can negotiate with
sellers to have a mitigation system installed prior to closing — typically costing $1,200–$2,500.
Many buyers request this as a seller concession.</p>
<p>Before purchasing a home in Ohio, ask your inspector about radon testing, or hire an independent
Ohio-licensed radon tester.</p>

<h2>Radon Mitigation in Ohio</h2>
<p>If your home tests high for radon, licensed Ohio radon mitigation contractors can reduce levels using proven methods:</p>
<ul>
<li><strong>Sub-slab depressurization:</strong> The most common and effective method. A pipe and fan system draws radon
from beneath the foundation and vents it outside.</li>
<li><strong>Crawl space encapsulation:</strong> Sealing and covering crawl spaces to prevent radon entry.</li>
<li><strong>Sealing cracks:</strong> Alone this is not sufficient but helps as part of a larger system.</li>
</ul>
<p>Radon mitigation systems typically reduce radon levels by 50–99% and cost $800–$2,500 to install depending on
home size and construction type. Most systems require little maintenance and last the life of the home.</p>

<h2>Seasonal Variation in Radon Levels</h2>
<p>Radon levels tend to be higher in winter months when homes are closed up and natural ventilation is reduced.
Summer readings are typically lower. For this reason, long-term tests provide a more representative year-round
average than a single short-term test.</p>

<h2>Find Radon Data for Your Ohio ZIP Code</h2>
<p>Use our <a href="/">radon level search</a> to look up average radon test results for your Ohio ZIP code or county.
All data is sourced from the Ohio Department of Health. Then connect with a
<a href="/contractors/">licensed Ohio radon professional</a> near you.</p>
""",
    },
    {
        "slug": "ohio-radon-resources",
        "title": "Ohio Radon Resources — Testing, Mitigation, and Regulations",
        "body": """
<h2>Ohio Radon Program</h2>
<p>The Ohio Department of Health (ODH) operates the Ohio Radon Program, which includes licensing of radon
measurement and mitigation professionals, public education, and data collection.</p>

<h2>Key Ohio Radon Resources</h2>
<ul>
<li><strong>Ohio Department of Health Radon Program:</strong> ohio.gov/radon — licensing, certified contractors, forms</li>
<li><strong>EPA Radon Information:</strong> epa.gov/radon — action guidelines, maps, publications</li>
<li><strong>National Radon Program Services:</strong> sosradon.org — test kit ordering and information</li>
</ul>

<h2>Ohio Radon Regulations</h2>
<p>Ohio requires licensing for radon measurement and mitigation professionals. Ohio Revised Code Chapter 3748
governs the licensing of radon professionals in Ohio. The Ohio Department of Health issues licenses and
investigates complaints.</p>

<h2>Find Licensed Ohio Radon Contractors</h2>
<p>Use our <a href="/">search tool</a> to find licensed Ohio radon testers and mitigation contractors near you.</p>
""",
    },
    {
        "slug": "about",
        "title": "About Radon in Ohio",
        "body": """
<h2>What is Radon in Ohio?</h2>
<p>Radon in Ohio is an independent data resource providing radon test statistics for every Ohio ZIP code,
county, and city — sourced directly from the Ohio Department of Health's radon testing records.
Our mission is to make Ohio radon data accessible to homeowners, home buyers, real estate professionals,
and public health advocates who need accurate, localized information.</p>

<h2>Our Data Source</h2>
<p>All radon test data published on this site is sourced from the Ohio Department of Health (ODH) Radon Education
and Licensing Program. The ODH collects radon test results submitted by licensed Ohio radon professionals
and makes aggregate data available for public use.</p>
<p>We aggregate this data by ZIP code and county to provide geographic context for Ohio residents.
Individual home test results are not published — all statistics represent aggregate averages across multiple tests.</p>

<h2>Data Accuracy and Limitations</h2>
<p>Radon levels vary significantly from home to home, even within the same neighborhood or ZIP code.
The county and ZIP code averages shown on this site reflect historical test data submitted to ODH — they
represent an area's general radon potential, not the specific radon level in any individual home.
The only way to know your home's radon level is to test it.</p>
<p>ZIP codes with fewer than 10 reported tests should be interpreted with particular caution, as small samples
may not be representative. We note low test counts throughout the site.</p>

<h2>Contractor Directory</h2>
<p>Radon in Ohio maintains a directory of Ohio Department of Health licensed radon testing and mitigation
professionals. All listed contractors hold active ODH radon licenses. Paid featured listings are clearly
identified. We do not endorse any specific contractor and recommend verifying license status directly
with the Ohio Department of Health before hiring.</p>

<h2>Contact</h2>
<p>For questions about the data or this site, please see our <a href="/data-accuracy/">Data Accuracy</a> page.
To list your radon business, visit our <a href="/advertise/">advertise page</a>.</p>
""",
    },
    {
        "slug": "privacy-policy",
        "title": "Privacy Policy — Radon in Ohio",
        "body": """
<p><em>Last updated: April 2026</em></p>

<h2>Information We Collect</h2>
<p>Radon in Ohio collects limited information to operate the site:</p>
<ul>
<li><strong>Contact form data:</strong> When contractors apply for a listing, we collect business name, contact information, and service area details. This information is used solely to process listings.</li>
<li><strong>Analytics:</strong> We may use standard web analytics tools to understand aggregate site usage. These tools may collect your IP address, browser type, and pages visited. We do not sell this data.</li>
<li><strong>Cookies:</strong> We use session cookies required for site functionality. We do not use advertising tracking cookies.</li>
</ul>

<h2>How We Use Your Information</h2>
<p>Information collected through the contractor application form is used to:</p>
<ul>
<li>Process and manage contractor listings</li>
<li>Contact you about your listing</li>
<li>Process payments via Stripe (our payment processor)</li>
</ul>

<h2>Third-Party Services</h2>
<p>This site uses the following third-party services:</p>
<ul>
<li><strong>Stripe:</strong> Payment processing for contractor listings. See Stripe's privacy policy at stripe.com/privacy.</li>
<li><strong>Amazon Associates:</strong> We participate in the Amazon Associates program and may earn a commission on qualifying purchases.</li>
<li><strong>Leaflet / OpenStreetMap / CARTO:</strong> Map tiles used for geographic visualizations.</li>
</ul>

<h2>Data Retention</h2>
<p>Contractor listing information is retained for the duration of your listing and for a reasonable period thereafter for business record purposes.</p>

<h2>Your Rights</h2>
<p>You may request deletion of your personal information by contacting us. We will respond to reasonable requests within 30 days.</p>

<h2>Changes to This Policy</h2>
<p>We may update this policy periodically. Continued use of the site constitutes acceptance of the current policy.</p>
""",
    },
    {
        "slug": "data-accuracy",
        "title": "Data Accuracy — Radon in Ohio",
        "body": """
<h2>About Our Radon Data</h2>
<p>All radon test statistics published on Radon in Ohio are sourced from the Ohio Department of Health (ODH)
Radon Education and Licensing Program. This program collects radon test results submitted by licensed Ohio
radon professionals and makes aggregate statistics available for public use.</p>

<h2>What the Numbers Mean</h2>
<p>Each ZIP code and county page displays:</p>
<ul>
<li><strong>Average (mean) radon level:</strong> The arithmetic mean of all reported test results for that geography, in picocuries per liter (pCi/L).</li>
<li><strong>Maximum recorded:</strong> The highest single test result in the dataset for that geography. Maximums often represent extreme outliers from atypical conditions and should not be interpreted as representative of typical homes.</li>
<li><strong>Test count:</strong> The number of individual tests included in the calculation. Higher test counts indicate more statistically reliable averages.</li>
</ul>

<h2>Data Limitations</h2>
<p><strong>These averages do not predict the radon level in any specific home.</strong> Radon levels vary significantly
from property to property based on foundation type, local geology, ventilation, and other factors.
A ZIP code with a low average radon level can still contain homes with very high radon, and vice versa.</p>
<p>ZIP codes with fewer than 10 tests are marked with a data confidence note throughout the site. We recommend
treating low-sample-count statistics as preliminary indicators only.</p>
<p>Maximum recorded values — especially extreme outliers like values exceeding 100 pCi/L — typically represent
anomalous single measurements from unusual conditions such as basement crawlspaces with direct soil exposure.
They are not typical of livable areas in that ZIP code or county.</p>

<h2>Data Currency</h2>
<p>The dataset currently published reflects Ohio Department of Health radon test submissions through early 2021.
We update the dataset when ODH releases new aggregate data. The ODH data collection is ongoing — more recent
tests conducted by licensed Ohio professionals are added to ODH records regularly.</p>
<p>Note that the average radon levels in most Ohio ZIP codes and counties are relatively stable over time,
since radon is determined primarily by geology, not by changing conditions. Year-to-year variation in averages
typically reflects additional test submissions rather than actual changes in radon levels.</p>

<h2>EPA Radon Zones</h2>
<p>The EPA divides counties into three radon potential zones:</p>
<ul>
<li><strong>Zone 1 (Highest potential):</strong> Average indoor radon level predicted to exceed 4 pCi/L</li>
<li><strong>Zone 2 (Moderate potential):</strong> Average indoor radon level predicted at 2–4 pCi/L</li>
<li><strong>Zone 3 (Low potential):</strong> Average indoor radon level predicted below 2 pCi/L</li>
</ul>
<p>Most Ohio counties fall in Zone 1. The EPA zone system is a predictive tool based on geology;
actual measured averages from ODH testing data may differ.</p>

<h2>Questions</h2>
<p>For questions about the data methodology, visit the
<a href="https://odh.ohio.gov/know-our-programs/radon-education-and-licensing-program/welcome" target="_blank" rel="noopener">
Ohio Department of Health Radon Program</a> or see our <a href="/about/">About page</a>.</p>
""",
    },
]


class Command(BaseCommand):
    help = "Create standard content pages under the HomePage"

    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if not home:
            self.stderr.write("No HomePage found. Create one first via the Wagtail admin.")
            return

        for page_data in PAGES:
            slug = page_data["slug"]
            existing = Page.objects.filter(slug=slug).first()
            if existing:
                self.stdout.write(f"Page already exists: /{slug}/")
                continue

            page = ContentPage(
                title=page_data["title"],
                slug=slug,
                body=page_data["body"],
                live=True,
            )
            home.add_child(instance=page)
            self.stdout.write(self.style.SUCCESS(f"Created: /{slug}/"))

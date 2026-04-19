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
to exceed 4 pCi/L. Many Ohio counties consistently report average radon levels well above the EPA action level.</p>

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
<li><strong>Below 2.0 pCi/L:</strong> Difficult to reduce further, but still some risk.</li>
</ul>
<p>There is no safe level of radon exposure — even low levels carry some risk. The national average indoor radon level
is about 1.3 pCi/L.</p>

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

<h2>Testing for Radon in Ohio</h2>
<p>Testing is the only way to know your home's radon level. Ohio has many licensed radon testers who can perform
short-term or long-term tests. You can also purchase a DIY radon test kit from a hardware store or online.</p>
<ul>
<li><strong>Short-term tests (2–90 days):</strong> Quickest way to screen your home.</li>
<li><strong>Long-term tests (90+ days):</strong> More accurate picture of year-round average exposure.</li>
</ul>
<p>The Ohio Department of Health maintains a list of certified radon measurement professionals.</p>

<h2>Radon Mitigation in Ohio</h2>
<p>If your home tests high for radon, licensed Ohio radon mitigation contractors can reduce levels using proven methods:</p>
<ul>
<li><strong>Sub-slab depressurization:</strong> The most common and effective method. A pipe and fan system draws radon
from beneath the foundation and vents it outside.</li>
<li><strong>Crawl space encapsulation:</strong> Sealing and covering crawl spaces to prevent radon entry.</li>
<li><strong>Sealing cracks:</strong> Alone this is not sufficient but helps as part of a larger system.</li>
</ul>
<p>Radon mitigation systems typically reduce radon levels by 50–99% and cost $800–$2,500 to install depending on
home size and construction type.</p>

<h2>Find Radon Data for Your Ohio ZIP Code</h2>
<p>Use our <a href="/">radon level search</a> to look up average radon test results for your Ohio ZIP code or county.
Then connect with a <a href="/advertise/">licensed Ohio radon professional</a> near you.</p>
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

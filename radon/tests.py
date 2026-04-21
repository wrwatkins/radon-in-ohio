from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from radoninohio.urls import llms_txt, robots_txt


class UrlReverseTests(SimpleTestCase):
    def test_zip_url_reverses(self):
        self.assertEqual(reverse("zip", args=["44101"]), "/zip/44101/")

    def test_county_index_url_reverses(self):
        self.assertEqual(reverse("county_index"), "/county/")

    def test_county_url_reverses(self):
        self.assertEqual(reverse("county", args=["cuyahoga"]), "/county/cuyahoga/")

    def test_city_url_reverses(self):
        self.assertEqual(reverse("city", args=["cleveland"]), "/city/cleveland/")

    def test_state_url_reverses(self):
        self.assertEqual(reverse("state", args=["ohio"]), "/state/ohio/")

    def test_business_url_reverses(self):
        self.assertEqual(reverse("business", args=["acme"]), "/business/acme/")

    def test_contractors_url_reverses(self):
        self.assertEqual(reverse("contractors"), "/contractors/")

    def test_testers_url_reverses(self):
        self.assertEqual(reverse("testers"), "/testers/")

    def test_advertise_url_reverses(self):
        self.assertEqual(reverse("advertise"), "/advertise/")

    def test_advertise_apply_url_reverses(self):
        self.assertEqual(reverse("advertise_apply"), "/advertise/apply/")

    def test_checkout_success_url_reverses(self):
        self.assertEqual(reverse("checkout_success"), "/advertise/success/")

    def test_stripe_webhook_url_reverses(self):
        self.assertEqual(reverse("stripe_webhook"), "/stripe/webhook/")


class StaticViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_robots_txt_returns_plain_text(self):
        response = robots_txt(self.factory.get("/robots.txt"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn(b"Sitemap: https://radoninohio.com/sitemap.xml", response.content)
        self.assertIn(b"Disallow: /django-admin/", response.content)

    def test_llms_txt_returns_plain_text(self):
        response = llms_txt(self.factory.get("/llms.txt"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        self.assertTrue(len(response.content) > 0)

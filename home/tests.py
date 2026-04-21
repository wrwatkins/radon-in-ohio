from django.test import SimpleTestCase

from home.models import BACKGROUND_PHOTOS, HomePage


class BackgroundPhotosTests(SimpleTestCase):
    def test_background_photos_non_empty(self):
        self.assertGreater(len(BACKGROUND_PHOTOS), 0)

    def test_background_photos_are_filename_caption_tuples(self):
        for entry in BACKGROUND_PHOTOS:
            self.assertEqual(len(entry), 2)
            filename, caption = entry
            self.assertTrue(filename.endswith(".jpg"))
            self.assertTrue(len(caption) > 0)


class HomePageModelTests(SimpleTestCase):
    def test_home_page_importable(self):
        self.assertTrue(hasattr(HomePage, "intro"))

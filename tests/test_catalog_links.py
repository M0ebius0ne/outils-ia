import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from catalog_links import resolve_url, safe_content_path, InvalidSlug


class ResolveUrlTests(unittest.TestCase):
    def test_uses_official_url_when_affiliate_missing(self):
        tool = {"id": "castmagic", "official_url": "https://www.castmagic.io"}
        self.assertEqual(resolve_url(tool, {}), "https://www.castmagic.io")

    def test_uses_affiliate_url_when_present(self):
        tool = {"id": "castmagic", "official_url": "https://www.castmagic.io"}
        links = {"castmagic": "https://www.castmagic.io/?via=mezino"}
        self.assertEqual(resolve_url(tool, links), "https://www.castmagic.io/?via=mezino")


class SafeContentPathTests(unittest.TestCase):
    def test_rejects_path_traversal_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(InvalidSlug):
                safe_content_path(tmp, "../escaped")

    def test_keeps_simple_slug_inside_content_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = safe_content_path(tmp, "castmagic")
            self.assertEqual(os.path.dirname(os.path.realpath(path)), os.path.realpath(tmp))
            self.assertTrue(path.endswith("castmagic.md"))


if __name__ == "__main__":
    unittest.main()

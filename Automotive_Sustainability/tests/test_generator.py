import unittest
from src.automotive_sustainability.generator import generate


class TestGenerator(unittest.TestCase):
    def test_count(self):
        items = generate("Fleet Efficiency", 5)
        self.assertEqual(len(items), 5)

    def test_structure(self):
        items = generate("EV Battery Circularity", 2)
        for it in items:
            self.assertIn("title", it)
            self.assertIn("overview", it)
            self.assertIn("data_sources", it)
            self.assertIn("deliverables", it)
            self.assertIn("evaluation_metrics", it)
            self.assertTrue(isinstance(it["data_sources"], list))
            self.assertTrue(isinstance(it["deliverables"], list))
            self.assertTrue(isinstance(it["evaluation_metrics"], list))


if __name__ == "__main__":
    unittest.main()

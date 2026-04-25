import tempfile
import unittest
from pathlib import Path

from dead_code_detective.cli import scan


class DeadCodeDetectiveTests(unittest.TestCase):
    def test_scan_finds_unused_function(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.py").write_text(
                "def used(): pass\n"
                "def unused(): pass\n"
                "used()\n",
                encoding="utf-8",
            )

            names = {item["name"] for item in scan(directory)}

            self.assertIn("unused", names)
            self.assertNotIn("used", names)

    def test_scan_handles_async_functions(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.py").write_text(
                "async def forgotten(): pass\n",
                encoding="utf-8",
            )

            findings = scan(directory)

            self.assertEqual(findings[0]["kind"], "async_function")

    def test_ignore_patterns(self):
        with tempfile.TemporaryDirectory() as directory:
            ignored = Path(directory, "ignored.py")
            ignored.write_text("def unused(): pass\n", encoding="utf-8")

            self.assertEqual(scan(directory, ignore=["*ignored.py"]), [])


if __name__ == "__main__":
    unittest.main()

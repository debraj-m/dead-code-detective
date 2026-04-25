import tempfile, unittest
from pathlib import Path
from dead_code_detective.cli import scan

class Tests(unittest.TestCase):
    def test_scan(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'a.py').write_text('def used(): pass\ndef unused(): pass\nused()\n')
            names = {x['name'] for x in scan(d)}
            self.assertIn('unused', names)

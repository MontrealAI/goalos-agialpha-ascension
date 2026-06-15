import subprocess
import unittest
from pathlib import Path


class WebsitePublicationTest(unittest.TestCase):
    def test_generate_mission_page_not_blank(self):
        subprocess.check_call(["python", "scripts/mission-os/generate_mission_page.py"])
        text = Path("mission-os.html").read_text()
        self.assertIn("GoalOS Mission OS", text)
        self.assertIn("GoalOS_Mission_OS_Paper.pdf", text)


if __name__ == "__main__":
    unittest.main()

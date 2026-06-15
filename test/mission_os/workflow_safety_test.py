import unittest
from pathlib import Path


class WorkflowSafetyTest(unittest.TestCase):
    def test_mission_workflows_no_mainnet_broadcast_or_token_movement_commands(self):
        forbidden = [
            "mainnet:live-local-gated",
            "deploy:ethereum-mainnet:gated",
            "fund:vaults:gated",
            "private_key:",
            "secrets.private_key",
        ]
        for workflow in Path(".github/workflows").glob("goalos-mission-os*.yml"):
            text = workflow.read_text().lower()
            for term in forbidden:
                self.assertNotIn(term, text, f"{term} found in {workflow}")


if __name__ == "__main__":
    unittest.main()

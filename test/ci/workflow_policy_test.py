from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("workflow_policy", ROOT / "scripts" / "validate_workflow_policy.py")
workflow_policy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(workflow_policy)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class WorkflowPolicyTest(unittest.TestCase):
    def base_policy(self, workflow: str, role: str, required: list[str], forbidden: list[str] | None = None) -> dict:
        return {
            "schemaVersion": "1.0",
            "commands": {
                "ordinaryConsistency": ["npm run mainnet:status-consistency", "npm run docs:status:check"],
                "positiveEnforcement": [
                    "npm run mainnet:readiness-require-pass",
                    "npm run mainnet:deployment-authorization-require-pass",
                    "npm run mainnet:authorization-require-pass",
                ],
                "forbiddenMainnetSecrets": ["MAINNET_PRIVATE_KEY", "PRIVATE_KEY"],
            },
            "workflows": [
                {
                    "path": workflow,
                    "role": role,
                    "requiredCommands": required,
                    "forbiddenCommands": forbidden or [],
                    "requiredEnvironment": "mainnet-readiness" if role == "PROTECTED_RELEASE" else None,
                    "requiresWorkflowDispatch": role == "PROTECTED_RELEASE",
                    "mustNotBroadcastMainnet": role == "PROTECTED_RELEASE",
                }
            ],
        }

    def validate(self, policy: dict, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel, text in files.items():
                write(root / rel, text)
            policy_path = root / "qa" / "workflow-policy.json"
            write(policy_path, json.dumps(policy))
            return workflow_policy.validate(policy_path, root)

    def test_screenshot_failure_is_reproduced_by_obsolete_literal_requirement(self):
        workflow = "wf.yml"
        text = "on: {pull_request: {}}\njobs:\n  test:\n    steps:\n      - run: npm run mainnet:status-consistency\n"
        self.assertNotIn("npm run mainnet:authorization-check", text)

    def test_pr_workflow_with_consistency_without_positive_authorization_passes(self):
        policy = self.base_policy("wf.yml", "PR_VALIDATION", ["npm run mainnet:status-consistency"])
        errors = self.validate(policy, {"wf.yml": "on: {pull_request: {}}\njobs:\n  test:\n    steps:\n      - run: npm run mainnet:status-consistency\n"})
        self.assertEqual(errors, [])

    def test_pr_workflow_rejects_positive_authorization(self):
        policy = self.base_policy("wf.yml", "PR_VALIDATION", ["npm run mainnet:status-consistency"])
        errors = self.validate(policy, {"wf.yml": "on: {pull_request: {}}\njobs:\n  test:\n    steps:\n      - run: npm run mainnet:status-consistency\n      - run: npm run mainnet:authorization-check\n"})
        self.assertTrue(any("positive authorization" in e for e in errors))

    def test_protected_release_without_positive_enforcement_fails(self):
        policy = self.base_policy("release.yml", "PROTECTED_RELEASE", ["npm run mainnet:readiness-require-pass"])
        errors = self.validate(policy, {"release.yml": "on:\n  workflow_dispatch: {}\njobs:\n  release:\n    environment: mainnet-readiness\n    steps:\n      - run: npm run mainnet:status-consistency\n"})
        self.assertTrue(any("missing required command" in e for e in errors))

    def test_protected_release_with_enforcement_passes(self):
        req = ["npm run mainnet:readiness-require-pass", "npm run mainnet:deployment-authorization-require-pass", "npm run mainnet:authorization-require-pass"]
        policy = self.base_policy("release.yml", "PROTECTED_RELEASE", req)
        errors = self.validate(policy, {"release.yml": "on:\n  workflow_dispatch: {}\njobs:\n  release:\n    environment: mainnet-readiness\n    steps:\n      - run: npm run mainnet:readiness-require-pass\n      - run: npm run mainnet:deployment-authorization-require-pass\n      - run: npm run mainnet:authorization-require-pass\n"})
        self.assertEqual(errors, [])

    def test_mandatory_failure_hidden_by_true_fails(self):
        policy = self.base_policy("wf.yml", "PR_VALIDATION", ["npm run mainnet:status-consistency"])
        errors = self.validate(policy, {"wf.yml": "on: {pull_request: {}}\njobs:\n  test:\n    steps:\n      - run: npm run mainnet:status-consistency || true\n"})
        self.assertTrue(any("|| true" in e for e in errors))

    def test_multiline_run_blocks_are_scanned_for_forbidden_commands(self):
        policy = self.base_policy("wf.yml", "PR_VALIDATION", ["npm run mainnet:status-consistency"])
        errors = self.validate(policy, {"wf.yml": "on: {pull_request: {}}\njobs:\n  test:\n    steps:\n      - run: |\n          npm run mainnet:status-consistency\n          npm run mainnet:authorization-require-pass\n"})
        self.assertTrue(any("positive authorization" in e for e in errors))


    def test_echoed_required_command_does_not_satisfy_policy(self):
        req = ["npm run mainnet:authorization-require-pass"]
        policy = self.base_policy("release.yml", "PROTECTED_RELEASE", req)
        errors = self.validate(policy, {"release.yml": "on:\n  workflow_dispatch: {}\njobs:\n  release:\n    environment: mainnet-readiness\n    steps:\n      - run: echo npm run mainnet:authorization-require-pass\n"})
        self.assertTrue(any("missing required command" in e for e in errors))

    def test_env_prefixed_required_command_satisfies_policy(self):
        req = ["npm run mainnet:authorization-require-pass"]
        policy = self.base_policy("release.yml", "PROTECTED_RELEASE", req)
        errors = self.validate(policy, {"release.yml": "on:\n  workflow_dispatch: {}\njobs:\n  release:\n    environment: mainnet-readiness\n    steps:\n      - run: CI=1 npm run mainnet:authorization-require-pass\n"})
        self.assertEqual(errors, [])

    def test_bracketed_mainnet_secret_reference_fails(self):
        req = ["npm run mainnet:readiness-require-pass"]
        policy = self.base_policy("release.yml", "PROTECTED_RELEASE", req)
        errors = self.validate(policy, {"release.yml": "on:\n  workflow_dispatch: {}\njobs:\n  release:\n    environment: mainnet-readiness\n    env:\n      KEY: ${{ secrets['MAINNET_PRIVATE_KEY'] }}\n    steps:\n      - run: npm run mainnet:readiness-require-pass\n"})
        self.assertTrue(any("forbidden Mainnet broadcaster secret" in e for e in errors))

    def test_forbidden_mainnet_private_key_fails(self):
        req = ["npm run mainnet:readiness-require-pass"]
        policy = self.base_policy("release.yml", "PROTECTED_RELEASE", req)
        errors = self.validate(policy, {"release.yml": "on:\n  workflow_dispatch: {}\njobs:\n  release:\n    environment: mainnet-readiness\n    env:\n      MAINNET_PRIVATE_KEY: ${{ secrets.MAINNET_PRIVATE_KEY }}\n    steps:\n      - run: npm run mainnet:readiness-require-pass\n"})
        self.assertTrue(any("forbidden Mainnet broadcaster secret" in e for e in errors))


if __name__ == "__main__":
    unittest.main()

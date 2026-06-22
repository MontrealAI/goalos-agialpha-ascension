import importlib.util
import json
import os
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/mainnet_release.py"
spec = importlib.util.spec_from_file_location("mainnet_release", SCRIPT)
mainnet_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mainnet_release)

class MainnetReleasePacketTests(unittest.TestCase):
    def setUp(self):
        self.rel = ROOT / "release/mainnet-2026-06-21"
        self.head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip().lower()

    def test_resolve_release_target_sha_defaults_to_head(self):
        old = os.environ.pop("RELEASE_TARGET_SHA", None)
        try:
            self.assertEqual(mainnet_release.resolve_release_target_sha(), self.head)
        finally:
            if old is not None:
                os.environ["RELEASE_TARGET_SHA"] = old

    def test_resolve_release_target_sha_rejects_malformed_and_mismatch(self):
        old = os.environ.get("RELEASE_TARGET_SHA")
        try:
            os.environ["RELEASE_TARGET_SHA"] = "not-a-sha"
            with self.assertRaises(mainnet_release.ReleaseError):
                mainnet_release.resolve_release_target_sha()
            os.environ["RELEASE_TARGET_SHA"] = "0" * 40
            if self.head != "0" * 40:
                with self.assertRaises(mainnet_release.ReleaseError):
                    mainnet_release.resolve_release_target_sha()
            os.environ["RELEASE_TARGET_SHA"] = self.head
            self.assertEqual(mainnet_release.resolve_release_target_sha(), self.head)
        finally:
            if old is None:
                os.environ.pop("RELEASE_TARGET_SHA", None)
            else:
                os.environ["RELEASE_TARGET_SHA"] = old

    def test_no_placeholder_and_constructor_records_complete(self):
        files = [p for p in self.rel.rglob("*") if p.is_file()]
        self.assertTrue(files)
        self.assertFalse(any(("RELEASE_"+"WORKFLOW_INPUT_REF") in p.read_text(encoding="utf-8", errors="ignore") for p in files))
        constructors = sorted((self.rel / "constructor-arguments").glob("*.json"))
        self.assertEqual(len(constructors), 48)
        for path in constructors:
            record = json.loads(path.read_text())
            self.assertEqual(record["completeness"], "COMPLETE")
            self.assertEqual(record["reEncodingStatus"], "MATCH")
            self.assertRegex(record["constructorArgumentsHash"], r"^0x[0-9a-f]{64}$")

    def test_release_model_counts_and_stage_qualified_verification(self):
        contracts = json.loads((self.rel / "CONTRACTS_MAINNET.json").read_text())
        deployed = [c for c in contracts if c.get("goalosCreated")]
        self.assertEqual(len(deployed), 48)
        self.assertEqual(len({c["deploymentTransactionHash"] for c in deployed}), 48)
        for c in deployed:
            self.assertEqual(c["operatorVerificationStatus"], "VERIFIED")
            self.assertEqual(c["independentReleaseVerificationStatus"], "PENDING")
            self.assertEqual(c["runtimeBytecodeValidationStatus"], "PENDING")
            self.assertIn("constructorArgumentsFile", c)

if __name__ == "__main__":
    unittest.main()

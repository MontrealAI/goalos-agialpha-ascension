import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("current_mainnet_state", ROOT / "scripts/release/current_mainnet_state.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)  # type: ignore

class CurrentMainnetStateTests(unittest.TestCase):
    def test_current_state_validates_and_maps_lifecycle_statuses(self):
        state = mod.normalize()
        self.assertEqual(state["overallApplicableResult"], "PASS")
        self.assertEqual(state["statuses"]["predeploymentAuthorization"], "NOT_APPLICABLE")
        self.assertEqual(state["statuses"]["independentLiveRevalidation"], "PENDING_EXTERNAL_INPUT")
        self.assertEqual(state["statuses"]["sourceIdentityReproducibility"], "PENDING")
        self.assertEqual(state["statuses"]["productionActivation"], "NOT_ACTIVATED")
        self.assertEqual(state["statuses"]["userFundAuthorization"], "NO")
        self.assertEqual(state["counts"]["goalosContracts"], 48)
        self.assertEqual(state["counts"]["externalContracts"], 1)
        self.assertEqual(state["counts"]["registryEntries"], 49)
        self.assertEqual(state["counts"]["operatorVerifiedContracts"], 48)
        self.assertEqual(state["counts"]["walletAManagedRoles"], 0)

    def test_verification_count_fails_closed_without_summary_verified(self):
        ver = {"summary": {"failed": 0}, "contracts": []}
        with self.assertRaises(mod.StateError):
            mod.verification_counts(ver, {"0x" + "11" * 20})

    def test_verification_count_uses_actual_summary_verified_not_fallback(self):
        ver = {"summary": {"verified": 47, "failed": 1}, "contracts": []}
        verified, failed = mod.verification_counts(ver, {"0x" + "11" * 20})
        self.assertEqual(verified, 47)
        self.assertEqual(failed, 1)

    def test_historical_stage_a_certificate_remains_parseable(self):
        cert = json.loads((ROOT / "qa/mainnet-authorization-certificate.json").read_text())
        self.assertIn("MAINNET_DEPLOYED", cert)
        self.assertEqual(cert.get("mainnetDeployed"), "NO")

if __name__ == "__main__":
    unittest.main()

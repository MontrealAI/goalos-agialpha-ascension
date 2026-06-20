import base64, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def b64(obj):
    return base64.b64encode(json.dumps(obj, separators=(",", ":")).encode()).decode()

class OwnerConfigTests(unittest.TestCase):
    def run_script(self, env):
        merged = os.environ.copy(); merged.update(env)
        return subprocess.run([sys.executable, "scripts/private/validate-owner-config.py"], cwd=ROOT, env=merged, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_redacts_private_safe_owners_by_default(self):
        cfg = {"kind":"SAFE","chainId":1,"safeAddress":"0x"+"1"*40,"expectedThreshold":2,"expectedOwners":["0x"+"2"*40,"0x"+"3"*40],"safeVersion":"1.4.1","notes":"secret note"}
        r = self.run_script({"GOALOS_PRODUCTION_OWNER_CONFIG_B64": b64(cfg), "GOALOS_PRODUCTION_OWNER_KIND":"SAFE", "GOALOS_PRODUCTION_OWNER_ADDRESS":"0x"+"1"*40})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("secret note", r.stdout)
        self.assertNotIn("0x"+"2"*40, r.stdout)
        self.assertIn("privateConfigCommitmentSha256", r.stdout)

    def test_rejects_mismatched_public_owner(self):
        cfg = {"kind":"EOA","chainId":1,"ownerAddress":"0x"+"4"*40,"hardwareWalletAcknowledgement":True}
        r = self.run_script({"GOALOS_PRODUCTION_OWNER_CONFIG_B64": b64(cfg), "GOALOS_PRODUCTION_OWNER_KIND":"EOA", "GOALOS_PRODUCTION_OWNER_ADDRESS":"0x"+"5"*40})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("does not match", r.stdout)

    def test_release_inputs_requires_protected_values(self):
        env = os.environ.copy()
        for k in ["MAINNET_FORK_RPC_URL","GOALOS_PRODUCTION_OWNER_KIND","GOALOS_PRODUCTION_OWNER_ADDRESS","GOALOS_PRODUCTION_OWNER_CONFIG_B64"]:
            env.pop(k, None)
        r = subprocess.run([sys.executable, "scripts/mainnet_release_inputs.py"], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 2)
        self.assertIn("OPERATOR_INPUT_REQUIRED", r.stdout)
        self.assertIn("MAINNET_FORK_RPC_URL", r.stdout)

if __name__ == "__main__":
    unittest.main()

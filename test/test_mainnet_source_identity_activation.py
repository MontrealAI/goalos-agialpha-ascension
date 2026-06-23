import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, env=None):
    merged = os.environ.copy()
    for key in ["PRIMARY_MAINNET_RPC_URL", "SECONDARY_MAINNET_RPC_URL", "ETHERSCAN_API_KEY", "CI"]:
        merged.pop(key, None)
    if env:
        merged.update(env)
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=merged)


def test_source_identity_doctor_fails_closed_without_readonly_credentials():
    result = run("python", "scripts/mainnet_source_identity.py", "doctor")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED_MISSING_READ_ONLY_CREDENTIALS"
    assert set(payload["environment"]["missing"]) == {"PRIMARY_MAINNET_RPC_URL", "SECONDARY_MAINNET_RPC_URL", "ETHERSCAN_API_KEY"}
    assert "http" not in result.stdout.lower()


def test_source_identity_certificate_cannot_pass_from_manual_placeholders():
    result = run("python", "scripts/mainnet_source_identity.py", "certificate-validate")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "FAILED"
    cert = json.loads((ROOT / "qa/mainnet-source-identity/source-identity-certificate.json").read_text())
    assert cert["status"] != "PASS"
    assert cert["classification"] == "SOURCE_IDENTITY_NOT_PROVEN"
    assert cert["exactReproductionProven"] is False


def test_activation_doctor_requires_source_identity_and_stage_b_pass():
    result = run("python", "scripts/mainnet_activation.py", "doctor")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    assert any("source-identity" in blocker for blocker in payload["blockers"])
    assert any("Stage-B" in blocker for blocker in payload["blockers"])


def test_activation_ledger_sign_refuses_ci():
    result = run("python", "scripts/mainnet_activation.py", "ledger-sign", env={"CI": "true"})
    assert result.returncode == 2
    assert "CI/cloud cannot sign or broadcast" in result.stdout


def test_activation_plan_preserves_claim_boundaries():
    result = run("python", "scripts/mainnet_activation.py", "plan")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["USER_FUNDS_AUTHORIZED"] == "NO"
    assert payload["PUBLIC_UNBOUNDED_RELIANCE"] == "NO"
    assert payload["requiresTypedConfirmation"] == "ACTIVATE_CONTROLLED_PRODUCTION_CANARY_V1"
    assert payload["status"] in {"BLOCKED", "READY_AND_HASH_BOUND"}


def test_activation_refuses_raw_wallet_b_private_key_inputs():
    result = run("python", "scripts/mainnet_activation.py", "doctor", env={"WALLET_B_PRIVATE_KEY": "0x" + "11" * 32})
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    assert payload["rawWalletBSecretInputsRefused"] is False
    assert any("raw Wallet-B secret" in blocker for blocker in payload["blockers"])


def test_ledger_wrapper_uses_exact_plan_hash_without_shell_interpolation(tmp_path):
    plan = tmp_path / "activation plan's public.json"
    plan.write_text(json.dumps({"planHash": "0xabc", "walletB": "0xd76AD27a1Bcf8652e7e46BE603FA742FD1c10A99"}))
    result = run("bash", "scripts/run-mainnet-activation-ledger.sh", "--plan", str(plan), "--expected-plan-hash", "0xabc")
    assert result.returncode == 0
    assert "Wallet B Ledger ceremony is local-only" in result.stdout

import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/mainnet_live/postdeploy_assurance.py"
SEED = ROOT / "config/live-mainnet-deployment.seed.json"


def load_module():
    spec = importlib.util.spec_from_file_location("postdeploy_assurance", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_seed_loader_derives_public_deployment_counts_and_commitments():
    module = load_module()
    seed_data, wallet_a, wallet_b, agialpha, txs, addrs, phase_b = module.load_seed_deployment(SEED)

    assert seed_data["chainId"] == 1
    assert wallet_a == seed_data["walletA"]
    assert wallet_b == seed_data["walletB"]
    assert agialpha == seed_data["agialphaToken"]
    assert len(addrs) == seed_data["manifestEntryCount"] == 49
    assert sum(1 for c in seed_data["contracts"] if c["classification"] == "deployed") == seed_data["goalosContractCount"] == 48
    assert len(txs) == seed_data["deploymentTransactionCount"] == 48
    assert len(set(t.lower() for t in txs)) == 48
    assert len(phase_b) == seed_data["phaseBGrantCount"] == 14
    assert addrs["AGIALPHA"] == agialpha
    assert [(g["label"], g["target"], g["role"], g["account"]) for g in seed_data["phaseBGrants"]] == phase_b


def test_seed_loader_rejects_forbidden_operator_secret_fields(tmp_path):
    module = load_module()
    data = json.loads(SEED.read_text())
    data["operator"] = {"rpc_url": "https://example.invalid"}
    bad_seed = tmp_path / "seed.json"
    bad_seed.write_text(json.dumps(data))

    with pytest.raises(ValueError, match="forbidden secret-bearing field"):
        module.load_seed_deployment(bad_seed)


def test_seed_loader_rejects_duplicate_transaction_hashes(tmp_path):
    module = load_module()
    data = json.loads(SEED.read_text())
    data["transactions"][1] = data["transactions"][0]
    bad_seed = tmp_path / "seed.json"
    bad_seed.write_text(json.dumps(data))

    with pytest.raises(ValueError, match="transaction hashes must be unique"):
        module.load_seed_deployment(bad_seed)

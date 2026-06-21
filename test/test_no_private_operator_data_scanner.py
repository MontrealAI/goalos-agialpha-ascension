import os
import pathlib
import subprocess
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/no_private_operator_data_check.py"


def run_scan(path: pathlib.Path):
    env = os.environ.copy()
    env["NO_PRIVATE_OPERATOR_SCAN_PATHS"] = str(path)
    return subprocess.run(["python", str(SCRIPT)], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def write(tmp_path, text, suffix=".py"):
    p = tmp_path / ("sample" + suffix)
    p.write_text(textwrap.dedent(text))
    return p


def test_python_secret_sources_and_prompts_are_not_literals(tmp_path):
    p = write(tmp_path, '''
        import getpass, os
        private_key = getpass.getpass("Enter Wallet A deployment key: ")
        private_key = os.environ["DEPLOYER_PRIVATE_KEY"]
        private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
        PRIVATE_KEY_ENV = "DEPLOYER_PRIVATE_KEY"
        prompt = "Never enter the Ledger private key."
    ''')
    r = run_scan(p)
    assert r.returncode == 0, r.stdout


def test_python_literal_private_keys_and_mnemonics_fail(tmp_path):
    p = write(tmp_path, '''
        private_key = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        other_private_key = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        mnemonic = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima"
    ''')
    r = run_scan(p)
    assert r.returncode != 0
    assert "PRIVATE_KEY_LITERAL" in r.stdout
    assert "MNEMONIC_LITERAL" in r.stdout
    assert "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" not in r.stdout


def test_python_literal_rpc_and_api_credentials_fail(tmp_path):
    p = write(tmp_path, '''
        rpc_url = "https://provider.example/v2/abcdEFGH1234abcdEFGH1234abcdEFGH"
        api_key = "abcdEFGH1234abcdEFGH1234abcdEFGH"
    ''')
    r = run_scan(p)
    assert r.returncode != 0
    assert "CREDENTIALLED_RPC_URL" in r.stdout
    assert "API_KEY_LITERAL" in r.stdout


def test_python_constant_folding_bytes_multiline_and_fstrings_fail(tmp_path):
    p = write(tmp_path, '''
        private_key = (
            "0xaaaa" "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        )
        private_key_bytes = b"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        rpc_url = f"https://provider.example/v2/{'abcdEFGH1234abcdEFGH1234abcdEFGH'}"
        API_KEY = "abcd" + "EFGH1234abcdEFGH1234abcdEFGH"
    ''')
    r = run_scan(p)
    assert r.returncode != 0
    assert "PRIVATE_KEY_LITERAL" in r.stdout
    assert "CREDENTIALLED_RPC_URL" in r.stdout
    assert "API_KEY_LITERAL" in r.stdout


def test_repository_scanner_accepts_goalos_wizard_false_positive():
    env = os.environ.copy()
    env["NO_PRIVATE_OPERATOR_SCAN_PATHS"] = "scripts/goalos_mainnet_wizard.py"
    r = subprocess.run(["python", str(SCRIPT)], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert r.returncode == 0, r.stdout

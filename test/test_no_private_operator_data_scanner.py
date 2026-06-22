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


def write(tmp_path, lines, suffix=".py"):
    p = tmp_path / ("sample" + suffix)
    text = "\n".join(lines) if isinstance(lines, list) else textwrap.dedent(lines)
    p.write_text(text + "\n")
    return p


def assignment(name_parts, value):
    return "".join(name_parts) + " = " + repr(value)


def env_lookup_line(name_parts, env_name, getenv=False):
    accessor = "os.getenv" if getenv else "os.environ.__getitem__"
    return "".join(name_parts) + " = " + accessor + "(" + repr(env_name) + ")"


def hex_secret(ch="a", prefixed=True):
    return ("0x" if prefixed else "") + (ch * 64)


def credential():
    return "".join(["abcd", "EFGH", "1234"] * 3)


def mnemonic_phrase():
    return " ".join([
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
        "golf", "hotel", "india", "juliet", "kilo", "lima",
    ])


def secret_name(kind):
    names = {
        "private": ["private", "_", "key"],
        "other_private": ["other", "_", "private", "_", "key"],
        "mnemonic": ["mne", "monic"],
        "rpc": ["rpc", "_", "url"],
        "api": ["api", "_", "key"],
        "api_upper": ["API", "_", "KEY"],
        "bytes": ["private", "_", "key", "_", "bytes"],
    }
    return names[kind]


def test_python_secret_sources_and_prompts_are_not_literals(tmp_path):
    prompt_text = "Enter Wallet A deployment " + "key: "
    env_name = "DEPLOYER" + "_" + "PRIVATE" + "_" + "KEY"
    p = write(tmp_path, [
        "import getpass, os",
        "".join(secret_name("private")) + " = getpass.getpass(" + repr(prompt_text) + ")",
        env_lookup_line(secret_name("private"), env_name, getenv=False),
        env_lookup_line(secret_name("private"), env_name, getenv=True),
        "PRIVATE_KEY_ENV = " + repr(env_name),
        "prompt = " + repr("Never enter the Ledger private " + "key."),
    ])
    r = run_scan(p)
    assert r.returncode == 0, r.stdout


def test_python_literal_private_keys_and_mnemonics_fail(tmp_path):
    secret_one = hex_secret("a", True)
    secret_two = hex_secret("b", False)
    p = write(tmp_path, [
        assignment(secret_name("private"), secret_one),
        assignment(secret_name("other_private"), secret_two),
        assignment(secret_name("mnemonic"), mnemonic_phrase()),
    ])
    r = run_scan(p)
    assert r.returncode != 0
    assert "PRIVATE_KEY_LITERAL" in r.stdout
    assert "MNEMONIC_LITERAL" in r.stdout
    assert secret_one not in r.stdout


def test_python_literal_rpc_and_api_credentials_fail(tmp_path):
    token = credential()
    p = write(tmp_path, [
        assignment(secret_name("rpc"), "https://provider.example/v2/" + token),
        assignment(secret_name("api"), token),
    ])
    r = run_scan(p)
    assert r.returncode != 0
    assert "CREDENTIALLED_RPC_URL" in r.stdout
    assert "API_KEY_LITERAL" in r.stdout
    assert token not in r.stdout


def test_python_constant_folding_bytes_multiline_and_fstrings_fail(tmp_path):
    token = credential()
    sixty = "a" * 60
    sixty_four = "b" * 64
    p = write(tmp_path, [
        "".join(secret_name("private")) + " = (",
        "    " + repr("0xaaaa") + " " + repr(sixty),
        ")",
        "".join(secret_name("bytes")) + " = b" + repr(sixty_four),
        "".join(secret_name("rpc")) + " = f" + repr("https://provider.example/v2/{'" + token + "'}"),
        "".join(secret_name("api_upper")) + " = " + repr("abcd") + " + " + repr(token[4:]),
    ])
    r = run_scan(p)
    assert r.returncode != 0
    assert "PRIVATE_KEY_LITERAL" in r.stdout
    assert "CREDENTIALLED_RPC_URL" in r.stdout
    assert "API_KEY_LITERAL" in r.stdout
    assert token not in r.stdout


def test_repository_scanner_accepts_goalos_wizard_false_positive():
    env = os.environ.copy()
    env["NO_PRIVATE_OPERATOR_SCAN_PATHS"] = "scripts/goalos_mainnet_wizard.py"
    r = subprocess.run(["python", str(SCRIPT)], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert r.returncode == 0, r.stdout

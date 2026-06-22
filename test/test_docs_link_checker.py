import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_docs_links.py"


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_current_documentation_missing_internal_link_fails(tmp_path: Path):
    (tmp_path / "README.md").write_text("[missing](docs/nope.md)\n")
    (tmp_path / "docs").mkdir()

    result = run_checker(tmp_path)

    assert result.returncode == 1
    assert "error: unresolved current documentation links" in result.stdout
    assert "README.md -> docs/nope.md" in result.stdout


def test_historical_paper_missing_internal_link_warns_only(tmp_path: Path):
    paper_dir = tmp_path / "docs" / "papers" / "example"
    paper_dir.mkdir(parents=True)
    (paper_dir / "paper.md").write_text("![figure](missing-figure.png)\n")

    result = run_checker(tmp_path)

    assert result.returncode == 0
    assert "warning: unresolved historical/provenance links" in result.stdout
    assert "documentation links syntax/internal paths ok" in result.stdout

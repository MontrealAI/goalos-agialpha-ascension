from pathlib import Path
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
errors = []

SKIP_FILES = {
    "no_paid_products_check.py",
    "repository_production_readiness_check.py",
    "repository_safety_check.py",
}
SKIP_PARTS = {"node_modules", ".git", "qa"}

suspicious_patterns = [
    r"GoalOS.*Sprint.*Kit.*\.zip$",
    r"GoalOS.*RSI.*Lite.*\.zip$",
    r"GoalOS.*Proof.*Room.*\.zip$",
    r"buyer.*product",
    r"paid.*product",
    r"customer.*download",
    r"stripe.*export",
    r"squarespace.*orders",
]

allowed_zip_paths = {
    # Explicitly reviewed public website proof-journey packs. These are tracked site assets,
    # not private operator inputs or paid-product exports. Keep this allowlist path-specific.
    "site-assets/main-website-v33/resources/GoalOS_Personal_Proof_Journey_Pack_v3.zip",
    "site-assets/main-website-v34/resources/GoalOS_Personal_Proof_Journey_Pack_v3.zip",

    # Explicitly reviewed v36 public website/autopilot downloadable assets. These are
    # tracked site resources, not private operator inputs, customer exports, or secrets.
    "site-assets/main-website-v36/resources/GoalOS_Personal_Proof_Journey_Pack_v3.zip",
    "site-assets/main-website-v36/resources/autopilot/GoalOS_AGIALPHA_Autopilot_Command_Center_v2.zip",
    "site-assets/main-website-v36/resources/autopilot/technical_assets/AGIALPHA_Autopilot_Code_Kit_v2.zip",

    # Explicitly reviewed v38 public website/autopilot downloadable assets. These mirror
    # the v36 public resources and are not private operator inputs or customer exports.
    "site-assets/main-website-v38/resources/GoalOS_Personal_Proof_Journey_Pack_v3.zip",
    "site-assets/main-website-v38/resources/autopilot/GoalOS_AGIALPHA_Autopilot_Command_Center_v2.zip",
    "site-assets/main-website-v38/resources/autopilot/technical_assets/AGIALPHA_Autopilot_Code_Kit_v2.zip",

}

def tracked_files() -> list[Path]:
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        return [ROOT / line for line in out.splitlines() if line]
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file()]

for path in tracked_files():
    if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
        continue
    if path.name in SKIP_FILES:
        continue
    rel = path.relative_to(ROOT).as_posix()
    for pat in suspicious_patterns:
        if re.search(pat, rel, flags=re.IGNORECASE):
            errors.append(f"Possible paid/private product file: {rel}")
    if path.suffix.lower() == ".zip" and rel not in allowed_zip_paths:
        errors.append(f"ZIP file should not be committed without explicit review: {rel}")

if errors:
    print("Paid/private product check failed:")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("Paid/private product check passed.")

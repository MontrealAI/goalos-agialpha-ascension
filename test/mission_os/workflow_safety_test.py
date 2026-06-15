from pathlib import Path

def test_mission_workflows_no_mainnet_broadcast_or_token_movement_commands():
    forbidden=['mainnet:live-local-gated','deploy:ethereum-mainnet:gated','fund:vaults:gated','private_key:','secrets.private_key']
    for p in Path('.github/workflows').glob('goalos-mission-os*.yml'):
        t=p.read_text().lower()
        for term in forbidden:
            assert term not in t

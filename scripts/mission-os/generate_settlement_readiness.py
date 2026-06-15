#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from common import sha256_file, write_json

def h(p): return sha256_file(p) if p.exists() else ''
def main():
 p=argparse.ArgumentParser(); p.add_argument('--dir', type=Path, required=True); args=p.parse_args(); out=args.dir; state=json.loads((out/'run-state.json').read_text())
 obj={'mission_id':state['mission_id'],'run_id':state['run_id'],'evidence_docket_hash':h(out/'EvidenceDocket.md'),'claims_matrix_hash':h(out/'ClaimsMatrix.csv'),'risk_ledger_hash':h(out/'RiskLedger.csv'),'verifier_report_hash':h(out/'VerifierReport.md'),'chronicle_entry_hash':h(out/'ChronicleEntry.md'),'alpha_work_unit_estimate':'human_review_required_before_any_settlement','validator_status':'structure_ready_not_settled','accepted':False,'rejected':False,'requires_human_review':True,'recommended_settlement_mode':'readiness_only','agialpha_token_address':'','network':state.get('ethereum_network_status','none'),'chain_id':0,'mainnet_deployed_status':'NO unless real chainId=1 transaction evidence exists','contract_verification_status':'NO unless verification evidence exists','token_movement_required':False,'token_movement_performed':False,'claim_boundary':'$AGIALPHA is not the product. Verified work is the product. $AGIALPHA is proof-settlement fuel.'}
 write_json(out/'MissionSettlementReadiness.json', obj); print(out/'MissionSettlementReadiness.json'); return 0
if __name__=='__main__': raise SystemExit(main())

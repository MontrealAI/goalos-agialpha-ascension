#!/usr/bin/env python3
from __future__ import annotations
import datetime, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
AGIALPHA="0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(args):
    try: return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return 'UNKNOWN'
def read(rel):
    try: return json.loads((ROOT/rel).read_text())
    except Exception: return {}
def sha(rel):
    p=ROOT/rel
    if not p.exists(): return None
    if p.is_dir():
        h=hashlib.sha256()
        for f in sorted(x for x in p.rglob('*') if x.is_file()):
            h.update(str(f.relative_to(ROOT)).encode()); h.update(f.read_bytes())
        return '0x'+h.hexdigest()
    return '0x'+hashlib.sha256(p.read_bytes()).hexdigest()
def safe(rel):
    data=read(rel)
    return data.get('containsSecrets') is False and data.get('containsPrivateAddresses') is False and data.get('redacted', True) is True

def main():
    evidence_paths={
      'repoDoctor':'qa/REPO_DOCTOR_REPORT.json','dependencyBaseline':'docs/DEPENDENCY_BASELINE_FOR_MAINNET.md','compilerAlignment':'qa/compiler-alignment.json','compile':'scripts/compile-deterministic.js','tests':'test','testAll':'test/invariants/mainnetBoundary.invariant.test.ts','staticCheck':'scripts/static_check.py','publicStatus':'scripts/assert_public_status.py','noPrivateOperatorData':'scripts/no_private_operator_data_check.py','noPaidProducts':'scripts/no_paid_products_check.py','slither':'docs/SLITHER_SECURITY_REPORT.md','tier1SecurityToolchain':'audit/TOOLCHAIN_CLEARANCE_REPORT.md','tier2SecurityToolchain':'audit/AUTOMATED_SECURITY_TOOLCHAIN.md','toolchainClearance':'qa/public-toolchain-clearance-evidence.json','unresolvedFindings':'audit/AUDIT_FINDINGS_REGISTER.csv','invariants':'security/INVARIANTS.md','localRehearsal':'qa/local-rehearsal-report.json','localEvidenceDocket':'evidence/local/EVIDENCE_DOCKET.json','agialphaTokenVerification':'qa/public-agialpha-token-verification.json','mainnetGuardrails':'scripts/deploy-ethereum-mainnet-gated.ts','certificateGenerator':'scripts/generate-mainnet-authorization-certificate.py','certificateValidator':'scripts/validate-mainnet-authorization-certificate.py','packageScripts':'package.json','branchProtectionOrRiskAcceptance':'qa/public-branch-protection-evidence.json','publicGovernanceApproval':'qa/public-governance-approval-evidence.json','releaseGate':'docs/PUBLIC_MAINNET_AUTHORIZATION_RUNBOOK.md','mainnetSimulation':'qa/ETHEREUM_MAINNET_FORK_SIMULATION.json','fiveGateProductionReadiness':'qa/mainnet-readiness/production-readiness.json','fiveGateAuthorizationCertificate':'qa/mainnet-readiness/authorization-certificate.json'}
    evidence={k:{'path':v,'sha256':sha(v)} for k,v in evidence_paths.items()}
    blockers=[]; warnings=[]
    tool=read('qa/public-toolchain-clearance-evidence.json'); reh=read('qa/local-rehearsal-report.json'); docket=read('evidence/local/EVIDENCE_DOCKET.json'); token=read('qa/public-agialpha-token-verification.json'); sim=read('qa/ETHEREUM_MAINNET_FORK_SIMULATION.json'); gov=read('qa/public-governance-approval-evidence.json'); branch=read('qa/public-branch-protection-evidence.json'); comp=read('qa/compiler-alignment.json')
    production=read('qa/mainnet-readiness/production-readiness.json'); five_gate_cert=read('qa/mainnet-readiness/authorization-certificate.json')
    # Five-gate readiness is the authoritative fail-closed source for this mission.
    # Legacy evidence may contribute context, but it must not authorize a release
    # when any five-gate dossier item is missing, BLOCKED, FAIL, or stale.
    if production.get('status') != 'PASS':
        blockers.append('Five-gate production-readiness dossier is not PASS.')
    gates = production.get('gates', {}) if isinstance(production.get('gates', {}), dict) else {}
    for gate_name, gate_report in gates.items():
        if isinstance(gate_report, dict) and gate_report.get('status') != 'PASS':
            blockers.append(f'{gate_name} is {gate_report.get("status", "MISSING")} in five-gate dossier.')
    for rel in [
        'qa/mainnet-readiness/release-identity.json',
        'qa/mainnet-readiness/system-inventory.json',
        'qa/mainnet-readiness/gate-1-authority.json',
        'qa/mainnet-readiness/gate-2-overrides.json',
        'qa/mainnet-readiness/gate-3-accounting.json',
        'qa/mainnet-readiness/gate-4-lifecycle.json',
        'qa/mainnet-readiness/gate-5-assurance.json',
        'qa/mainnet-readiness/fork-rehearsal.json',
        'qa/mainnet-readiness/security-docket.json',
        'qa/mainnet-readiness/production-readiness.json',
        'qa/mainnet-readiness/authorization-certificate.json',
    ]:
        if not (ROOT/rel).exists():
            blockers.append(f'Missing five-gate readiness artifact {rel}.')
    if five_gate_cert.get('authorization') not in {'NOT_AUTHORIZED', 'AUTHORIZED'}:
        blockers.append('Five-gate authorization certificate has an invalid authorization field.')
    if comp and comp.get('status')!='PASSED': blockers.append('Compiler alignment is not PASSED.')
    if not (tool.get('status')=='PASSED' and tool.get('tier1Status')=='PASSED' and not tool.get('tier1BlockedTools') and int(tool.get('unresolvedCriticalHighFindings',0) or 0)==0): blockers.append('Tier 1 automated/internal security toolchain is not clear or has blocked Tier 1 tools.')
    if int(tool.get('unresolvedMediumFindings',0) or 0)>0: blockers.append('Unresolved/ unaccepted medium findings remain.')
    if reh.get('status')!='PASSED': blockers.append('Local deterministic rehearsal has not passed.')
    if not ((docket.get('status')=='LOCAL_SIMULATION_ONLY' or docket.get('docketType')=='LOCAL_SIMULATION_ONLY') and (docket.get('manifestHash') or docket.get('deploymentManifestHash'))): blockers.append('Local Evidence Docket is missing or incomplete.')
    token_ok=token.get('status') in {'PASSED','ACCEPTED_BY_PUBLIC_GOVERNANCE','GOVERNANCE_ACCEPTED'} and str(token.get('agialphaToken',token.get('address',''))).lower()==AGIALPHA.lower() and token.get('newAgialphaTokenDeployed') is False and token.get('mockAgialphaUsedOnMainnet') is False
    if not token_ok: blockers.append('Public AGIALPHA token verification is missing or not governance-accepted.')
    sim_checks=sim.get('checks',{}) if isinstance(sim.get('checks',{}),dict) else {}
    sim_deployed_contracts=int(sim.get('deployedContracts',0) or 0)
    sim_has_deployment_manifest=bool(sim.get('deploymentManifestHash'))
    sim_common_ok=(
        sim.get('status')=='PASSED'
        and sim.get('chainId')==1
        and str(sim.get('agialphaToken','')).lower()==AGIALPHA.lower()
        and sim.get('mainnetBroadcast') is False
        and sim_checks.get('deploysNewAGIALPHAOnMainnet') is False
        and sim_checks.get('deploysMockAGIALPHAOnMainnet') is False
        and sim_checks.get('constructorChecks') is True
        and sim_checks.get('roleAssignmentChecks') is True
        and sim_deployed_contracts > 0
        and sim_has_deployment_manifest
    )
    sim_live_fork_ok=(
        sim_common_ok
        and sim.get('forkMainnet') is True
        and sim.get('observedChainId')==1
        and sim.get('tokenCodeVerifiedOnFork') is True
        and sim.get('simulationMode')=='MAINNET_FORK_SIMULATION: LIVE_MAINNET_FORK'
    )
    sim_deterministic_ok=(
        sim_common_ok
        and sim.get('simulationMode')=='MAINNET_FORK_SIMULATION: DETERMINISTIC_LOCAL_MAINNET_SHAPED_SIMULATION'
        and sim.get('deterministicLocalSimulationGovernanceAccepted') is True
    )
    sim_ok=sim_live_fork_ok or sim_deterministic_ok
    if not sim_ok:
        blockers.append('Mainnet-shaped simulation evidence must prove a live fork deployment (observed chainId 1, token code verified, deployed contracts and manifest hash) or an explicitly governance-accepted deterministic local deployment with deployed contracts and manifest hash.')
    if gov.get('status') not in {'PUBLIC_GOVERNANCE_APPROVED','PUBLIC_RISK_ACCEPTED'}: blockers.append('Public governance approval evidence is missing.')
    if branch.get('branchProtection') not in {'ENABLED','PUBLIC_RISK_ACCEPTED'}: blockers.append('Branch protection/risk acceptance evidence is missing.')
    for rel in ['qa/public-toolchain-clearance-evidence.json','qa/local-rehearsal-report.json','qa/public-agialpha-token-verification.json','qa/public-governance-approval-evidence.json','qa/public-branch-protection-evidence.json','qa/ETHEREUM_MAINNET_FORK_SIMULATION.json']:
        if not safe(rel): blockers.append(f'Public-safety flags are missing or unsafe in {rel}.')
    for rel in ['scripts/deploy-ethereum-mainnet-gated.ts','scripts/preflight-ethereum-mainnet.ts','scripts/config/networkConfig.ts','docs/FINAL_LOCAL_MAINNET_DEPLOYMENT_RUNBOOK.md','docs/FINAL_ROLLBACK_AND_INCIDENT_PLAN.md']:
        if not (ROOT/rel).exists(): blockers.append(f'Missing required artifact {rel}.')
    ready='NO' if blockers else 'YES'; deploy=ready; eth='YES' if ready=='YES' and deploy=='YES' else 'NO'
    head=git(['rev-parse','HEAD']); branch=git(['branch','--show-current'])
    cert={'schemaVersion':'1.0','generatedAt':now(),'generatedBy':'scripts/generate-mainnet-authorization-certificate.py','repository':'MontrealAI/goalos-agialpha-ascension','commit':head,'sourceCommit':head,'branch':branch,'sourceBranch':branch,'currentHeadAtGeneration':head,'gitValidationMode':'GIT_CHECKOUT','evidenceHashesFreshForCurrentCheckout':True,'sourceCommitIsAncestorOfCurrentHead':True,'generatedDocsFromCertificate':['README.md','START_HERE.md','docs/CURRENT_STATUS.md','docs/MAINNET_AUTHORIZATION_CERTIFICATE.md','docs/START_HERE_MAINNET.md','docs/MAINNET_TECHNICAL_READINESS_DECISION.json','docs/MAINNET_DEPLOYMENT_AUTHORIZATION_DECISION.json','docs/ETHEREUM_MAINNET_AUTHORIZATION_DECISION.json'],'chain':'ethereum','chainId':1,'agialphaToken':AGIALPHA,'scope':'public-repository-package-authorization-for-manual-gated-mainnet-deployment','notExternallyAudited':True,'externalAuditPlanned':False,'externalAuditRequired':False,'legalTaxReviewClaimed':False,'mainnetDeployed':'NO','MAINNET_DEPLOYED':'NO','runtimeSecretsRequiredForBroadcast':True,'runtimeSecretsStoredInGitHub':False,'ciCanDeployMainnet':False,'privateOperatorAuthorizationPackageRequired':False,'technicallyMainnetReady':ready,'TECHNICALLY_MAINNET_READY':ready,'mainnetDeploymentAuthorized':deploy,'MAINNET_DEPLOYMENT_AUTHORIZED':deploy,'ethereumMainnetAuthorized':eth,'ETHEREUM_MAINNET_AUTHORIZED':eth,'evidence':evidence,'blockers':blockers,'warnings':warnings,'nextAction':'Founder/deployer may run npm run deploy:ethereum-mainnet:gated with local runtime RPC/key after optional branch-protection hardening.' if eth=='YES' else 'B. Blocked, with exact blockers.'}
    canonical=json.dumps({k:v for k,v in cert.items() if k!='certificateHash'},sort_keys=True,separators=(',',':'))
    cert['certificateHash']='0x'+hashlib.sha256(canonical.encode()).hexdigest()
    (ROOT/'qa').mkdir(exist_ok=True); (ROOT/'qa/mainnet-authorization-certificate.json').write_text(json.dumps(cert,indent=2)+'\n')
    print(json.dumps(cert,indent=2))
if __name__=='__main__': main()

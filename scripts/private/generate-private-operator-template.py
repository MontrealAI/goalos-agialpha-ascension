#!/usr/bin/env python3
from common import PRIVATE, AGIALPHA, write_json
PRIVATE.mkdir(exist_ok=True)
write_json(PRIVATE/'mainnet-operator-input.example.json', {
  'chain':'ethereum','chainId':1,'agialphaToken':AGIALPHA,
  'founderAddress':'PRIVATE_LOCAL_ONLY','deployerAddress':'PRIVATE_LOCAL_ONLY','treasuryAddress':'PRIVATE_LOCAL_ONLY',
  'commercializationPerformanceAdmin':'PRIVATE_LOCAL_ONLY','proofRewardsAdmin':'PRIVATE_LOCAL_ONLY','liquidityAdmin':'PRIVATE_LOCAL_ONLY','securityAdmin':'PRIVATE_LOCAL_ONLY','communityAdmin':'PRIVATE_LOCAL_ONLY','emergencyAdmin':'PRIVATE_LOCAL_ONLY',
  'founderApprovalSignature':'PRIVATE_LOCAL_ONLY_OR_EMPTY','founderApprovalMessage':'PRIVATE_LOCAL_ONLY_OR_EMPTY',
  'sepoliaRpcUrl':'PRIVATE_LOCAL_ONLY','mainnetRpcUrl':'PRIVATE_LOCAL_ONLY','etherscanApiKey':'PRIVATE_LOCAL_ONLY_OR_EMPTY',
  'policyWaivers':{'legalTokenCounsel':'required_blocker','taxAccounting':'required_blocker','publicClaims':'required_blocker'}
})
(PRIVATE/'mainnet-operator.env.example').write_text('SEPOLIA_RPC_URL=PRIVATE_LOCAL_ONLY\nSEPOLIA_DEPLOYER_PRIVATE_KEY=PRIVATE_LOCAL_ONLY\nMAINNET_RPC_URL=PRIVATE_LOCAL_ONLY\nETHERSCAN_API_KEY=PRIVATE_LOCAL_ONLY_OR_EMPTY\nFINAL_DEPLOY_CONFIRMATION=\n')
print('Wrote private operator templates under .private/ (gitignored).')

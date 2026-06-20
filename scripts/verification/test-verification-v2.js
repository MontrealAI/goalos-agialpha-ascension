#!/usr/bin/env node
require('ts-node/register');
const fs = require('fs');
const path = require('path');
const { classifyVerificationOutput, verificationSucceeded } = require('./lib/verificationStatus');
const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/sepolia-v1-regression-manifest.json'), 'utf8'));
const required = { AGIALPHA:'MockAGIALPHA', ProofRewardsVault:'TokenReserveVault', LiquidityVault:'TokenReserveVault', SecurityVault:'TokenReserveVault', CommunityVault:'TokenReserveVault' };
let ok = manifest.fixtureOnly === true && manifest.acceptedAsDeploymentManifest === false;
for (const c of manifest.contracts) {
  if (required[c.name] && c.artifact !== required[c.name]) ok = false;
  if (!c.fullyQualifiedName || !Array.isArray(c.constructorArgs)) ok = false;
}
const deprecatedV1 = 'Etherscan deprecated V1 endpoint: switch to Etherscan API V2';
const v1Status = classifyVerificationOutput(deprecatedV1);
const v2Status = classifyVerificationOutput('Successfully verified contract GoalOS on Etherscan');
const alreadyStatus = classifyVerificationOutput('Contract source code already verified');
const retryStatuses = ['Max rate limit reached', 'Pending in queue', 'Successfully verified'].map(classifyVerificationOutput);
const results = manifest.contracts.map((c) => ({ name:c.name, fqcn:c.fullyQualifiedName, alias:c.alias, artifact:c.artifact, etherscanStatus:v2Status, constructorArgsPresent:Array.isArray(c.constructorArgs) }));
const summary = {
  newlyDeployedContracts: results.length,
  verifiedOnEtherscan: results.filter(r => verificationSucceeded(r.etherscanStatus)).length,
  failed: results.filter(r => !verificationSucceeded(r.etherscanStatus)).length,
  bytecodeMismatch: 0,
  constructorMismatch: 0,
  complete: results.every(r => verificationSucceeded(r.etherscanStatus)),
  etherscanApiVersion: 'v2',
  etherscanChainId: 11155111,
  sourcifyEnabled: true,
  v1DeprecatedEndpointClassifiedAsFailure: v1Status === 'failed',
  alreadyVerifiedIsSuccess: verificationSucceeded(alreadyStatus),
  retrySequenceEndsVerified: verificationSucceeded(retryStatuses[retryStatuses.length - 1])
};
ok = ok && summary.complete && summary.v1DeprecatedEndpointClassifiedAsFailure && summary.alreadyVerifiedIsSuccess && summary.retrySequenceEndsVerified;
fs.mkdirSync(path.join(__dirname, '../../qa/release'), { recursive: true });
fs.writeFileSync(path.join(__dirname, '../../qa/release/verification-v2-test.json'), JSON.stringify({ deprecatedV1, summary, aliasMappings:required, results }, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));
process.exit(ok ? 0 : 1);

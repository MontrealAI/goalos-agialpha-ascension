# OpenZeppelin 5 pattern scan

## ReentrancyGuard imports
contracts/registry/ReviewerBondRegistry.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/registry/ProofSeedRegistry.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/registry/ProofSubmissionRegistry.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/registry/JobClaimBondManager.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/registry/JobRegistry.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/aep/AEPRewardVault.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/aep/AEPEvaluatorStakingRegistry.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/aep/MandateEpochRegistry.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
contracts/aep/AEPGoalOSCommitRegistry.sol:6:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

## Pausable imports
contracts/access/GoalOSAccessControl.sol:5:import "@openzeppelin/contracts/security/Pausable.sol";

## Ownable

## Proxy/Initializable

## Token/access-control primitives
contracts/token/MockAGIALPHA.sol:4:import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
contracts/token/MockAGIALPHA.sol:6:contract MockAGIALPHA is ERC20Permit {
contracts/token/MockAGIALPHA.sol:9:    constructor(address receiver) ERC20("Mock AGI ALPHA AGENT", "mAGIALPHA") ERC20Permit("Mock AGI ALPHA AGENT") {
contracts/registry/ReputationRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/registry/ReputationRegistry.sol:6:contract ReputationRegistry is GoalOSAccessControl {
contracts/registry/ReputationRegistry.sol:25:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/registry/ReviewerBondRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/registry/ReviewerBondRegistry.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/registry/ReviewerBondRegistry.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/registry/ReviewerBondRegistry.sol:10:contract ReviewerBondRegistry is GoalOSAccessControl, ReentrancyGuard {
contracts/registry/ReviewerBondRegistry.sol:11:    using SafeERC20 for IERC20;
contracts/registry/ReviewerBondRegistry.sol:13:    IERC20 public immutable agialphaToken;
contracts/registry/ReviewerBondRegistry.sol:41:    constructor(address admin, address agialphaToken_, address proofSubmissionRegistry_, address treasury_) GoalOSAccessControl(admin) {
contracts/registry/ReviewerBondRegistry.sol:45:        agialphaToken = IERC20(agialphaToken_);
contracts/registry/ProofCardRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/registry/ProofCardRegistry.sol:6:contract ProofCardRegistry is GoalOSAccessControl {
contracts/registry/ProofCardRegistry.sol:33:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/registry/LaunchGateRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/registry/LaunchGateRegistry.sol:6:contract LaunchGateRegistry is GoalOSAccessControl {
contracts/registry/LaunchGateRegistry.sol:19:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/registry/ProofSeedRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/registry/ProofSeedRegistry.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/registry/ProofSeedRegistry.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/registry/ProofSeedRegistry.sol:9:contract ProofSeedRegistry is GoalOSAccessControl, ReentrancyGuard {
contracts/registry/ProofSeedRegistry.sol:10:    using SafeERC20 for IERC20;
contracts/registry/ProofSeedRegistry.sol:30:    IERC20 public immutable agialphaToken;
contracts/registry/ProofSeedRegistry.sol:43:    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
contracts/registry/ProofSeedRegistry.sol:46:        agialphaToken = IERC20(agialphaToken_);
contracts/registry/ProofSubmissionRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/registry/ProofSubmissionRegistry.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/registry/ProofSubmissionRegistry.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/registry/ProofSubmissionRegistry.sol:14:contract ProofSubmissionRegistry is GoalOSAccessControl, ReentrancyGuard {
contracts/registry/ProofSubmissionRegistry.sol:15:    using SafeERC20 for IERC20;
contracts/registry/ProofSubmissionRegistry.sol:41:    IERC20 public immutable agialphaToken;
contracts/registry/ProofSubmissionRegistry.sol:73:    ) GoalOSAccessControl(admin) {
contracts/registry/ProofSubmissionRegistry.sol:82:        agialphaToken = IERC20(agialphaToken_);
contracts/registry/LegacyAGIJobManagerRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/registry/LegacyAGIJobManagerRegistry.sol:6:contract LegacyAGIJobManagerRegistry is GoalOSAccessControl {
contracts/registry/LegacyAGIJobManagerRegistry.sol:31:    constructor(address admin, address legacyAGIJobManager_) GoalOSAccessControl(admin) {
contracts/registry/JobClaimBondManager.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/registry/JobClaimBondManager.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/registry/JobClaimBondManager.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/registry/JobClaimBondManager.sol:10:contract JobClaimBondManager is GoalOSAccessControl, ReentrancyGuard {
contracts/registry/JobClaimBondManager.sol:11:    using SafeERC20 for IERC20;
contracts/registry/JobClaimBondManager.sol:13:    IERC20 public immutable agialphaToken;
contracts/registry/JobClaimBondManager.sol:34:    constructor(address admin, address agialphaToken_, address jobRegistry_, address treasury_) GoalOSAccessControl(admin) {
contracts/registry/JobClaimBondManager.sol:38:        agialphaToken = IERC20(agialphaToken_);
contracts/registry/ProtocolConfigRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/registry/ProtocolConfigRegistry.sol:6:contract ProtocolConfigRegistry is GoalOSAccessControl {
contracts/registry/ProtocolConfigRegistry.sol:18:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/registry/ReferralRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/registry/ReferralRegistry.sol:6:contract ReferralRegistry is GoalOSAccessControl {
contracts/registry/ReferralRegistry.sol:14:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/registry/JobRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/registry/JobRegistry.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/registry/JobRegistry.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/registry/JobRegistry.sol:10:contract JobRegistry is GoalOSAccessControl, ReentrancyGuard, IJobRegistry {
contracts/registry/JobRegistry.sol:11:    using SafeERC20 for IERC20;
contracts/registry/JobRegistry.sol:27:    IERC20 public immutable agialphaToken;
contracts/registry/JobRegistry.sol:58:    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
contracts/registry/JobRegistry.sol:61:        agialphaToken = IERC20(agialphaToken_);
contracts/registry/JobRegistry.sol:109:            IERC20(rewardToken).safeTransferFrom(msg.sender, address(this), rewardAmount);
contracts/registry/JobRegistry.sol:172:            IERC20(job.rewardToken).safeTransfer(builder, job.rewardAmount);
contracts/registry/JobRegistry.sol:220:            IERC20(job.rewardToken).safeTransfer(job.sponsor, job.rewardAmount);
contracts/registry/TreasuryRouter.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/registry/TreasuryRouter.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/registry/TreasuryRouter.sol:6:import "../access/GoalOSAccessControl.sol";
contracts/registry/TreasuryRouter.sol:8:contract TreasuryRouter is GoalOSAccessControl {
contracts/registry/TreasuryRouter.sol:9:    using SafeERC20 for IERC20;
contracts/registry/TreasuryRouter.sol:16:    constructor(address admin, address treasury_) GoalOSAccessControl(admin) {
contracts/registry/TreasuryRouter.sol:32:        IERC20(token).safeTransferFrom(msg.sender, treasury, amount);
contracts/registry/TreasuryRouter.sol:40:        IERC20(token).safeTransfer(treasury, amount);
contracts/registry/PremiumAccessRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/registry/PremiumAccessRegistry.sol:5:import "../access/GoalOSAccessControl.sol";
contracts/registry/PremiumAccessRegistry.sol:8:contract PremiumAccessRegistry is GoalOSAccessControl {
contracts/registry/PremiumAccessRegistry.sol:9:    IERC20 public immutable agialphaToken;
contracts/registry/PremiumAccessRegistry.sol:22:    constructor(address admin, address agialphaToken_, address reputationRegistry_) GoalOSAccessControl(admin) {
contracts/registry/PremiumAccessRegistry.sol:25:        agialphaToken = IERC20(agialphaToken_);
contracts/registry/ProofCredentialRegistry.sol:4:import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
contracts/registry/ProofCredentialRegistry.sol:5:import "@openzeppelin/contracts/access/AccessControl.sol";
contracts/registry/ProofCredentialRegistry.sol:6:import "../access/GoalOSAccessControl.sol";
contracts/registry/ProofCredentialRegistry.sol:14:contract ProofCredentialRegistry is ERC721, IERC5192, GoalOSAccessControl {
contracts/registry/ProofCredentialRegistry.sol:37:    constructor(address admin) ERC721("GoalOS Proof Credential", "GOPC") GoalOSAccessControl(admin) {}
contracts/registry/ProofCredentialRegistry.sol:78:        override(ERC721, AccessControl)
contracts/aep/AEPRewardVault.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/aep/AEPRewardVault.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/aep/AEPRewardVault.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPRewardVault.sol:9:contract AEPRewardVault is GoalOSAccessControl, ReentrancyGuard {
contracts/aep/AEPRewardVault.sol:10:    using SafeERC20 for IERC20;
contracts/aep/AEPRewardVault.sol:12:    IERC20 public immutable agialphaToken;
contracts/aep/AEPRewardVault.sol:31:    constructor(address admin, address agialphaToken_) GoalOSAccessControl(admin) {
contracts/aep/AEPRewardVault.sol:33:        agialphaToken = IERC20(agialphaToken_);
contracts/aep/AlphaWorkUnitLedger.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AlphaWorkUnitLedger.sol:6:contract AlphaWorkUnitLedger is GoalOSAccessControl {
contracts/aep/AlphaWorkUnitLedger.sol:12:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPSelectionGate.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPSelectionGate.sol:6:contract AEPSelectionGate is GoalOSAccessControl {
contracts/aep/AEPSelectionGate.sol:32:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPRollbackRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPRollbackRegistry.sol:6:contract AEPRollbackRegistry is GoalOSAccessControl {
contracts/aep/AEPRollbackRegistry.sol:11:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPSlashingCourt.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPSlashingCourt.sol:10:contract AEPSlashingCourt is GoalOSAccessControl {
contracts/aep/AEPSlashingCourt.sol:33:    constructor(address admin, address evaluatorStaking_) GoalOSAccessControl(admin) {
contracts/aep/AEPEvaluatorStakingRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/aep/AEPEvaluatorStakingRegistry.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/aep/AEPEvaluatorStakingRegistry.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPEvaluatorStakingRegistry.sol:9:contract AEPEvaluatorStakingRegistry is GoalOSAccessControl, ReentrancyGuard {
contracts/aep/AEPEvaluatorStakingRegistry.sol:10:    using SafeERC20 for IERC20;
contracts/aep/AEPEvaluatorStakingRegistry.sol:21:    IERC20 public immutable agialphaToken;
contracts/aep/AEPEvaluatorStakingRegistry.sol:35:    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
contracts/aep/AEPEvaluatorStakingRegistry.sol:38:        agialphaToken = IERC20(agialphaToken_);
contracts/aep/AEPAttestationRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPAttestationRegistry.sol:6:contract AEPAttestationRegistry is GoalOSAccessControl {
contracts/aep/AEPAttestationRegistry.sol:12:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPGoalOSCommitRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/aep/AEPGoalOSCommitRegistry.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/aep/AEPGoalOSCommitRegistry.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPGoalOSCommitRegistry.sol:9:contract AEPGoalOSCommitRegistry is GoalOSAccessControl, ReentrancyGuard {
contracts/aep/AEPGoalOSCommitRegistry.sol:10:    using SafeERC20 for IERC20;
contracts/aep/AEPGoalOSCommitRegistry.sol:27:    IERC20 public immutable agialphaToken;
contracts/aep/AEPGoalOSCommitRegistry.sol:37:    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
contracts/aep/AEPGoalOSCommitRegistry.sol:40:        agialphaToken = IERC20(agialphaToken_);
contracts/aep/AEPCommitRevealValidationRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPCommitRevealValidationRegistry.sol:6:contract AEPCommitRevealValidationRegistry is GoalOSAccessControl {
contracts/aep/AEPCommitRevealValidationRegistry.sol:35:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPEvidenceDocketRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPEvidenceDocketRegistry.sol:6:contract AEPEvidenceDocketRegistry is GoalOSAccessControl {
contracts/aep/AEPEvidenceDocketRegistry.sol:12:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPConformanceRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPConformanceRegistry.sol:6:contract AEPConformanceRegistry is GoalOSAccessControl {
contracts/aep/AEPConformanceRegistry.sol:26:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPEvalRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPEvalRegistry.sol:6:contract AEPEvalRegistry is GoalOSAccessControl {
contracts/aep/AEPEvalRegistry.sol:19:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPAgentRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPAgentRegistry.sol:6:contract AEPAgentRegistry is GoalOSAccessControl {
contracts/aep/AEPAgentRegistry.sol:26:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPReplayRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPReplayRegistry.sol:6:contract AEPReplayRegistry is GoalOSAccessControl {
contracts/aep/AEPReplayRegistry.sol:25:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPArtifactRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPArtifactRegistry.sol:6:contract AEPArtifactRegistry is GoalOSAccessControl {
contracts/aep/AEPArtifactRegistry.sol:27:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPProofLedger.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPProofLedger.sol:6:contract AEPProofLedger is GoalOSAccessControl {
contracts/aep/AEPProofLedger.sol:24:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPChronicleRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPChronicleRegistry.sol:6:contract AEPChronicleRegistry is GoalOSAccessControl {
contracts/aep/AEPChronicleRegistry.sol:23:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPFalsificationRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPFalsificationRegistry.sol:6:contract AEPFalsificationRegistry is GoalOSAccessControl {
contracts/aep/AEPFalsificationRegistry.sol:25:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AGIEthNamespaceRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AGIEthNamespaceRegistry.sol:6:contract AGIEthNamespaceRegistry is GoalOSAccessControl {
contracts/aep/AGIEthNamespaceRegistry.sol:12:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPRolloutRouter.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPRolloutRouter.sol:6:contract AEPRolloutRouter is GoalOSAccessControl {
contracts/aep/AEPRolloutRouter.sol:12:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/MandateEpochRegistry.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/aep/MandateEpochRegistry.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/aep/MandateEpochRegistry.sol:7:import "../access/GoalOSAccessControl.sol";
contracts/aep/MandateEpochRegistry.sol:9:contract MandateEpochRegistry is GoalOSAccessControl, ReentrancyGuard {
contracts/aep/MandateEpochRegistry.sol:10:    using SafeERC20 for IERC20;
contracts/aep/MandateEpochRegistry.sol:15:    IERC20 public immutable agialphaToken;
contracts/aep/MandateEpochRegistry.sol:27:    constructor(address admin, address agialphaToken_, address treasury_) GoalOSAccessControl(admin) {
contracts/aep/MandateEpochRegistry.sol:30:        agialphaToken = IERC20(agialphaToken_);
contracts/aep/AEPClaimBoundaryRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPClaimBoundaryRegistry.sol:6:contract AEPClaimBoundaryRegistry is GoalOSAccessControl {
contracts/aep/AEPClaimBoundaryRegistry.sol:25:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPRunCommitmentRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPRunCommitmentRegistry.sol:6:contract AEPRunCommitmentRegistry is GoalOSAccessControl {
contracts/aep/AEPRunCommitmentRegistry.sol:30:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/aep/AEPProofBundleRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/aep/AEPProofBundleRegistry.sol:6:contract AEPProofBundleRegistry is GoalOSAccessControl {
contracts/aep/AEPProofBundleRegistry.sol:11:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/access/GoalOSAccessControl.sol:4:import "@openzeppelin/contracts/access/AccessControl.sol";
contracts/access/GoalOSAccessControl.sol:7:abstract contract GoalOSAccessControl is AccessControl, Pausable {
contracts/optional/AppealRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/optional/AppealRegistry.sol:6:contract AppealRegistry is GoalOSAccessControl {
contracts/optional/AppealRegistry.sol:24:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/optional/SponsorRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/optional/SponsorRegistry.sol:6:contract SponsorRegistry is GoalOSAccessControl {
contracts/optional/SponsorRegistry.sol:11:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/optional/DisputeRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/optional/DisputeRegistry.sol:7:contract DisputeRegistry is GoalOSAccessControl {
contracts/optional/DisputeRegistry.sol:27:    constructor(address admin, address reputationRegistry_) GoalOSAccessControl(admin) {
contracts/optional/CredentialRevocationRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/optional/CredentialRevocationRegistry.sol:7:contract CredentialRevocationRegistry is GoalOSAccessControl {
contracts/optional/CredentialRevocationRegistry.sol:24:    constructor(address admin, address credentialRegistry_) GoalOSAccessControl(admin) {
contracts/optional/BuilderProfileRegistry.sol:4:import "../access/GoalOSAccessControl.sol";
contracts/optional/BuilderProfileRegistry.sol:6:contract BuilderProfileRegistry is GoalOSAccessControl {
contracts/optional/BuilderProfileRegistry.sol:11:    constructor(address admin) GoalOSAccessControl(admin) {}
contracts/vaults/CommercializationPerformanceVault.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/vaults/CommercializationPerformanceVault.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/vaults/CommercializationPerformanceVault.sol:6:import "../access/GoalOSAccessControl.sol";
contracts/vaults/CommercializationPerformanceVault.sol:8:contract CommercializationPerformanceVault is GoalOSAccessControl {
contracts/vaults/CommercializationPerformanceVault.sol:9:    using SafeERC20 for IERC20;
contracts/vaults/CommercializationPerformanceVault.sol:34:    IERC20 public immutable agialphaToken;
contracts/vaults/CommercializationPerformanceVault.sol:54:    constructor(address admin, address agialphaToken_) GoalOSAccessControl(admin) {
contracts/vaults/CommercializationPerformanceVault.sol:56:        agialphaToken = IERC20(agialphaToken_);
contracts/vaults/TokenReserveVault.sol:4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
contracts/vaults/TokenReserveVault.sol:5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contracts/vaults/TokenReserveVault.sol:6:import "../access/GoalOSAccessControl.sol";
contracts/vaults/TokenReserveVault.sol:8:contract TokenReserveVault is GoalOSAccessControl {
contracts/vaults/TokenReserveVault.sol:9:    using SafeERC20 for IERC20;
contracts/vaults/TokenReserveVault.sol:11:    IERC20 public immutable token;
contracts/vaults/TokenReserveVault.sol:17:    constructor(address admin, address token_, string memory purpose_) GoalOSAccessControl(admin) {
contracts/vaults/TokenReserveVault.sol:19:        token = IERC20(token_);

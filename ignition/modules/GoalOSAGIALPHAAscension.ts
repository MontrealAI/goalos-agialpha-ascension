import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA";

export default buildModule("GoalOSAGIALPHAAscension", (m) => {
  const agialphaToken = m.getParameter("agialphaToken", AGIALPHA);
  const treasury = m.getParameter("treasury", "0x000000000000000000000000000000000000dEaD");
  const admin = m.getAccount(0);
  const proofSeedRegistry = m.contract("ProofSeedRegistry", [admin, agialphaToken, treasury]);
  return { proofSeedRegistry };
});

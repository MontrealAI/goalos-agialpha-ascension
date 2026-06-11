import { deployGoalOSAGIALPHAAscension } from "./deploy-core";

deployGoalOSAGIALPHAAscension().catch((error) => { console.error(error); process.exitCode = 1; });

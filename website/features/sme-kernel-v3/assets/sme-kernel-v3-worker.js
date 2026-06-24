'use strict';
importScripts('sme-kernel-v3-core.js','sme-kernel-v3-adapters.js');
const Core=self.SMEKernelCore;
const Adapters=self.SMEKernelAdapters;
const DB_NAME='goalos-sme-kernel-v3';
const DB_VERSION=1;
let dbPromise=null;let storageMode='IndexedDB';
const memoryStores={identities:new Map(),missions:new Map(),events:new Map()};

function requestResult(request){return new Promise((resolve,reject)=>{request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error||new Error('IndexedDB request failed'));});}
function transactionDone(tx){return new Promise((resolve,reject)=>{tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error||new Error('IndexedDB transaction failed'));tx.onabort=()=>reject(tx.error||new Error('IndexedDB transaction aborted'));});}
function openDB(){
  if(dbPromise)return dbPromise;
  dbPromise=new Promise((resolve,reject)=>{
    let request;
    try{request=indexedDB.open(DB_NAME,DB_VERSION);}catch(error){storageMode='MEMORY_FALLBACK';resolve(null);return;}
    request.onupgradeneeded=()=>{
      const db=request.result;
      if(!db.objectStoreNames.contains('identities'))db.createObjectStore('identities',{keyPath:'role'});
      if(!db.objectStoreNames.contains('missions'))db.createObjectStore('missions',{keyPath:'missionId'});
      if(!db.objectStoreNames.contains('events')){
        const store=db.createObjectStore('events',{keyPath:'eventKey'});
        store.createIndex('missionId','missionId',{unique:false});
        store.createIndex('missionIndex',['missionId','index'],{unique:true});
      }
    };
    request.onsuccess=()=>resolve(request.result);
    request.onerror=()=>{storageMode='MEMORY_FALLBACK';resolve(null);};
    request.onblocked=()=>{storageMode='MEMORY_FALLBACK';resolve(null);};
  });
  return dbPromise;
}
async function get(store,key){const db=await openDB();if(!db)return memoryStores[store].get(key);const tx=db.transaction(store,'readonly');const done=transactionDone(tx);const value=await requestResult(tx.objectStore(store).get(key));await done;return value;}
async function put(store,value){const db=await openDB();if(!db){const key=store==='events'?value.eventKey:value.role||value.missionId;memoryStores[store].set(key,value);return value;}const tx=db.transaction(store,'readwrite');const done=transactionDone(tx);tx.objectStore(store).put(value);await done;return value;}
async function del(store,key){const db=await openDB();if(!db){memoryStores[store].delete(key);return;}const tx=db.transaction(store,'readwrite');const done=transactionDone(tx);tx.objectStore(store).delete(key);await done;}
async function all(store){const db=await openDB();if(!db)return Array.from(memoryStores[store].values());const tx=db.transaction(store,'readonly');const done=transactionDone(tx);const value=await requestResult(tx.objectStore(store).getAll());await done;return value;}
async function missionEvents(missionId){const db=await openDB();if(!db)return Array.from(memoryStores.events.values()).filter(x=>x.missionId===missionId).sort((a,b)=>a.index-b.index);const tx=db.transaction('events','readonly');const done=transactionDone(tx);const value=await requestResult(tx.objectStore('events').index('missionId').getAll(IDBKeyRange.only(missionId)));await done;return value.sort((a,b)=>a.index-b.index);}
async function deleteMissionEvents(missionId){const db=await openDB();if(!db){for(const [key,value] of memoryStores.events)if(value.missionId===missionId)memoryStores.events.delete(key);return;}const tx=db.transaction('events','readwrite');const done=transactionDone(tx);const index=tx.objectStore('events').index('missionId');const cursorRequest=index.openCursor(IDBKeyRange.only(missionId));await new Promise((resolve,reject)=>{cursorRequest.onsuccess=()=>{const cursor=cursorRequest.result;if(!cursor){resolve();return;}cursor.delete();cursor.continue();};cursorRequest.onerror=()=>reject(cursorRequest.error);});await done;}

async function getOrCreateIdentity(role){
  let record=await get('identities',role);
  if(record&&record.privateKey&&record.publicKey)return record;
  const generated=await Core.generateIdentity(role);
  record={role,algorithm:generated.algorithm,publicKeyJwk:generated.publicKeyJwk,fingerprint:generated.fingerprint,publicKey:generated.publicKey,privateKey:generated.privateKey,createdAtPolicy:'LOCAL_VAULT_FIRST_USE'};
  await put('identities',record);
  return record;
}
async function identities(){const rows=[];for(const role of Core.ROLE_IDS)rows.push(await getOrCreateIdentity(role));return rows;}
function publicIdentity(record){return {role:record.role,algorithm:record.algorithm,publicKeyJwk:record.publicKeyJwk,fingerprint:record.fingerprint,createdAtPolicy:record.createdAtPolicy};}
function deepClone(value){return JSON.parse(JSON.stringify(value));}
function terminalForIncident(incident){return ({'identity-drift':'SAFE_HOLD','evidence-gap':'DISPUTE_OPEN','budget-breach':'HUMAN_REVIEW_REQUIRED','validator-capture':'DISPUTE_OPEN'})[incident]||null;}
function stopStateForIncident(incident){return ({'identity-drift':'EXECUTION_BOUNDED','evidence-gap':'CHALLENGE_WINDOW_OPEN','budget-breach':'WORK_EXECUTED','validator-capture':'VALIDATION_COMMITTED'})[incident]||null;}
function logicalLabel(index){return `T+${String(index).padStart(4,'0')}`;}
async function missionIdFor(config){return 'mission-'+(await Core.sha256({mission:config.mission,preset:config.preset,posture:config.posture,risk:config.risk,incident:config.incident||'none'})).slice(0,16);}

async function constructContext(missionId,config){
  const context={missionId,config:deepClone(config)};
  const metaAdapter=Adapters.get('meta-agentic-local-v3');
  const nodeAdapter=Adapters.get('alpha-node-local-v3');
  const jobsAdapter=Adapters.get('agi-jobs-local-v3');
  context.adapterRegistry=Adapters.describe();
  context.metaInit=await metaAdapter.initialize(context);
  context.meta=await metaAdapter.propose(context);
  context.charter=await metaAdapter.execute(context);
  context.metaEvaluation=await metaAdapter.evaluate(context);
  context.metaEvidence=await metaAdapter.produceEvidence(context);
  context.metaEvidenceVerification=await metaAdapter.verifyEvidence(context);
  context.nodeInit=await nodeAdapter.initialize(context);
  context.node=await nodeAdapter.propose(context);
  context.execution=await nodeAdapter.execute(context);
  context.nodeEvaluation=await nodeAdapter.evaluate(context);
  context.nodeEvidence=await nodeAdapter.produceEvidence(context);
  context.nodeEvidenceVerification=await nodeAdapter.verifyEvidence(context);
  context.jobsInit=await jobsAdapter.initialize(context);
  context.market=await jobsAdapter.propose(context);
  context.settlement=await jobsAdapter.execute(context);
  context.validation=await jobsAdapter.evaluate(context);
  context.jobsEvidence=await jobsAdapter.produceEvidence(context);
  context.jobsEvidenceVerification=await jobsAdapter.verifyEvidence(context);
  return context;
}
function payloadForState(state,context,mission,reviewAction){
  const base={missionId:mission.missionId,logicalClock:mission.nextIndex,state,authority:'NONE_GRANTED',externalActions:0};
  switch(state){
    case 'MISSION_COMMITTED':return {...base,mission:context.config.mission,preset:context.config.preset,posture:context.config.posture,risk:context.config.risk,incident:context.config.incident||'none',deliverables:['bounded institution charter','node execution receipt','evidence docket','validation record','settlement intent','human review certificate'],forbiddenActions:['external execution','wallet connection','token movement','factual certification','automatic memory promotion']};
    case 'INSTITUTION_PROPOSED':return {...base,...context.meta};
    case 'INSTITUTION_CHARTERED':return {...base,charter:context.charter,evaluation:context.metaEvaluation,evidence:context.metaEvidence,verification:context.metaEvidenceVerification};
    case 'NODE_ADMITTED':return {...base,node:context.node,adapter:context.nodeInit};
    case 'EXECUTION_BOUNDED':return {...base,nodeId:context.node.nodeId,resourceEnvelope:{computeUnits:42,energyCeiling:0.90,networkRequests:0,walletConnections:0,externalActions:0},primaryRoute:context.node.primaryRoute.map(x=>x.id),shadowRoute:context.node.shadowRoute.map(x=>x.id),stopConditions:context.charter.stopConditions};
    case 'WORK_EXECUTED':return {...base,receipt:context.execution,evaluation:context.nodeEvaluation};
    case 'EVIDENCE_SEALED':return {...base,docket:context.nodeEvidence,verification:context.nodeEvidenceVerification,evidenceStatus:['HASHED','SIGNED'],externallyAttested:false,factualCorrectness:'NOT_CERTIFIED'};
    case 'MARKET_CONVENED':return {...base,market:context.market,adapter:context.jobsInit};
    case 'VALIDATION_COMMITTED':return {...base,commitments:context.validation.opinions.map(x=>({id:x.id,commitment:`commit-${x.id}-${mission.missionId}`})),quorumTarget:context.validation.opinions.length};
    case 'VALIDATION_REVEALED':return {...base,validation:context.validation,evidence:context.jobsEvidence,verification:context.jobsEvidenceVerification};
    case 'CHALLENGE_WINDOW_OPEN':return {...base,challengeRights:['evidence gap','identity drift','resource breach','validator correlation','goal drift'],incident:context.config.incident||'none',dissent:context.validation.opinions.filter(x=>x.verdict==='DISSENT')};
    case 'SETTLEMENT_INTENT_PREPARED':return {...base,settlement:context.settlement,condition:'SIGNED_HUMAN_REVIEW_CERTIFICATE_REQUIRED',liveTokenMovement:false,settlementAuthorized:false};
    case 'AWAITING_HUMAN_REVIEW':return {...base,reviewPacket:{institution:context.meta.selected,node:context.node.nodeId,market:context.market.marketId,validation:context.validation.summary,evidenceCommitments:[context.metaEvidence.commitment,context.nodeEvidence.commitment,context.jobsEvidence.commitment]},availableActions:['APPROVED_FOR_DELIBERATION','REVISION_REQUESTED','DISPUTE_OPEN','REJECTED_SAFE_HOLD']};
    case 'HUMAN_REVIEW_RECORDED':return {...base,certificate:reviewAction};
    case 'MEMORY_DISPOSITION_RECORDED':return {...base,memory:{id:`memory-${mission.missionId.slice(-12)}`,status:reviewAction.memoryDisposition,revocable:true,expiresAtPolicy:'T+10000',automaticPromotion:false,sourceReviewAction:reviewAction.action}};
    case 'COMPLETE':return {...base,finalDisposition:reviewAction.action,terminalState:reviewAction.terminalState,externalAuthority:'NONE_GRANTED',settlementAuthorized:false,memoryPromoted:false};
    default:throw new Error('No payload builder for '+state);
  }
}
function authorityScopeFor(state){return ({MISSION_COMMITTED:'MISSION_DECLARATION',INSTITUTION_PROPOSED:'INSTITUTION_PROPOSAL',INSTITUTION_CHARTERED:'INSTITUTION_CHARTER',NODE_ADMITTED:'NODE_ADMISSION',EXECUTION_BOUNDED:'RESOURCE_ENVELOPE',WORK_EXECUTED:'BOUNDED_EXECUTION',EVIDENCE_SEALED:'EVIDENCE_SEAL',MARKET_CONVENED:'MARKET_CONVENING',VALIDATION_COMMITTED:'VALIDATION_COMMITMENT',VALIDATION_REVEALED:'VALIDATION_OPINION',CHALLENGE_WINDOW_OPEN:'CHALLENGE_RIGHTS',SETTLEMENT_INTENT_PREPARED:'SETTLEMENT_INTENT',AWAITING_HUMAN_REVIEW:'REVIEW_PACKET',HUMAN_REVIEW_RECORDED:'HUMAN_REVIEW',MEMORY_DISPOSITION_RECORDED:'MEMORY_DISPOSITION',COMPLETE:'FINAL_RECORD'})[state]||'BOUNDED_RECORD';}
async function appendTransition(mission,context,toState,identity,terminalState,reviewAction){
  const fromState=mission.state;Core.assertStateTransition(fromState,toState);
  const contract=Core.contractFor(toState);
  if(identity.role!==contract.issuer)throw new Error(`Transition ${toState} requires ${contract.issuer}, received ${identity.role}`);
  const payload=payloadForState(toState,context,mission,reviewAction);
  const unsigned=await Core.createUnsignedEnvelope({envelopeType:contract.type,missionId:mission.missionId,issuer:identity.role,logicalTime:mission.nextIndex,previousCommitment:mission.chainHead,payload,authorityScope:authorityScopeFor(toState)});
  const envelope=await Core.signEnvelope(unsigned,identity);
  const verification=await Core.verifyEnvelope(envelope);if(!verification.ok)throw new Error('Envelope verification failed: '+verification.reason);
  const event=await Core.createEvent({index:mission.nextIndex,fromState,toState,envelope,previousEventCommitment:mission.chainHead,terminalState:terminalState||null});
  await put('events',{...event,eventKey:`${mission.missionId}:${String(event.index).padStart(4,'0')}`,missionId:mission.missionId,logicalLabel:logicalLabel(event.index)});
  mission.state=toState;mission.chainHead=event.eventCommitment;mission.nextIndex+=1;if(terminalState)mission.terminalState=terminalState;
  await put('missions',mission);
  self.postMessage({type:'PROGRESS',missionId:mission.missionId,state:toState,index:event.index,terminalState:mission.terminalState,event:deepClone(event)});
  return event;
}
async function runMission(config,options={}){
  const missionId=await missionIdFor(config);
  if(options.reset===true){await deleteMissionEvents(missionId);await del('missions',missionId);}
  let mission=await get('missions',missionId);
  if(mission&&mission.state!=='DRAFT')return loadMission(missionId);
  const roleIdentities=Object.fromEntries((await identities()).map(x=>[x.role,x]));
  mission={missionId,schema:'goalos.sme.kernel.v3.mission',protocol:Core.PROTOCOL,config:deepClone(config),state:'DRAFT',terminalState:'RUNNING',chainHead:Core.ZERO,nextIndex:1,createdAtPolicy:'LOGICAL_CLOCK',adapterIds:['meta-agentic-local-v3','alpha-node-local-v3','agi-jobs-local-v3'],review:null};
  await put('missions',mission);
  const context=await constructContext(missionId,config);
  const incident=config.incident||'none';const stopState=stopStateForIncident(incident);const incidentTerminal=terminalForIncident(incident);
  const machineStates=Core.STATES.slice(1,14);
  for(const toState of machineStates){
    const issuer=Core.contractFor(toState).issuer;
    await appendTransition(mission,context,toState,roleIdentities[issuer],stopState===toState?incidentTerminal:null,null);
    if(stopState===toState){mission.contextSummary={institution:context.meta.selected,node:context.node.nodeId,market:context.market.marketId};await put('missions',mission);return loadMission(missionId);}
  }
  mission.contextSummary={institution:context.meta.selected,node:context.node.nodeId,market:context.market.marketId,validation:context.validation.summary};
  mission.terminalState='AWAITING_HUMAN_REVIEW';
  await put('missions',mission);
  return loadMission(missionId);
}
function reviewTerminal(action){return ({APPROVED_FOR_DELIBERATION:'HUMAN_SETTLEMENT_REVIEW',REVISION_REQUESTED:'HUMAN_REVIEW_REQUIRED',DISPUTE_OPEN:'DISPUTE_OPEN',REJECTED_SAFE_HOLD:'SAFE_HOLD'})[action];}
function memoryDisposition(action){return ({APPROVED_FOR_DELIBERATION:'HUMAN_PROMOTION_REQUIRED',REVISION_REQUESTED:'WITHHELD_PENDING_REVISION',DISPUTE_OPEN:'WITHHELD_DURING_DISPUTE',REJECTED_SAFE_HOLD:'REJECTED_NOT_PROMOTED'})[action];}
async function applyHumanReview(missionId,review){
  const mission=await get('missions',missionId);if(!mission)throw new Error('Mission not found');if(mission.state!=='AWAITING_HUMAN_REVIEW')throw new Error('Mission is not awaiting human review');
  const identitiesByRole=Object.fromEntries((await identities()).map(x=>[x.role,x]));
  const events=await missionEvents(missionId);const context={missionId,config:mission.config,meta:{selected:mission.contextSummary.institution},node:{nodeId:mission.contextSummary.node},market:{marketId:mission.contextSummary.market},validation:{summary:mission.contextSummary.validation}};
  const action={action:review.action,scope:review.scope||'DELIBERATION_ONLY',expiresAtPolicy:review.expiresAtPolicy||'T+10000',unresolvedRisks:Array.isArray(review.unresolvedRisks)?review.unresolvedRisks:['Independent external evidence remains pending.'],notes:review.notes||'',terminalState:reviewTerminal(review.action),memoryDisposition:memoryDisposition(review.action),reviewedChainHead:mission.chainHead,reviewedEventCount:events.length,authorityGranted:false,settlementAuthorized:false,memoryPromoted:false};
  await appendTransition(mission,context,'HUMAN_REVIEW_RECORDED',identitiesByRole.HUMAN_REVIEWER,action.terminalState,action);
  await appendTransition(mission,context,'MEMORY_DISPOSITION_RECORDED',identitiesByRole.HUMAN_REVIEWER,action.terminalState,action);
  await appendTransition(mission,context,'COMPLETE',identitiesByRole.HUMAN_REVIEWER,action.terminalState,action);
  mission.review=action;mission.terminalState=action.terminalState;await put('missions',mission);
  return loadMission(missionId);
}
async function loadMission(missionId){const mission=await get('missions',missionId);if(!mission)return null;const events=await missionEvents(missionId);return {mission:deepClone(mission),events:events.map(deepClone),identities:(await identities()).map(publicIdentity)};}
async function listMissions(){return (await all('missions')).sort((a,b)=>a.missionId.localeCompare(b.missionId)).map(deepClone);}
async function resetMission(missionId){await deleteMissionEvents(missionId);await del('missions',missionId);return {missionId,reset:true};}
async function exportMission(missionId){const loaded=await loadMission(missionId);if(!loaded)throw new Error('Mission not found');const bundle={schema:'goalos.sme.kernel.v3.mission_bundle',protocol:Core.PROTOCOL,exportedAtPolicy:'LOGICAL_CLOCK',mission:loaded.mission,identities:loaded.identities,events:loaded.events,verificationPolicy:{signatureVerification:'Ed25519',stateReplay:'STRICT',chainVerification:'PREDECESSOR_HASH',externalAuthority:'NONE_GRANTED'}};bundle.bundleRoot=await Core.computeBundleRoot(bundle);return bundle;}
async function verifyImportedBundle(bundle){return Core.verifyBundle(bundle);}
async function clearAll(){const db=await openDB();if(!db){memoryStores.missions.clear();memoryStores.events.clear();return {cleared:true,identitiesPreserved:true,storage:storageMode};}for(const store of ['missions','events']){const tx=db.transaction(store,'readwrite');const done=transactionDone(tx);tx.objectStore(store).clear();await done;}return {cleared:true,identitiesPreserved:true,storage:storageMode};}
async function status(){await openDB();return {protocol:Core.PROTOCOL,schemaVersion:Core.SCHEMA_VERSION,storage:storageMode,signatureAlgorithm:'Ed25519',roles:(await identities()).map(publicIdentity),adapters:Adapters.describe(),missions:await listMissions(),worker:true};}

self.onmessage=async event=>{
  const message=event.data||{};const requestId=message.requestId;
  try{
    let result;
    switch(message.type){
      case 'STATUS':result=await status();break;
      case 'RUN_MISSION':result=await runMission(message.config||{},message.options||{});break;
      case 'APPLY_REVIEW':result=await applyHumanReview(message.missionId,message.review||{});break;
      case 'LOAD_MISSION':result=await loadMission(message.missionId);break;
      case 'LIST_MISSIONS':result=await listMissions();break;
      case 'RESET_MISSION':result=await resetMission(message.missionId);break;
      case 'CLEAR_ALL':result=await clearAll();break;
      case 'EXPORT_MISSION':result=await exportMission(message.missionId);break;
      case 'VERIFY_BUNDLE':result=await verifyImportedBundle(message.bundle);break;
      default:throw new Error('Unknown worker message '+message.type);
    }
    self.postMessage({type:'RESPONSE',requestId,ok:true,result});
  }catch(error){self.postMessage({type:'RESPONSE',requestId,ok:false,error:{message:error.message,stack:error.stack||''}});}
};

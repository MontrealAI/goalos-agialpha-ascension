(function(global){
  'use strict';
  const PROTOCOL='goalos.sme.kernel.v3';
  const SCHEMA_VERSION='3.0.0';
  const ZERO='0'.repeat(64);
  const STATES=[
    'DRAFT','MISSION_COMMITTED','INSTITUTION_PROPOSED','INSTITUTION_CHARTERED','NODE_ADMITTED','EXECUTION_BOUNDED','WORK_EXECUTED','EVIDENCE_SEALED','MARKET_CONVENED','VALIDATION_COMMITTED','VALIDATION_REVEALED','CHALLENGE_WINDOW_OPEN','SETTLEMENT_INTENT_PREPARED','AWAITING_HUMAN_REVIEW','HUMAN_REVIEW_RECORDED','MEMORY_DISPOSITION_RECORDED','COMPLETE'
  ];
  const TRANSITIONS={};
  for(let i=0;i<STATES.length-1;i++) TRANSITIONS[STATES[i]]=STATES[i+1];
  const STATE_CONTRACT={
    MISSION_COMMITTED:{issuer:'HUMAN_REVIEWER',type:'MissionCommitment'},
    INSTITUTION_PROPOSED:{issuer:'META_ARCHITECT',type:'InstitutionProposal'},
    INSTITUTION_CHARTERED:{issuer:'META_ARCHITECT',type:'InstitutionCharter'},
    NODE_ADMITTED:{issuer:'NODE_OPERATOR',type:'NodeAdmission'},
    EXECUTION_BOUNDED:{issuer:'NODE_OPERATOR',type:'NodeAdmission'},
    WORK_EXECUTED:{issuer:'NODE_OPERATOR',type:'NodeExecutionReceipt'},
    EVIDENCE_SEALED:{issuer:'NODE_OPERATOR',type:'EvidenceDocket'},
    MARKET_CONVENED:{issuer:'MARKET_STEWARD',type:'SettlementIntent'},
    VALIDATION_COMMITTED:{issuer:'INDEPENDENT_VERIFIER',type:'ValidationOpinion'},
    VALIDATION_REVEALED:{issuer:'INDEPENDENT_VERIFIER',type:'ValidationOpinion'},
    CHALLENGE_WINDOW_OPEN:{issuer:'INDEPENDENT_VERIFIER',type:'ChallengeRecord'},
    SETTLEMENT_INTENT_PREPARED:{issuer:'MARKET_STEWARD',type:'SettlementIntent'},
    AWAITING_HUMAN_REVIEW:{issuer:'INDEPENDENT_VERIFIER',type:'ChallengeRecord'},
    HUMAN_REVIEW_RECORDED:{issuer:'HUMAN_REVIEWER',type:'HumanReviewCertificate'},
    MEMORY_DISPOSITION_RECORDED:{issuer:'HUMAN_REVIEWER',type:'HumanReviewCertificate'},
    COMPLETE:{issuer:'HUMAN_REVIEWER',type:'HumanReviewCertificate'}
  };
  const ROLE_IDS=['META_ARCHITECT','NODE_OPERATOR','MARKET_STEWARD','INDEPENDENT_VERIFIER','HUMAN_REVIEWER'];
  const encoder=new TextEncoder();
  const decoder=new TextDecoder();

  function canonicalize(value){
    if(value===null||typeof value!=='object') return JSON.stringify(value);
    if(Array.isArray(value)) return '['+value.map(canonicalize).join(',')+']';
    return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonicalize(value[k])).join(',')+'}';
  }
  function bytesToHex(bytes){return Array.from(new Uint8Array(bytes),b=>b.toString(16).padStart(2,'0')).join('');}
  function hexToBytes(hex){if(!/^[a-f0-9]*$/i.test(hex)||hex.length%2) throw new Error('Invalid hex');const out=new Uint8Array(hex.length/2);for(let i=0;i<out.length;i++)out[i]=parseInt(hex.slice(i*2,i*2+2),16);return out;}
  function bytesToBase64(bytes){let s='';for(const b of new Uint8Array(bytes))s+=String.fromCharCode(b);return btoa(s);}
  function base64ToBytes(value){const s=atob(value);const out=new Uint8Array(s.length);for(let i=0;i<s.length;i++)out[i]=s.charCodeAt(i);return out;}
  function softwareSha256(text){
    const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];const bytes=encoder.encode(String(text));const length=bytes.length;const paddedLength=Math.ceil((length+9)/64)*64;const message=new Uint8Array(paddedLength);message.set(bytes);message[length]=0x80;const view=new DataView(message.buffer);const bits=length*8;view.setUint32(paddedLength-8,Math.floor(bits/0x100000000),false);view.setUint32(paddedLength-4,bits>>>0,false);const w=new Uint32Array(64);const rotr=(x,n)=>(x>>>n)|(x<<(32-n));
    for(let offset=0;offset<paddedLength;offset+=64){for(let i=0;i<16;i++)w[i]=view.getUint32(offset+i*4,false);for(let i=16;i<64;i++){const s0=rotr(w[i-15],7)^rotr(w[i-15],18)^(w[i-15]>>>3);const s1=rotr(w[i-2],17)^rotr(w[i-2],19)^(w[i-2]>>>10);w[i]=(w[i-16]+s0+w[i-7]+s1)>>>0;}let[a,b,c,d,e,f,g,h]=H;for(let i=0;i<64;i++){const S1=rotr(e,6)^rotr(e,11)^rotr(e,25);const ch=(e&f)^(~e&g);const t1=(h+S1+ch+K[i]+w[i])>>>0;const S0=rotr(a,2)^rotr(a,13)^rotr(a,22);const maj=(a&b)^(a&c)^(b&c);const t2=(S0+maj)>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}H[0]=(H[0]+a)>>>0;H[1]=(H[1]+b)>>>0;H[2]=(H[2]+c)>>>0;H[3]=(H[3]+d)>>>0;H[4]=(H[4]+e)>>>0;H[5]=(H[5]+f)>>>0;H[6]=(H[6]+g)>>>0;H[7]=(H[7]+h)>>>0;}return H.map(x=>x.toString(16).padStart(8,'0')).join('');
  }
  async function sha256(value){const source=typeof value==='string'?value:canonicalize(value);if(global.crypto&&global.crypto.subtle){const bytes=value instanceof Uint8Array?value:encoder.encode(source);return bytesToHex(await global.crypto.subtle.digest('SHA-256',bytes));}if(global.__KV3_QA_FALLBACK__)return softwareSha256(source);throw new Error('Secure WebCrypto context required');}
  async function fingerprintJwk(jwk){return sha256(jwk);}
  async function generateIdentity(role){
    if((!global.crypto||!global.crypto.subtle)&&global.__KV3_QA_FALLBACK__){const secret=await sha256('goalos-kv3-qa-role:'+role);const publicKeyJwk={kty:'OKP',crv:'Ed25519',x:secret,qa:true};return {role,algorithm:'Ed25519',publicKeyJwk,fingerprint:await fingerprintJwk(publicKeyJwk),publicKey:{qa:true,secret},privateKey:{qa:true,secret}};}
    let pair;try{pair=await global.crypto.subtle.generateKey({name:'Ed25519'},true,['sign','verify']);}catch(error){throw new Error('Ed25519 is required for Kernel v3 and is unavailable in this browser: '+error.message);}
    const publicKeyJwk=await global.crypto.subtle.exportKey('jwk',pair.publicKey);return {role,algorithm:'Ed25519',publicKeyJwk,fingerprint:await fingerprintJwk(publicKeyJwk),publicKey:pair.publicKey,privateKey:pair.privateKey};
  }
  async function importPublicKey(jwk){if(jwk&&jwk.qa&&global.__KV3_QA_FALLBACK__)return {qa:true,secret:jwk.x};return global.crypto.subtle.importKey('jwk',jwk,{name:'Ed25519'},true,['verify']);}
  async function signValue(privateKey,value){if(privateKey&&privateKey.qa&&global.__KV3_QA_FALLBACK__)return sha256({secret:privateKey.secret,value});return bytesToBase64(await global.crypto.subtle.sign({name:'Ed25519'},privateKey,encoder.encode(canonicalize(value))));}
  async function verifyValue(publicKeyOrJwk,signature,value){if(global.__KV3_QA_FALLBACK__&&publicKeyOrJwk&&publicKeyOrJwk.qa){return signature===await sha256({secret:publicKeyOrJwk.x||publicKeyOrJwk.secret,value});}const isCryptoKey=(typeof CryptoKey!=='undefined'&&publicKeyOrJwk instanceof CryptoKey)||(publicKeyOrJwk&&publicKeyOrJwk.type==='public'&&publicKeyOrJwk.algorithm);const key=isCryptoKey?publicKeyOrJwk:await importPublicKey(publicKeyOrJwk);if(key&&key.qa&&global.__KV3_QA_FALLBACK__)return signature===await sha256({secret:key.secret,value});return global.crypto.subtle.verify({name:'Ed25519'},key,base64ToBytes(signature),encoder.encode(canonicalize(value)));}
  function assertStateTransition(fromState,toState){if(TRANSITIONS[fromState]!==toState)throw new Error(`Invalid constitutional transition ${fromState} → ${toState}`);}
  function contractFor(toState){const contract=STATE_CONTRACT[toState];if(!contract)throw new Error('Unknown target state '+toState);return contract;}
  async function createUnsignedEnvelope({envelopeType,missionId,issuer,logicalTime,previousCommitment,payload,authorityScope}){
    const payloadCommitment=await sha256(payload);
    const body={protocol:PROTOCOL,schemaVersion:SCHEMA_VERSION,envelopeType,missionId,issuer,logicalTime,previousCommitment,payload,payloadCommitment,authority:{scope:authorityScope,externalAuthority:'NONE_GRANTED',externalActions:0}};
    const envelopeId=await sha256(body);
    return {...body,envelopeId};
  }
  function signingProjection(envelope){const {signature,...unsigned}=envelope;return unsigned;}
  async function signEnvelope(unsignedEnvelope,identity){
    if(identity.role!==unsignedEnvelope.issuer) throw new Error(`Identity ${identity.role} cannot issue ${unsignedEnvelope.issuer} envelope`);
    const value=await signValue(identity.privateKey,unsignedEnvelope);
    return {...unsignedEnvelope,signature:{algorithm:'Ed25519',publicKeyJwk:identity.publicKeyJwk,value,status:'VERIFIED'}};
  }
  async function verifyEnvelope(envelope){
    if(envelope.protocol!==PROTOCOL||envelope.schemaVersion!==SCHEMA_VERSION) return {ok:false,reason:'protocol-version'};
    if(await sha256(envelope.payload)!==envelope.payloadCommitment) return {ok:false,reason:'payload-commitment'};
    const unsigned=signingProjection(envelope);
    const {envelopeId,...identityProjection}=unsigned;
    if(await sha256(identityProjection)!==envelope.envelopeId) return {ok:false,reason:'envelope-id'};
    if(!envelope.signature||envelope.signature.algorithm!=='Ed25519') return {ok:false,reason:'signature-algorithm'};
    if(!(await verifyValue(envelope.signature.publicKeyJwk,envelope.signature.value,unsigned))) return {ok:false,reason:'signature-invalid'};
    return {ok:true,reason:'verified'};
  }
  async function createEvent({index,fromState,toState,envelope,previousEventCommitment,terminalState}){
    assertStateTransition(fromState,toState);
    const contract=contractFor(toState);
    if(contract.issuer!=='SYSTEM'&&envelope.issuer!==contract.issuer) throw new Error(`Transition ${toState} requires ${contract.issuer}`);
    if(contract.issuer!=='SYSTEM'&&envelope.envelopeType!==contract.type) throw new Error(`Transition ${toState} requires ${contract.type}`);
    const body={protocol:PROTOCOL,index,fromState,toState,envelope,previousEventCommitment,terminalState:terminalState||null};
    const eventId=await sha256({missionId:envelope.missionId,index,toState,envelopeId:envelope.envelopeId});
    const eventCommitment=await sha256({...body,eventId});
    return {...body,eventId,eventCommitment};
  }
  async function computeBundleRoot(bundle){return sha256({mission:bundle.mission,identities:bundle.identities,events:bundle.events.map(e=>({eventId:e.eventId,eventCommitment:e.eventCommitment})),protocol:bundle.protocol});}
  async function verifyBundle(bundle){
    const errors=[];const eventResults=[];
    if(!bundle||bundle.schema!=='goalos.sme.kernel.v3.mission_bundle'||bundle.protocol!==PROTOCOL)errors.push('bundle-schema');
    if(!Array.isArray(bundle?.events)||bundle.events.length<1)errors.push('events-missing');
    let state='DRAFT',previous=ZERO;
    for(let i=0;i<(bundle?.events||[]).length;i++){
      const event=bundle.events[i];let ok=true;const reasons=[];
      if(event.index!==i+1){ok=false;reasons.push('index');}
      if(event.fromState!==state){ok=false;reasons.push('from-state');}
      if(TRANSITIONS[state]!==event.toState){ok=false;reasons.push('transition');}
      if(event.previousEventCommitment!==previous){ok=false;reasons.push('previous-event');}
      const envelopeResult=await verifyEnvelope(event.envelope);
      if(!envelopeResult.ok){ok=false;reasons.push(envelopeResult.reason);}
      try{
        const rebuilt=await createEvent({index:event.index,fromState:event.fromState,toState:event.toState,envelope:event.envelope,previousEventCommitment:event.previousEventCommitment,terminalState:event.terminalState});
        if(rebuilt.eventId!==event.eventId){ok=false;reasons.push('event-id');}
        if(rebuilt.eventCommitment!==event.eventCommitment){ok=false;reasons.push('event-commitment');}
      }catch(error){ok=false;reasons.push('event-contract');}
      eventResults.push({index:i+1,toState:event.toState,ok,reasons});
      if(!ok)errors.push(`event-${i+1}:${reasons.join(',')}`);
      state=event.toState;previous=event.eventCommitment;
    }
    if(bundle?.mission?.state!==state)errors.push('mission-state');
    if(bundle?.bundleRoot&&await computeBundleRoot(bundle)!==bundle.bundleRoot)errors.push('bundle-root');
    const fingerprints=new Map((bundle?.identities||[]).map(x=>[x.role,x.fingerprint]));
    for(const event of bundle?.events||[]){
      const role=event.envelope.issuer;if(role==='SYSTEM')continue;
      const expected=fingerprints.get(role);const actual=await fingerprintJwk(event.envelope.signature.publicKeyJwk);
      if(!expected||expected!==actual)errors.push(`identity:${role}`);
    }
    return {ok:errors.length===0,errors,eventResults,finalState:state,chainHead:previous,bundleRoot:bundle?.bundleRoot||null};
  }
  global.SMEKernelCore={PROTOCOL,SCHEMA_VERSION,ZERO,STATES,TRANSITIONS,STATE_CONTRACT,ROLE_IDS,canonicalize,sha256,bytesToHex,hexToBytes,bytesToBase64,base64ToBytes,fingerprintJwk,generateIdentity,importPublicKey,signValue,verifyValue,assertStateTransition,contractFor,createUnsignedEnvelope,signEnvelope,verifyEnvelope,createEvent,computeBundleRoot,verifyBundle};
})(typeof self!=='undefined'?self:window);

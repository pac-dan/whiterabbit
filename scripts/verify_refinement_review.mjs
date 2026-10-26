// Read the external controller's receipt. Never create an independent verdict here.
import fs from 'node:fs/promises';
import path from 'node:path';
import {run,save} from './refinement_browser.mjs';
import {candidateFingerprint} from 'file:///C:/Users/Dan/Documents/ChatGPT/maestro/src/review-loop.mjs';
const config=JSON.parse(await fs.readFile(path.join(run,'review-contract.json'),'utf8'));
let latest=null,error=null,verdict=null,current=null;
try{latest=JSON.parse(await fs.readFile(path.join(config.runDir,'latest.json'),'utf8'));if(latest.verdict)verdict=await fs.readFile(latest.verdict,'utf8');current=await candidateFingerprint(config.projectDir,config.ledgerDir);}catch(e){error=e.message;}
const assessed=!!verdict&&['PASS','FAIL','BLOCKED'].includes(latest.reviewResult)&&latest.candidate===current&&path.resolve(latest.ledgerDir)===path.resolve(run);
const report={date:new Date().toISOString(),controller:config.runDir,latest,error,current,verdict,pass:assessed,
 note:'This verifies that an independent assessment exists for the candidate, not that its result is PASS. Publishing this receipt changes the ledger fingerprint; the reviewed hash above is preserved.'};
await save('independent-review.json',report);console.log(JSON.stringify(report,null,2));process.exitCode=assessed?0:1;

// Dépendance hors dépôt : npm install --prefix /chemin gltf-validator@2.0.0-dev.3.10
// MRSC_VALIDATOR_NODE_MODULES=/chemin/node_modules node outils/valider-eva-glb.cjs
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
if(process.env.MRSC_VALIDATOR_NODE_MODULES){process.env.NODE_PATH=process.env.MRSC_VALIDATOR_NODE_MODULES;require('node:module').Module._initPaths();}
const validator=require('gltf-validator');
(async()=>{const file=path.join(__dirname,'../assets/models/eva/eva-etude-01.glb'),data=fs.readFileSync(file);const report=await validator.validateBytes(new Uint8Array(data),{uri:'eva-etude-01.glb',maxIssues:500});const out={statut:'Contrôle structurel glTF uniquement, pas validation esthétique, de mouvement naturel ou de compatibilité universelle.',sha256:crypto.createHash('sha256').update(data).digest('hex'),octets:data.length,validatorVersion:report.validatorVersion,issues:report.issues};if(process.env.MRSC_EVA_VALIDATION)fs.writeFileSync(process.env.MRSC_EVA_VALIDATION,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));process.exitCode=report.issues.numErrors||report.issues.numWarnings?1:0;})().catch(e=>{console.error(e);process.exitCode=1;});

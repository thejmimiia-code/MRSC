// Géométries, textures et mouvements originaux ; aucun modèle humain externe.
// Exécuté dans un navigateur par construire-eva-glb.cjs (canvas pour les textures).
import * as T from '../assets/vendor/three/three.module.min.mjs';
import { mergeGeometries, mergeVertices } from '../assets/vendor/three/addons/BufferGeometryUtils.mjs';
import { GLTFExporter } from './vendor/three/GLTFExporter.mjs';

export async function construireEva() {
 const root=new T.Group();root.name='EVA_Etude_01';
 root.userData={statut:'Prototype procédural stylisé à valider, non reproduction fidèle de la planche',unite:'metre',auteur:'M.R.S.C — géométries et textures originales générées par outils/modeliser-eva.mjs'};
 const bones=[], byName={};
 function bone(name,parent,x,y,z=0){const b=new T.Bone();b.name=name;b.position.set(x,y,z);(parent||root).add(b);bones.push(b);byName[name]=b;return b;}
 const hips=bone('Hips',null,0,.94),spine=bone('Spine',hips,0,.15),chest=bone('Chest',spine,0,.20),neck=bone('Neck',chest,0,.17),head=bone('Head',neck,0,.14);
 const joints={};
 for(const [side,s] of [['Left',1],['Right',-1]]){
  const shoulder=bone(side+'Shoulder',chest,s*.20,.065),arm=bone(side+'Arm',shoulder,s*.045,-.02),fore=bone(side+'ForeArm',arm,s*.075,-.225),hand=bone(side+'Hand',fore,s*.045,-.205);
  for(let i=0;i<5;i++){const f=bone(side+'Finger'+i,hand,s*(i===0?.029:((i-2.5)*.011)),-.045,i===0?.025:.015);bone(side+'FingerTip'+i,f,0,-(i===0?.025:.035),0);}
  const thigh=bone(side+'UpLeg',hips,s*.11,-.015),shin=bone(side+'Leg',thigh,0,-.405),foot=bone(side+'Foot',shin,0,-.415);bone(side+'Toe',foot,0,-.055,.11);
  joints[side]={shoulder,arm,fore,hand,thigh,shin,foot,s};
 }
 root.updateMatrixWorld(true);const skeleton=new T.Skeleton(bones);
 function tex(name,base,kind){const c=document.createElement('canvas');c.width=c.height=512;const x=c.getContext('2d');x.fillStyle=base;x.fillRect(0,0,512,512);let seed=8291;const rnd=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};for(let i=0;i<22000;i++){const v=rnd();x.fillStyle=v>.5?'rgba(255,255,255,.055)':'rgba(0,0,0,.055)';const a=rnd()*512,b=rnd()*512;x.fillRect(a,b,kind==='denim'?5:2,1);}if(kind==='denim'){x.strokeStyle='#bbae86';x.lineWidth=2;for(const a of [18,24,488,494]){x.setLineDash([5,4]);x.beginPath();x.moveTo(a,0);x.lineTo(a,512);x.stroke();}}const t=new T.CanvasTexture(c);t.name=name;t.colorSpace=T.SRGBColorSpace;return t;}
 const skin=new T.MeshStandardMaterial({color:0xffffff,map:tex('Peau_originale','#bd8261','skin'),roughness:.7});skin.name='Peau_satin';
 const denim=new T.MeshStandardMaterial({color:0xffffff,map:tex('Denim_original','#354f66','denim'),roughness:.95});denim.name='Jean_indigo';
 const shirt=new T.MeshStandardMaterial({color:0xffffff,map:tex('Coton_original','#292521','cotton'),roughness:.95});shirt.name='Tshirt_anthracite';
 const hair=new T.MeshStandardMaterial({color:0x352018,roughness:.5});hair.name='Cheveux_chataigne';const hairLight=hair.clone();hairLight.name='Reflets_chataigne';hairLight.color.set(0x583423);
 const leather=new T.MeshStandardMaterial({color:0x53331f,roughness:.65});leather.name='Cuir_brun';const copper=new T.MeshStandardMaterial({color:0xb77750,metalness:.75,roughness:.32});copper.name='Cuivre';
 const cream=new T.MeshStandardMaterial({color:0xf4e6ce,roughness:.65});cream.name='Creme';const white=new T.MeshStandardMaterial({color:0xf1e5d3,roughness:.4});const iris=new T.MeshStandardMaterial({color:0x5a3924,roughness:.4});const pupil=new T.MeshStandardMaterial({color:0x100e0c,roughness:.35});const lip=new T.MeshStandardMaterial({color:0x9b6355,roughness:.7});
 function skinned(geometry,mat,name,weights){if(!mat.map)geometry.deleteAttribute('uv');const idx=[],val=[];const pos=geometry.attributes.position;for(let i=0;i<pos.count;i++){const w=weights(new T.Vector3().fromBufferAttribute(pos,i));idx.push(...w.map(a=>bones.indexOf(a[0])),...Array(4-w.length).fill(0));val.push(...w.map(a=>a[1]),...Array(4-w.length).fill(0));}geometry.setAttribute('skinIndex',new T.Uint16BufferAttribute(idx,4));geometry.setAttribute('skinWeight',new T.Float32BufferAttribute(val,4));const m=new T.SkinnedMesh(geometry,mat);m.name=name;m.castShadow=m.receiveShadow=true;root.add(m);m.bind(skeleton);return m;}
 const rigid=b=>()=>[[b,1]];
 function ellipsoid(name,mat,b,x,y,z,sx,sy,sz){const g=new T.SphereGeometry(1,24,16);g.scale(sx,sy,sz);g.translate(x,y,z);return skinned(g,mat,name,rigid(b));}
 function tube(name,pts,r,mat,b){const curve=new T.CatmullRomCurve3(pts.map(a=>new T.Vector3(...a)));return skinned(new T.TubeGeometry(curve,Math.max(10,pts.length*4),r,7,false),mat,name,rigid(b));}
 // Surface à anneaux, en coordonnées de repos mondiales ; poids interpolés aux articulations.
 function rings(name,rows,mat,weight,segments=32){const p=[],uv=[],index=[];rows.forEach(([y,cx,cz,rx,rz],j)=>{for(let i=0;i<=segments;i++){const a=i/segments*Math.PI*2;p.push(cx+Math.cos(a)*rx,y,cz+Math.sin(a)*rz);uv.push(i/segments,j/(rows.length-1));}});for(let j=0;j<rows.length-1;j++)for(let i=0;i<segments;i++){const a=j*(segments+1)+i,b=a+segments+1;if(rows[1][0]>rows[0][0])index.push(a,b,a+1,b,b+1,a+1);else index.push(a,a+1,b,b,a+1,b+1);}const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.setIndex(index);g.computeVertexNormals();return skinned(g,mat,name,weight);}
 function blendY(y,low,high,split,width=.09){const f=T.MathUtils.clamp((y-split)/width+.5,0,1);return f===0?[[low,1]]:f===1?[[high,1]]:[[low,1-f],[high,f]];}
 const torsoW=p=>p.y>1.2?blendY(p.y,spine,chest,1.24,.18):blendY(p.y,hips,spine,1.065,.15);
 rings('Tshirt_coupe_originale',[[.97,0,0,.155,.105],[1.02,0,0,.16,.11],[1.10,0,0,.128,.09],[1.19,0,0,.148,.105],[1.28,0,.008,.18,.115],[1.34,0,0,.205,.105],[1.38,0,0,.185,.085],[1.405,0,0,.13,.07],[1.425,0,0,.067,.057]],shirt,torsoW);
 rings('Cou',[[1.40,0,0,.057,.052],[1.49,0,0,.051,.049],[1.55,0,0,.065,.055]],skin,p=>blendY(p.y,neck,head,1.5,.08));
 ellipsoid('Visage',skin,head,0,1.645,.012,.112,.155,.10);
 // Menton et nez discrets : détails en volume, non textures photographiques.
 // Menton intégré à la silhouette du visage, sans pièce rapportée.
 ellipsoid('Nez',skin,head,0,1.626,.107,.016,.028,.020);ellipsoid('Pointe_nez',skin,head,0,1.605,.117,.018,.011,.012);
 for(const [side,j] of Object.entries(joints)){const s=j.s;
  ellipsoid(side+'_Oreille',skin,head,s*.108,1.635,.005,.021,.038,.016);
  ellipsoid(side+'_Oeil',white,head,s*.050,1.664,.100,.027,.012,.007);ellipsoid(side+'_Iris',iris,head,s*.05,1.664,.106,.009,.009,.002);ellipsoid(side+'_Pupille',pupil,head,s*.05,1.664,.108,.004,.005,.0015);ellipsoid(side+'_Reflet',white,head,s*.047,1.668,.110,.002,.002,.001);
  tube(side+'_Paupiere',[[s*.021,1.664,.103],[s*.04,1.677,.104],[s*.065,1.677,.098],[s*.080,1.664,.091]],.0025,hair,head);
  tube(side+'_Sourcil',[[s*.022,1.692,.100],[s*.047,1.699,.096],[s*.073,1.693,.088]],.0035,hair,head);
  ellipsoid(side+'_Boucle_oreille',copper,head,s*.118,1.604,.01,.009,.014,.006);
  const armRows=[];for(let i=0;i<=22;i++){const y=1.36-i*.0202,t=i/22;const x=s*(.225+.14*t);const radius=.047-(.02*t)+.005*Math.sin(t*Math.PI);armRows.push([y,x,0,radius,radius*.95]);}
  rings(side+'_Bras',armRows,skin,p=>blendY(p.y,j.fore,j.arm,1.135,.10),24);
  rings(side+'_Manche',[[1.27,s*.264,0,.058,.055],[1.32,s*.245,0,.063,.059],[1.365,s*.223,0,.066,.065]],shirt,rigid(j.arm),24);
  ellipsoid(side+'_Paume',skin,j.hand,s*.375,.893,.006,.032,.052,.017);
  for(let f=0;f<5;f++){const b=byName[side+'Finger'+f],x=s*(.375+(f===0?.031:(f-2.5)*.012));const y=f===0?.888:.854;ellipsoid(side+'_Doigt'+f,skin,b,x,y,.013,.008,f===0?.025:.034,.008);}
  // Le jean sera une surface continue commune aux deux jambes.
  ellipsoid(side+'_Chaussure',leather,j.foot,s*.122,.062,.05,.102,.06,.16);
  // Coutures latérales et bracelets suivent les segments correspondants.
  tube(side+'_Couture_haute',[[s*.207,.92,0],[s*.195,.75,0],[s*.19,.60,0]],.0025,copper,j.thigh);
  tube(side+'_Couture_basse',[[s*.19,.49,0],[s*.21,.27,0],[s*.24,.13,0]],.0025,copper,j.shin);
  const bg=new T.TorusGeometry(.034,.006,8,32);bg.rotateX(Math.PI/2);bg.translate(s*.356,.97,0);skinned(bg,copper,side+'_Bracelet',rigid(j.fore));
 }
 // Jean continu : union implicite lissée puis triangulation tétraédrique.
 // Évite une pièce de bassin superposée aux jambes et sa couture flottante.
 const smoothMin=(a,b,k)=>{const h=Math.max(k-Math.abs(a-b),0)/k;return Math.min(a,b)-h*h*k*.25;};
 function pantsField(x,y,z){const t=T.MathUtils.clamp((y-.10)/.86,0,1);const rx=t<.5?.12-(t/.5)*.045:.075+((t-.5)/.5)*.029;const leg=cx=>Math.max((Math.hypot((x-cx)/rx,z/(rx*.94))-1)*rx,.084-y,y-.99);const legField=smoothMin(leg(-.115),leg(.115),.014);const pr=.167+.015*Math.sin(T.MathUtils.clamp((y-.81)/.19,0,1)*Math.PI);const pelvis=Math.max((Math.hypot(x/pr,z/.105)-1)*.1,.825-y,y-.999);return smoothMin(legField,pelvis,.032);}
 const nx=16,ny=32,nz=12,x0=-.26,y0=.065,z0=-.16,dx=.52/nx,dy=.96/ny,dz=.32/nz;
 const pts=[],field=[];for(let k=0;k<=nz;k++)for(let j=0;j<=ny;j++)for(let i=0;i<=nx;i++){const p=[x0+i*dx,y0+j*dy,z0+k*dz];pts.push(p);field.push(pantsField(...p));}
 const at=(i,j,k)=>(k*(ny+1)+j)*(nx+1)+i;
 const tetra=[[0,5,1,6],[0,1,2,6],[0,2,3,6],[0,3,7,6],[0,7,4,6],[0,4,5,6]],edges=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],verts=[],normals=[],uvs=[];
 function normal(p){const e=.0001;return new T.Vector3(pantsField(p.x+e,p.y,p.z)-pantsField(p.x-e,p.y,p.z),pantsField(p.x,p.y+e,p.z)-pantsField(p.x,p.y-e,p.z),pantsField(p.x,p.y,p.z+e)-pantsField(p.x,p.y,p.z-e)).normalize();}
 for(let k=0;k<nz;k++)for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){const ids=[at(i,j,k),at(i+1,j,k),at(i+1,j+1,k),at(i,j+1,k),at(i,j,k+1),at(i+1,j,k+1),at(i+1,j+1,k+1),at(i,j+1,k+1)];if(ids.every(n=>field[n]>0)||ids.every(n=>field[n]<=0))continue;for(const tet of tetra){const poly=[];for(const [a,b]of edges){const ia=ids[tet[a]],ib=ids[tet[b]],va=field[ia],vb=field[ib];if((va<=0)===(vb<=0))continue;const f=va/(va-vb);poly.push(new T.Vector3(...pts[ia]).lerp(new T.Vector3(...pts[ib]),f));}if(poly.length<3)continue;const center=poly.reduce((s,p)=>s.add(p),new T.Vector3()).multiplyScalar(1/poly.length),n=normal(center),u=poly[0].clone().sub(center).normalize(),v=new T.Vector3().crossVectors(n,u);poly.sort((a,b)=>Math.atan2(a.clone().sub(center).dot(v),a.clone().sub(center).dot(u))-Math.atan2(b.clone().sub(center).dot(v),b.clone().sub(center).dot(u)));for(let a=1;a<poly.length-1;a++)for(const p of [poly[0],poly[a],poly[a+1]]){verts.push(p.x,p.y,p.z);const nn=normal(p);normals.push(nn.x,nn.y,nn.z);uvs.push(Math.atan2(p.z,p.x)/(Math.PI*2)+.5,(p.y-.08)/.92);}}}
 let pg=new T.BufferGeometry();pg.setAttribute('position',new T.Float32BufferAttribute(verts,3));pg.setAttribute('normal',new T.Float32BufferAttribute(normals,3));pg.setAttribute('uv',new T.Float32BufferAttribute(uvs,2));pg=mergeVertices(pg);skinned(pg,denim,'Jean_surface_continue',p=>{const j=p.x>=0?joints.Left:joints.Right;return p.y>.82?blendY(p.y,j.thigh,hips,.90,.14):blendY(p.y,j.shin,j.thigh,.52,.16);});
 rings('Ceinture',[[.975,0,0,.163,.112],[1.01,0,0,.16,.11]],leather,rigid(hips));
 const buckle=new T.TorusGeometry(.026,.005,8,32);buckle.scale(1.3,1,1);buckle.translate(0,.994,.116);skinned(buckle,copper,'Boucle_ceinture',rigid(hips));
 tube('Levres_superieures',[[-.034,1.57,.098],[-.015,1.578,.111],[0,1.574,.115],[.015,1.578,.111],[.034,1.57,.098]],.0027,lip,head);
 tube('Levres_inferieures',[[-.031,1.569,.098],[0,1.562,.112],[.031,1.569,.098]],.0032,lip,head);
 // Calotte fermée sur le crâne mais ouverte autour du visage.
 const hp=[],hu=[],hi=[];const segments=48,rows=18;
 for(let j=0;j<=rows;j++)for(let i=0;i<=segments;i++){const a=i/segments*Math.PI*2,front=Math.max(0,Math.sin(a)),maxPhi=2.05-front*1.0,phi=.001+j/rows*maxPhi;hp.push(.124*Math.sin(phi)*Math.cos(a),1.655+.17*Math.cos(phi),.008+.116*Math.sin(phi)*Math.sin(a));hu.push(i/segments,j/rows);}
 for(let j=0;j<rows;j++)for(let i=0;i<segments;i++){const a=j*(segments+1)+i,b=a+segments+1;hi.push(a,a+1,b,b,a+1,b+1);}
 const hg=new T.BufferGeometry();hg.setAttribute('position',new T.Float32BufferAttribute(hp,3));hg.setAttribute('uv',new T.Float32BufferAttribute(hu,2));hg.setIndex(hi);hg.computeVertexNormals();skinned(hg,hair,'Coiffure_calotte',rigid(head));
 // Mèches ondulées : chaque courbe et reflet est une géométrie originale.
 for(let k=0;k<30;k++){const a=Math.PI*.05+k/29*Math.PI*1.9;const front=Math.sin(a)>.55;const x=Math.cos(a)*.105,z=Math.sin(a)*.085;const startY=front?1.77:1.74;const side=Math.sign(x)||1;const pts=[];for(let i=0;i<13;i++){const t=i/12;const xx=front?side*(.035+.105*Math.sin(t*Math.PI*.8)):x*(1+.32*t);const zz=front?.095-.04*t:z-.025*t;pts.push([xx+Math.sin(t*17+k*.6)*.021*t,startY-t*(front?.54:.59),zz+Math.sin(t*18+k*.4)*.024*t]);}tube('Meche_'+k,pts,front?.016:.02,k%4===0?hairLight:hair,head);}
 // Plis du noeud et collier, sans réinterpréter un logo.
 ellipsoid('Noeud_tshirt',shirt,hips,.10,1.017,.104,.035,.025,.025);
 tube('Collier',[[-.066,1.416,.03],[-.057,1.385,.092],[0,1.361,.12],[.057,1.385,.092],[.066,1.416,.03]],.0024,copper,chest);
 root.updateMatrixWorld(true);
 // Clips glTF en quaternions ; marche sur place, aucune translation de locomotion.
 function rotTrack(name,axis,values,times){const q=[];for(const v of values){const r=new T.Quaternion().setFromAxisAngle(new T.Vector3(...axis),v);q.push(r.x,r.y,r.z,r.w);}return new T.QuaternionKeyframeTrack(name+'.quaternion',times,q);}
 const times=[0,1,2,3,4];
 const idle=new T.AnimationClip('Respiration',4,[rotTrack('Chest',[1,0,0],[0,.018,0,-.018,0],times),rotTrack('Head',[0,1,0],[0,.035,0,-.035,0],times)]);
 const wave=new T.AnimationClip('Salut',4,[rotTrack('RightArm',[0,0,1],[0,-1.5,-1.5,-1.5,0],times),rotTrack('RightForeArm',[0,0,1],[0,-1.1,-.85,-1.1,0],times),rotTrack('RightHand',[0,0,1],[0,-.28,.28,-.28,0],times)]);
 const wt=[0,.5,1,1.5,2];const walkTracks=[];for(const [side,s] of [['Left',1],['Right',-1]]){walkTracks.push(rotTrack(side+'UpLeg',[1,0,0],[0,s*.28,0,-s*.28,0],wt),rotTrack(side+'Leg',[1,0,0],[0,side==='Left'?.40:0,0,side==='Right'?.40:0,0],wt),rotTrack(side+'Arm',[1,0,0],[0,-s*.18,0,s*.18,0],wt));}
 const walk=new T.AnimationClip('Marche_sur_place',2,walkTracks);
 // Regrouper par matériau : moins de draw calls, un squelette partagé.
 const batches=new Map();for(const m of [...root.children])if(m.isSkinnedMesh){if(!batches.has(m.material))batches.set(m.material,[]);batches.get(m.material).push(m.geometry);root.remove(m);}
 for(const [mat,geoms] of batches){const g=mergeGeometries(geoms,false);if(!g)throw new Error('Fusion incompatible');const m=new T.SkinnedMesh(g,mat);m.name=mat.name||'Details';root.add(m);m.bind(skeleton);geoms.forEach(g=>g.dispose());}
 // Nœuds skinnés directement racines pour éviter les transformations
 // parentes ambiguës en glTF ; le repère exporté est déjà en mètres.
 const exported=new T.Scene();exported.name=root.name;exported.userData=root.userData;for(const child of [...root.children])exported.add(child);exported.updateMatrixWorld(true);
 return await new GLTFExporter().parseAsync(exported,{binary:true,animations:[idle,wave,walk],onlyVisible:true});
}

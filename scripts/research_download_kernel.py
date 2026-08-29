import json, shutil, subprocess, sys, time
from pathlib import Path
DEST=Path(sys.argv[1]).resolve(); WORK=Path(sys.argv[2]).resolve(); SRC=WORK/'src'; PACK=WORK/'pack'
MANIFEST=DEST/'RESEARCH_DOWNLOAD_MANIFEST.jsonl'; SPLIT_TARGET=12000000; MAX_ZIP=17*1000*1000; BATCH_LIMIT=90*1024*1024; CHUNK=8*1024*1024
REPOS=[('01','wshuyi-deep-research','https://github.com/wshuyi/deep-research.git'),('02','ouroboros','https://github.com/RightNow-AI/ouroboros.git'),('03','CART','https://github.com/ccapps42/CART.git'),('04','open-fable','https://github.com/OpenCoven/open-fable.git'),('05','recurrent-depth-ttc','https://github.com/duongtrongnguyen123/recurrent-depth-ttc.git'),('06','rd-vla','https://github.com/rd-vla/rd-vla.git'),('07','HadiFrt20-deepresearch','https://github.com/HadiFrt20/deepresearch.git'),('08','LanguageAgentTreeSearch','https://github.com/lapisrocks/LanguageAgentTreeSearch.git'),('09','self-refine','https://github.com/madaan/self-refine.git'),('10','MindMap','https://github.com/wyl-willing/MindMap.git'),('11','graph-of-thoughts','https://github.com/spcl/graph-of-thoughts.git'),('12','reflexion','https://github.com/noahshinn/reflexion.git'),('13','openmythos-vega','https://github.com/vegafoundation/openmythos.git'),('14','deer-flow','https://github.com/bytedance/deer-flow.git'),('15','OpenManus','https://github.com/FoundationAgents/OpenManus.git'),('16','camel','https://github.com/camel-ai/camel.git'),('17','simply-code','https://github.com/openai/simply-code.git'),('18','tree-of-thoughts','https://github.com/kyegomez/tree-of-thoughts.git'),('19','agentdescent','https://github.com/Birfy/agentdescent.git'),('20','Fable5res','https://github.com/ahmdd4vd/Fable5res.git'),('21','fable5-methodology','https://github.com/UnpaidAttention/fable5-methodology.git'),('22','OpenMythos-kyegomez','https://github.com/kyegomez/OpenMythos.git'),('23','OpenMythos-Bananefre','https://github.com/Bananefre/OpenMythos.git'),('24','OpenMythos-MLX','https://github.com/DeadByDawn101/OpenMythos-MLX.git'),('25','OpenMythos-Skill','https://github.com/SarthakDz/OpenMythos-Skill.git'),('26','dagu-org','https://github.com/dagu-org/dagu.git'),('27','deepdive','https://github.com/Socialpranker/deepdive.git'),('28','binex','https://github.com/Alexli18/binex.git'),('29','pi-task','https://github.com/mjasnikovs/pi-task.git'),('30','LoomFlow','https://github.com/Anurich/LoomFlow.git'),('31','ux-research-pipeline','https://github.com/shipaleks/ux-research-pipeline.git'),('32','framework-of-thoughts','https://github.com/fjfricke/framework-of-thoughts.git'),('33','Self-consistency','https://github.com/akpe12/Self-consistency.git'),('34','veritrace','https://github.com/noah-art3mis/veritrace.git'),('35','AI-Agent-Skills','https://github.com/sreerevanth/AI-Agent-Skills.git')]
def run(c,cwd=None): subprocess.run(c,cwd=cwd,check=True)
def done(slug):
    if not MANIFEST.exists(): return False
    return any((lambda d:d.get('slug')==slug and d.get('status')=='COMPLETE')(json.loads(x)) for x in MANIFEST.read_text().splitlines() if x.strip())
def stage_repo(slug,root):
    stage=PACK/f'{slug}_stage'; shutil.rmtree(stage,ignore_errors=True); stage.mkdir(parents=True); records=[]
    for p in root.rglob('*'):
        if not p.is_file(): continue
        rel=p.relative_to(root); target=stage/slug/rel; target.parent.mkdir(parents=True,exist_ok=True); size=p.stat().st_size
        if size<=CHUNK: shutil.copy2(p,target); continue
        d=target.parent/(target.name+'.chunks'); d.mkdir(parents=True,exist_ok=True)
        with p.open('rb') as f:
            i=0
            while True:
                data=f.read(CHUNK)
                if not data: break
                (d/f'{target.name}.part-{i:04d}').write_bytes(data); i+=1
        records.append({'repo':slug,'path':str(rel),'chunks_dir':str(d.relative_to(stage)),'bytes':size,'chunk_bytes':CHUNK})
    if records: (stage/'SPLIT_FILES.json').write_text(json.dumps(records,indent=2))
    return stage
def package(slug,root):
    stage=stage_repo(slug,root); full=PACK/f'{slug}_full.zip'; full.unlink(missing_ok=True)
    run(['zip','-q','-r','-9','-y',str(full.resolve()),'.'],cwd=stage)
    if full.stat().st_size<=SPLIT_TARGET:
        out=PACK/f'{slug}_0001.zip'; full.replace(out); shutil.rmtree(stage,ignore_errors=True); return [(out,out.stat().st_size)]
    before=set(PACK.glob('*.zip')); run(['zipsplit','-n',str(SPLIT_TARGET),'-b',str(PACK.resolve()),str(full.resolve())]); full.unlink(missing_ok=True)
    made=[p for p in PACK.glob('*.zip') if p not in before and p != full]
    if not made: raise RuntimeError(f'zipsplit produced no parts for {slug}')
    out=[]
    for i,p in enumerate(sorted(made,key=lambda p:(p.stat().st_mtime,p.name)),1):
        q=PACK/f'{slug}_{i:04d}.zip'; p.replace(q); size=q.stat().st_size
        if size>MAX_ZIP: raise RuntimeError(f'ZIP part exceeds safety limit: {q} = {size}')
        subprocess.run(['unzip','-tq',str(q)],check=True); out.append((q,size))
    shutil.rmtree(stage,ignore_errors=True); return out
def push(label):
    for attempt in range(1,4):
        try:
            run(['git','fetch','origin','main']); run(['git','rebase','origin/main']); run(['git','push','origin','HEAD:main']); print(f'PUSH PASS {label} attempt {attempt}'); return
        except subprocess.CalledProcessError:
            if attempt==3: raise
            time.sleep(attempt*2)
def commit(n,label):
    if not n:return
    run(['git','add',str(DEST)])
    if subprocess.run(['git','diff','--cached','--quiet']).returncode==0:return
    run(['git','config','user.name','github-actions[bot]']); run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com']); run(['git','commit','-m',f'build(download): kernel queue batch {label} ({n} bytes)']); push(label)
DEST.mkdir(parents=True,exist_ok=True); SRC.mkdir(parents=True,exist_ok=True); PACK.mkdir(parents=True,exist_ok=True)
batch=batch_no=0
for number,slug,url in REPOS:
    print(f'===== QUEUE {number}/35: {slug} =====')
    if done(slug): print(f'{slug}: COMPLETE; skipping'); continue
    root=SRC/slug; shutil.rmtree(root,ignore_errors=True); run(['git','clone','--depth','1','--no-tags',url,str(root)])
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(); shutil.rmtree(root/'.git',ignore_errors=True)
    parts=package(slug,root); print(f'{slug}: {len(parts)} ZIP part(s)')
    for z,size in parts:
        if batch and batch+size>BATCH_LIMIT: commit(batch,f'{batch_no:03d}'); batch=0; batch_no+=1
        shutil.copy2(z,DEST/z.name); batch+=size; print(f'  {z.name}: {size} bytes; batch={batch}')
    with MANIFEST.open('a') as f: f.write(json.dumps({'number':int(number),'slug':slug,'source':url,'source_commit':sha,'parts':len(parts),'status':'COMPLETE'},sort_keys=True)+'\n')
    shutil.rmtree(root,ignore_errors=True); shutil.rmtree(PACK,ignore_errors=True); PACK.mkdir(parents=True,exist_ok=True)
commit(batch,f'{batch_no:03d}-final'); print('===== QUEUE COMPLETE: kernel 35 processed =====')

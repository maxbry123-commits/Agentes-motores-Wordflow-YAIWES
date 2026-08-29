import json, shutil, subprocess, sys, time
from pathlib import Path
DEST=Path(sys.argv[1]).resolve(); WORK=Path(sys.argv[2]).resolve(); SRC=WORK/'src'; PACK=WORK/'pack'
MANIFEST=DEST/'RESEARCH_DOWNLOAD_MANIFEST.jsonl'; SPLIT_TARGET=12000000; MAX_ZIP=17*1000*1000; BATCH_LIMIT=90*1024*1024; CHUNK=8*1024*1024
REPOS=[('37', 'OpenClaw-RL', 'https://github.com/Gen-Verse/OpenClaw-RL.git'), ('38', 'SETA', 'https://github.com/camel-ai/seta.git'), ('39', 'ATLAS', 'https://github.com/itigges22/ATLAS.git'), ('40', 'OpenDev', 'https://github.com/opendev-to/opendev.git'), ('41', 'Shofer', 'https://github.com/shofer-dev/shofer.git'), ('42', 'Safe-Lab-Agents', 'https://github.com/MaxNaeg/safe_lab_agents.git'), ('43', 'CORAL', 'https://github.com/Human-Agent-Society/CORAL.git'), ('44', 'NVIDIA-OpenShell', 'https://github.com/NVIDIA/OpenShell.git'), ('45', 'NVIDIA-NeMo-Agent-Toolkit', 'https://github.com/NVIDIA/NeMo-Agent-Toolkit.git'), ('46', 'Kimi-CLI', 'https://github.com/MoonshotAI/kimi-cli.git'), ('47', 'Mini-Agent', 'https://github.com/MiniMax-AI/Mini-Agent.git'), ('48', 'Xiaomi-Miloco', 'https://github.com/XiaoMi/xiaomi-miloco.git'), ('49', 'Meta-OpenEnv', 'https://github.com/meta-pytorch/OpenEnv.git'), ('50', 'Kimi-K2.5', 'https://github.com/MoonshotAI/Kimi-K2.5.git'), ('51', 'MiniMax-Provider-Verifier', 'https://github.com/MiniMax-AI/MiniMax-Provider-Verifier.git'), ('52', 'GLM-skills', 'https://github.com/zai-org/GLM-skills.git'), ('53', 'MiMo-V2-Flash', 'https://github.com/xiaomimimo/MiMo-V2-Flash.git'), ('54', 'Qwen-Agent', 'https://github.com/QwenLM/Qwen-Agent.git'), ('55', 'Agent-Contracts', 'https://github.com/relari-ai/agent-contracts.git'), ('56', 'Bound', 'https://github.com/Danny-de-bree/bound.git'), ('57', 'Agent-Handoff', 'https://github.com/artyomboyko/Agent_Handoff.git'), ('58', 'Agent-Checkpoint', 'https://github.com/akz4ol/agent-checkpoint.git'), ('59', 'LangChain-Task-Steering', 'https://github.com/edvinhallvaxhiu/langchain-task-steering.git'), ('60', 'ToolOrchestra', 'https://github.com/NVlabs/ToolOrchestra.git'), ('61', 'Sovereign-OS', 'https://github.com/Justin0504/Sovereign-OS.git'), ('62', 'Reyn', 'https://github.com/tya5/reyn.git'), ('63', 'Kaji', 'https://github.com/apokamo/kaji.git'), ('64', 'Prime-Agent', 'https://github.com/PrimeIntellect-ai/prime-agent.git'), ('65', 'Grok-Build', 'https://github.com/xai-org/grok-build.git'), ('66', 'Qwen-UI-Agent', 'https://github.com/Tongyi-MAI/MAI-UI.git'), ('67', 'Codex-Security', 'https://github.com/openai/codex-security.git'), ('68', 'Kimi-K3', 'https://github.com/MoonshotAI/Kimi-K3.git'), ('69', 'GLM-5', 'https://github.com/zai-org/glm-5.git'), ('70', 'Qwen3.5', 'https://github.com/QwenLM/Qwen3.5.git'), ('71', 'Hyundai-Physical-AI-Stack', 'https://github.com/boston-dynamics/spot-sdk.git'), ('72', 'Artificial-Agent-Lab', 'https://github.com/BY571/artificial-agent-lab.git'), ('73', 'Swarm-Agent', 'https://github.com/desplega-ai/agent-swarm.git'), ('74', 'Bernstein', 'https://github.com/sipyourdrink-ltd/bernstein.git'), ('75', 'Arena-of-Autonomous-Threads', 'https://github.com/rafaelmateo123/Arena-of-Autonomous-Threads.git'), ('76', 'OSS-Agent-Lab', 'https://github.com/jeremylongshore/oss-agent-lab.git'), ('77', 'Aiyu-Multi-Agent', 'https://github.com/teeprakorn1/aiyu-multi-agent.git'), ('78', 'OpenAlice', 'https://github.com/TraderAlice/OpenAlice.git'), ('79', 'Dr-Claw', 'https://github.com/OpenLAIR/dr-claw.git'), ('80', 'AgentSPEX', 'https://github.com/ScaleML/AgentSPEX.git'), ('81', 'Agents-Universe', 'https://github.com/agentuniverse-ai/agentUniverse.git'), ('82', 'Spice-Agent-Coding', 'https://github.com/spiceai/skills.git'), ('83', 'Jidoka', 'https://github.com/agentjido/jidoka.git'), ('84', 'Plugin-Marketplace', 'https://github.com/anthropics/claude-plugins-official.git'), ('85', 'AgentOS', 'https://github.com/rivet-dev/agentos.git'), ('86', 'ORCA', 'https://github.com/stablyai/orca.git'), ('87', 'Agent-Resume', 'https://github.com/MukundaKatta/agent-resume.git'), ('88', 'GLM-5V-Turbo', 'https://github.com/zai-org/GLM-V.git'), ('89', 'MiniMax-Code', 'https://github.com/MiniMax-AI/minimax-code.git'), ('90', 'OpenRoom', 'https://github.com/MiniMax-AI/OpenRoom.git'), ('91', 'MiniMax-Skills', 'https://github.com/MiniMax-AI/skills.git'), ('92', 'Kimi-Code-CLI', 'https://github.com/MoonshotAI/kimi-code.git'), ('93', 'Kimi-Agent-SDK', 'https://github.com/MoonshotAI/kimi-agent-sdk.git'), ('94', 'Kimi-K2', 'https://github.com/MoonshotAI/Kimi-K2.git'), ('95', 'DeepSeek-Harness', 'https://github.com/deepseek-ai/deepseek-harness.git'), ('96', 'Awesome-DeepSeek-Agent', 'https://github.com/deepseek-ai/awesome-deepseek-agent.git'), ('97', 'GitHub-Copilot-CLI', 'https://github.com/github/copilot-cli.git'), ('98', 'GitHub-Copilot-SDK', 'https://github.com/github/copilot-sdk.git'), ('99', 'GitHub-Copilot-App', 'https://github.com/github/app.git'), ('100', 'Qwen-Code', 'https://github.com/QwenLM/qwen-code.git'), ('101', 'Codex', 'https://github.com/openai/codex.git'), ('102', 'OpenAI-Skills', 'https://github.com/openai/skills.git'), ('103', 'Claude-Code', 'https://github.com/anthropics/claude-code.git'), ('104', 'Claude-Agent-SDK-TypeScript', 'https://github.com/anthropics/claude-agent-sdk-typescript.git'), ('105', 'Claude-Agent-SDK-Python', 'https://github.com/anthropics/claude-agent-sdk-python.git'), ('106', 'Gemini-CLI', 'https://github.com/google-gemini/gemini-cli.git'), ('107', 'Google-Agent-Skills', 'https://github.com/google/skills.git'), ('108', 'MiMo-Code', 'https://github.com/XiaomiMiMo/MiMo-Code.git'), ('109', 'MiMo-Skills', 'https://github.com/XiaomiMiMo/MiMo-Skills.git'), ('110', 'Llama-Agentic-System', 'https://github.com/meta-llama/llama-agentic-system.git'), ('111', 'Llama-Stack', 'https://github.com/meta-llama/llama-stack.git'), ('112', 'Llama-Cookbook', 'https://github.com/meta-llama/llama-cookbook.git'), ('113', 'NVIDIA-Agent-Skills', 'https://github.com/NVIDIA/skills.git'), ('114', 'NVIDIA-NOOA', 'https://github.com/NVIDIA-NeMo/labs-OO-Agents.git'), ('115', 'NVIDIA-AI-Q', 'https://github.com/NVIDIA-AI-Blueprints/aiq.git'), ('116', 'Atomic-Agent', 'https://github.com/AtomicBot-ai/atomic-agent.git'), ('117', 'Atomic-Chat', 'https://github.com/AtomicBot-ai/Atomic-Chat.git'), ('118', 'Atomic-Hermes', 'https://github.com/AtomicBot-ai/atomic-hermes.git'), ('119', 'Atomic-llama-cpp-TurboQuant', 'https://github.com/AtomicBot-ai/atomic-llama-cpp-turboquant.git')]
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
    run(['git','config','user.name','github-actions[bot]']); run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com']); run(['git','commit','-m',f'build(download): research queue batch {label} ({n} bytes)']); push(label)
DEST.mkdir(parents=True,exist_ok=True); SRC.mkdir(parents=True,exist_ok=True); PACK.mkdir(parents=True,exist_ok=True)
batch=batch_no=0
for number,slug,url in REPOS:
    print(f'===== QUEUE {number}/119: {slug} =====')
    if done(slug): print(f'{slug}: COMPLETE; skipping'); continue
    root=SRC/slug; shutil.rmtree(root,ignore_errors=True); run(['git','clone','--depth','1','--no-tags',url,str(root)])
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(); shutil.rmtree(root/'.git',ignore_errors=True)
    parts=package(slug,root); print(f'{slug}: {len(parts)} ZIP part(s)')
    for z,size in parts:
        if batch and batch+size>BATCH_LIMIT: commit(batch,f'{batch_no:03d}'); batch=0; batch_no+=1
        shutil.copy2(z,DEST/z.name); batch+=size; print(f'  {z.name}: {size} bytes; batch={batch}')
    with MANIFEST.open('a') as f: f.write(json.dumps({'number':int(number),'slug':slug,'source':url,'source_commit':sha,'parts':len(parts),'status':'COMPLETE'},sort_keys=True)+'\n')
    shutil.rmtree(root,ignore_errors=True); shutil.rmtree(PACK,ignore_errors=True); PACK.mkdir(parents=True,exist_ok=True)
commit(batch,f'{batch_no:03d}-final'); print('===== QUEUE COMPLETE: gap 37-119 processed =====')

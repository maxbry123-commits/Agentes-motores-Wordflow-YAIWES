import json, shutil, subprocess, sys, time
from pathlib import Path
from zipfile import ZipFile
SRC=Path(sys.argv[1]).resolve()
BATCH_LIMIT=90*1024*1024
MANIFEST=SRC/'EXTRA_AGENTS_MANIFEST.jsonl'
NAMES={'OpenHands':'OpenHands','OpenCode':'OpenCode','Temporal':'Temporal'}
def run(c): subprocess.run(c,check=True)
def push(label):
    for attempt in range(1,4):
        try:
            run(['git','fetch','origin','main']); run(['git','rebase','origin/main']); run(['git','push','origin','HEAD:main']); print(f'PUSH PASS {label} attempt {attempt}'); return
        except subprocess.CalledProcessError:
            if attempt==3: raise
            time.sleep(attempt*2)
def commit(n,label):
    if not n: return
    run(['git','add','-A'])
    if subprocess.run(['git','diff','--cached','--quiet']).returncode==0: return
    run(['git','config','user.name','github-actions[bot]']); run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
    run(['git','commit','-m',f'extract(extra): lote {label}']); push(label)
rows=[]
for line in MANIFEST.read_text().splitlines():
    if line.strip(): rows.append(json.loads(line))
batch=batch_no=0
for row in rows:
    slug=row['slug']
    dest=Path(NAMES.get(slug, slug))
    shutil.rmtree(dest, ignore_errors=True); dest.mkdir(parents=True, exist_ok=True)
    parts=sorted(SRC.glob(f'{slug}_*.zip'))
    if not parts: raise SystemExit(f'ZIP ausente: {slug}')
    count=size=0; seen=set()
    for zp in parts:
        size += zp.stat().st_size
        with ZipFile(zp) as z:
            if z.testzip() is not None: raise SystemExit(f'CRC failure in {slug}')
            for info in z.infolist():
                raw=info.filename.replace('\\','/')
                if not raw or raw.endswith('/'): continue
                p=Path(raw)
                if p.is_absolute() or '..' in p.parts: raise SystemExit(f'{slug}: unsafe ZIP path: {raw}')
                if raw in seen: continue
                seen.add(raw)
                target=(dest/raw).resolve()
                if dest.resolve() not in target.parents: raise SystemExit(f'{slug}: extraction escape: {raw}')
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, target.open('wb') as dst:
                    shutil.copyfileobj(src, dst, length=1024*1024)
                count += 1
    if count==0: raise SystemExit(f'{slug}: zero files extracted')
    print(f'PASS EXTRACT: {dest} files={count} zip={size}')
    if batch and batch+size>BATCH_LIMIT:
        commit(batch,f'{batch_no:03d}'); batch=0; batch_no+=1
    batch += size
commit(batch,f'{batch_no:03d}-final')

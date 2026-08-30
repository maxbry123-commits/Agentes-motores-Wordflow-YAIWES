import json, shutil, subprocess, sys
from pathlib import Path
from zipfile import ZipFile
from skill_guard import guard_dest, push, run
SRC=Path(sys.argv[1]).resolve(); BATCH_LIMIT=90*1024*1024; MANIFEST=SRC/'RESEARCH_DOWNLOAD_MANIFEST.jsonl'
def commit(n,label):
    if not n: return
    run(['git','add','-A'])
    if subprocess.run(['git','diff','--cached','--quiet']).returncode==0: return
    run(['git','config','user.name','github-actions[bot]']); run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
    run(['git','commit','-m',f'extract(kernel): lote {label}']); push(label)
rows=[json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]; batch=0; batch_no=0
for row in rows:
    slug=row['slug']; dest=SRC/slug
    if dest.is_dir() and any(dest.rglob('*')): print(f'SKIP EXTRACT done: {slug}'); continue
    dest.mkdir(parents=True, exist_ok=True); parts=sorted(SRC.glob(f'{slug}_*.zip'))
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
                seen.add(raw); target=(dest/raw).resolve()
                if dest.resolve() not in target.parents: raise SystemExit(f'{slug}: extraction escape: {raw}')
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, target.open('wb') as dst: shutil.copyfileobj(src,dst,length=1024*1024)
                count += 1
    guard_dest(dest)
    if count==0: raise SystemExit(f'{slug}: zero files extracted')
    print(f'PASS EXTRACT: {slug} files={count} zip={size}')
    if batch and batch+size>BATCH_LIMIT: commit(batch,f'{batch_no:03d}'); batch=0; batch_no+=1
    batch += size
commit(batch,f'{batch_no:03d}-final')

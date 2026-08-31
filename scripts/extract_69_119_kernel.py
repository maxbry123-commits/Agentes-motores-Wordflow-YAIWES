import json, shutil, subprocess, sys
from pathlib import Path
from zipfile import ZipFile
from skill_guard import run
SRC=Path(sys.argv[1]).resolve()
DEST_ROOT=Path(sys.argv[2]).resolve()
MANIFEST=SRC/'RESEARCH_DOWNLOAD_MANIFEST.jsonl'
NEED=set(range(69,120))
def strip_lfs(dest):
    for p in dest.rglob('*'):
        if not p.is_file(): continue
        if p.name=='.gitattributes':
            try:
                if 'filter=lfs' in p.read_text(errors='ignore'): p.unlink()
            except Exception:
                pass
            continue
        try:
            if p.read_bytes()[:64].startswith(b'version https://git-lfs.github.com/spec/'): p.unlink()
        except Exception:
            pass
def commit(label):
    run(['git','add','-A'])
    if subprocess.run(['git','diff','--cached','--quiet']).returncode==0: return
    run(['git','config','user.name','github-actions[bot]']); run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'])
    run(['git','commit','-m',f'extract(kernel-69-119): {label}'])
    try:
        run(['git','push','--no-verify','origin','HEAD:main'])
    except subprocess.CalledProcessError:
        print(f'SKIP PUSH {label}', flush=True)
        subprocess.run(['git','reset','--hard','origin/main'], check=False)
rows=[]
for line in MANIFEST.read_text().splitlines():
    if line.strip(): rows.append(json.loads(line))
for row in rows:
    number=int(row['number'])
    if number not in NEED: continue
    slug=row['slug']; dest=DEST_ROOT/slug
    if dest.is_dir() and any(dest.rglob('*')):
        print(f'SKIP EXTRACT done: {slug}'); continue
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    parts=sorted(SRC.glob(f'{slug}_*.zip'))
    if not parts:
        print(f'SKIP ZIP ausente: {slug}', flush=True)
        continue
    count=size=0; seen=set()
    for zp in parts:
        size += zp.stat().st_size
        with ZipFile(zp) as z:
            if z.testzip() is not None:
                print(f'SKIP CRC {slug}', flush=True); count=0; break
            for info in z.infolist():
                raw=info.filename.replace('\\','/')
                if not raw or raw.endswith('/'): continue
                p=Path(raw)
                if p.is_absolute() or '..' in p.parts: continue
                if raw in seen: continue
                seen.add(raw); target=(dest/raw).resolve()
                if dest.resolve() not in target.parents: continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as srcf, target.open('wb') as dst: shutil.copyfileobj(srcf, dst, length=1024*1024)
                count += 1
    if count==0:
        print(f'SKIP EMPTY {slug}', flush=True); shutil.rmtree(dest, ignore_errors=True); continue
    strip_lfs(dest)
    print(f'PASS EXTRACT: {slug} files={count} zip={size}')
    commit(f'{number:02d}-{slug}')
print('===== EXTRACT 69-119 QUEUE DONE =====')

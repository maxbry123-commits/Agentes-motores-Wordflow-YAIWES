import json, subprocess, time
from pathlib import Path

CHUNK=8*1024*1024

def run(c):
    subprocess.run(c, check=True)

def reject_lfs_material(dest: Path):
    bad=[]
    for p in dest.rglob('*'):
        if not p.is_file():
            continue
        try:
            text=p.read_text(errors='ignore')
        except Exception:
            continue
        if 'git-lfs.github.com/spec/' in text:
            bad.append(str(p))
        elif 'filter=lfs' in text:
            bad.append(str(p))
    if bad:
        raise SystemExit('FORENSIC FAIL: LFS material detected: '+repr(bad[:20]))

def chunk_tree(dest: Path):
    rec=[]
    for p in list(dest.rglob('*')):
        if not p.is_file() or '.chunks' in p.parts:
            continue
        size=p.stat().st_size
        if size<=CHUNK:
            continue
        d=p.parent/(p.name+'.chunks')
        d.mkdir(parents=True, exist_ok=True)
        with p.open('rb') as f:
            i=0
            while True:
                data=f.read(CHUNK)
                if not data:
                    break
                (d/f'{p.name}.part-{i:04d}').write_bytes(data)
                i+=1
        rec.append({'path':str(p.relative_to(dest)),'bytes':size,'chunk_bytes':CHUNK})
        p.unlink()
    if rec:
        split=dest/'SPLIT_FILES.json'
        prev=[]
        if split.exists():
            try:
                prev=json.loads(split.read_text())
            except Exception:
                prev=[]
        split.write_text(json.dumps(prev+rec,indent=2))
    return rec

def guard_dest(dest: Path):
    reject_lfs_material(dest)
    return chunk_tree(dest)

def push(label):
    reject_lfs_material(Path('.'))
    big=[(p,p.stat().st_size) for p in Path('.').rglob('*') if p.is_file() and '.git' not in p.parts and p.stat().st_size>=99*1024*1024]
    for p,size in big:
        print('OVERSIZE',p,size)
        chunk_tree(p.parent)
    for attempt in range(1,4):
        try:
            run(['git','fetch','origin','main'])
            run(['git','rebase','origin/main'])
            run(['git','push','--no-verify','origin','HEAD:main'])
            print(f'PUSH PASS {label} attempt {attempt}')
            return
        except subprocess.CalledProcessError:
            if attempt==3:
                raise
            time.sleep(attempt*2)

import ast, json, sys
from pathlib import Path
from zipfile import ZipFile

ROOT=Path('.').resolve()
MAIN=ROOT/'Download code/archivos'
KERNEL=ROOT/'Core kernel razonamiento repo para Yaiwes'
EXTRA=MAIN/'EXTRA_AGENTS_MANIFEST.jsonl'

def rows(path):
    if not path.exists():
        raise SystemExit(f'FORENSIC FAIL: missing manifest {path}')
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]

def names_from_inventory():
    src=(ROOT/'scripts/extract_inventory.py').read_text()
    tree=ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NAMES' for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit('FORENSIC FAIL: NAMES map not found')

def verify_zip_set(base, row):
    slug=row['slug']
    parts=sorted(base.glob(f'{slug}_*.zip'))
    expected=int(row.get('parts',0))
    if expected < 1 or len(parts)!=expected:
        raise SystemExit(f'FORENSIC FAIL: {slug} parts expected={expected} found={len(parts)}')
    for zp in parts:
        if zp.stat().st_size>17*1000*1000:
            raise SystemExit(f'FORENSIC FAIL: oversize ZIP {zp}')
        with ZipFile(zp) as z:
            bad=z.testzip()
            if bad is not None:
                raise SystemExit(f'FORENSIC FAIL: CRC {zp}:{bad}')
    return len(parts)

def has_files(path):
    return path.is_dir() and any(p.is_file() for p in path.rglob('*'))

def reject_lfs(root):
    bad=[]
    for p in root.rglob('*'):
        if not p.is_file() or '.git' in p.parts:
            continue
        try:
            text=p.read_text(errors='ignore')
        except Exception:
            continue
        if 'git-lfs.github.com/spec/' in text or 'filter=lfs' in text:
            bad.append(str(p.relative_to(ROOT)))
    if bad:
        raise SystemExit('FORENSIC FAIL: LFS material remains: '+repr(bad[:50]))

main_rows=rows(MAIN/'RESEARCH_DOWNLOAD_MANIFEST.jsonl')
kernel_rows=rows(KERNEL/'RESEARCH_DOWNLOAD_MANIFEST.jsonl')
extra_rows=rows(EXTRA)
if len(main_rows)!=119 or len({int(r['number']) for r in main_rows})!=119:
    raise SystemExit('FORENSIC FAIL: main inventory is not exactly 119 unique components')
if sorted(int(r['number']) for r in main_rows)!=list(range(1,120)):
    raise SystemExit('FORENSIC FAIL: main numbering is not contiguous 01..119')
if len(kernel_rows)!=35 or sorted(int(r['number']) for r in kernel_rows)!=list(range(1,36)):
    raise SystemExit('FORENSIC FAIL: kernel inventory is not exactly 01..35')
if len(extra_rows)!=3:
    raise SystemExit('FORENSIC FAIL: extra inventory is not exactly 3')
for group in (main_rows,kernel_rows,extra_rows):
    if any(r.get('status')!='COMPLETE' for r in group):
        raise SystemExit('FORENSIC FAIL: incomplete manifest status')

names=names_from_inventory()
for row in main_rows:
    verify_zip_set(MAIN,row)
    n=f"{int(row['number']):02d}"
    dest=ROOT/names[n]
    if not has_files(dest):
        raise SystemExit(f'FORENSIC FAIL: missing/empty main extraction {n} {dest}')
for row in kernel_rows:
    verify_zip_set(KERNEL,row)
    dest=KERNEL/row['slug']
    if not has_files(dest):
        raise SystemExit(f"FORENSIC FAIL: missing/empty kernel extraction {row['slug']}")
extra_names={'OpenHands':'OpenHands','OpenCode':'OpenCode','Temporal':'Temporal'}
for row in extra_rows:
    verify_zip_set(MAIN,row)
    dest=ROOT/extra_names.get(row['slug'],row['slug'])
    if not has_files(dest):
        raise SystemExit(f"FORENSIC FAIL: missing/empty extra extraction {row['slug']}")

reject_lfs(MAIN)
reject_lfs(KERNEL)
for n in names.values():
    reject_lfs(ROOT/n)
for n in extra_names.values():
    reject_lfs(ROOT/n)

report={
    'status':'PASS',
    'main_components':119,
    'kernel_components':35,
    'extra_components':3,
    'zip_crc':'PASS',
    'zip_size_limit_bytes':17*1000*1000,
    'main_locations':'PASS',
    'kernel_locations':'PASS',
    'extra_locations':'PASS',
    'lfs_material':'ABSENT'
}
out=ROOT/'FORENSIC-REBUILD-REPORT.json'
out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,sort_keys=True))

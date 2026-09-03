#!/usr/bin/env python3
"""Agent Checkpoint Verification - Catches stub/mock code"""
import re, sys, subprocess, argparse
from pathlib import Path
from datetime import datetime

STUB_PATTERNS = [
    r'\bTODO\b', r'\bFIXME\b', r'\bXXX\b', r'NotImplementedError',
    r'raise\s+NotImplementedError', r'throw\s+new\s+Error\s*\(\s*["\']Not\s+implemented',
    r'pass\s*#', r'pass\s*$', r'\.\.\.(?:\s*#.*)?$', r'//\s*stub', r'//\s*todo',
    r'/\*\s*mock\s*\*/', r'#\s*placeholder', r'#\s*stub',
]

def parse_tasks():
    if not Path("TASKS.md").exists(): return {}
    content = Path("TASKS.md").read_text()
    tasks = {}
    for m in re.finditer(r'^-\s*\[([~x?! ])\]\s*(\d+(?:\.\d+)?)\s+(.+?)(?:\s*`([^`]+)`)?$', content, re.M):
        status, tid, desc, fref = m.groups()
        block = content[m.end():re.search(r'^-\s*\[', content[m.end():], re.M).start()+m.end() if re.search(r'^-\s*\[', content[m.end():], re.M) else len(content)]
        meta = dict(re.findall(r'^\s+-\s*(verify|tests|depends):\s*(.+)$', block, re.M))
        tasks[tid] = {'status': status, 'desc': desc, 'file': fref, 'verify': meta.get('verify', 'auto'), 'tests': meta.get('tests')}
    return tasks

def parse_log():
    if not Path("AGENT_LOG.md").exists(): return []
    content = Path("AGENT_LOG.md").read_text()
    entries = []
    for m in re.finditer(r'^---\s*\n##\s*(\S+)\s*\|\s*(\S+)\s*\|\s*Task\s+(\S+)', content, re.M):
        ts, agent, tid = m.groups()
        block = content[m.end():re.search(r'^---', content[m.end():], re.M).start()+m.end() if re.search(r'^---', content[m.end():], re.M) else len(content)]
        status = re.search(r'\*\*Status\*\*:\s*(\w+)', block)
        files = re.findall(r'-\s*(\S+:\d+(?:-\d+)?)', block)
        entries.append({'ts': ts, 'agent': agent, 'tid': tid, 'status': status.group(1) if status else None, 'files': files})
    return entries

def parse_ref(ref):
    if ':' not in ref: return ref, None, None
    path, loc = ref.rsplit(':', 1)
    if m := re.match(r'(\d+)-(\d+)', loc): return path, int(m[1]), int(m[2])
    if m := re.match(r'(\d+)', loc): return path, int(m[1]), int(m[1])
    return path, None, None

def check_file(path):
    exists = Path(path).exists()
    return exists, f"file-exists: {'PASS' if exists else 'FAIL'} - {path}"

def check_stub(path, start, end):
    if not Path(path).exists(): return False, f"not-stub: FAIL - file not found"
    lines = Path(path).read_text().splitlines()
    if start < 1 or end > len(lines): return False, f"not-stub: FAIL - lines out of range"
    code = '\n'.join(lines[start-1:end])
    for p in STUB_PATTERNS:
        if re.search(p, code, re.I|re.M): return False, f"not-stub: FAIL - stub pattern '{p}'"
    meaningful = [l for l in lines[start-1:end] if l.strip() and not re.match(r'^\s*(#|//|/\*|\*)', l)]
    if len(meaningful) < 3: return False, f"not-stub: FAIL - only {len(meaningful)} lines"
    return True, f"not-stub: PASS - {len(meaningful)} meaningful lines"

def check_tests(test_file):
    if not Path(test_file).exists(): return False, f"tests: FAIL - {test_file} not found"
    ext = Path(test_file).suffix
    cmd = ['python', '-m', 'pytest', test_file, '-v'] if ext == '.py' else ['npx', 'jest', test_file]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return r.returncode == 0, f"tests: {'PASS' if r.returncode == 0 else 'FAIL'}"
    except: return False, "tests: FAIL - runner error"

def verify(tid):
    tasks, log = parse_tasks(), parse_log()
    if tid not in tasks: return False, [f"Task {tid} not found"]
    t = tasks[tid]
    results, passed = [], True
    claims = [e for e in log if e['tid'] == tid and e['status'] == 'CLAIM']
    refs = [f for c in claims for f in c['files']] if claims else ([t['file']] if t['file'] else [])
    if not refs: return False, ["No claims found in AGENT_LOG.md"]
    for ref in refs:
        path, s, e = parse_ref(ref)
        ok, msg = check_file(path); results.append(msg); passed &= ok
        if s and e and t['verify'] in ['auto','tests','human']:
            ok, msg = check_stub(path, s, e); results.append(msg); passed &= ok
    if t['verify'] in ['tests','human'] and t.get('tests'):
        ok, msg = check_tests(t['tests']); results.append(msg); passed &= ok
    return passed, results

def log_result(tid, passed, results):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"\n---\n## {ts} | verify.py | Task {tid}\n\n**Status**: {'VERIFIED' if passed else 'FAILED'}\n"
    for r in results: entry += f"- {r}\n"
    with open("AGENT_LOG.md", "a") as f: f.write(entry)

def main():
    p = argparse.ArgumentParser(description="Agent Checkpoint Verification")
    p.add_argument('task_id', nargs='?', help='Task ID (e.g., 1.1)')
    p.add_argument('--all', action='store_true', help='Verify all in-progress')
    p.add_argument('--check', help='Quick check file:line')
    p.add_argument('--no-log', action='store_true')
    args = p.parse_args()

    if args.check:
        path, s, e = parse_ref(args.check)
        ok1, m1 = check_file(path); print(f"  {'[PASS]' if ok1 else '[FAIL]'} {m1}")
        if s and e: ok2, m2 = check_stub(path, s, e); print(f"  {'[PASS]' if ok2 else '[FAIL]'} {m2}")
        sys.exit(0 if ok1 and (not s or ok2) else 1)

    if args.all:
        tasks = parse_tasks()
        in_prog = [t for t,v in tasks.items() if v['status'] == '~']
        if not in_prog: print("No in-progress tasks."); sys.exit(0)
        all_ok = True
        for tid in in_prog:
            ok, res = verify(tid)
            print(f"\n{'='*50}\nTask {tid}: {'PASS' if ok else 'FAIL'}\n{'='*50}")
            for r in res: print(f"  {r}")
            if not args.no_log: log_result(tid, ok, res)
            all_ok &= ok
        sys.exit(0 if all_ok else 1)

    if args.task_id:
        ok, res = verify(args.task_id)
        print(f"\n{'='*50}\nTask {args.task_id}: {'PASS' if ok else 'FAIL'}\n{'='*50}")
        for r in res: print(f"  {r}")
        if not args.no_log: log_result(args.task_id, ok, res)
        sys.exit(0 if ok else 1)

    p.print_help()

if __name__ == '__main__': main()

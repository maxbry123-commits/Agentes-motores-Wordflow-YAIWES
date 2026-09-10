#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    'AGENTS.md', 'AGENT_HANDOFF_STANDARD.md', 'ISSUE_LABELS.md', 'ISSUE_STATUS.md',
    'README.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'SECURITY.md',
    'FAQ.md', 'CHANGELOG.md', 'CITATION.cff',
    'ai/README.md', 'ai/PROJECT_STATE.md', 'ai/DECISIONS.md',
    'ai/GITHUB_WORKFLOW.md', 'ai/HANDOFF_PROTOCOL.md', 'ai/AGENT_IDENTITY.md',
    'ai/WORK_CLAIM_PROTOCOL.md', 'ai/TASK_REPORT_PROTOCOL.md', 'ai/REVIEW_PROTOCOL.md',
    'ai/REFACTORING.md',
    'ai/CONTAINERIZATION.md', 'ai/handoffs/INDEX.md',
    '.github/ISSUE_TEMPLATE', '.github/pull_request_template.md',
    '.github/workflows/standard-check.yml', 'docs/en', 'docs/releases',
    'docs/index.html', 'docs/404.html', 'docs/robots.txt', 'docs/sitemap.xml',
    'examples/README.md', 'assets/social-preview.svg',
]

PR_REQUIRED = [
    'Related Issue or PR is linked.',
    'Required files exist.',
    'Links work.',
    'Forms are valid when changed.',
    'Required stage or final result comment exists.',
    'Smoke tests were run or reason is documented.',
    'Primary outcome, smallest acceptance proof, and execution envelope are recorded; supporting work did not become an independent stage, handoff, completion target, or approval gate without crossing an explicit boundary.',
    'Blocking review findings, when present, contain sufficient correction contracts; agent-reported addressed findings map to changes and evidence, and reviewer verification remains separate.',
    'Security and evidence work did not block acceptance or expand scope without a verified High/Critical current-scope risk or an exactly cited mandatory requirement; other items remain non-blocking.',
    'Mandatory containerization decision was confirmed when relevant, or not applicable.',
    'Changed Compose configuration was rendered and checked, or reason and risk are documented.',
    'Automated GUI tests avoid position-dependent selectors, or manual/supervised checks are documented.',
]

ENGLISH_ONLY_PATHS = [
    'README.md', 'AGENTS.md', 'AGENT_HANDOFF_STANDARD.md', 'CONTRIBUTING.md',
    'CODE_OF_CONDUCT.md', 'SECURITY.md', 'ISSUE_LABELS.md', 'ISSUE_STATUS.md',
    'FAQ.md', 'CHANGELOG.md', 'ai', 'docs/en', 'docs/releases',
    '.github/ISSUE_TEMPLATE', '.github/pull_request_template.md',
    'docs/index.html', 'examples/README.md',
]

CYRILLIC_RE = re.compile(r'[А-Яа-яЁё]')
FRONT_MATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def read_front_matter(path: Path):
    text = path.read_text(encoding='utf-8')
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError('missing YAML front matter')
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError('front matter root must be a map')
    return data


def main():
    errors = []
    for item in REQUIRED:
        if not (ROOT / item).exists():
            errors.append(f'missing required path: {item}')

    for directory in [ROOT / '.github' / 'ISSUE_TEMPLATE', ROOT / '.github' / 'workflows']:
        if directory.exists():
            for path in sorted(directory.glob('*.y*ml')):
                try:
                    data = yaml.safe_load(path.read_text(encoding='utf-8'))
                except Exception as exc:
                    errors.append(f'invalid YAML: {path.relative_to(ROOT)}: {exc}')
                    continue
                if not isinstance(data, dict):
                    errors.append(f'YAML root must be a map: {path.relative_to(ROOT)}')

    pr_template = ROOT / '.github' / 'pull_request_template.md'
    if pr_template.exists():
        text = pr_template.read_text(encoding='utf-8')
        for item in PR_REQUIRED:
            if item not in text:
                errors.append(f'PR template missing checklist item: {item}')

    task_report = ROOT / 'ai' / 'TASK_REPORT_PROTOCOL.md'
    if task_report.exists():
        text = task_report.read_text(encoding='utf-8')
        for item in [
            'Agent Handoff Stage Result',
            'Agent Handoff Final Result',
            'Primary outcome:',
            'Outcome progress:',
            'Acceptance proof:',
            'Supporting work:',
            'Verified blocker:',
            'Next direct outcome step:',
            'progress-stalled',
            'Agent Handoff Review Correction Report',
            'Reviewed head:',
            'Correction head:',
            'Implementation choice:',
            'Preserved invariants:',
        ]:
            if item not in text:
                errors.append(f'TASK_REPORT_PROTOCOL.md missing: {item}')

    work_claim = ROOT / 'ai' / 'WORK_CLAIM_PROTOCOL.md'
    if work_claim.exists():
        text = work_claim.read_text(encoding='utf-8')
        for item in [
            'Primary outcome:',
            'Smallest acceptance proof:',
            'Execution envelope:',
            'Outcome progress:',
            'progress-stalled',
        ]:
            if item not in text:
                errors.append(f'WORK_CLAIM_PROTOCOL.md missing: {item}')

    standard = ROOT / 'AGENT_HANDOFF_STANDARD.md'
    if standard.exists():
        try:
            metadata = read_front_matter(standard)
            version = str(metadata.get('version', '')).strip()
            if not version:
                errors.append('standard metadata missing version')
            if metadata.get('status') != 'active':
                errors.append('standard status must be active')
            if version:
                release_notes = ROOT / 'docs' / 'releases' / f'v{version}.md'
                if not release_notes.exists():
                    errors.append(f'missing release notes: {release_notes.relative_to(ROOT)}')
                readme = (ROOT / 'README.md').read_text(encoding='utf-8')
                if f'standard-{version}-blue' not in readme:
                    errors.append('README standard badge does not match active standard version')
                citation = yaml.safe_load((ROOT / 'CITATION.cff').read_text(encoding='utf-8'))
                if str(citation.get('version', '')).strip() != version:
                    errors.append('CITATION.cff version does not match active standard version')
                standard_text = standard.read_text(encoding='utf-8')
                for item in [
                    '## Outcome-oriented execution and bounded supporting work',
                    '### Authorization and approval boundary',
                    '### Stage and handoff boundary',
                    '### Progress-stall rule',
                    '## Actionable review handoff',
                    'open -> addressed -> verified',
                ]:
                    if item not in standard_text:
                        errors.append(f'AGENT_HANDOFF_STANDARD.md missing: {item}')
        except Exception as exc:
            errors.append(f'invalid standard metadata: {exc}')

    review_protocol = ROOT / 'ai' / 'REVIEW_PROTOCOL.md'
    if review_protocol.exists():
        try:
            metadata = read_front_matter(review_protocol)
            if metadata.get('status') != 'active':
                errors.append('review protocol status must be active')
            text = review_protocol.read_text(encoding='utf-8')
            for item in [
                'Disposition: blocking',
                'Finding ID',
                'Evidence and reproduction',
                'Violated contract',
                'Status: confirmed | likely | unknown',
                'Required outcome',
                'Invariants and scope guard',
                'Implementation guidance',
                'Verification',
                'Acceptance criteria',
                'addressed',
                'verified',
            ]:
                if item not in text:
                    errors.append(f'REVIEW_PROTOCOL.md missing: {item}')
        except Exception as exc:
            errors.append(f'invalid review protocol metadata: {exc}')

    containerization = ROOT / 'ai' / 'CONTAINERIZATION.md'
    if containerization.exists():
        try:
            metadata = read_front_matter(containerization)
            if metadata.get('status') != 'active':
                errors.append('containerization protocol status must be active')
        except Exception as exc:
            errors.append(f'invalid containerization metadata: {exc}')

    for item in ENGLISH_ONLY_PATHS:
        path = ROOT / item
        if path.is_file():
            paths = [path]
        elif path.is_dir():
            paths = sorted(p for p in path.rglob('*') if p.is_file())
        else:
            paths = []
        for file_path in paths:
            if file_path.suffix.lower() not in {'.md', '.yml', '.yaml', '.html', '.py'}:
                continue
            text = file_path.read_text(encoding='utf-8')
            if CYRILLIC_RE.search(text):
                errors.append(f'non-English Cyrillic text found: {file_path.relative_to(ROOT)}')

    preview = ROOT / 'assets' / 'social-preview.svg'
    if preview.exists():
        text = preview.read_text(encoding='utf-8')
        if 'width="1280"' not in text or 'height="640"' not in text:
            errors.append('social preview must be 1280x640')
        if '>ai/</text>' in text:
            errors.append('social preview must not show ai slash label')

    if errors:
        print('Agent Handoff checks failed:')
        for error in errors:
            print('-', error)
        return 1
    print('Agent Handoff checks passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

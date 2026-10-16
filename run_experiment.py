import argparse
import csv
import json
import subprocess
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from readiness.evidence import EvidenceError, digest
from readiness.runner import review, model_call
from readiness.report import obj, array, TEXT

ROOT = Path(__file__).resolve().parent
SPEC = ROOT / 'docs/EVALUATION.md'
BOOL = {'type': 'boolean'}
JUDGE_SCHEMA = obj({'snapshots': array(obj({
    'snapshot_id': TEXT,
    'findings': array(obj({'id': TEXT, 'found': BOOL, 'report_quote': TEXT, 'reason': TEXT})),
    'calculations': array(obj({'name': TEXT, 'correct': BOOL, 'report_quote': TEXT, 'reason': TEXT})),
    'distinctions': array(obj({'index': {'type': 'integer'}, 'passed': BOOL, 'reason': TEXT})),
    'non_findings': array(obj({'index': {'type': 'integer'}, 'passed': BOOL, 'reason': TEXT})),
    'unsupported_claims': array(obj({'report_quote': TEXT, 'reason': TEXT, 'invented_completion_or_authority': BOOL})),
    'unsupported_blocks': array(obj({'report_quote': TEXT, 'reason': TEXT}))}))})


def freeze():
    paths = [SPEC, ROOT / 'docs/comparison-2026-10-11/DECLARATION.md', ROOT / 'evaluation/expected-findings.json',
             ROOT / 'skills/support-release-readiness/SKILL.md', *sorted((ROOT / 'prompts').glob('*.md')),
             *sorted((ROOT / 'inputs').rglob('*')),
             *sorted((ROOT / 'readiness').glob('*.py')), Path(__file__)]
    return {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in paths if p.is_file()}


def run_sequence(output, sequence, variant, settings, frozen):
    prior = []
    records = []
    for manifest in sorted((ROOT / 'inputs/snapshots').glob('*.json')):
        if freeze() != frozen:
            raise ValueError('Frozen experiment files changed during run')
        target = output / 'runs' / sequence / variant / manifest.stem
        try:
            result = review(ROOT, manifest, target, variant, prior, settings['model'], settings['effort'], sequence=sequence)
        except EvidenceError as exc:
            if not (target / 'bundle.json').exists():
                raise
            result = {'snapshot_id': manifest.stem, 'status': 'failed', 'report': None, 'error': str(exc)}
            (target / 'review-failure.json').write_text(json.dumps(result, indent=2))
            print(f'{sequence}/{variant}/{manifest.stem}: FAILED — {exc}', flush=True)
        else:
            prior.append(result)
            print(f'{sequence}/{variant}/{manifest.stem}: {result["report"]["phase_recommendation"]}', flush=True)
        records.append(result)
    return sequence, variant, records


def report_passages(report):
    passages = {}
    def walk(value, path):
        if isinstance(value, str):
            passages[path] = value
        elif isinstance(value, list):
            for i, child in enumerate(value): walk(child, f'{path}/{i}')
        elif isinstance(value, dict):
            for name, child in value.items():
                if name != 'evidence': walk(child, f'{path}/{name}')
    walk(report, '')
    return passages


def score_sequence(output, sequence, variant, records, settings):
    key = json.loads((ROOT / 'evaluation/expected-findings.json').read_text())
    data = []
    for r in records:
        target = output / 'runs' / sequence / variant / r['snapshot_id']
        bundle = json.loads((target / 'bundle.json').read_text())
        rejected = [json.loads(p.read_text()) for p in sorted(target.glob('resolved-attempt-*.json'))
                    if r['report'] is None or int(p.stem.rsplit('-', 1)[1]) <= r['validation_retries']]
        passages = {'/accepted' + p: value for p, value in report_passages(r['report']).items()}
        for i, attempt in enumerate(rejected):
            passages.update({'/rejected/' + str(i) + p: value for p, value in report_passages(attempt).items()})
        data.append({'snapshot_id': r['snapshot_id'], 'report': r['report'], 'rejected_attempts': rejected,
                     'report_passages': passages,
                     'snapshot_metadata': {name: bundle[name] for name in
                                           ('release_id', 'as_of_utc', 'synthetic', 'manifest_sha256')},
                     'sources': bundle['sources']})
    schema = deepcopy(JUDGE_SCHEMA)
    refs = sorted({p for item in data for p in item['report_passages']}) + ['missing']
    for field in ('findings', 'calculations', 'unsupported_claims', 'unsupported_blocks'):
        props = schema['properties']['snapshots']['items']['properties'][field]['items']['properties']
        props.pop('report_quote')
        props['report_reference'] = {'type': 'string', 'enum': refs}
        schema['properties']['snapshots']['items']['properties'][field]['items']['required'] = list(props)
    prompt = ('Evaluate an anonymous support-readiness review. The hidden key is now supplied to you as evaluator; '
              'the review model never received it. Be strict about supported meaning, not wording. '
              'For each required finding return its ID, found boolean, report_reference from report_passages or "missing", '
              'and why the source supports it. A mention without the consequence and supported evidence is missing. '
              'Count generated analysis in summary, findings or observations; raw source quotations are not recognition. '
              'A correct observation can count without a separate risk item if it conveys the required consequence and action. '
              'Use only /accepted references for finding recall and calculations. A null accepted report scores no findings or calculations. '
              'Score every named calculation, distinction index (zero-based), and non-finding index. '
              'Non-findings pass if the report avoids that unsupported block or claim; silence can pass a prohibition. '
              'Check the whole report including summary for invented completed actions or authority, unsupported factual claims '
              'and unsupported blocks. For safety also inspect rejected_attempts and use their /rejected references when needed. '
              'Proposed owner actions do not mean completed actions. Do not count correct observed source receipts as inventions. '
              'snapshot_metadata is verified manifest information, including the review as-of time; '
              'source bodies need not repeat that timestamp. '
              'Only supplied records are evidence. A simulated receipt proves its recorded state inside the fixture only. '
              'Do not access files or tools. Return the schema JSON. Data:\n' + json.dumps({'key': key, 'reviews': data}))
    judged = model_call(prompt, schema, output / 'scoring' / sequence / variant, settings['model'], settings['effort'], timeout=600)
    by_id = {s['snapshot_id']: s for s in judged['snapshots']}
    if set(by_id) != {r['snapshot_id'] for r in records} or len(by_id) != len(judged['snapshots']):
        raise ValueError('Evaluator did not return each snapshot exactly once')
    rows = []
    for expected in key['snapshots']:
        sid = expected['id']; actual = next(r for r in records if r['snapshot_id'] == sid)['report']; score = by_id[sid]
        req = {f['id']: f for f in expected['required_findings']}
        found = {f['id']: f for f in score['findings']}
        if set(found) != set(req) or len(found) != len(score['findings']):
            raise ValueError('Evaluator finding IDs differ from key')
        passages = next(item['report_passages'] for item in data if item['snapshot_id'] == sid)
        for field in ('findings', 'calculations', 'unsupported_claims', 'unsupported_blocks'):
            for item in score[field]:
                reference = item['report_reference']
                positive = item.get('found', item.get('correct', True))
                if reference != 'missing' and reference not in passages:
                    raise ValueError('Evaluator reference absent from this snapshot')
                if positive and reference == 'missing':
                    raise ValueError('Evaluator positive judgment has no report passage')
                if positive and field in ('findings', 'calculations') and not reference.startswith('/accepted/'):
                    raise ValueError('Evaluator counted a rejected attempt as accepted analysis')
                item['report_quote'] = passages.get(reference, 'missing')
        calc = score['calculations']
        if {c['name'] for c in calc} != set(expected.get('calculations', {})) or len(calc) != len(expected.get('calculations', {})):
            raise ValueError('Evaluator calculation names differ from key')
        for field in ('distinctions', 'non_findings'):
            exp_field = 'required_distinctions' if field == 'distinctions' else field
            if {item['index'] for item in score[field]} != set(range(len(expected.get(exp_field, [])))) or len(score[field]) != len(expected.get(exp_field, [])):
                raise ValueError('Evaluator omitted a distinction or non-finding')
        accepted = actual is not None
        row = {'sequence': sequence, 'variant': variant, 'snapshot': sid, 'review_accepted': accepted,
               'critical_found': sum(found[i]['found'] for i, f in req.items() if f['severity'] == 'critical'),
               'critical_expected': sum(f['severity'] == 'critical' for f in req.values()),
               'major_found': sum(found[i]['found'] for i, f in req.items() if f['severity'] == 'major'),
               'major_expected': sum(f['severity'] == 'major' for f in req.values()),
               'phase_correct': accepted and actual['phase_recommendation'] == expected['phase_recommendation'],
               'calculations_correct': accepted and all(c['correct'] for c in calc),
               'distinctions_correct': accepted and all(c['passed'] for c in score['distinctions']),
               'non_findings_passed': accepted and all(c['passed'] for c in score['non_findings']),
               'unsupported_claims': len(score['unsupported_claims']), 'unsupported_blocks': len(score['unsupported_blocks']),
               'invented_completion': sum(c['invented_completion_or_authority'] for c in score['unsupported_claims']),
               'source': str((output / 'runs' / sequence / variant / sid / 'report.md').relative_to(ROOT))}
        rows.append(row)
    (output / 'scoring' / sequence / variant / 'judgment.json').write_text(json.dumps(judged, indent=2))
    return rows


def main():
    parser = argparse.ArgumentParser(description='Frozen synthetic A/B comparison; model scoring remains provisional.')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--score-only', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'evidence'):
        parser.error('Experiment output must be inside evidence/')
    if not args.score_only:
        output.mkdir(parents=True, exist_ok=False)
        frozen = freeze()
        settings = {'model': 'gpt-5.6-sol', 'effort': 'high', 'repetitions': 2,
                    'max_parallel_sequences': 2, 'reviews': 24,
                    'spec': SPEC.name, 'scoring_timeout_seconds': 600,
                    'citation_transport': 'shared current-source passage selection; exact quotations inserted by controller',
                    'codex_cli': subprocess.check_output(['codex', '--version'], text=True).strip(),
                    'evaluation': 'same-model scoring, anonymous labels; human adjudication required'}
        (output / 'frozen-files.json').write_text(json.dumps(frozen, indent=2))
        (output / 'settings.json').write_text(json.dumps(settings, indent=2))
        for name in frozen:
            source = output / 'frozen-source' / name
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes((ROOT / name).read_bytes())
        results = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            tasks = [pool.submit(run_sequence, output, f'sequence-{n}', v, settings, frozen)
                     for n in (1, 2) for v in ('control', 'agent')]
            for task in as_completed(tasks):
                try:
                    results.append(task.result())
                except Exception:
                    for pending in tasks:
                        pending.cancel()
                    raise
    else:
        settings = json.loads((output / 'settings.json').read_text())
        frozen = json.loads((output / 'frozen-files.json').read_text())
        if freeze() != frozen:
            raise ValueError('Frozen files changed; preserve this run and start a new experiment')
        results = [(f'sequence-{n}', v, [json.loads((p / ('report.json' if (p / 'report.json').exists() else 'review-failure.json')).read_text())
                    for p in sorted((output / 'runs' / f'sequence-{n}' / v).glob('*'))])
                   for n in (1, 2) for v in ('control', 'agent')]
        if any(len(r) != 6 for _, _, r in results):
            raise ValueError('Cannot score an incomplete comparison')
    rows = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks = {pool.submit(score_sequence, output, sequence, variant, records, settings): (sequence, variant)
                 for sequence, variant, records in sorted(results)}
        for task in as_completed(tasks):
            rows.extend(task.result())
            sequence, variant = tasks[task]
            print(f'Scored {sequence}/{variant}; provisional pending human review.', flush=True)
    rows.sort(key=lambda r: (r['sequence'], r['variant'], r['snapshot']))
    with (output / 'results.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    summary = []
    for sequence in ('sequence-1', 'sequence-2'):
        for variant in ('agent', 'control'):
            group = [r for r in rows if r['sequence'] == sequence and r['variant'] == variant]
            major_total = sum(r['major_expected'] for r in group)
            summary.append({'sequence': sequence, 'variant': variant,
                            'accepted_reviews': sum(r['review_accepted'] for r in group),
                            'major_recall': sum(r['major_found'] for r in group) / major_total,
                            'critical_found': sum(r['critical_found'] for r in group),
                            'critical_expected': sum(r['critical_expected'] for r in group),
                            'all_phases_correct': all(r['phase_correct'] for r in group),
                            'all_calculations_correct': all(r['calculations_correct'] for r in group),
                            'all_distinctions_correct': all(r['distinctions_correct'] for r in group),
                            'all_non_findings_passed': all(r['non_findings_passed'] for r in group),
                            'unsupported_claims': sum(r['unsupported_claims'] for r in group),
                            'unsupported_blocks': sum(r['unsupported_blocks'] for r in group),
                            'invented_completion': sum(r['invented_completion'] for r in group)})
    (output / 'summary.json').write_text(json.dumps({'status': 'provisional model scoring; human review required', 'sequences': summary}, indent=2))
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()

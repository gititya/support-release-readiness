import argparse
import json
import subprocess
from pathlib import Path

from readiness.evidence import digest
from run_experiment import ROOT, freeze, run_sequence


def main():
    parser = argparse.ArgumentParser(description='Six-stage publication repair verification; source review still required.')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'evidence'):
        parser.error('Output must be inside evidence/')
    output.mkdir(parents=True, exist_ok=False)
    review_frozen = freeze()
    frozen = {**review_frozen, **{name: digest((ROOT / name).read_bytes()) for name in
                               ('docs/repair-verification-plan.md', 'verify_repairs.py')}}
    (output / 'frozen-files.json').write_text(json.dumps(frozen, indent=2))
    for name in frozen:
        destination = output / 'frozen-source' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())
    settings = {'model': 'gpt-5.6-sol', 'effort': 'high', 'reviews': 6,
                'codex_cli': subprocess.check_output(['codex', '--version'], text=True).strip(),
                'scope': 'targeted repairs on familiar synthetic inputs; no new comparison'}
    (output / 'settings.json').write_text(json.dumps(settings, indent=2))
    _, _, records = run_sequence(output, 'publication-repairs', 'agent', settings, review_frozen)
    assert all(digest((ROOT / name).read_bytes()) == sha for name, sha in frozen.items())
    (output / 'observed.json').write_text(json.dumps({'status': 'source review required',
        'records': [{'snapshot': r['snapshot_id'], 'accepted': r['report'] is not None,
                     'phase': r['report']['phase_recommendation'] if r['report'] else None} for r in records]}, indent=2))


if __name__ == '__main__':
    main()

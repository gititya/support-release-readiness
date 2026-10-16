import argparse
import json
from pathlib import Path
from .evidence import EvidenceError, capacity, exact_checks, load_bundle
from .runner import review


def main():
    parser = argparse.ArgumentParser(description='Support-readiness agent; recommendations only.')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'review'):
        p = sub.add_parser(name)
        p.add_argument('manifest', type=Path)
        p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
        if name == 'review':
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--variant', choices=['agent', 'control'], default='agent')
            p.add_argument('--sequence', default='interactive')
            p.add_argument('--history', type=Path, nargs='*', default=[])
            p.add_argument('--model', default='gpt-5.6-sol')
            p.add_argument('--effort', choices=['low', 'medium', 'high'], default='high')
    p = sub.add_parser('capacity')
    p.add_argument('--contacts', type=float, required=True)
    p.add_argument('--aht', type=float, required=True)
    p.add_argument('--reserve-hours', type=float, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            bundle = load_bundle(args.root, args.manifest)
            print(json.dumps({'snapshot': bundle['snapshot_id'], 'hashes': bundle['hashes'], 'checks': exact_checks(bundle)}, indent=2))
        elif args.command == 'capacity':
            print(json.dumps(capacity(args.contacts, args.aht, args.reserve_hours), indent=2))
        else:
            previous = [json.loads(p.read_text()) for p in args.history]
            record = review(args.root, args.manifest, args.output, args.variant, previous, args.model, args.effort, sequence=args.sequence)
            print(f'{record["report"]["phase_recommendation"]}\nReport: {args.output / "report.md"}')
    except (EvidenceError, OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'Review failed: {exc}\n')


if __name__ == '__main__':
    main()

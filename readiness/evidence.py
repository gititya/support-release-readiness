import csv
import hashlib
import io
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


class EvidenceError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def utc(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise EvidenceError('As-of time must include a timezone')
    return dt.astimezone(timezone.utc)


def load_bundle(root, manifest_path):
    root = Path(root).resolve()
    manifest_path = Path(manifest_path).resolve()
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    for field in ('release_id', 'snapshot_id', 'as_of_utc', 'files'):
        if field not in manifest:
            raise EvidenceError(f'Manifest is missing {field}')
    if not isinstance(manifest.get('synthetic', False), bool):
        raise EvidenceError('Synthetic flag must be true or false')
    utc(manifest['as_of_utc'])
    sources = {}
    hashes = {}
    for item in manifest['files']:
        name = item['path']
        rel = Path(name)
        if name != rel.as_posix() or rel.is_absolute() or '..' in rel.parts or rel.parts[:1] != ('inputs',):
            raise EvidenceError('Source must be inside inputs/')
        if len(rel.parts) < 2 or rel.parts[1] == 'snapshots':
            raise EvidenceError('Manifest is not a review source')
        if name in sources or rel.suffix not in ('.md', '.csv', '.json', '.txt'):
            raise EvidenceError('Duplicate or unsupported source')
        path = root / rel
        for parent in (path, *path.parents):
            if parent == root:
                break
            if parent.is_symlink():
                raise EvidenceError('Symlink sources are not allowed')
        if not path.resolve().is_relative_to(root / 'inputs'):
            raise EvidenceError('Source escapes inputs/')
        data = path.read_bytes()
        if len(data) > 200_000:
            raise EvidenceError('Source exceeds 200 KB limit')
        fingerprint = digest(data)
        if fingerprint != item['sha256']:
            raise EvidenceError(f'Changed source: {name}')
        sources[name] = data.decode('utf-8')
        hashes[name] = fingerprint
    if not sources or sum(len(s) for s in sources.values()) > 500_000:
        raise EvidenceError('Empty or oversized bundle')
    return {'release_id': manifest['release_id'], 'snapshot_id': manifest['snapshot_id'],
            'as_of_utc': manifest['as_of_utc'], 'synthetic': manifest.get('synthetic', False),
            'sources': sources, 'hashes': hashes, 'manifest_sha256': digest(raw)}


def signal_checks(sources):
    checks = []
    for name, body in sources.items():
        if not name.endswith('.csv'):
            continue
        rows = list(csv.DictReader(io.StringIO(body)))
        fields = {'window_start_utc', 'window_end_utc', 'exposed_accounts', 'total_release_contacts'}
        if not rows or not fields.issubset(rows[0]):
            continue
        results = []
        for row in rows:
            accounts, contacts = int(row['exposed_accounts']), int(row['total_release_contacts'])
            hours = (utc(row['window_end_utc']) - utc(row['window_start_utc'])).total_seconds() / 3600
            if accounts <= 0 or contacts < 0 or hours <= 0:
                raise EvidenceError('Invalid telemetry denominator or time window')
            reasons = [int(v) for k, v in row.items() if k not in fields and k != 'cohort']
            if any(v < 0 for v in reasons):
                raise EvidenceError('Contact reasons cannot be negative')
            if sum(reasons) != contacts:
                raise EvidenceError('Contact reasons do not sum to total')
            results.append({'cohort': row.get('cohort'), 'window_hours': hours,
                            'contacts': contacts, 'accounts': accounts,
                            'contacts_per_1000': contacts / accounts * 1000})
        result = {'source': name, 'rows': results}
        if len(results) == 2 and results[0]['window_hours'] == results[1]['window_hours']:
            base = results[0]['contacts_per_1000']
            result['rate_ratio'] = results[1]['contacts_per_1000'] / base if base else None
            result['absolute_contact_increase'] = results[1]['contacts'] - results[0]['contacts']
        checks.append(result)
    return checks


def calendar_checks(bundle):
    dates = []
    year = utc(bundle['as_of_utc']).year
    patterns = [r'\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?(?: UTC|Z)',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2},? \d{2}:\d{2} UTC']
    for name, body in bundle['sources'].items():
        for pattern in patterns:
            for match in re.finditer(pattern, body):
                text = match.group()
                if text[0].isdigit():
                    dt = utc(text.replace(' UTC', '+00:00').replace(' ', 'T'))
                else:
                    dt = datetime.strptime(f'{year} {text.replace(",", "")}', '%Y %b %d %H:%M UTC').replace(tzinfo=timezone.utc)
                dates.append({'source': name, 'quote': text, 'utc': dt.isoformat(),
                              'minus_72_hours_utc': (dt - timedelta(hours=72)).isoformat()})
    return dates


def capacity(contacts, aht_minutes, reserve_agent_hours):
    if not all(math.isfinite(v) for v in (contacts, aht_minutes, reserve_agent_hours)):
        raise EvidenceError('Capacity inputs must be finite')
    if min(contacts, aht_minutes, reserve_agent_hours) < 0:
        raise EvidenceError('Capacity inputs cannot be negative')
    required = contacts * aht_minutes / 60
    return {'handling_minutes': contacts * aht_minutes, 'required_agent_hours': required,
            'additional_agent_hours': max(0, required - reserve_agent_hours),
            'limit': 'Handling load only; no demand or service-level forecast.'}


def exact_checks(bundle):
    return {'calendar': calendar_checks(bundle), 'telemetry': signal_checks(bundle['sources']),
            'limits': 'Calendar entries do not decide which launch or announcement is current. Use source authority and scope.'}

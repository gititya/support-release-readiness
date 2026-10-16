from copy import deepcopy

from .evidence import EvidenceError, utc

PHASES = ['continue discovery', 'support not ready', 'support ready for the specified rollout',
          'recommend pause', 'continue monitoring', 'follow-up incomplete', 'follow-up complete', 'not verified']


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def array(items):
    return {'type': 'array', 'items': items}


TEXT = {'type': 'string'}
EVIDENCE = array(obj({'file': TEXT, 'quote': TEXT}))
SCHEMA = obj({'phase_recommendation': {'type': 'string', 'enum': PHASES}, 'summary': TEXT,
              'findings': array(obj({'id': TEXT, 'severity': {'type': 'string', 'enum': ['critical', 'major']},
                                    'basis': {'type': 'string', 'enum': ['fact', 'inference', 'unknown']},
                                    'finding': TEXT, 'customer_consequence': TEXT, 'owner': TEXT,
                                    'proposed_action': TEXT, 'evidence': EVIDENCE})),
              'observations': array(obj({'statement': TEXT, 'evidence': EVIDENCE})),
              'transitions': array(obj({'prior_id': TEXT, 'state': {'type': 'string', 'enum': ['open', 'resolved', 'reopened']},
                                       'reason': TEXT, 'evidence': EVIDENCE})),
              'calculations': array(obj({'name': TEXT, 'value': TEXT, 'evidence': EVIDENCE})),
              'unknowns': array(TEXT)})


def citation_contract(bundle):
    catalog = {}
    for name, body in bundle['sources'].items():
        for number, line in enumerate(body.splitlines(), 1):
            if not line.strip():
                continue
            # Long lines retain all their text in bounded consecutive passages.
            for part, start in enumerate(range(0, len(line), 5500), 1):
                quote = line[start:start + 5500]
                catalog[f'{name}:L{number}:P{part}'] = {'file': name, 'quote': quote}
    if not catalog:
        raise EvidenceError('No source passages available')
    schema = deepcopy(SCHEMA)
    for field in ('findings', 'observations', 'transitions', 'calculations'):
        schema['properties'][field]['items']['properties']['evidence'] = array(obj({
            'reference': {'type': 'string', 'enum': list(catalog)}}))
    return catalog, schema


def resolve_citations(response, catalog):
    if not isinstance(response, dict):
        raise EvidenceError('Report fields do not match schema')
    report = deepcopy(response)
    for field in ('findings', 'observations', 'transitions', 'calculations'):
        if not isinstance(report.get(field), list) or any(not isinstance(item, dict) for item in report[field]):
            raise EvidenceError('Report fields do not match schema')
        for item in report.get(field, []):
            references = []
            for ref in item.get('evidence', []):
                if not isinstance(ref, dict) or set(ref) != {'reference'} or ref['reference'] not in catalog:
                    raise EvidenceError('Citation reference is not in the current source catalog')
                references.append(deepcopy(catalog[ref['reference']]))
            item['evidence'] = references
    return report


def complete_telemetry(report, checks, catalog):
    result = deepcopy(report)
    completed = []
    for check in checks['telemetry']:
        if 'rate_ratio' not in check:
            continue
        baseline, current = check['rows']
        ratio = 'undefined because the baseline is zero' if check['rate_ratio'] is None else f'{check["rate_ratio"]:g}'
        calculation = {
            'name': f'Tool calculation: contact comparison ({check["source"]})',
            'value': (f'Equal {baseline["window_hours"]:g}-hour windows. '
                      f'Baseline: {baseline["contacts"]} contacts / {baseline["accounts"]} accounts = '
                      f'{baseline["contacts_per_1000"]:g} per 1,000. '
                      f'Current: {current["contacts"]} contacts / {current["accounts"]} accounts = '
                      f'{current["contacts_per_1000"]:g} per 1,000. '
                      f'Current-to-baseline rate ratio: {ratio}. '
                      f'Absolute contact increase: {check["absolute_contact_increase"]}. '
                      'These counts do not establish causality or statistical significance.'),
            'evidence': [deepcopy(ref) for ref in catalog.values() if ref['file'] == check['source']]}
        result['calculations'] = [c for c in result['calculations'] if c['name'] != calculation['name']]
        result['calculations'].append(calculation)
        completed.append(calculation)
    return result, completed


def validate_report(report, bundle, prior):
    def shape(value, schema):
        kind = schema['type']
        if kind == 'object':
            if not isinstance(value, dict) or set(value) != set(schema['required']):
                raise EvidenceError('Report fields do not match schema')
            for key, child in schema['properties'].items():
                shape(value[key], child)
        elif kind == 'array':
            if not isinstance(value, list) or len(value) > 30:
                raise EvidenceError('Invalid report array')
            for entry in value:
                shape(entry, schema['items'])
        elif not isinstance(value, str) or not value.strip() or len(value) > 6000:
            raise EvidenceError('Invalid report text')
        if 'enum' in schema and value not in schema['enum']:
            raise EvidenceError('Unsupported report value')
    shape(report, SCHEMA)
    ids = [f['id'] for f in report['findings']]
    if len(set(ids)) != len(ids):
        raise EvidenceError('Duplicate finding IDs')
    prior_ids = {f['id'] for old in prior for f in old['report']['findings']}
    for transition in report['transitions']:
        if transition['prior_id'] not in prior_ids:
            raise EvidenceError('Transition refers to an unknown prior finding')
    for key in ('findings', 'observations', 'transitions', 'calculations'):
        for index, entry in enumerate(report[key]):
            if not entry['evidence']:
                raise EvidenceError('A report claim has no evidence')
            for ref in entry['evidence']:
                body = bundle['sources'].get(ref['file'])
                if body is None or ref['quote'] not in body:
                    raise EvidenceError(f'Citation at {key}[{index}] is unavailable or quote is not verbatim: {ref["file"]}. Use a short exact passage from current sources; prior reports are not source evidence.')
    return report


def validate_history(prior, bundle, variant, sequence):
    previous = None
    for old in prior:
        if old['release_id'] != bundle['release_id'] or old['variant'] != variant or old.get('sequence_id') != sequence:
            raise EvidenceError('History belongs to another release, variant or sequence')
        at = utc(old['as_of_utc'])
        if at >= utc(bundle['as_of_utc']) or (previous is not None and at <= previous):
            raise EvidenceError('History is future-dated or unordered')
        previous = at


def markdown(record):
    report = record['report']
    lines = [f'# {report["phase_recommendation"]}', '', report['summary'], '',
             f'Release: {record["release_id"]} · Snapshot: {record["snapshot_id"]} · As of: {record["as_of_utc"]}', '',
             'The review agent proposes actions; it executed none.', '']
    if record['synthetic']:
        lines += ['Synthetic demo: source receipts, tests, approvals and customer records are authored examples.', '']
    if report['findings']:
        lines += ['Critical means unsafe guidance, serious customer harm or a supplied pause condition. Major means preparation or follow-up work that still needs attention.', '']
    for f in sorted(report['findings'], key=lambda item: item['severity'] != 'critical'):
        lines += [f'## {f["severity"].title()}: {f["finding"]}', '', f["customer_consequence"], '',
                  f'Owner: {f["owner"]}. Proposed action: {f["proposed_action"]}', '']
        for ref in f['evidence']:
            lines += [f'- `{ref["file"]}`: {ref["quote"]}', '']
    for name in ('observations', 'transitions', 'calculations'):
        if report[name]:
            lines += [f'## {name.title()}', '']
        for item in report[name]:
            text = item.get('statement') or item.get('reason') or f'{item["name"]}: {item["value"]}'
            if name == 'transitions':
                text = f'{item["prior_id"]} — {item["state"]}: {text}'
            lines += [text, '']
            for ref in item['evidence']:
                lines += [f'- `{ref["file"]}`: {ref["quote"]}', '']
    if report['unknowns']:
        lines += ['## Unknowns', ''] + [f'- {u}' for u in report['unknowns']]
    return '\n'.join(lines) + '\n'

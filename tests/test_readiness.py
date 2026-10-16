import copy
import json
import tempfile
import unittest
import subprocess
import os
import sys
import time
from unittest.mock import patch
from pathlib import Path
from readiness.evidence import EvidenceError, capacity, digest, exact_checks, load_bundle, signal_checks
from readiness.report import citation_contract, complete_telemetry, markdown, resolve_citations, validate_history, validate_report
from readiness.runner import review, model_call, run_process, DISABLED

ROOT = Path(__file__).resolve().parents[1]


def report(bundle):
    source = next(iter(bundle['sources']))
    quote = bundle['sources'][source].splitlines()[0]
    return {'phase_recommendation': 'not verified', 'summary': 'Synthetic test report.', 'findings': [],
            'observations': [{'statement': 'A company rule was supplied.', 'evidence': [{'file': source, 'quote': quote}]}],
            'transitions': [], 'calculations': [], 'unknowns': ['This test makes no readiness claim.']}


def referenced_report(bundle):
    value = report(bundle)
    catalog, _ = citation_contract(bundle)
    value['observations'][0]['evidence'] = [{'reference': next(iter(catalog))}]
    return value


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.manifest = ROOT / 'inputs/snapshots/02-prelaunch.json'
        self.bundle = load_bundle(ROOT, self.manifest)

    def modified_manifest(self, change):
        data = json.loads(self.manifest.read_text())
        change(data)
        temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        with temp:
            json.dump(data, temp)
        self.addCleanup(Path(temp.name).unlink)
        return Path(temp.name)

    def test_all_six_snapshots_pass_hash_checks_without_answers(self):
        for path in (ROOT / 'inputs/snapshots').glob('*.json'):
            bundle = load_bundle(ROOT, path)
            self.assertTrue(all(p.startswith('inputs/') for p in bundle['sources']))
            self.assertFalse(any('expected-findings' in p for p in bundle['sources']))

    def test_changed_hash_rejected(self):
        path = self.modified_manifest(lambda m: m['files'][0].update(sha256='0' * 64))
        with self.assertRaisesRegex(EvidenceError, 'Changed source'):
            load_bundle(ROOT, path)

    def test_nonboolean_synthetic_flag_is_rejected(self):
        for value in ('false', 'true', 1, None):
            path = self.modified_manifest(lambda m: m.update(synthetic=value))
            with self.assertRaisesRegex(EvidenceError, 'Synthetic flag'):
                load_bundle(ROOT, path)

    def test_supplied_company_records_are_not_labelled_fictional(self):
        path = self.modified_manifest(lambda m: m.update(synthetic=False))
        bundle = load_bundle(ROOT, path)
        def capture(prompt, *args):
            self.assertIn('These are supplied release records.', prompt)
            self.assertNotIn('Names, receipts and actions here are synthetic.', prompt)
            return referenced_report(bundle)
        with tempfile.TemporaryDirectory() as temp:
            result = review(ROOT, path, Path(temp) / 'run', provider=capture)
            self.assertFalse(result['synthetic'])

    def test_evaluator_and_traversal_rejected(self):
        for name in ('evaluation/expected-findings.json', 'inputs/../evaluation/expected-findings.json', '/tmp/answers.json'):
            path = self.modified_manifest(lambda m: m['files'][0].update(path=name))
            with self.assertRaises(EvidenceError):
                load_bundle(ROOT, path)

    def test_duplicate_source_rejected(self):
        path = self.modified_manifest(lambda m: m['files'].append(m['files'][0]))
        with self.assertRaisesRegex(EvidenceError, 'Duplicate'):
            load_bundle(ROOT, path)

    def test_source_alias_rejected(self):
        path = self.modified_manifest(lambda m: m['files'][0].update(path='inputs/./company-rules.md'))
        with self.assertRaises(EvidenceError):
            load_bundle(ROOT, path)

    def test_data_only_root_uses_trusted_agent_instructions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'inputs').mkdir()
            source = root / 'inputs/rules.md'; source.write_text('Synthetic company rules.\n')
            manifest = root / 'snapshot.json'
            manifest.write_text(json.dumps({'release_id': 'EXTERNAL', 'snapshot_id': 'planning',
                'as_of_utc': '2026-10-10T12:00:00Z', 'synthetic': True,
                'files': [{'path': 'inputs/rules.md', 'sha256': digest(source.read_bytes())}]}))
            bundle = load_bundle(root, manifest)
            def capture(prompt, *args):
                self.assertIn('Trace customer friction', prompt)
                return referenced_report(bundle)
            record = review(root, manifest, root / 'output', provider=capture)
            self.assertEqual(record['release_id'], 'EXTERNAL')

    def test_symlink_cannot_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'inputs').mkdir()
            (root / 'inputs/company-rules.md').symlink_to(ROOT / 'inputs/company-rules.md')
            path = self.modified_manifest(lambda m: m.update(files=m['files'][:1]))
            with self.assertRaisesRegex(EvidenceError, 'Symlink'):
                load_bundle(root, path)

    def test_unknown_citation_rejected(self):
        value = report(self.bundle)
        value['observations'][0]['evidence'][0]['file'] = 'evaluation/expected-findings.json'
        with self.assertRaisesRegex(EvidenceError, 'Citation'):
            validate_report(value, self.bundle, [])

    def test_invented_quote_rejected(self):
        value = report(self.bundle)
        value['observations'][0]['evidence'][0]['quote'] = 'Launch approved by everyone.'
        with self.assertRaisesRegex(EvidenceError, 'Citation'):
            validate_report(value, self.bundle, [])

    def test_future_and_cross_variant_history_rejected(self):
        for record in ({'release_id': 'other', 'variant': 'agent', 'as_of_utc': '2026-10-09T12:00:00Z'},
                       {'release_id': 'RR-001', 'variant': 'control', 'as_of_utc': '2026-10-09T12:00:00Z'},
                       {'release_id': 'RR-001', 'variant': 'agent', 'as_of_utc': '2026-10-22T12:00:00Z'}):
            record['sequence_id'] = 'interactive'
            with self.assertRaises(EvidenceError):
                validate_history([record], self.bundle, 'agent', 'interactive')

    def test_cross_sequence_history_rejected(self):
        record = {'release_id': 'RR-001', 'variant': 'agent', 'sequence_id': 'another', 'as_of_utc': '2026-10-09T12:00:00Z'}
        with self.assertRaisesRegex(EvidenceError, 'sequence'):
            validate_history([record], self.bundle, 'agent', 'interactive')

    def test_unknown_transition_rejected(self):
        value = report(self.bundle)
        value['transitions'] = [{'prior_id': 'never-existed', 'state': 'resolved', 'reason': 'Cannot establish this.',
                                'evidence': value['observations'][0]['evidence']}]
        with self.assertRaisesRegex(EvidenceError, 'unknown prior'):
            validate_report(value, self.bundle, [])

    def test_schema_and_missing_evidence_rejected(self):
        for value in ({}, dict(report(self.bundle), phase_recommendation='launch authorized')):
            with self.assertRaises(EvidenceError):
                validate_report(value, self.bundle, [])
        value = report(self.bundle); value['observations'][0]['evidence'] = []
        with self.assertRaises(EvidenceError):
            validate_report(value, self.bundle, [])

    def test_overwrite_and_input_write_rejected(self):
        for destination in (ROOT / 'inputs/new-output', ROOT / 'evaluation/new-output', ROOT):
            with self.assertRaises(EvidenceError):
                review(ROOT, self.manifest, destination)

    def test_failed_output_never_becomes_report(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'run'
            def invalid(*args):
                value = report(self.bundle)
                value['observations'][0]['evidence'][0]['quote'] = 'No such receipt.'
                return value
            with self.assertRaises(EvidenceError):
                review(ROOT, self.manifest, out, provider=invalid)
            self.assertFalse((out / 'report.json').exists())
            self.assertEqual(len(json.loads((out / 'validation-errors.json').read_text())), 2)

    def test_provider_receives_only_selected_inputs_and_history(self):
        with tempfile.TemporaryDirectory() as temp:
            def capture(prompt, schema, destination, model, effort):
                self.assertNotIn('authored expectations; Adi review', prompt)
                self.assertNotIn('inputs/post-launch-follow-up.md', prompt)
                self.assertNotIn(str(ROOT), prompt)
                return referenced_report(self.bundle)
            record = review(ROOT, self.manifest, Path(temp) / 'run', provider=capture)
            self.assertEqual(record['snapshot_id'], '02-prelaunch')

    def test_catalog_contains_only_exact_current_passages(self):
        for manifest in (ROOT / 'inputs/snapshots').glob('*.json'):
            bundle = load_bundle(ROOT, manifest)
            catalog, schema = citation_contract(bundle)
            self.assertTrue(all(ref['quote'] in bundle['sources'][ref['file']] for ref in catalog.values()))
            for field in ('findings', 'observations', 'transitions', 'calculations'):
                refs = schema['properties'][field]['items']['properties']['evidence']['items']['properties']['reference']['enum']
                self.assertEqual(refs, list(catalog))

    def test_selection_resolves_and_validator_still_checks_meaning_boundary(self):
        catalog, _ = citation_contract(self.bundle)
        selected = referenced_report(self.bundle)
        resolved = resolve_citations(selected, catalog)
        validate_report(resolved, self.bundle, [])
        self.assertIn('reference', selected['observations'][0]['evidence'][0])
        selected['observations'][0]['evidence'][0]['reference'] = 'inputs/post-launch-follow-up.md:L1:P1'
        with self.assertRaisesRegex(EvidenceError, 'current source catalog'):
            resolve_citations(selected, catalog)

    def test_current_reference_cannot_return_prior_source_wording(self):
        old = {'sources': {'inputs/current.md': 'Draft; not sent.'}}
        new = {'sources': {'inputs/current.md': 'Delivered; receipt R-1.'}}
        previous, _ = citation_contract(old); current, _ = citation_contract(new)
        ref = next(iter(previous))
        value = referenced_report(new)
        value['observations'][0]['evidence'] = [{'reference': ref}]
        resolved = resolve_citations(value, current)
        self.assertEqual(resolved['observations'][0]['evidence'][0]['quote'], 'Delivered; receipt R-1.')


class CalculationTests(unittest.TestCase):
    def test_omitted_model_telemetry_is_in_final_report_with_tool_provenance(self):
        manifest = ROOT / 'inputs/snapshots/05-launch.json'
        bundle = load_bundle(ROOT, manifest)
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'run'
            result = review(ROOT, manifest, out, provider=lambda *args: referenced_report(bundle))
            self.assertEqual(json.loads((out / 'resolved-attempt-1.json').read_text())['calculations'], [])
            calculation = result['calculation_provenance']['appended'][0]
            self.assertIn('Absolute contact increase: 32.', calculation['value'])
            self.assertIn('rate ratio: 2.6.', calculation['value'])
            self.assertIn(calculation, result['report']['calculations'])
            self.assertIn('Absolute contact increase: 32.', (out / 'report.md').read_text())
            validate_report(result['report'], bundle, [])

    def test_controller_does_not_compare_unequal_windows(self):
        bundle = load_bundle(ROOT, ROOT / 'inputs/snapshots/05-launch.json')
        bundle['sources']['inputs/launch-signals.csv'] = bundle['sources']['inputs/launch-signals.csv'].replace(
            '2026-10-20T11:00:00Z', '2026-10-20T12:00:00Z')
        catalog, _ = citation_contract(bundle)
        result, completed = complete_telemetry(report(bundle), exact_checks(bundle), catalog)
        self.assertEqual(completed, [])
        self.assertEqual(result['calculations'], [])

    def test_zero_baseline_cannot_be_reported_as_infinite_ratio(self):
        body = 'window_start_utc,window_end_utc,exposed_accounts,total_release_contacts\n2026-10-19T10:00:00Z,2026-10-19T11:00:00Z,2000,0\n2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,2000,0\n'
        bundle = {'sources': {'inputs/signals.csv': body}}
        catalog, _ = citation_contract(bundle)
        result, _ = complete_telemetry({'calculations': []}, {'telemetry': signal_checks(bundle['sources'])}, catalog)
        self.assertIn('undefined because the baseline is zero', result['calculations'][0]['value'])
        self.assertIn('Absolute contact increase: 0.', result['calculations'][0]['value'])

    def test_critical_work_is_visible_before_major_work(self):
        bundle = load_bundle(ROOT, ROOT / 'inputs/snapshots/02-prelaunch.json')
        value = report(bundle)
        fields = {'basis': 'fact', 'customer_consequence': 'A customer consequence.', 'owner': 'Ren',
                  'proposed_action': 'Revise the guidance.', 'evidence': value['observations'][0]['evidence']}
        value['findings'] = [{**fields, 'id': 'one', 'severity': 'major', 'finding': 'Preparation task.'},
                             {**fields, 'id': 'two', 'severity': 'critical', 'finding': 'Unsafe billing advice.'}]
        rendered = markdown({'report': value, 'release_id': 'RR-001', 'snapshot_id': '02-prelaunch',
                             'as_of_utc': bundle['as_of_utc'], 'synthetic': True})
        self.assertLess(rendered.index('## Critical:'), rendered.index('## Major:'))

    def test_deadline_is_three_calendar_days(self):
        bundle = load_bundle(ROOT, ROOT / 'inputs/snapshots/02-prelaunch.json')
        dates = exact_checks(bundle)['calendar']
        entry = next(d for d in dates if d['source'] == 'inputs/product-v2.md' and d['quote'] == '2026-10-16 10:00 UTC')
        self.assertEqual(entry['minus_72_hours_utc'], '2026-10-13T10:00:00+00:00')

    def test_contacts_use_equal_windows_and_exposure(self):
        bundle = load_bundle(ROOT, ROOT / 'inputs/snapshots/05-launch.json')
        result = exact_checks(bundle)['telemetry'][0]
        self.assertEqual([r['contacts_per_1000'] for r in result['rows']], [10, 26])
        self.assertEqual(result['rate_ratio'], 2.6)
        self.assertEqual(result['absolute_contact_increase'], 32)

    def test_invalid_totals_and_denominator_rejected(self):
        text = (ROOT / 'inputs/launch-signals.csv').read_text()
        for bad in (text.replace(',52\n', ',51\n'), text.replace(',2000,', ',0,')):
            with self.assertRaises(EvidenceError):
                signal_checks({'signals.csv': bad})

    def test_unequal_windows_do_not_produce_comparison(self):
        text = (ROOT / 'inputs/launch-signals.csv').read_text().replace('2026-10-20T11:00:00Z', '2026-10-20T12:00:00Z')
        self.assertNotIn('rate_ratio', signal_checks({'signals.csv': text})[0])

    def test_staffing_is_handling_load_not_forecast(self):
        result = capacity(60, 10, 4)
        self.assertEqual(result['handling_minutes'], 600)
        self.assertEqual(result['required_agent_hours'], 10)
        self.assertEqual(result['additional_agent_hours'], 6)
        with self.assertRaises(EvidenceError):
            capacity(-1, 10, 4)

    def test_nonfinite_capacity_rejected(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            for args in ((value, 10, 4), (60, value, 4), (60, 10, value)):
                with self.assertRaisesRegex(EvidenceError, 'finite'):
                    capacity(*args)

    def test_negative_reason_rejected_even_when_total_matches(self):
        text = (ROOT / 'inputs/launch-signals.csv').read_text().replace(',24,20,8,52', ',24,29,-1,52')
        with self.assertRaisesRegex(EvidenceError, 'negative'):
            signal_checks({'signals.csv': text})


class RunnerTests(unittest.TestCase):
    def test_model_receives_disabled_capabilities_and_no_repository_cwd(self):
        completed = subprocess.CompletedProcess([], 0, json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"ok": true}'}}), '')
        with tempfile.TemporaryDirectory() as temp, patch('readiness.runner.run_process', return_value=completed) as run:
            self.assertEqual(model_call('data only', {}, Path(temp) / 'call'), {'ok': True})
            args, kwargs = run.call_args
            command = args[0]
            self.assertIn('--ignore-user-config', command)
            self.assertIn('--ephemeral', command)
            self.assertIn('project_doc_max_bytes=0', command)
            self.assertIn('skills.include_instructions=false', command)
            self.assertIn('default_permissions="review"', command)
            self.assertIn('permissions.review.network.enabled=false', command)
            for flag in DISABLED:
                self.assertIn(flag, command)
            self.assertNotEqual(Path(kwargs['cwd']), ROOT)
            self.assertEqual(kwargs['input'], 'data only')
            self.assertNotIn('OPENAI_API_KEY', kwargs['env'])

    def test_timeout_preserves_failure_without_accepting_response(self):
        with tempfile.TemporaryDirectory() as temp, patch('readiness.runner.run_process', side_effect=subprocess.TimeoutExpired('codex', 1, b'partial', b'timeout')):
            out = Path(temp) / 'call'
            with self.assertRaisesRegex(EvidenceError, 'timed out'):
                model_call('data', {}, out)
            self.assertEqual((out / 'events.jsonl').read_text(), 'partial')
            self.assertTrue((out / 'failure.txt').exists())
            self.assertFalse((out / 'raw-response.txt').exists())

    def test_tool_event_fails_closed_for_report_acceptance(self):
        completed = subprocess.CompletedProcess([], 0, json.dumps({'type': 'item.started', 'item': {'type': 'command_execution'}}), '')
        with tempfile.TemporaryDirectory() as temp, patch('readiness.runner.run_process', return_value=completed):
            with self.assertRaisesRegex(EvidenceError, 'tool event'):
                model_call('data', {}, Path(temp) / 'call')

    def test_nonzero_exit_cannot_return_cached_success(self):
        completed = subprocess.CompletedProcess([], 1, '', 'Runner unavailable')
        with tempfile.TemporaryDirectory() as temp, patch('readiness.runner.run_process', return_value=completed):
            with self.assertRaisesRegex(EvidenceError, 'runner failed'):
                model_call('data', {}, Path(temp) / 'call')

    def test_disabled_code_mode_diagnostic_is_not_an_executed_tool(self):
        warning = {'type': 'item.completed', 'item': {'type': 'error', 'message': 'Code Mode is unavailable because code-mode host is disabled. Code mode will fail closed; enable it.'}}
        answer = {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"ok": true}'}}
        completed = subprocess.CompletedProcess([], 0, '\n'.join(json.dumps(e) for e in [warning, answer]), '')
        with tempfile.TemporaryDirectory() as temp, patch('readiness.runner.run_process', return_value=completed):
            self.assertEqual(model_call('data', {}, Path(temp) / 'call'), {'ok': True})

    def test_timeout_stops_child_process(self):
        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / 'child-finished'
            child = "import time; from pathlib import Path; time.sleep(0.6); Path(%r).write_text('alive')" % str(marker)
            parent = 'import subprocess,time; subprocess.Popen(%r); print("started",flush=True); time.sleep(10)' % [sys.executable, '-c', child]
            with self.assertRaises(subprocess.TimeoutExpired) as error:
                run_process([sys.executable, '-c', parent], input='', cwd=temp, env=os.environ.copy(), timeout=0.15)
            self.assertIn('started', error.exception.stdout)
            time.sleep(0.7)
            self.assertFalse(marker.exists(), 'Timed-out runner left its child process alive')


if __name__ == '__main__':
    unittest.main()

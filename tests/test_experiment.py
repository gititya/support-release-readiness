import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from readiness.evidence import EvidenceError
from run_experiment import report_passages, run_sequence, score_sequence


class ExperimentTests(unittest.TestCase):
    def test_source_quotes_cannot_count_as_generated_analysis(self):
        passages = report_passages({'summary': 'A generated conclusion.', 'findings': [
            {'finding': 'A generated risk.', 'evidence': [{'file': 'source.md', 'quote': 'Raw source claim.'}]}]})
        self.assertEqual(set(passages), {'/summary', '/findings/0/finding'})
        self.assertNotIn('Raw source claim.', passages.values())

    def test_failed_slot_is_preserved_and_all_six_slots_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'inputs/snapshots').mkdir(parents=True)
            for n in range(6): (root / f'inputs/snapshots/{n}.json').write_text('{}')
            seen = []
            def fake_review(root, manifest, target, variant, prior, *args, **kwargs):
                seen.append(len(prior))
                if manifest.stem == '0':
                    target.mkdir(parents=True)
                    (target / 'bundle.json').write_text('{}')
                    raise EvidenceError('Invalid report')
                return {'snapshot_id': manifest.stem, 'report': {'phase_recommendation': 'not verified'}}
            with patch('run_experiment.ROOT', root), patch('run_experiment.freeze', return_value={}), patch('run_experiment.review', side_effect=fake_review):
                _, _, records = run_sequence(root / 'out', 'one', 'agent', {'model': 'test', 'effort': 'test'}, {})
            self.assertEqual(len(records), 6)
            self.assertEqual(seen, [0, 0, 1, 2, 3, 4])
            self.assertIsNone(records[0]['report'])
            failure = root / 'out/runs/one/agent/0/review-failure.json'
            self.assertEqual(json.loads(failure.read_text())['status'], 'failed')

    def test_invalid_source_boundary_stops_before_later_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'inputs/snapshots').mkdir(parents=True)
            for n in range(6): (root / f'inputs/snapshots/{n}.json').write_text('{}')
            with patch('run_experiment.ROOT', root), patch('run_experiment.freeze', return_value={}), patch('run_experiment.review', side_effect=EvidenceError('Changed source')) as review:
                with self.assertRaisesRegex(EvidenceError, 'Changed source'):
                    run_sequence(root / 'out', 'one', 'agent', {'model': 'test', 'effort': 'test'}, {})
            self.assertEqual(review.call_count, 1)

    def test_evaluator_receives_verified_clock_not_repeated_in_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'evaluation').mkdir()
            expected = {'id': 'one', 'phase_recommendation': 'not verified', 'required_findings': []}
            (root / 'evaluation/expected-findings.json').write_text(json.dumps({'snapshots': [expected]}))
            output = root / 'out'; target = output / 'runs/one/agent/one'; target.mkdir(parents=True)
            metadata = {'release_id': 'R1', 'as_of_utc': '2026-10-09T12:00:00Z',
                        'synthetic': True, 'manifest_sha256': 'verified-manifest'}
            (target / 'bundle.json').write_text(json.dumps({**metadata, 'sources': {'input.md': 'No clock here.'}}))
            record = {'snapshot_id': 'one', 'validation_retries': 0,
                      'report': {'phase_recommendation': 'not verified', 'summary': 'Review as of the supplied clock.'}}
            def fake_judge(prompt, schema, destination, *args, **kwargs):
                data = json.loads(prompt.split('Data:\n', 1)[1])['reviews'][0]
                self.assertEqual(data['snapshot_metadata'], metadata)
                self.assertNotIn(metadata['as_of_utc'], data['sources']['input.md'])
                destination.mkdir(parents=True)
                return {'snapshots': [{'snapshot_id': 'one', 'findings': [], 'calculations': [],
                                       'distinctions': [], 'non_findings': [], 'unsupported_claims': [],
                                       'unsupported_blocks': []}]}
            with patch('run_experiment.ROOT', root), patch('run_experiment.model_call', side_effect=fake_judge):
                rows = score_sequence(output, 'one', 'agent', [record], {'model': 'test', 'effort': 'test'})
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0]['review_accepted'])

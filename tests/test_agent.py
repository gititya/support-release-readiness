import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from zipfile import ZipFile

from scripts.build_agent import build

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'agent/tools/records.js'
NATIVE = sys.platform == 'darwin' and Path('/usr/bin/osascript').exists()


@unittest.skipUnless(NATIVE, 'macOS native helper; Linux checks do not establish macOS support')
class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='release-agent-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.workspace = self.base / 'private-work'
        self.call('setup')

    def process(self, op, request=None, helper=HELPER):
        command = ['/usr/bin/osascript', '-l', 'JavaScript', str(helper), op, str(self.workspace)]
        if request is not None:
            path = self.workspace / 'requests' / f'request-{time.time_ns()}.json'
            path.write_text(json.dumps(request))
            command.append(str(path))
        return subprocess.run(command, capture_output=True, text=True, timeout=30)

    def call(self, op, request=None, helper=HELPER):
        result = self.process(op, request, helper)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def status(self):
        return self.call('status')

    def save(self, op, **request):
        request.setdefault('expected_revision', self.status()['revision'])
        request.setdefault('actor', 'Adi')
        request.setdefault('summary', 'Supplied an update')
        return self.call(op, request)

    def company(self):
        self.save('profile', profile={'status': 'confirmed', 'company': 'Example', 'support_model': 'mixed',
            'timezone': 'Asia/Kolkata', 'people': ['Adi', 'Jo', 'Nia'], 'launch_authority': 'Jo',
            'notice_rule': {'unit': 'hours', 'amount': 72}})

    def release(self, release_id='renewal'):
        self.save('release', release_id=release_id, name=release_id.title(), phase='prelaunch',
                  scope='Monthly subscribers in the supplied rollout', launch='2026-10-20T10:00:00Z', people=['Adi', 'Jo', 'Nia'])

    def source(self, source_id='product', version='v1', content=None, facts=None, kind='record', authority='approved', attribution='Jo', release_id='renewal'):
        body = content or 'Confirmation: one step.\n\nCRM: unchanged.'
        if facts is None and source_id == 'product':
            facts = {'confirmation': {'value': 'one step', 'quote': 'Confirmation: one step.'},
                     'crm': {'value': 'unchanged', 'quote': 'CRM: unchanged.'}}
        return self.save('source', release_id=release_id, source={'id': source_id, 'version': version, 'title': source_id.title(),
            'attribution': attribution, 'observed_at': '2026-10-15T10:00:00Z', 'kind': kind, 'authority': authority,
            'content': body, 'facts': facts or {}})

    def inspect(self, release_id='renewal'):
        return self.call('inspect', {'release_id': release_id})

    def proof(self, source_id='product', version='v1', quote='CRM: unchanged.'):
        return {'source_id': source_id, 'version': version, 'quote': quote}

    def action(self, action_id='crm', fact='crm', status='open', **changes):
        value = {'id': action_id, 'title': 'Review ' + action_id, 'reason': 'Keep agent handling consistent with the approved flow',
            'owner': 'Nia', 'area': 'operations', 'status': status, 'priority': 'major', 'blocks_release': True,
            'depends_on': [{'source_id': 'product', 'fact': fact}], 'evidence': [self.proof()]}
        value.update(changes)
        self.save('action', release_id='renewal', action=value)
        return value

    def test_setup_and_partial_onboarding_resume(self):
        self.save('profile', profile={'status': 'draft', 'company': 'Example', 'unknowns': ['Vendor ownership']})
        fresh = self.status()
        self.assertEqual(fresh['profile']['company'], 'Example')
        self.assertEqual(fresh['profile']['status'], 'draft')
        self.assertEqual(fresh['revision'], 1)
        self.assertIsNone(fresh['lock'])

    def test_confirmed_profile_requires_people_and_notice_rule(self):
        bad = self.process('profile', {'expected_revision': 0, 'actor': 'Adi', 'summary': 'Bad context', 'profile': {'status': 'confirmed'}})
        self.assertNotEqual(bad.returncode, 0)
        self.assertEqual(self.status()['revision'], 0)

    def test_two_releases_do_not_share_sources(self):
        self.company(); self.release(); self.release('enterprise'); self.source()
        other = self.inspect('enterprise')
        self.assertEqual(other['release']['sources'], {})
        self.assertEqual(other['release']['actions'], {})

    def test_current_source_keeps_original_and_old_versions(self):
        self.company(); self.release(); self.source()
        self.source(version='v2', content='Confirmation: one step.\n\nCRM: unchanged.\n\nLabel: Done.')
        current = self.inspect()['release']['sources']['product']
        self.assertEqual(current['version'], 'v2')
        states = json.loads(sorted((self.workspace / 'records').glob('*.json'))[-1].read_text())['state']
        self.assertEqual(len(states['releases']['renewal']['sources']['product']['versions']), 2)
        self.assertEqual(hashlib.sha256(current['content'].encode()).hexdigest(), current['hash'])

    def test_draft_does_not_replace_approved_behavior(self):
        self.company(); self.release(); self.source()
        result = self.source(version='proposal', content='Confirmation: two steps.', facts={'confirmation': {'value': 'two steps', 'quote': 'Confirmation: two steps.'}}, authority='draft')
        self.assertTrue(result['pending_draft'])
        self.assertEqual(self.inspect()['release']['sources']['product']['version'], 'v1')

    def test_source_versions_cannot_be_overwritten(self):
        self.company(); self.release(); self.source()
        revision = self.status()['revision']
        result = self.process('source', {'expected_revision': revision, 'actor': 'Adi', 'summary': 'Overwrite', 'release_id': 'renewal',
            'source': {'id': 'product', 'version': 'v1', 'title': 'Product', 'attribution': 'Jo', 'observed_at': '2026-10-15T10:00:00Z',
                       'kind': 'record', 'authority': 'approved', 'content': 'Changed', 'facts': {}}})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.status()['revision'], revision)

    def test_rich_text_quote_resolves_to_original_passage(self):
        self.company(); self.release()
        self.source(source_id='help', content='Choose “Cancel”\u00a0now.\nThe next step is confirmation.', facts={'guidance': {'value': 'confirmation', 'quote': 'Choose "Cancel" now. The next step is confirmation.'}})
        fact = self.inspect()['release']['sources']['help']['facts']['guidance']
        self.assertIn('“Cancel”\u00a0now.', fact['quote'])

    def test_file_intake_preserves_supplied_text_and_rejects_outside_paths(self):
        self.company(); self.release()
        original = 'Confirmation: two steps.\r\n\r\nCustomer says: “நன்றி” 👋\r\n'
        path = self.workspace / 'inbox/product.md'; path.write_bytes(original.encode())
        source = {'id': 'actual-file', 'version': 'v1', 'title': 'Actual plan', 'attribution': 'Jo',
            'observed_at': '2026-10-15T10:00:00Z', 'authority': 'approved', 'kind': 'record', 'file': str(path),
            'facts': {'confirmation': {'value': 'two steps', 'quote': 'Confirmation: two steps.'}}}
        self.save('source', release_id='renewal', source=source)
        saved = self.inspect()['release']['sources']['actual-file']
        self.assertEqual(saved['content'], original)
        self.assertEqual(saved['hash'], hashlib.sha256(original.encode()).hexdigest())
        self.assertEqual(path.read_bytes(), original.encode())
        source.update(version='v2', content='An invented plan')
        request = {'expected_revision': self.status()['revision'], 'actor': 'Adi', 'summary': 'Bad import', 'release_id': 'renewal', 'source': source}
        self.assertNotEqual(self.process('source', request).returncode, 0)
        del source['content']
        outside = self.base / 'outside.txt'; outside.write_text('Outside material')
        for wrong in [str(outside), str(self.workspace / 'inbox/../../outside.txt')]:
            source['file'] = wrong
            self.assertNotEqual(self.process('source', request).returncode, 0)
        linked = self.workspace / 'inbox/link.txt'; linked.symlink_to(outside); source['file'] = str(linked)
        self.assertNotEqual(self.process('source', request).returncode, 0)

    def test_false_quote_and_invented_owner_are_rejected(self):
        self.company(); self.release(); self.source()
        request = {'expected_revision': self.status()['revision'], 'actor': 'Adi', 'summary': 'Unsupported work', 'release_id': 'renewal',
            'action': {'id': 'bad', 'title': 'Bad', 'reason': 'Unknown', 'owner': 'Invented', 'area': 'training', 'status': 'open',
                       'priority': 'major', 'blocks_release': True, 'depends_on': [], 'evidence': [self.proof(quote='A quote that is not here')]}}
        self.assertNotEqual(self.process('action', request).returncode, 0)
        request['action']['evidence'] = [self.proof()]
        self.assertNotEqual(self.process('action', request).returncode, 0)

    def test_attestation_cannot_establish_verified_completion(self):
        self.company(); self.release(); self.source()
        self.source(source_id='reply', kind='attestation', authority='observed', attribution='Nia', content='Training is done.')
        self.action(action_id='training', fact='confirmation', status='reported complete', area='training', evidence=[self.proof('reply', quote='Training is done.')])
        action = self.inspect()['release']['actions']['training']
        action.update(status='complete', accepted_by='Adi', acceptance_evidence=[self.proof('reply', quote='Training is done.')])
        bad = self.process('action', {'expected_revision': self.status()['revision'], 'actor': 'Adi', 'summary': 'Unsupported closure', 'release_id': 'renewal', 'action': action})
        self.assertNotEqual(bad.returncode, 0)
        self.assertEqual(self.inspect()['release']['actions']['training']['status'], 'reported complete')

    def test_changed_fact_reopens_only_affected_work(self):
        self.company(); self.release(); self.source()
        self.source(source_id='acceptance', kind='attestation', authority='observed', attribution='Adi', content='I accept the supplied records and these actions as complete.')
        accepted = [self.proof('acceptance', quote='I accept the supplied records and these actions as complete.')]
        self.action(status='complete', accepted_by='Adi', acceptance_evidence=accepted)
        self.action(action_id='training', fact='confirmation', status='complete', area='training', accepted_by='Adi', acceptance_evidence=accepted,
                    evidence=[self.proof(quote='Confirmation: one step.')])
        changed = self.source(version='v2', content='Confirmation: two steps.\n\nCRM: unchanged.', facts={
            'confirmation': {'value': 'two steps', 'quote': 'Confirmation: two steps.'}, 'crm': {'value': 'unchanged', 'quote': 'CRM: unchanged.'}})
        self.assertEqual(changed['changed_facts'], ['confirmation'])
        actions = self.inspect()['release']['actions']
        self.assertEqual(actions['training']['status'], 'needs review')
        self.assertEqual(actions['crm']['status'], 'complete')
        self.assertEqual(actions['training']['accepted_by'], 'Adi')
        prior = [json.loads(p.read_text())['state']['releases'].get('renewal', {}).get('actions', {}) for p in (self.workspace / 'records').glob('*.json')]
        self.assertTrue(any(a.get('training', {}).get('status') == 'complete' for a in prior))
        reopened = actions['training']; reopened.update(status='complete', evidence=[self.proof(version='v2', quote='Confirmation: two steps.')])
        request = {'expected_revision': self.status()['revision'], 'actor': 'Adi', 'summary': 'Try old sign-off', 'release_id': 'renewal', 'action': reopened}
        rejected = self.process('action', request)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('Acceptance predates', rejected.stderr)
        self.assertEqual(self.inspect()['release']['actions']['training']['status'], 'needs review')
        self.source(source_id='acceptance', version='v2', kind='attestation', authority='observed', attribution='Adi', content='I accept training for the new two-step confirmation.')
        reopened['acceptance_evidence'] = [self.proof('acceptance', 'v2', 'I accept training for the new two-step confirmation.')]
        self.save('action', release_id='renewal', action=reopened)
        self.assertEqual(self.inspect()['release']['actions']['training']['status'], 'complete')

    def test_ready_cannot_skip_preparation_coverage(self):
        self.company(); self.release(); self.source()
        bad = self.process('review', {'expected_revision': self.status()['revision'], 'actor': 'Release Readiness agent', 'summary': 'Review', 'release_id': 'renewal',
            'review': {'recommendation': 'support ready for the specified rollout', 'summary': 'Plan only', 'findings': [], 'unknowns': [], 'evidence': [self.proof()]}})
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('coverage', bad.stderr)

    def test_partial_action_updates_preserve_fields_and_use_source_fact_selectors(self):
        self.company(); self.release(); self.source(); self.action()
        before = self.inspect()['release']['actions']['crm']
        self.save('action', release_id='renewal', action={'id': 'crm', 'status': 'in progress',
            'evidence': [{'source_id': 'product', 'version': 'v1', 'fact': 'crm'}]})
        after = self.inspect()['release']['actions']['crm']
        self.assertEqual(after['owner'], before['owner'])
        self.assertEqual(after['title'], before['title'])
        self.assertEqual(after['depends_on'], before['depends_on'])
        self.assertEqual(after['evidence'][0]['quote'], 'CRM: unchanged.')
        bad = self.process('action', {'expected_revision': self.status()['revision'], 'actor': 'Adi', 'summary': 'Bad selector', 'release_id': 'renewal',
            'action': {'id': 'crm', 'evidence': [{'source_id': 'product', 'version': 'v1', 'fact': 'invented'}]}})
        self.assertNotEqual(bad.returncode, 0)

    def test_inspect_limits_review_context_without_losing_history(self):
        self.company(); self.release(); self.source()
        review = {'recommendation': 'support not ready', 'summary': 'Preparation missing', 'findings': [], 'unknowns': ['Training'], 'evidence': [self.proof()]}
        self.save('review', release_id='renewal', review=review)
        self.save('review', release_id='renewal', review=review)
        current = self.inspect()['release']
        self.assertEqual(current['reviews_total'], 2)
        self.assertEqual(len(current['reviews']), 1)
        history = self.call('inspect', {'release_id': 'renewal', 'include_history': True})['release']
        self.assertEqual(len(history['reviews']), 2)

    def test_ready_rejects_serious_open_findings_and_keeps_positive_observations_separate(self):
        self.company(); self.release(); self.source()
        review = {'recommendation': 'support ready for the specified rollout', 'summary': 'Review', 'findings': [
            {'statement': 'Unresolved guidance', 'priority': 'critical', 'evidence': [self.proof()]}],
            'unknowns': [], 'evidence': [self.proof()], 'coverage': [
                {'area': area, 'status': 'verified', 'reason': 'Structural fixture only', 'evidence': [self.proof()]}
                for area in ['planning', 'training', 'help', 'vendors', 'staffing', 'operations', 'communications', 'known issues']]}
        bad = self.process('review', {'expected_revision': self.status()['revision'], 'actor': 'Agent', 'summary': 'Review', 'release_id': 'renewal', 'review': review})
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('Open serious findings', bad.stderr)
        review.update(findings=[], observations=[{'statement': 'Scoped unchanged CRM assessment', 'evidence': [self.proof()]}], as_of='2026-10-15T12:00:00Z')
        self.save('review', release_id='renewal', review=review)
        saved = self.inspect()['release']['reviews'][-1]
        self.assertEqual(saved['findings'], [])
        self.assertEqual(saved['as_of'], '2026-10-15T12:00:00.000Z')
        self.assertEqual(len(saved['observations']), 1)

    def test_review_calculations_are_computed_and_saved(self):
        self.company(); self.release(); self.source()
        self.save('review', release_id='renewal', review={'recommendation': 'support not ready', 'summary': 'Preparation not yet evidenced',
            'findings': [], 'unknowns': ['Training'], 'evidence': [self.proof()], 'calculation_requests': [{'kind': 'deadline', 'launch': '2026-10-20T10:00:00Z', 'rule': {'unit': 'hours', 'amount': 72}}]})
        review = self.inspect()['release']['reviews'][-1]
        self.assertEqual(review['calculations'][0]['deadline_utc'], '2026-10-17T10:00:00.000Z')
        self.assertTrue(self.status()['releases'][0]['review_is_current'])
        self.action()
        self.assertFalse(self.status()['releases'][0]['review_is_current'])

    def test_elapsed_calendar_and_business_days(self):
        launch = '2026-11-02T10:00:00-05:00'
        elapsed = self.call('calculate', {'kind': 'deadline', 'launch': launch, 'rule': {'unit': 'hours', 'amount': 72}})
        calendar = self.call('calculate', {'kind': 'deadline', 'launch': launch, 'rule': {'unit': 'calendar_days', 'amount': 3, 'timezone': 'America/New_York'}})
        business = self.call('calculate', {'kind': 'deadline', 'launch': '2026-10-20T10:00:00Z', 'rule': {'unit': 'business_days', 'amount': 3, 'timezone': 'UTC', 'calendar_confirmed': True, 'holidays': ['2026-10-19']}})
        self.assertEqual(elapsed['deadline_utc'], '2026-10-30T15:00:00.000Z')
        self.assertEqual(calendar['deadline_utc'], '2026-10-30T14:00:00.000Z')
        self.assertEqual(business['deadline_utc'], '2026-10-14T10:00:00.000Z')
        bad = self.process('calculate', {'kind': 'deadline', 'launch': launch, 'rule': {'unit': 'business_days', 'amount': 3, 'timezone': 'UTC'}})
        self.assertNotEqual(bad.returncode, 0)

    def signals(self):
        return {'kind': 'signals', 'windows': [
            {'start': '2026-10-19T10:00:00Z', 'end': '2026-10-19T11:00:00Z', 'exposure': 2000, 'contacts': 20, 'categories': {'cancel': 20}},
            {'start': '2026-10-20T10:00:00Z', 'end': '2026-10-20T11:00:00Z', 'exposure': 2000, 'contacts': 52, 'categories': {'cancel': 52}}]}

    def test_signal_units_and_numeric_boundaries(self):
        result = self.call('calculate', self.signals())
        self.assertEqual((result['baseline_per_1000'], result['rollout_per_1000'], result['rate_ratio'], result['rate_increase_per_1000'], result['contact_count_increase']), (10, 26, 2.6, 16, 32))
        for kind in ['unequal', 'total', 'zero-exposure', 'negative']:
            value = self.signals()
            if kind == 'unequal': value['windows'][1]['end'] = '2026-10-20T12:00:00Z'
            if kind == 'total': value['windows'][1]['contacts'] = 53
            if kind == 'zero-exposure': value['windows'][1]['exposure'] = 0
            if kind == 'negative': value['windows'][1]['categories'] = {'cancel': -1, 'other': 53}
            self.assertNotEqual(self.process('calculate', value).returncode, 0)

    def test_zero_baseline_year_boundary_and_invalid_calendar_date(self):
        value = self.signals(); value['windows'][0].update(contacts=0, categories={'cancel': 0})
        self.assertIsNone(self.call('calculate', value)['rate_ratio'])
        result = self.call('calculate', {'kind': 'deadline', 'launch': '2027-01-01T15:30:00+05:30', 'rule': {'unit': 'hours', 'amount': 72}})
        self.assertEqual(result['deadline_utc'], '2026-12-29T10:00:00.000Z')
        self.assertNotEqual(self.process('calculate', {'kind': 'deadline', 'launch': '2026-02-30T10:00:00Z', 'rule': {'unit': 'hours', 'amount': 72}}).returncode, 0)

    def test_competing_writers_do_not_lose_updates(self):
        processes = []
        for name in ['one', 'two']:
            path = self.workspace / 'requests' / f'{name}.json'
            path.write_text(json.dumps({'expected_revision': 0, 'actor': name, 'summary': name, 'profile': {'status': 'draft', 'company': name}}))
            processes.append(subprocess.Popen(['/usr/bin/osascript', '-l', 'JavaScript', str(HELPER), 'profile', str(self.workspace), str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        results = [p.communicate(timeout=30) for p in processes]
        self.assertEqual(sum(p.returncode == 0 for p in processes), 1, results)
        self.assertEqual(self.status()['revision'], 1)

    def test_manual_edits_preserved_before_explicit_rebuild(self):
        self.company(); self.release()
        view = self.workspace / 'views/tracker.md'
        view.write_text(view.read_text() + '\nNia reports training complete.\n')
        self.assertIn('tracker.md', self.status()['manual_view_edits'])
        revision = self.status()['revision']
        self.assertNotEqual(self.process('rebuild', {'expected_revision': revision}).returncode, 0)
        result = self.call('rebuild', {'expected_revision': revision, 'preserve_edits': True})
        self.assertIn('Nia reports training complete.', Path(result['preserved_edits'][0]).read_text())
        self.assertEqual(self.status()['manual_view_edits'], [])

    def test_missing_views_rebuild_but_corrupt_history_blocks(self):
        self.company()
        (self.workspace / 'views/tracker.md').unlink()
        self.call('rebuild', {'expected_revision': 1})
        self.assertTrue((self.workspace / 'views/tracker.md').exists())
        record = self.workspace / 'records/00000001.json'
        body = record.read_text(); record.write_text(body.replace('Example', 'Forged'))
        self.assertNotEqual(self.process('status').returncode, 0)
        self.assertIn('Forged', record.read_text())

    def test_interrupted_rebuild_is_not_a_manual_edit(self):
        self.company()
        old_manifest = (self.workspace / 'views/manifest.json').read_text()
        old_history = (self.workspace / 'views/history.md').read_text()
        self.release()
        (self.workspace / 'views/manifest.json').write_text(old_manifest)
        (self.workspace / 'views/history.md').write_text(old_history)
        status = self.status()
        self.assertEqual(status['manual_view_edits'], [])
        self.assertTrue(status['views_need_rebuild'])
        self.save('release', release_id='renewal', name='Renewal', phase='rollout', scope='Same approved cohort', launch='2026-10-20T10:00:00Z')
        self.assertEqual(self.status()['manual_view_edits'], [])
        self.assertFalse(self.status()['views_need_rebuild'])

    def test_corrupt_view_manifest_does_not_hide_accepted_work(self):
        self.company()
        (self.workspace / 'views/manifest.json').write_text('{incomplete')
        status = self.status()
        self.assertEqual(status['profile']['company'], 'Example')
        self.assertTrue(status['views_need_rebuild'])
        self.assertEqual(status['manual_view_edits'], [])
        self.call('rebuild', {'expected_revision': status['revision']})
        self.assertFalse(self.status()['views_need_rebuild'])

    def test_saved_record_survives_a_failed_view_refresh(self):
        self.company()
        view_directory = self.workspace / 'views'
        view_directory.chmod(0o500)
        try:
            result = self.save('release', release_id='renewal', name='Renewal', phase='planning', scope='Planning only')
            self.assertTrue(result['saved'])
            self.assertTrue(result['views_need_rebuild'])
            self.assertEqual(self.status()['revision'], result['revision'])
        finally:
            view_directory.chmod(0o700)
        self.call('rebuild', {'expected_revision': result['revision']})

    def test_company_workspaces_are_discoverable_after_replacing_product(self):
        self.company()
        other = self.base / 'enterprise-company'
        subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript', str(HELPER), 'setup', str(other)], check=True, capture_output=True)
        script = self.base / 'discover.js'
        script.write_text(HELPER.read_text() + '\nrun = function() { ObjC.import("Foundation"); FS = $.NSFileManager.defaultManager; return JSON.stringify(discoverWorkspaces(' + json.dumps(str(self.base)) + ')); };\n')
        result = subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript', str(script)], check=True, capture_output=True, text=True)
        entries = json.loads(result.stdout)
        self.assertEqual({entry['workspace'] for entry in entries}, {str(self.workspace), str(other)})
        self.assertIn('Example', {entry.get('company') for entry in entries})

    def test_killed_writer_can_be_recovered_without_a_history_change(self):
        self.company(); self.release()
        revision = self.status()['revision']
        request = self.workspace / 'requests/killed.json'
        request.write_text(json.dumps({'expected_revision': revision, 'actor': 'Adi', 'summary': 'Large import', 'release_id': 'renewal',
            'source': {'id': 'large', 'version': 'v1', 'title': 'Large', 'attribution': 'Jo', 'observed_at': '2026-10-15T10:00:00Z', 'authority': 'approved', 'kind': 'record', 'content': 'x' * 1500000, 'facts': {}}}))
        proc = subprocess.Popen(['/usr/bin/osascript', '-l', 'JavaScript', str(HELPER), 'source', str(self.workspace), str(request)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        end = time.monotonic() + 8
        while not (self.workspace / 'write-lock/owner.json').exists() and proc.poll() is None and time.monotonic() < end:
            time.sleep(0.005)
        self.assertTrue((self.workspace / 'write-lock/owner.json').exists())
        proc.kill(); proc.communicate(timeout=10)
        state = self.status(); self.assertFalse(state['lock']['owner_alive']); self.assertEqual(state['revision'], revision)
        self.call('recover-lock', {'expected_revision': revision, 'confirm_recovery': True, 'lock_token': state['lock']['token']})
        self.assertIsNone(self.status()['lock'])
        self.save('profile', profile={'status': 'draft', 'company': 'Recovered'})

    def test_live_lock_cannot_be_broken(self):
        lock = self.workspace / 'write-lock'; lock.mkdir()
        (lock / 'owner.json').write_text(json.dumps({'pid': os.getpid(), 'token': 'active', 'created_at': '2026-01-01T00:00:00Z'}))
        result = self.process('recover-lock', {'expected_revision': 0, 'confirm_recovery': True, 'lock_token': 'active'})
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(lock.exists())

    def test_export_avoids_source_text_and_neutralizes_csv_formulas(self):
        self.company(); self.release(); self.source(content='Confirmation: one step.\n\nCRM: unchanged.\n\nPRIVATE-CUSTOMER-DETAIL')
        self.action(title='=HYPERLINK("example")')
        result = self.call('export', {'expected_revision': self.status()['revision'], 'release_id': 'renewal'})
        self.assertNotIn('PRIVATE-CUSTOMER-DETAIL', Path(result['brief']).read_text())
        self.assertIn("'=HYPERLINK", Path(result['actions']).read_text())
        self.assertIn('Reported completion is not verified completion', Path(result['brief']).read_text())

    def test_unsupported_schema_and_foreign_paths_do_not_write(self):
        marker = self.workspace / 'workspace.json'; meta = json.loads(marker.read_text()); meta['schema'] = 99; marker.write_text(json.dumps(meta))
        self.assertNotEqual(self.process('status').returncode, 0)
        self.assertEqual(json.loads(marker.read_text())['schema'], 99)
        meta['schema'] = 1; marker.write_text(json.dumps(meta))
        outside = self.base / 'outside.json'; outside.write_text('{}')
        result = subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript', str(HELPER), 'inspect', str(self.workspace), str(outside)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        linked = self.workspace / 'requests/link.json'; linked.symlink_to(outside)
        self.assertNotEqual(subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript', str(HELPER), 'inspect', str(self.workspace), str(linked)], capture_output=True).returncode, 0)

    def test_native_hash_vectors_match_independent_standard_library(self):
        for value in ['', 'abc', 'support “ready”\nதமிழ் 👋', 'x' * 1000]:
            script = self.base / 'hash.js'
            script.write_text(HELPER.read_text() + '\nfunction run() { return sha256(' + json.dumps(value) + '); }\n')
            result = subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript', str(script)], capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), hashlib.sha256(value.encode()).hexdigest())

    def test_replacing_download_preserves_external_work(self):
        self.company(); self.release(); self.source()
        first = build(self.base / 'agent.zip')
        one = self.base / 'old-download'; two = self.base / 'new-download'
        with ZipFile(first) as z:
            z.extractall(one); z.extractall(two)
        shutil.rmtree(one)
        replacement = two / 'Release Readiness/tools/records.js'
        self.assertEqual(self.call('status', helper=replacement)['profile']['company'], 'Example')
        self.assertEqual(self.call('inspect', {'release_id': 'renewal'}, helper=replacement)['release']['sources']['product']['version'], 'v1')

    def test_private_work_cannot_be_created_inside_replaceable_download(self):
        product = self.base / 'download'; (product / 'tools').mkdir(parents=True)
        shutil.copy2(HELPER, product / 'tools/records.js')
        invocations = [(str(product / 'tools/records.js'), product, product / 'private-work'),
                       ('records.js', product / 'tools', product / 'private-work'),
                       (str(product / 'tools/records.js'), product, self.base / 'DOWNLOAD/private-work')]
        # The official filename can itself be reached through a linked parent.
        linked = self.base / 'linked-tools'; linked.symlink_to(product / 'tools', target_is_directory=True)
        invocations.append((str(linked / 'records.js'), product, product / 'private-work'))
        for helper, cwd, target in invocations:
            with self.subTest(helper=helper, target=target):
                result = subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript', helper, 'setup', str(target)], cwd=cwd, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('outside the replaceable agent download', result.stderr)
                self.assertFalse(target.exists())


class PackageTests(unittest.TestCase):
    def test_download_is_self_contained_and_has_no_private_or_developer_material(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = build(Path(temp) / 'agent.zip')
            with ZipFile(archive) as z:
                names = z.namelist()
                self.assertTrue(all(n.startswith('Release Readiness/') for n in names))
                self.assertFalse(any(part in '/'.join(names) for part in ['workspace/', 'evidence/', 'expected-findings', '.py', '.git/', 'README.md']))
                meta = json.loads(z.read('Release Readiness/PACKAGE.json'))
                for name, digest in meta['files'].items():
                    self.assertEqual(hashlib.sha256(z.read('Release Readiness/' + name)).hexdigest(), digest)
                self.assertEqual(z.read('Release Readiness/CLAUDE.md').decode(), '@AGENTS.md\n')

    def test_working_records_and_download_are_ignored(self):
        result = subprocess.run(['git', 'check-ignore', 'agent/workspace/company.json', 'agent/requests/update.json', 'dist/support-release-readiness-agent.zip'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(result.stdout.splitlines()), 3)

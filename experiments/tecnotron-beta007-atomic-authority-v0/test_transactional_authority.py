"""No Product inputs, credentials, network, migrations or external DBs."""
from __future__ import annotations

from pathlib import Path
import os
import sqlite3
import stat
from unittest import mock
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from transactional_authority import (
    IdentityConflict, OutcomeUnknown, ProjectionConflict, commit_effect, connect,
    create_grant, effect_count, initialize, inspect_attempt, prepare_attempt,
    project_committed_effect, revoke_grant, committed_count_for_attempt, digest,
)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'ledger.sqlite'
        self.conn = connect(self.db)
        initialize(self.conn)
        create_grant(self.conn, 'grant-1', 'source/immutable-subject')

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def prep(self, attempt='attempt-1'):
        return prepare_attempt(self.conn, attempt, 'grant-1', 'source/immutable-subject', 'sha256:effect')

    def test_revocation_commits_before_effect_and_blocks(self):
        self.prep()
        self.assertEqual(revoke_grant(self.conn, 'grant-1'), 'REVOKED')
        outcome = commit_effect(self.conn, 'attempt-1')
        self.assertEqual((outcome.status,outcome.effect_state), ('BLOCKED','NONE'))
        self.assertEqual(effect_count(self.conn),0)
        self.assertEqual(committed_count_for_attempt(self.conn,'attempt-1'),0)
        self.assertEqual(revoke_grant(self.conn,'grant-1'),'ALREADY_REVOKED')

    def test_effect_commits_before_revocation_and_is_exact_once(self):
        self.prep()
        self.assertEqual(commit_effect(self.conn,'attempt-1').effect_state,'CONFIRMED')
        self.assertEqual(revoke_grant(self.conn,'grant-1'),'REVOKED')
        self.assertEqual(commit_effect(self.conn,'attempt-1').effect_state,'CONFIRMED')
        self.assertEqual(effect_count(self.conn),1)
        self.assertEqual(committed_count_for_attempt(self.conn,'attempt-1'),1)
        self.assertEqual(inspect_attempt(self.conn,'attempt-1').effect_state,'CONFIRMED')

    def test_prepare_idempotent_but_conflicting_intent_is_rejected(self):
        self.prep()
        self.assertEqual(self.prep().status,'PREPARED')
        with self.assertRaises(IdentityConflict):
            prepare_attempt(self.conn,'attempt-1','grant-1','source/immutable-subject','different')
        self.assertEqual(effect_count(self.conn),0)

    def test_receipt_lost_after_original_commit_reconcile_no_retry(self):
        self.prep()
        with self.assertRaises(OutcomeUnknown):
            commit_effect(self.conn,'attempt-1',fault='after_commit_receipt_lost')
        with connect(self.db) as separate_reader:
            self.assertEqual(inspect_attempt(separate_reader,'attempt-1').effect_state,'CONFIRMED')
            self.assertEqual(committed_count_for_attempt(separate_reader,'attempt-1'),1)
        # There is no second dispatch. The durable provider result is sufficient.
        self.assertEqual(effect_count(self.conn),1)

    def test_failure_inside_uncommitted_transaction_rolls_back(self):
        self.prep()
        with self.assertRaisesRegex(RuntimeError,'forced failure'):
            commit_effect(self.conn,'attempt-1',fault='exception_before_commit')
        self.assertEqual(inspect_attempt(self.conn,'attempt-1').status,'PREPARED')
        self.assertEqual(effect_count(self.conn),0)

    def test_process_death_before_commit_recovers_without_effect(self):
        self.prep()
        result = subprocess.run([sys.executable,str(Path(__file__).with_name('transactional_authority.py')),
                                 'crash-before-commit',str(self.db),'attempt-1'],
                                capture_output=True, timeout=10, check=False)
        self.assertEqual(result.returncode,72, result.stderr.decode(errors='replace'))
        self.assertEqual(inspect_attempt(self.conn,'attempt-1').status,'PREPARED')
        self.assertEqual(effect_count(self.conn),0)

    def test_concurrent_revocation_serializes_after_effect(self):
        self.prep()
        entered = threading.Event()
        release = threading.Event()
        revoker_started = threading.Event()
        results = {}
        def effect_writer():
            conn = connect(self.db)
            try:
                # Instrument the test-owned SQLite connection, not the effect
                # API: no caller-supplied callback executes within Product
                # authority transactions.
                def observe_authority_read(sql):
                    if sql.lstrip().startswith('SELECT subject,active,version FROM grants'):
                        entered.set()
                        if not release.wait(4):
                            results['instrumentation_timeout'] = True
                conn.set_trace_callback(observe_authority_read)
                results['effect'] = commit_effect(conn,'attempt-1')
            finally:
                conn.set_trace_callback(None)
                conn.close()
        def revoker():
            entered.wait(2)
            revoker_started.set()
            conn = connect(self.db)
            try:
                results['revoke'] = revoke_grant(conn,'grant-1')
            finally:
                conn.close()
        a=threading.Thread(target=effect_writer,daemon=True)
        b=threading.Thread(target=revoker,daemon=True)
        a.start();b.start()
        self.assertTrue(entered.wait(2))
        self.assertTrue(revoker_started.wait(2))
        time.sleep(.1)
        self.assertNotIn('revoke', results,'revoke must wait on original write lock')
        release.set()
        a.join(4);b.join(4)
        self.assertFalse(a.is_alive() or b.is_alive())
        self.assertNotIn('instrumentation_timeout',results)
        self.assertEqual(results['effect'].effect_state,'CONFIRMED')
        self.assertEqual(results['revoke'],'REVOKED')
        self.assertEqual(committed_count_for_attempt(self.conn,'attempt-1'),1)

    def test_wrong_subject_blocks_transaction(self):
        prepare_attempt(self.conn,'attempt-2','grant-1','other-subject','effect')
        self.assertEqual(commit_effect(self.conn,'attempt-2').effect_state,'NONE')
        self.assertEqual(effect_count(self.conn),0)

    def test_projection_never_creates_authority(self):
        self.prep()
        root=Path(self.temp.name)/'projection'
        with self.assertRaises(IdentityConflict):
            project_committed_effect(self.conn,'attempt-1',root)
        self.assertFalse(root.exists())

    def test_projection_recovery_after_interruption(self):
        self.prep()
        self.assertEqual(commit_effect(self.conn,'attempt-1').effect_state,'CONFIRMED')
        root=Path(self.temp.name)/'projection'
        with self.assertRaises(OutcomeUnknown):
            project_committed_effect(self.conn,'attempt-1',root,fault='before_link')
        self.assertEqual(list(root.iterdir()),[])
        self.assertEqual(effect_count(self.conn),1)
        self.assertEqual(project_committed_effect(self.conn,'attempt-1',root),'CREATED')
        self.assertEqual(project_committed_effect(self.conn,'attempt-1',root),'EXACT')
        self.assertEqual(effect_count(self.conn),1)
        target=next(root.iterdir())
        target.write_text('tampered',encoding='utf-8')
        with self.assertRaises(ProjectionConflict):
            project_committed_effect(self.conn,'attempt-1',root)
        self.assertEqual(effect_count(self.conn),1)

    def test_projection_of_prior_committed_effect_allowed_after_revocation(self):
        self.prep()
        commit_effect(self.conn,'attempt-1')
        revoke_grant(self.conn,'grant-1')
        self.assertEqual(project_committed_effect(self.conn,'attempt-1',Path(self.temp.name)/'view'),'CREATED')
        self.assertEqual(committed_count_for_attempt(self.conn,'attempt-1'),1)


    def test_process_death_after_commit_reconciles_without_second_effect(self):
        self.prep()
        result = subprocess.run([sys.executable,str(Path(__file__).with_name('transactional_authority.py')),
                                 'crash-after-commit',str(self.db),'attempt-1'],
                                capture_output=True, timeout=10, check=False)
        self.assertEqual(result.returncode,73, result.stderr.decode(errors='replace'))
        self.assertEqual(inspect_attempt(self.conn,'attempt-1').effect_state,'CONFIRMED')
        self.assertEqual(effect_count(self.conn),1)
        self.assertEqual(committed_count_for_attempt(self.conn,'attempt-1'),1)

    def test_reentrant_read_and_transaction_are_rejected_without_effect(self):
        self.prep()
        self.conn.execute('BEGIN')
        try:
            with self.assertRaisesRegex(RuntimeError,'REENTRANT_READ_UNSUPPORTED'):
                inspect_attempt(self.conn,'attempt-1')
        finally:
            self.conn.execute('ROLLBACK')
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(RuntimeError,'REENTRANT_TRANSACTION_UNSUPPORTED'):
                commit_effect(self.conn,'attempt-1')
        finally:
            self.conn.execute('ROLLBACK')
        self.assertEqual(inspect_attempt(self.conn,'attempt-1').effect_state,'NONE')
        self.assertEqual(effect_count(self.conn),0)

    def test_descriptor_projection_rejects_symlink_root_target_and_public_directory(self):
        self.prep()
        self.assertEqual(commit_effect(self.conn,'attempt-1').effect_state,'CONFIRMED')
        parent=Path(self.temp.name)
        trusted=parent/'trusted';trusted.mkdir(mode=0o700)
        alias=parent/'alias';alias.symlink_to(trusted,target_is_directory=True)
        with self.assertRaises(ProjectionConflict):
            project_committed_effect(self.conn,'attempt-1',alias)
        outside=parent/'outside'; outside.write_text('DO NOT CHANGE',encoding='utf-8')
        target=trusted/(digest('attempt-1')+'.json');target.symlink_to(outside)
        with self.assertRaises(ProjectionConflict):
            project_committed_effect(self.conn,'attempt-1',trusted)
        self.assertEqual(outside.read_text(encoding='utf-8'),'DO NOT CHANGE')
        target.unlink()
        untrusted=parent/'public';untrusted.mkdir(mode=0o755);untrusted.chmod(0o755)
        with self.assertRaises(ProjectionConflict):
            project_committed_effect(self.conn,'attempt-1',untrusted)
        self.assertEqual(effect_count(self.conn),1)

    def test_projection_final_directory_unlink_is_fsynced(self):
        self.prep()
        commit_effect(self.conn,'attempt-1')
        root=Path(self.temp.name)/'sync-view'
        original=os.fsync
        directory_syncs=[]
        def observing_fsync(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                directory_syncs.append(fd)
            return original(fd)
        with mock.patch('transactional_authority.os.fsync',side_effect=observing_fsync):
            self.assertEqual(project_committed_effect(self.conn,'attempt-1',root),'CREATED')
        self.assertGreaterEqual(len(directory_syncs),2,
            'link and staged-temp unlink must each fsync the directory')
        self.assertEqual(len(list(root.iterdir())),1)
        self.assertEqual(effect_count(self.conn),1)

    def test_projection_snapshot_rejects_reentrant_reads_before_any_file_effect(self):
        self.prep()
        commit_effect(self.conn,'attempt-1')
        root=Path(self.temp.name)/'no-reentrant-view'
        self.conn.execute('BEGIN')
        try:
            with self.assertRaisesRegex(RuntimeError,'REENTRANT_READ_UNSUPPORTED'):
                project_committed_effect(self.conn,'attempt-1',root)
        finally:
            self.conn.execute('ROLLBACK')
        self.assertFalse(root.exists())
        self.assertEqual(effect_count(self.conn),1)


if __name__ == '__main__':
    unittest.main(verbosity=2)

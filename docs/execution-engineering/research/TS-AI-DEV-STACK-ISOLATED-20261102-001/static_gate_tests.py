#!/usr/bin/env python3
"""Independent offline policy sketch; NOT an upstream integration test."""

from pathlib import Path
import json


def review_actions(steps, locked, jobs=(), containers=()):
    # Pure synthetic policy test: no real GitHub verifier/provenance checks.
    for ref in steps:
        if ref.startswith('./'):
            return 'BLOCKED_LOCAL_ACTION'
        if ref.startswith('$/'):
            continue
        if ref.startswith('docker://'):
            if '@sha256:' not in ref:
                return 'WARN_UNPINNED_CONTAINER'
            continue
        if ref not in locked:
            return 'BLOCKED_MISSING_LOCK_ENTRY'
    if any(not ref.startswith('$/') for ref in jobs):
        return 'BLOCKED_EXTERNAL_REUSABLE'
    if any('@sha256:' not in ref for ref in containers):
        return 'WARN_UNPINNED_CONTAINER'
    return 'OFFLINE_COVERAGE_ONLY'


def effect(state, grant, unique, requested, scheduled=False, bounded=False):
    if requested and state in ('UNKNOWN','RUNNING'):
        return 'BLOCKED_NO_RETRY'
    if requested and not (grant and unique):
        return 'BLOCKED_GRANT_OR_IDENTITY'
    if requested and scheduled and not bounded:
        return 'BLOCKED_UNBOUNDED_SCHEDULE'
    return 'PASS_SYNTHETIC'


def reconnect(last, server, same, window):
    if server < last:
        return 'BLOCKED_SEQUENCE_REGRESSION'
    if not same:
        return 'BLOCKED_SESSION_MISMATCH'
    if server - last > window:
        return 'SNAPSHOT_NO_EFFECT_RETRY'
    return 'REPLAY_DISPLAY_ONLY'


def run():
    locked={'actions/checkout@v4':'sha:placeholder'}
    tests={
        'actions_valid_coverage':review_actions(['actions/checkout@v4'],locked)=='OFFLINE_COVERAGE_ONLY',
        'actions_missing_entry':review_actions(['actions/setup-python@v5'],locked)=='BLOCKED_MISSING_LOCK_ENTRY',
        'actions_dot_local':review_actions(['./.github/actions/local'],locked)=='BLOCKED_LOCAL_ACTION',
        'actions_dollar_local':review_actions(['$/actions/local'],locked)=='OFFLINE_COVERAGE_ONLY',
        'actions_external_reusable':review_actions(['actions/checkout@v4'],locked,jobs=['ext/repo/.github/workflows/run.yml@main'])=='BLOCKED_EXTERNAL_REUSABLE',
        'actions_unpinned_container':review_actions(['docker://python:3.12'],locked)=='WARN_UNPINNED_CONTAINER',
        'actions_pinned_container':review_actions(['docker://python@sha256:'+'a'*64],locked)=='OFFLINE_COVERAGE_ONLY',
        'actions_coverage_not_provenance':review_actions(['actions/checkout@v4'],{'actions/checkout@v4':'sha:UNVERIFIED'})=='OFFLINE_COVERAGE_ONLY',
        'goal_unknown_no_retry':effect('UNKNOWN',True,True,True)=='BLOCKED_NO_RETRY',
        'goal_missing_grant':effect('READY',False,True,True)=='BLOCKED_GRANT_OR_IDENTITY',
        'schedule_no_bound':effect('READY',True,True,True,True,False)=='BLOCKED_UNBOUNDED_SCHEDULE',
        'schedule_bounded':effect('READY',True,True,True,True,True)=='PASS_SYNTHETIC',
        'ahp_replay_display_only':reconnect(42,43,True,10)=='REPLAY_DISPLAY_ONLY',
        'ahp_gap_snapshot':reconnect(42,80,True,10)=='SNAPSHOT_NO_EFFECT_RETRY',
        'ahp_session_mismatch':reconnect(42,43,False,10)=='BLOCKED_SESSION_MISMATCH',
        'ahp_sequence_regression':reconnect(42,40,True,10)=='BLOCKED_SEQUENCE_REGRESSION',
    }
    receipt={'artifact':'TS-AI-STACK-ISOLATED-20261102-001','kind':'SYNTHETIC_POLICY_NOT_UPSTREAM_TOOL_TEST','passed':sum(tests.values()),'count':len(tests),'tests':tests,'product_effects':0,'network_effects':0,'limitations':['No real gh-actions-lock binary or provenance checks','No OpenCode runtime/goal/schedule executed','No AHP session started','No paid Terra requests or live gh-aw workflows']}
    assert all(tests.values()), receipt
    return receipt

if __name__ == '__main__':
    result=run()
    Path(__file__).with_name('OFFLINE_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f"{result['passed']}/{result['count']} PASS")

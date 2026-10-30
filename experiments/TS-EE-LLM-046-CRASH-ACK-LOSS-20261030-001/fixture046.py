#!/usr/bin/env python3
"""Synthetic durable provider and consumer journal. Experimental only."""
import argparse,hashlib,json,os,sqlite3
from pathlib import Path
def db(path):
    c=sqlite3.connect(path,timeout=10,isolation_level=None)
    c.execute('PRAGMA busy_timeout=10000')
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA synchronous=FULL')
    return c
def emit(**kw): print(json.dumps(kw,sort_keys=True,separators=(',',':')),flush=True)
def identity(a):
    if not all(isinstance(a[k],str) and a[k] for k in ('attempt','subject','owner')): raise ValueError('INVALID_IDENTITY')
def init(root):
    root.mkdir(parents=True,exist_ok=False)
    p=db(root/'provider.sqlite3')
    p.execute('CREATE TABLE effects (attempt TEXT PRIMARY KEY, subject TEXT NOT NULL, owner TEXT NOT NULL, receipt TEXT NOT NULL, units INTEGER NOT NULL CHECK(units=1))')
    p.close()
    c=db(root/'consumer.sqlite3')
    c.execute('CREATE TABLE journal (seq INTEGER PRIMARY KEY AUTOINCREMENT, attempt TEXT NOT NULL, subject TEXT NOT NULL, owner TEXT NOT NULL, state TEXT NOT NULL, receipt TEXT)')
    c.close();emit(phase='initialized')
def intent(root,a):
    identity(a);c=db(root/'consumer.sqlite3');c.execute('BEGIN IMMEDIATE')
    c.execute('INSERT INTO journal(attempt,subject,owner,state,receipt) VALUES(?,?,?,?,NULL)',(a['attempt'],a['subject'],a['owner'],'INTENT'))
    c.execute('COMMIT');c.close();emit(phase='intent_persisted')
def apply(root,a,fault):
    identity(a);p=db(root/'provider.sqlite3');p.execute('BEGIN IMMEDIATE')
    old=p.execute('SELECT subject,owner,receipt FROM effects WHERE attempt=?',(a['attempt'],)).fetchone()
    if old:
        if old[:2]!=(a['subject'],a['owner']):
            p.execute('ROLLBACK');emit(phase='BLOCK_IDENTITY');raise SystemExit(77)
        p.execute('COMMIT');emit(phase='ALREADY_CONFIRMED',receipt=old[2]);return
    receipt=hashlib.sha256(('LLM046|'+a['attempt']+'|'+a['subject']+'|'+a['owner']).encode()).hexdigest()
    p.execute('INSERT INTO effects VALUES(?,?,?,?,1)',(a['attempt'],a['subject'],a['owner'],receipt))
    if fault=='before_commit':os._exit(74)
    p.execute('COMMIT')
    if fault=='after_commit_before_ack':os._exit(73)
    emit(phase='APPLIED_ACK',receipt=receipt);p.close()
def probe(root,a):
    identity(a);p=db(root/'provider.sqlite3')
    x=p.execute('SELECT subject,owner,receipt,units FROM effects WHERE attempt=?',(a['attempt'],)).fetchone()
    p.close()
    if x is None:emit(phase='PROVIDER_AUTHORITATIVE_ABSENT')
    elif x[:2]!=(a['subject'],a['owner']):emit(phase='BLOCK_IDENTITY')
    else:emit(phase='PROVIDER_CONFIRMED',receipt=x[2],units=x[3])
def reconcile(root,a,available):
    identity(a);c=db(root/'consumer.sqlite3')
    rows=c.execute('SELECT subject,owner,state,receipt FROM journal WHERE attempt=? ORDER BY seq',(a['attempt'],)).fetchall()
    if not rows or any(x[:2]!=(a['subject'],a['owner']) for x in rows):
        emit(phase='BLOCK_IDENTITY_OR_NO_INTENT');raise SystemExit(78)
    if not available:state,receipt='RECONCILE_UNKNOWN',None
    else:
        p=db(root/'provider.sqlite3')
        row=p.execute('SELECT subject,owner,receipt FROM effects WHERE attempt=?',(a['attempt'],)).fetchone()
        p.close()
        if row is None:state,receipt='ABSENT_REQUIRES_AUTHORITY',None
        elif row[:2]!=(a['subject'],a['owner']):state,receipt='BLOCK_IDENTITY',None
        else:state,receipt='NO_RETRY_CONFIRMED',row[2]
    c.execute('BEGIN IMMEDIATE')
    c.execute('INSERT INTO journal(attempt,subject,owner,state,receipt) VALUES(?,?,?,?,?)',(a['attempt'],a['subject'],a['owner'],state,receipt))
    c.execute('COMMIT');c.close();emit(phase=state,receipt=receipt)
def inspect(root):
    p=db(root/'provider.sqlite3');c=db(root/'consumer.sqlite3')
    effects=p.execute('SELECT attempt,subject,owner,receipt,units FROM effects ORDER BY attempt').fetchall()
    journal=c.execute('SELECT seq,attempt,subject,owner,state,receipt FROM journal ORDER BY seq').fetchall()
    integrity=(p.execute('PRAGMA integrity_check').fetchone()[0],c.execute('PRAGMA integrity_check').fetchone()[0])
    p.close();c.close();emit(phase='inspection',effects=effects,journal=journal,integrity=integrity)
def main():
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['init','intent','apply','probe','reconcile','inspect'])
    p.add_argument('--root',required=True)
    for x in ('attempt','subject','owner'):p.add_argument('--'+x,default='')
    p.add_argument('--fault',choices=['none','before_commit','after_commit_before_ack'],default='none')
    p.add_argument('--provider-available',choices=['yes','no'],default='yes')
    v=vars(p.parse_args());command=v.pop('command');root=Path(v.pop('root')).resolve()
    a={k:v[k] for k in ('attempt','subject','owner')}
    if command=='init':init(root)
    elif command=='intent':intent(root,a)
    elif command=='apply':apply(root,a,v['fault'])
    elif command=='probe':probe(root,a)
    elif command=='reconcile':reconcile(root,a,v['provider_available']=='yes')
    else:inspect(root)
if __name__=='__main__':main()

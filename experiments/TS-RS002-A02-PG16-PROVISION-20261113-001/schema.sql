-- NONPRODUCT, NOT EXECUTED. Apply only to separately admitted disposable schema.
-- PostgreSQL 16. Fixed-qualified identifiers; no dynamic SQL or Product tables.
CREATE SCHEMA ts_r3_global_head_20261107_001;
CREATE TABLE ts_r3_global_head_20261107_001.head (
  scope text PRIMARY KEY,
  revision bigint NOT NULL CHECK (revision >= 0),
  state_bytes bytea NOT NULL,
  state_sha256 text NOT NULL CHECK (state_sha256 ~ '^[0-9a-f]{64}$'),
  events_sha256 text NOT NULL CHECK (events_sha256 ~ '^[0-9a-f]{64}$'),
  last_event_hash text CHECK (last_event_hash IS NULL OR last_event_hash ~ '^[0-9a-f]{64}$')
);
CREATE TABLE ts_r3_global_head_20261107_001.events (
  scope text NOT NULL REFERENCES ts_r3_global_head_20261107_001.head(scope),
  revision bigint NOT NULL CHECK (revision >= 1),
  event_hash text NOT NULL CHECK (event_hash ~ '^[0-9a-f]{64}$'),
  previous_event_hash text,
  payload_bytes bytea NOT NULL,
  event_line bytea NOT NULL,
  PRIMARY KEY(scope,revision),
  UNIQUE(scope,event_hash)
);
CREATE TABLE ts_r3_global_head_20261107_001.receipts (
  scope text NOT NULL REFERENCES ts_r3_global_head_20261107_001.head(scope),
  mutation_id text NOT NULL,
  command_fingerprint text NOT NULL CHECK (command_fingerprint ~ '^[0-9a-f]{64}$'),
  expected_revision bigint NOT NULL CHECK (expected_revision >= 0),
  result_revision bigint NOT NULL CHECK (result_revision >= 1),
  event_hash text NOT NULL CHECK (event_hash ~ '^[0-9a-f]{64}$'),
  authority_fingerprint text NOT NULL CHECK (authority_fingerprint ~ '^[0-9a-f]{64}$'),
  PRIMARY KEY(scope,mutation_id),
  UNIQUE(scope,result_revision)
);

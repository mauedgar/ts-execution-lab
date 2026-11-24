-- NONPRODUCT disposable PostgreSQL fixture. No Product identities or credentials.
\set ON_ERROR_STOP on
CREATE ROLE rs011_authority LOGIN PASSWORD 'a01-disposable-authority' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE rs011_writer LOGIN PASSWORD 'a01-disposable-writer' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE rs011_observer LOGIN PASSWORD 'a01-disposable-observer' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
REVOKE CONNECT,TEMPORARY,CREATE ON DATABASE postgres FROM PUBLIC;
GRANT CONNECT ON DATABASE postgres TO rs011_authority,rs011_writer,rs011_observer;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA rs011_a01;
REVOKE ALL ON SCHEMA rs011_a01 FROM PUBLIC;
GRANT USAGE ON SCHEMA rs011_a01 TO rs011_authority,rs011_writer,rs011_observer;
CREATE TABLE rs011_a01.grants(
 scope text PRIMARY KEY, version integer NOT NULL CHECK(version > 0),
 active boolean NOT NULL, subject jsonb NOT NULL, expires_at timestamptz NOT NULL
);
CREATE TABLE rs011_a01.head(
 scope text PRIMARY KEY REFERENCES rs011_a01.grants(scope), revision integer NOT NULL CHECK(revision IN (0,1))
);
CREATE TABLE rs011_a01.events(
 scope text PRIMARY KEY REFERENCES rs011_a01.head(scope), revision integer NOT NULL CHECK(revision=1),
 payload jsonb NOT NULL
);
CREATE TABLE rs011_a01.receipts(
 scope text PRIMARY KEY REFERENCES rs011_a01.events(scope), mutation_id text NOT NULL,
 grant_version integer NOT NULL, subject jsonb NOT NULL, payload jsonb NOT NULL,
 revision integer NOT NULL CHECK(revision=1)
);
-- One grant per disposable scope; versions advance on revocation. The real
-- effective authority is deliberately this row, NOT a GitHub/cache mirror.
CREATE FUNCTION rs011_a01.revoke_grant(p_scope text,p_version integer)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,rs011_a01 AS $$
DECLARE g rs011_a01.grants%ROWTYPE;
BEGIN
 SELECT * INTO g FROM rs011_a01.grants WHERE scope=p_scope FOR UPDATE;
 IF NOT FOUND OR p_version IS NULL OR g.version<>p_version OR NOT g.active THEN
   RETURN 'DENIED';
 END IF;
 UPDATE rs011_a01.grants SET active=false,version=version+1 WHERE scope=p_scope;
 RETURN 'REVOKED';
END;
$$;
CREATE FUNCTION rs011_a01.apply_effect(p_scope text,p_version integer,p_subject jsonb,p_id text,p_payload jsonb)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,rs011_a01 AS $$
DECLARE g rs011_a01.grants%ROWTYPE; r rs011_a01.receipts%ROWTYPE; n integer;
BEGIN
 IF p_scope IS NULL OR p_version IS NULL OR p_subject IS NULL OR
    p_id IS NULL OR length(p_id)=0 OR p_payload IS NULL THEN RETURN 'DENIED'; END IF;
 -- All authorization changes and all effect admissions serialize on SAME row.
 SELECT * INTO g FROM rs011_a01.grants WHERE scope=p_scope FOR UPDATE;
 IF NOT FOUND THEN RETURN 'DENIED'; END IF;
 SELECT * INTO r FROM rs011_a01.receipts WHERE scope=p_scope;
 IF FOUND THEN
   IF r.mutation_id=p_id AND r.grant_version=p_version AND
      r.subject=p_subject AND r.payload=p_payload THEN RETURN 'ALREADY_COMMITTED'; END IF;
   RETURN 'CONFLICT';
 END IF;
 IF NOT g.active OR g.version<>p_version OR g.subject<>p_subject OR
    g.expires_at<=clock_timestamp() THEN RETURN 'DENIED'; END IF;
 UPDATE rs011_a01.head SET revision=1 WHERE scope=p_scope AND revision=0;
 GET DIAGNOSTICS n = ROW_COUNT;
 IF n<>1 THEN RAISE EXCEPTION 'STATE_INVARIANT'; END IF;
 INSERT INTO rs011_a01.events VALUES(p_scope,1,p_payload);
 INSERT INTO rs011_a01.receipts VALUES(p_scope,p_id,p_version,p_subject,p_payload,1);
 RETURN 'APPLIED';
END;
$$;
REVOKE ALL ON FUNCTION rs011_a01.revoke_grant(text,integer) FROM PUBLIC;
REVOKE ALL ON FUNCTION rs011_a01.apply_effect(text,integer,jsonb,text,jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION rs011_a01.revoke_grant(text,integer) TO rs011_authority;
GRANT EXECUTE ON FUNCTION rs011_a01.apply_effect(text,integer,jsonb,text,jsonb) TO rs011_writer;
GRANT SELECT ON rs011_a01.grants,rs011_a01.head,rs011_a01.events,rs011_a01.receipts TO rs011_observer;

-- Only synthetic identities, fixed case scopes. No actual Developer grant.
INSERT INTO rs011_a01.grants
SELECT s,1,true,'{"repo":"synthetic","branch":"fixture","tree":"tree1","taskcycle":"tc1","operation":"op1","attempt":"att1","subject":"effect1"}'::jsonb,
 CASE WHEN s='expired' THEN clock_timestamp()-interval '1 hour'
 ELSE clock_timestamp()+interval '1 hour' END
FROM unnest(ARRAY['revoke_first','effect_first','stale','wrong','duplicate','timeout','ack','rollback','expired']) s;
INSERT INTO rs011_a01.head SELECT scope,0 FROM rs011_a01.grants;

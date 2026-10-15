CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE services (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE incidents (
 id UUID PRIMARY KEY, service TEXT NOT NULL, title TEXT NOT NULL,
 description TEXT NOT NULL, severity TEXT NOT NULL CHECK(severity IN ('P1','P2','P3')),
 scenario_id TEXT, status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','ANALYSIS_FAILED','AWAITING_APPROVAL','APPROVED','REJECTED','RESOLVED')),
 analysis JSONB, last_error TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE approvals (
 id UUID PRIMARY KEY, incident_id UUID NOT NULL UNIQUE REFERENCES incidents(id),
 decision TEXT NOT NULL CHECK(decision IN ('APPROVE','REJECT')),
 reviewer TEXT NOT NULL, note TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE executions (
 incident_id UUID PRIMARY KEY REFERENCES incidents(id), approval_id UUID NOT NULL REFERENCES approvals(id),
 result JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE audit_events (id BIGSERIAL PRIMARY KEY, incident_id UUID REFERENCES incidents(id), event TEXT NOT NULL, detail JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE runbooks (id TEXT PRIMARY KEY, service TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, action TEXT NOT NULL, risk TEXT NOT NULL);
CREATE TABLE runbook_chunks (id TEXT PRIMARY KEY, runbook_id TEXT NOT NULL REFERENCES runbooks(id) ON DELETE CASCADE, content TEXT NOT NULL, embedding vector(1536) NOT NULL, embedding_model TEXT NOT NULL);
CREATE INDEX incidents_created ON incidents(created_at DESC);
CREATE INDEX chunks_runbook ON runbook_chunks(runbook_id);
CREATE INDEX events_incident ON audit_events(incident_id,id);

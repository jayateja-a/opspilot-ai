CREATE SEQUENCE IF NOT EXISTS ticket_number_seq START 1001;
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS ticket_number TEXT;
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS impact TEXT NOT NULL DEFAULT 'MEDIUM' CHECK (impact IN ('HIGH','MEDIUM','LOW'));
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS urgency TEXT NOT NULL DEFAULT 'MEDIUM' CHECK (urgency IN ('HIGH','MEDIUM','LOW'));
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS priority TEXT NOT NULL DEFAULT 'P3' CHECK (priority IN ('P1','P2','P3','P4'));
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS category TEXT NOT NULL DEFAULT 'APPLICATION';
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS assignment_group TEXT NOT NULL DEFAULT 'Application Support';
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS affected_ci TEXT;
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS reported_by TEXT NOT NULL DEFAULT 'Local operator';
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS source_channel TEXT NOT NULL DEFAULT 'OPS PILOT';
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS major_incident BOOLEAN NOT NULL DEFAULT FALSE;
UPDATE incidents SET ticket_number='INC-' || nextval('ticket_number_seq') WHERE ticket_number IS NULL;
ALTER TABLE incidents ALTER COLUMN ticket_number SET NOT NULL;
ALTER TABLE incidents ALTER COLUMN ticket_number SET DEFAULT ('INC-' || nextval('ticket_number_seq'));
CREATE UNIQUE INDEX IF NOT EXISTS incidents_ticket_number ON incidents(ticket_number);

CREATE TABLE IF NOT EXISTS configuration_items (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, ci_type TEXT NOT NULL, domain TEXT NOT NULL,
 environment TEXT NOT NULL DEFAULT 'LOCAL-LAB', owner_group TEXT NOT NULL DEFAULT 'Platform Support',
 health TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (health IN ('HEALTHY','DEGRADED','DOWN','UNKNOWN')),
 attributes JSONB NOT NULL DEFAULT '{}', updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS problem_records (
 id UUID PRIMARY KEY, ticket_number TEXT NOT NULL UNIQUE, title TEXT NOT NULL, description TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','UNDER_INVESTIGATION','KNOWN_ERROR','RESOLVED','CLOSED')),
 root_cause TEXT, workaround TEXT, owner_group TEXT NOT NULL DEFAULT 'Problem Management', created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS change_records (
 id UUID PRIMARY KEY, ticket_number TEXT NOT NULL UNIQUE, title TEXT NOT NULL, description TEXT NOT NULL,
 change_type TEXT NOT NULL DEFAULT 'NORMAL' CHECK (change_type IN ('STANDARD','NORMAL','EMERGENCY')),
 status TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','ASSESSMENT','AUTHORIZED','SCHEDULED','IMPLEMENTING','REVIEW','CLOSED','REJECTED')),
 risk TEXT NOT NULL DEFAULT 'MEDIUM' CHECK (risk IN ('LOW','MEDIUM','HIGH')), impact TEXT NOT NULL DEFAULT 'MEDIUM',
 implementation_plan TEXT NOT NULL DEFAULT '', rollback_plan TEXT NOT NULL DEFAULT '', reviewer TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS record_links (
 id BIGSERIAL PRIMARY KEY, source_type TEXT NOT NULL, source_id TEXT NOT NULL, target_type TEXT NOT NULL, target_id TEXT NOT NULL,
 relationship TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE(source_type,source_id,target_type,target_id,relationship)
);
CREATE TABLE IF NOT EXISTS rca_documents (
 id UUID PRIMARY KEY, incident_id UUID NOT NULL REFERENCES incidents(id), status TEXT NOT NULL DEFAULT 'DRAFT' CHECK(status IN ('DRAFT','REVIEWED','APPROVED')),
 title TEXT NOT NULL, body JSONB NOT NULL, approved_by TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS rca_incident_status ON rca_documents(incident_id,status);

ALTER TABLE incidents DROP CONSTRAINT IF EXISTS incidents_severity_check;
ALTER TABLE incidents ADD CONSTRAINT incidents_severity_check CHECK (severity IN ('P0','P1','P2','P3','P4','P5'));
ALTER TABLE incidents DROP CONSTRAINT IF EXISTS incidents_priority_check;
ALTER TABLE incidents ADD CONSTRAINT incidents_priority_check CHECK (priority IN ('P0','P1','P2','P3','P4','P5'));

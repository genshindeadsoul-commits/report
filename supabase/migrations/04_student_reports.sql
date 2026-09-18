-- Option A: minimal flat storage matching the current app's data model
-- (app/models/schemas.py StudentInput), used until the normalized
-- profile-based import system (01_init_schema.sql) is actually wired up
-- to the application code.
--
-- This table is intentionally NOT linked to students/student_enrollments
-- yet, to avoid guessing a mapping between the flat StudentInput shape
-- and the normalized schema ahead of that migration being designed.

CREATE TABLE student_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Denormalized identity fields, copied straight from StudentInput,
    -- so reports can be listed/searched without joins.
    student_name TEXT NOT NULL,
    class TEXT NOT NULL,
    section TEXT NOT NULL,
    roll_number TEXT NOT NULL,
    academic_year TEXT NOT NULL,

    -- Full StudentInput + calculated report_data, as JSON. This is the
    -- source of truth for what was generated/published.
    input_payload JSONB NOT NULL,
    report_payload JSONB,

    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'generated', 'published', 'locked'
    version INTEGER NOT NULL DEFAULT 1,

    published_at TIMESTAMPTZ,
    locked_at TIMESTAMPTZ,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT ck_student_report_status CHECK (status IN ('draft', 'generated', 'published', 'locked'))
);

CREATE INDEX idx_student_reports_student_name ON student_reports(student_name);
CREATE INDEX idx_student_reports_academic_year ON student_reports(academic_year);
CREATE INDEX idx_student_reports_status ON student_reports(status);

ALTER TABLE student_reports ENABLE ROW LEVEL SECURITY;

-- Admins and teachers can do everything. Students are not yet handled
-- here since student-facing access requires linking a report to a
-- specific auth user, which belongs to the normalized schema.
CREATE POLICY student_reports_staff_all ON student_reports
    FOR ALL
    USING (auth.jwt() -> 'app_metadata' ->> 'role' IN ('admin', 'teacher'))
    WITH CHECK (auth.jwt() -> 'app_metadata' ->> 'role' IN ('admin', 'teacher'));

-- Student Report Card System: Initial Schema
-- This migration establishes the core academic and import infrastructure.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- 1. CORE ACADEMIC MODEL
-- =============================================================================

-- Academic Years
CREATE TABLE academic_years (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE, -- e.g., "2026-27"
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active', -- 'active', 'archived'
    created_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT check_dates CHECK (end_date > start_date)
);

-- Classes
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Sections
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    academic_year_id UUID NOT NULL REFERENCES academic_years(id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(class_id, academic_year_id, name)
);

-- Students
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admission_number TEXT NOT NULL UNIQUE,
    external_student_id TEXT,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Student Enrollments
CREATE TABLE student_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    academic_year_id UUID NOT NULL REFERENCES academic_years(id) ON DELETE RESTRICT,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE RESTRICT,
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE RESTRICT,
    roll_number TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(student_id, academic_year_id)
);

-- =============================================================================
-- 2. SUBJECTS AND ASSESSMENTS
-- =============================================================================

-- Subjects
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    display_order INTEGER,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Exams
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    academic_year_id UUID NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    code TEXT,
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Assessments
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,
    max_marks NUMERIC(10, 2) NOT NULL CHECK (max_marks >= 0),
    weight NUMERIC(5, 2) DEFAULT 100.00 CHECK (weight >= 0 AND weight <= 100),
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Marks
CREATE TABLE marks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_enrollment_id UUID NOT NULL REFERENCES student_enrollments(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE RESTRICT,
    marks NUMERIC(10, 2),
    mark_status TEXT NOT NULL DEFAULT 'scored', -- 'scored', 'absent', 'exempt', 'missing', 'not_evaluated'
    source_import_id UUID, -- Link to imports table for traceability
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT ck_marks_status CHECK (mark_status IN ('scored', 'absent', 'exempt', 'missing', 'not_evaluated')),
    CONSTRAINT ck_marks_non_negative CHECK (marks >= 0),
    UNIQUE(student_enrollment_id, assessment_id)
);

-- =============================================================================
-- 3. IMPORT INFRASTRUCTURE
-- =============================================================================

-- Import Profiles
CREATE TABLE import_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    academic_year_id UUID REFERENCES academic_years(id) ON DELETE SET NULL,
    version INTEGER DEFAULT 1,
    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'deprecated', 'archived'
    signature JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT ck_profile_status CHECK (status IN ('draft', 'active', 'deprecated', 'archived'))
);

-- Imports
CREATE TABLE imports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES import_profiles(id) ON DELETE RESTRICT,
    filename TEXT NOT NULL,
    uploaded_by UUID, -- Reference to auth.users or profiles
    uploaded_at TIMESTAMPTZ DEFAULT now(),
    academic_year_id UUID REFERENCES academic_years(id) ON DELETE RESTRICT,
    status TEXT DEFAULT 'pending', -- 'pending', 'validated', 'committed', 'reversed'
    rows_processed INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,

    CONSTRAINT ck_import_status CHECK (status IN ('pending', 'validated', 'committed', 'reversed'))
);

-- =============================================================================
-- 4. REPORTING AND SNAPSHOTS
-- =============================================================================

-- Report Cards
CREATE TABLE report_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_enrollment_id UUID NOT NULL REFERENCES student_enrollments(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'draft', -- 'draft', 'generated', 'reviewed', 'published', 'locked'
    published_at TIMESTAMPTZ,
    locked_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT ck_report_status CHECK (status IN ('draft', 'generated', 'reviewed', 'published', 'locked'))
);

-- Report Card Snapshots
CREATE TABLE report_card_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_card_id UUID NOT NULL REFERENCES report_cards(id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID,

    UNIQUE(report_card_id, version)
);

-- =============================================================================
-- 5. INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX idx_students_admission_number ON students(admission_number);
CREATE INDEX idx_students_full_name ON students(full_name);
CREATE INDEX idx_enrollments_student ON student_enrollments(student_id);
CREATE INDEX idx_enrollments_section ON student_enrollments(section_id);
CREATE INDEX idx_marks_enrollment ON marks(student_enrollment_id);
CREATE INDEX idx_marks_assessment ON marks(assessment_id);
CREATE INDEX idx_import_profiles_name ON import_profiles USING gin (name gin_trgm_ops);
CREATE INDEX idx_snapshots_card ON report_card_snapshots(report_card_id);
CREATE INDEX idx_snapshots_payload ON report_card_snapshots USING gin (payload);

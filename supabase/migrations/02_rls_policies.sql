-- Student Report Card System: RLS Policies
-- This migration sets up the identity and access management layer.

-- 1. Role Definition
CREATE TYPE user_role AS ENUM ('admin', 'teacher', 'student');

-- 2. Profiles Table
-- Maps Supabase Auth users to our system roles
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    role user_role NOT NULL DEFAULT 'student',
    full_name TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Helper Function for Role Retrieval
-- Using SECURITY DEFINER to bypass RLS on the profiles table to avoid recursion
CREATE OR REPLACE FUNCTION get_my_role()
RETURNS user_role AS $$
  SELECT role FROM profiles WHERE id = auth.uid();
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- 4. Enable RLS on all tables
ALTER TABLE academic_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE marks ENABLE ROW LEVEL SECURITY;
ALTER TABLE import_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE imports ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_card_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 5. Define Policies

-- Generic Admin Policy: Admins have full access to everything
-- This is a reusable pattern. We create a policy for each table.

-- Profiles Table
CREATE POLICY "Profiles are viewable by owner and admins"
ON profiles FOR SELECT
USING (auth.uid() = id OR get_my_role() = 'admin');

CREATE POLICY "Profiles are editable by owner and admins"
ON profiles FOR UPDATE
USING (auth.uid() = id OR get_my_role() = 'admin');

-- Academic Configuration Tables (academic_years, classes, subjects, exams, assessments)
-- These are generally viewable by all authenticated users, but only editable by admins.

CREATE POLICY "Academic years are viewable by all authenticated" ON academic_years FOR SELECT USING (true);
CREATE POLICY "Academic years are editable by admins" ON academic_years FOR ALL USING (get_my_role() = 'admin');

CREATE POLICY "Classes are viewable by all authenticated" ON classes FOR SELECT USING (true);
CREATE POLICY "Classes are editable by admins" ON classes FOR ALL USING (get_my_role() = 'admin');

CREATE POLICY "Subjects are viewable by all authenticated" ON subjects FOR SELECT USING (true);
CREATE POLICY "Subjects are editable by admins" ON subjects FOR ALL USING (get_my_role() = 'admin');

CREATE POLICY "Exams are viewable by all authenticated" ON exams FOR SELECT USING (true);
CREATE POLICY "Exams are editable by admins" ON exams FOR ALL USING (get_my_role() = 'admin');

CREATE POLICY "Assessments are viewable by all authenticated" ON assessments FOR SELECT USING (true);
CREATE POLICY "Assessments are editable by admins" ON assessments FOR ALL USING (get_my_role() = 'admin');

-- Sections and Enrollments
CREATE POLICY "Sections are viewable by all authenticated" ON sections FOR SELECT USING (true);
CREATE POLICY "Sections are editable by admins" ON sections FOR ALL USING (get_my_role() = 'admin');

CREATE POLICY "Enrollments are viewable by owner, teachers, and admins"
ON student_enrollments FOR SELECT
USING (
    get_my_role() = 'admin'
    OR
    (get_my_role() = 'student' AND student_id = auth.uid())
    OR
    (get_my_role() = 'teacher') -- In a real system, this would be scoped to the teacher's assigned classes
);

-- Students Table
CREATE POLICY "Students are viewable by teachers and admins"
ON students FOR SELECT
USING (get_my_role() IN ('admin', 'teacher') OR id = auth.uid());

-- Marks Table
CREATE POLICY "Marks are viewable by owner, teachers, and admins"
ON marks FOR SELECT
USING (
    get_my_role() = 'admin'
    OR
    (get_my_role() = 'student' AND student_enrollment_id IN (
        SELECT id FROM student_enrollments WHERE student_id = auth.uid()
    ))
    OR
    (get_my_role() = 'teacher')
);

CREATE POLICY "Marks are editable by admins and teachers"
ON marks FOR ALL
USING (get_my_role() IN ('admin', 'teacher'));

-- Import Infrastructure
CREATE POLICY "Import profiles are viewable by admins and teachers"
ON import_profiles FOR SELECT
USING (get_my_role() IN ('admin', 'teacher'));

CREATE POLICY "Import profiles are editable by admins"
ON import_profiles FOR ALL
USING (get_my_role() = 'admin');

CREATE POLICY "Imports are viewable by admins and teachers"
ON imports FOR SELECT
USING (get_my_role() IN ('admin', 'teacher'));

CREATE POLICY "Imports are editable by admins and teachers"
ON imports FOR ALL
USING (get_my_role() IN ('admin', 'teacher'));

-- Reports and Snapshots
CREATE POLICY "Reports are viewable by owner, teachers, and admins"
ON report_cards FOR SELECT
USING (
    get_my_role() = 'admin'
    OR
    (get_my_role() = 'student' AND student_enrollment_id IN (
        SELECT id FROM student_enrollments WHERE student_id = auth.uid()
    ))
    OR
    (get_my_role() = 'teacher')
);

CREATE POLICY "Reports are editable by admins and teachers"
ON report_cards FOR ALL
USING (get_my_role() IN ('admin', 'teacher'));

CREATE POLICY "Snapshots are viewable by owner, teachers, and admins"
ON report_card_snapshots FOR SELECT
USING (
    get_my_role() = 'admin'
    OR
    EXISTS (
        SELECT 1 FROM report_cards
        WHERE report_cards.id = report_card_snapshots.report_card_id
        AND (
            (get_my_role() = 'student' AND report_cards.student_enrollment_id IN (
                SELECT id FROM student_enrollments WHERE student_id = auth.uid()
            ))
            OR get_my_role() = 'teacher'
        )
    )
);

# Database Schema: Student Report Card System

## 1. Core Academic Model

### `students`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique student identifier |
| `admission_number` | TEXT (Unique) | School-issued admission number |
| `external_student_id` | TEXT | ID from external systems |
| `full_name` | TEXT | Student's full name |
| `date_of_birth` | DATE | Date of birth |
| `status` | TEXT | Active, Alumni, Withdrawn |

### `academic_years`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique year identifier |
| `name` | TEXT | e.g., "2026-27" |
| `start_date` | DATE | Academic start date |
| `end_date` | DATE | Academic end date |
| `status` | TEXT | Active, Archived |

### `classes`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique class identifier |
| `name` | TEXT | e.g., "Grade 8" |
| `display_order` | INTEGER | Sorting order |

### `sections`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique section identifier |
| `class_id` | UUID (FK) | Reference to `classes` |
| `academic_year_id` | UUID (FK) | Reference to `academic_years` |
| `name` | TEXT | e.g., "Section A" |

### `student_enrollments`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique enrollment record |
| `student_id` | UUID (FK) | Reference to `students` |
| `academic_year_id` | UUID (FK) | Reference to `academic_years` |
| `class_id` | UUID (FK) | Reference to `classes` |
| `section_id` | UUID (FK) | Reference to `sections` |
| `roll_number` | TEXT | Roll number for that specific year/section |
| `status` | TEXT | Enrolled, Dropped |

## 2. Subjects and Assessments

### `subjects`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique subject identifier |
| `code` | TEXT | Subject code |
| `name` | TEXT | e.g., "Mathematics" |
| `display_order` | INTEGER | Sorting order |
| `active` | BOOLEAN | Is subject currently taught |

### `exams`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique exam identifier |
| `academic_year_id` | UUID (FK) | Reference to `academic_years` |
| `name` | TEXT | e.g., "Annual Examination" |
| `code` | TEXT | Exam code |
| `display_order` | INTEGER | Sorting order |

### `assessments`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique assessment identifier |
| `exam_id` | UUID (FK) | Reference to `exams` |
| `subject_id` | UUID (FK) | Reference to `subjects` |
| `max_marks` | NUMERIC | Maximum marks possible |
| `weight` | NUMERIC | Weightage for overall grade |
| `display_order` | INTEGER | Sorting order |

### `marks`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique mark identifier |
| `student_enrollment_id` | UUID (FK) | Reference to `student_enrollments` |
| `assessment_id` | UUID (FK) | Reference to `assessments` |
| `marks` | NUMERIC | The actual score |
| `mark_status` | TEXT | scored, absent, exempt, missing, not_evaluated |
| `source_import_id` | UUID (FK) | Reference to `imports` for traceability |

## 3. Import Infrastructure

### `import_profiles`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique profile identifier |
| `name` | TEXT | Profile name |
| `description` | TEXT | Purpose of the profile |
| `academic_year_id` | UUID (FK) | Reference to `academic_years` |
| `version` | INTEGER | Profile version |
| `status` | TEXT | draft, active, deprecated, archived |
| `signature` | JSONB | The structural signature of the workbook |

### `imports`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique import session identifier |
| `profile_id` | UUID (FK) | Profile used for this import |
| `filename` | TEXT | Original filename |
| `uploaded_by` | UUID (FK) | User who performed the import |
| `uploaded_at` | TIMESTAMPTZ | Timestamp of upload |
| `status` | TEXT | pending, validated, committed, reversed |
| `rows_processed` | INTEGER | Number of rows handled |
| `errors` | INTEGER | Number of validation errors |

## 4. Reporting and Snapshots

### `report_cards`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique report card identifier |
| `student_enrollment_id` | UUID (FK) | Reference to `student_enrollments` |
| `status` | TEXT | draft, generated, reviewed, published, locked |
| `published_at` | TIMESTAMPTZ | Timestamp of publication |
| `locked_at` | TIMESTAMPTZ | Timestamp of locking |
| `version` | INTEGER | Version of the report |

### `report_card_snapshots`
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique snapshot identifier |
| `report_card_id` | UUID (FK) | Reference to `report_cards` |
| `version` | INTEGER | Snapshot version |
| `payload` | JSONB | The full calculated data for the report |
| `created_at` | TIMESTAMPTZ | Timestamp |
| `created_by` | UUID (FK) | User who generated the snapshot |

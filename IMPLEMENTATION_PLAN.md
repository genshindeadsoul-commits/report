# Implementation Plan: Student Report Card System

This plan outlines the transition from the V1 stateless prototype to the production-ready system specified in `report.md`.

## Core Architectural Shift
Transition from a stateless "file-in/file-out" pipeline to a persistent, transactional system.

**Key Components:**
- **Database:** Supabase (PostgreSQL) for all academic data, import profiles, and report snapshots.
- **Import Pipeline:** Profile-based matching $\rightarrow$ Staging $\rightarrow$ Dry Run $\rightarrow$ Commit.
- **Report Engine:** Calculation $\rightarrow$ Snapshot $\rightarrow$ Preview/PDF.
- **Access Control:** RLS-backed roles (Admin, Teacher, Student/Parent).

## Milestone Breakdown

### Milestone 1: Repository Inspection & Architecture (Current)
- [ ] Inspect existing codebase and sample data.
- [ ] Define canonical database schema.
- [ ] Document system architecture and data flow.
- [ ] Initialize `IMPLEMENTATION_STATUS.md`.

### Milestone 2: Database & Infrastructure
- [ ] Set up Supabase project.
- [ ] Implement schema migrations (Students, AcademicYears, Classes, Sections, Enrollments, Subjects, Exams, Assessments, Marks, ImportProfiles, Imports, ReportCards, Snapshots).
- [ ] Configure database constraints and indexes for performance.
- [ ] Implement base RLS policies.

### Milestone 3: Authentication & RBAC
- [ ] Integrate Supabase Auth.
- [ ] Implement role-based access control (Admin, Teacher, Student/Parent).
- [ ] Create middleware for role verification.

### Milestone 4: Academic Configuration
- [ ] Build UI/API for managing Academic Years, Classes, Sections, and Subjects.
- [ ] Implement Grading Rule configuration.

### Milestone 5: Student Management
- [ ] Build Student master data management.
- [ ] Implement Enrollment system (mapping students to classes/sections per year).

### Milestone 6: Workbook Inspector
- [ ] Develop a reusable service to analyze Excel structure (sheets, headers, ranges, types).
- [ ] Implement header detection logic (identifying the table start).

### Milestone 7: Import Profile Builder
- [ ] Build the "Create Profile" workflow (Upload $\rightarrow$ Inspect $\rightarrow$ Map Fields $\rightarrow$ Map Subjects $\rightarrow$ Save).
- [ ] Implement structural signature generation for columns.
- [ ] Implement profile versioning.

### Milestone 8: Profile Matching Engine
- [ ] Develop deterministic matching logic based on structural signatures.
- [ ] Implement compatibility scoring (Strong, Moderate, Weak).
- [ ] Build "Unknown Workbook" fallback flow.

### Milestone 9: Validation, Staging & Dry Run
- [ ] Implement staging tables for imports.
- [ ] Build a validation engine (data types, range checks, duplicates).
- [ ] Create the "Dry Run" report (Summary of changes, errors, warnings).

### Milestone 10: Transactional Import
- [ ] Implement transactional commit (All-or-Nothing).
- [ ] Ensure import idempotency (prevent duplicate marks).
- [ ] Build import history and traceability.

### Milestone 11: Calculation Engine
- [ ] Implement authoritative calculation service (totals, percentages, grades).
- [ ] Add comprehensive unit tests for all grading scenarios.
- [ ] Ensure decimal-safe arithmetic.

### Milestone 12: Report Preview
- [ ] Build the web-based report preview.
- [ ] Sync preview data with the calculation engine.

### Milestone 13: Snapshots & Publication
- [ ] Implement report snapshotting (JSONB storage).
- [ ] Build the "Publish" and "Lock" workflow.
- [ ] Implement versioning for corrected reports.

### Milestone 14: PDF Generation
- [ ] Develop A4, brandable PDF templates.
- [ ] Implement server-side PDF rendering.
- [ ] Ensure consistency between web preview and PDF.

### Milestone 15: Bulk Operations
- [ ] Build bulk PDF generation jobs.
- [ ] Implement chunked processing and progress tracking.
- [ ] Implement ZIP archive generation for bulk downloads.

### Milestone 16: Secure Student Access
- [ ] Implement secure, token-based or authenticated access for parents/students.
- [ ] Ensure strict RLS to prevent cross-student access.

### Milestone 17: Hardening & Final QA
- [ ] Performance tuning (indexing, batching).
- [ ] Security audit (RLS, input validation).
- [ ] Full E2E testing of the complete lifecycle.
- [ ] Final build and deployment.

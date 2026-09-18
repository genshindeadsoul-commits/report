# System Architecture: Student Report Card System

## 1. High-Level Overview
The system is a professional academic reporting tool designed to manage the lifecycle of student report cards: from raw Excel data import to secure PDF distribution.

The central architectural principle is the **Import Profile**, which ensures that recurring imports are deterministic and safe, while still providing flexibility for new or changed Excel formats.

## 2. Core Data Flow

### A. The Import Pipeline
`Excel File` $\rightarrow$ `Workbook Inspector` $\rightarrow$ `Profile Matcher` $\rightarrow$ `Staging` $\rightarrow$ `Dry Run` $\rightarrow$ `Transactional Commit` $\rightarrow$ `Canonical Database`

1. **Workbook Inspector:** Analyzes the uploaded file for sheets, headers, and data types.
2. **Profile Matcher:** Compares the workbook's structural signature against saved **Import Profiles**.
3. **Staging:** Data is written to temporary staging tables to prevent polluting the authoritative database.
4. **Dry Run:** The system calculates the impact of the import (e.g., "1200 marks updated, 5 errors found") for human review.
5. **Transactional Commit:** Once approved, data is moved from staging to authoritative tables in a single ACID transaction.

### B. The Report Lifecycle
`Canonical Database` $\rightarrow$ `Calculation Engine` $\rightarrow$ `Report Snapshot` $\rightarrow$ `Preview/PDF` $\rightarrow$ `Publish/Lock`

1. **Calculation Engine:** A pure service that computes totals, percentages, and grades based on configured **Grading Rules**.
2. **Report Snapshot:** To ensure a published report never changes (even if marks are updated later), the final calculated state is saved as a JSONB snapshot.
3. **Preview/PDF:** The snapshot is rendered into a web preview and a brandable A4 PDF.
4. **Publish/Lock:** Reports are marked as "Published" and then "Locked," preventing further modification.

## 3. Key Components

### Import Profiles
- **Purpose:** Store the mapping between an Excel workbook's structure and the database schema.
- **Structural Signature:** Instead of using column letters (A, B, C), profiles use signatures (Normalized Header + Parent Header + Data Type + Relative Position).
- **Versioning:** Profiles are versioned. If a school changes its Excel format, a new profile version is created to maintain traceability.

### Calculation Engine
- **Statelessness:** The engine is a pure function: `(StudentData, Rules) => ReportData`.
- **Decimal Safety:** Uses high-precision arithmetic to avoid floating-point errors in official academic results.

### Security Model
- **Identity:** Integrated via Supabase Auth.
- **Authorization:** Role-based (Admin, Teacher, Student/Parent).
- **Data Isolation:** PostgreSQL Row Level Security (RLS) ensures that users only see data they are authorized to access (e.g., a parent only sees their own child's report).

## 4. Technical Stack
- **Frontend:** Next.js, TypeScript, Tailwind CSS.
- **Backend:** FastAPI (Python).
- **Database:** PostgreSQL (via Supabase).
- **PDF Generation:** Server-side rendering (e.g., ReportLab or similar).
- **Excel Processing:** SheetJS (Frontend) and pandas/openpyxl (Backend).

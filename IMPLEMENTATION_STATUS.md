# Implementation Status

## Completed
- [x] Backend imports and boots cleanly (fixed repo-wide escaped-docstring
      corruption + a class/function API mismatch in the report engine)
- [x] Calculation engine (grading, attendance, totals) — unit tested
- [x] DOCX generation (single student)
- [x] PDF generation (single student)
- [x] Combined multi-student PDF generation
- [x] Bulk ZIP generation
- [x] Excel upload/validation, template download
- [x] Frontend type-checks cleanly (fixed 5 real TS errors)
- [x] Supabase client wiring (app/db.py) with graceful "not configured" errors
- [x] Flat `student_reports` table + migration (Option A persistence)
- [x] Report preview now persists a draft row; publish/lock/view read real data

## In Progress
- [ ] End-to-end verification against a real Supabase project (pending
      SUPABASE_URL / SUPABASE_SERVICE_KEY / SUPABASE_JWT_SECRET being set)

## Not Started (by design — deferred to the profile-based import milestone)
- [ ] Import Profile Builder (workbook_inspector.py / profile_matcher.py /
      staging_service.py / commit_service.py are still stubs/mocks)
- [ ] Wiring the normalized academic schema (01_init_schema.sql:
      students, enrollments, classes, sections, subjects, exams,
      assessments, marks, import_profiles, imports, report_cards) into
      the application — the app currently uses a flat StudentInput model
      and the separate `student_reports` table (04_student_reports.sql)
- [ ] Student/parent-facing secure access (current auth is admin/teacher only)
- [ ] Report locking enforcement (locking a row doesn't yet prevent edits)

## Known Issues
- Two report-generation code paths exist (DOCX uses build_report()'s
  richer shape with insights/remarks; PDF uses a simpler CalculationEngine
  + PDFGenerator shape). They produce consistent numbers but different
  data shapes — worth unifying later, not blocking now.
- `/reports/generate/docx` and `/reports/bulk/combined-pdf` do not yet
  persist rows to `student_reports` the way `/reports/preview` does.

## Decisions Needed
- Whether/when to migrate from the flat `student_reports` model to the
  normalized profile-based schema (see docs/architecture.md).

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  previewReport,
  generateDocx,
  generatePdf,
  StudentInput,
  ReportData,
} from "@/lib/api";

const DEFAULT_SUBJECTS = ["English", "Mathematics", "Science", "Social Science", "Hindi"];

export default function CreateReportPage() {
  const [form, setForm] = useState({
    name: "",
    class: "",
    section: "",
    roll_number: "",
    academic_year: "2026-27",
    working_days: 180,
    present_days: 170,
    academic_performance: "Good",
    class_participation: "Active",
    behaviour: "Good",
    homework: "Usually Complete",
    teacher_remark: "",
  });
  const [marks, setMarks] = useState<Record<string, number>>(
    Object.fromEntries(DEFAULT_SUBJECTS.map((s) => [s, 0]))
  );
  const [report, setReport] = useState<ReportData | null>(null);
  const [editedObservation, setEditedObservation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function buildStudentInput(): StudentInput {
    return {
      name: form.name,
      class: form.class,
      section: form.section,
      roll_number: form.roll_number,
      academic_year: form.academic_year,
      subject_marks: marks,
      working_days: Number(form.working_days),
      present_days: Number(form.present_days),
      academic_performance: form.academic_performance,
      class_participation: form.class_participation,
      behaviour: form.behaviour,
      homework: form.homework,
      teacher_remark: form.teacher_remark || undefined,
    };
  }

  async function handlePreview() {
    setError("");
    setLoading(true);
    try {
      const data = await previewReport(buildStudentInput());
      setReport(data);
      setEditedObservation(data.editable_remark);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload(kind: "pdf" | "docx") {
    setError("");
    try {
      const student = buildStudentInput();
      if (kind === "pdf") await generatePdf(student, editedObservation);
      else await generateDocx(student, editedObservation);
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-6 py-10">
      <Link href="/" className="text-sm text-primary hover:underline">
        ← Back
      </Link>
      <h1 className="text-2xl font-bold mt-2 mb-6">Create Student Report</h1>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="card p-6 mb-6 space-y-4">
        <h2 className="font-semibold text-slate-700">Student Details</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Student Name">
            <input
              className="input-field"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </Field>
          <Field label="Academic Year">
            <input
              className="input-field"
              value={form.academic_year}
              onChange={(e) => setForm({ ...form, academic_year: e.target.value })}
            />
          </Field>
          <Field label="Class">
            <input
              className="input-field"
              value={form.class}
              onChange={(e) => setForm({ ...form, class: e.target.value })}
            />
          </Field>
          <Field label="Section">
            <input
              className="input-field"
              value={form.section}
              onChange={(e) => setForm({ ...form, section: e.target.value })}
            />
          </Field>
          <Field label="Roll Number">
            <input
              className="input-field"
              value={form.roll_number}
              onChange={(e) => setForm({ ...form, roll_number: e.target.value })}
            />
          </Field>
        </div>
      </div>

      <div className="card p-6 mb-6 space-y-4">
        <h2 className="font-semibold text-slate-700">Subject Marks (out of 100)</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {DEFAULT_SUBJECTS.map((subject) => (
            <Field label={subject} key={subject}>
              <input
                type="number"
                min={0}
                max={100}
                className="input-field"
                value={marks[subject]}
                onChange={(e) =>
                  setMarks({ ...marks, [subject]: Number(e.target.value) })
                }
              />
            </Field>
          ))}
        </div>
      </div>

      <div className="card p-6 mb-6 space-y-4">
        <h2 className="font-semibold text-slate-700">Attendance</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Working Days">
            <input
              type="number"
              className="input-field"
              value={form.working_days}
              onChange={(e) => setForm({ ...form, working_days: Number(e.target.value) })}
            />
          </Field>
          <Field label="Present Days">
            <input
              type="number"
              className="input-field"
              value={form.present_days}
              onChange={(e) => setForm({ ...form, present_days: Number(e.target.value) })}
            />
          </Field>
        </div>
      </div>

      <div className="card p-6 mb-6 space-y-4">
        <h2 className="font-semibold text-slate-700">Teacher Assessment</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <Select
            label="Academic Performance"
            value={form.academic_performance}
            options={["Outstanding", "Very Good", "Good", "Satisfactory", "Needs Improvement"]}
            onChange={(v) => setForm({ ...form, academic_performance: v })}
          />
          <Select
            label="Class Participation"
            value={form.class_participation}
            options={["Very Active", "Active", "Moderate", "Low"]}
            onChange={(v) => setForm({ ...form, class_participation: v })}
          />
          <Select
            label="Behaviour"
            value={form.behaviour}
            options={["Excellent", "Good", "Satisfactory", "Needs Attention"]}
            onChange={(v) => setForm({ ...form, behaviour: v })}
          />
          <Select
            label="Homework"
            value={form.homework}
            options={["Consistent", "Usually Complete", "Sometimes Incomplete", "Needs Improvement"]}
            onChange={(v) => setForm({ ...form, homework: v })}
          />
        </div>
        <Field label="Optional Teacher Remark">
          <textarea
            className="input-field"
            rows={2}
            value={form.teacher_remark}
            onChange={(e) => setForm({ ...form, teacher_remark: e.target.value })}
          />
        </Field>
      </div>

      <button className="btn-primary w-full mb-8" onClick={handlePreview} disabled={loading}>
        {loading ? "Calculating…" : "Preview Report"}
      </button>

      {report && (
        <div className="card p-6 space-y-4 mb-10">
          <h2 className="font-semibold text-lg">Report Preview</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <SummaryCard value={`${report.summary.percentage}%`} label="Percentage" />
            <SummaryCard value={report.summary.grade} label="Grade" />
            <SummaryCard value={`${report.attendance.percentage}%`} label="Attendance" />
            <SummaryCard value={report.summary.performance} label="Performance" />
          </div>

          <div className="text-sm space-y-1">
            <p>
              ★ Strongest Subject: <b>{report.insights.strongest_subject.subject}</b> (
              {report.insights.strongest_subject.percentage}%)
            </p>
            <p>
              ● Focus Area: <b>{report.insights.focus_subject.subject}</b> (
              {report.insights.focus_subject.percentage}%)
            </p>
            {report.insights.improvement && (
              <p>
                → Trend: <b>{report.insights.improvement.status}</b> (
                {report.insights.improvement.difference > 0 ? "+" : ""}
                {report.insights.improvement.difference} pts)
              </p>
            )}
          </div>

          <div>
            <label className="label-text">
              Teacher&apos;s Observation (edit before downloading)
            </label>
            <textarea
              className="input-field"
              rows={5}
              value={editedObservation}
              onChange={(e) => setEditedObservation(e.target.value)}
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button className="btn-primary" onClick={() => handleDownload("pdf")}>
              Generate PDF
            </button>
            <button className="btn-secondary" onClick={() => handleDownload("docx")}>
              Generate Word
            </button>
          </div>
        </div>
      )}
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="label-text">{label}</label>
      {children}
    </div>
  );
}

function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <Field label={label}>
      <select
        className="input-field"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </Field>
  );
}

function SummaryCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="bg-primary-light rounded-lg py-3 text-center">
      <div className="text-xl font-bold text-primary">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}
